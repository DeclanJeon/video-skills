"""Preserve mandatory upstream closure locally; dependency pins are not upload grants."""
import hashlib
from collections.abc import Mapping
from pathlib import Path
from typing import ClassVar, Literal, assert_never

from pydantic import BaseModel, ConfigDict, TypeAdapter

from production.files import verified_file
from production.models import ContractError, Frozen, Pin, Requirement, State


class Upstream(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")


class Speech(Upstream):
    id: str
    voice_artifact_id: str | None = None


class Spatial(Upstream):
    artifact_id: str | None = None


class Shot(Upstream):
    id: str
    speech: tuple[Speech, ...] = ()
    audio_cue_ids: tuple[str, ...] = ()
    asset_ids: tuple[str, ...] = ()
    character_ids: tuple[str, ...] = ()
    spatial: Spatial = Spatial()
    start_s: float | None = None
    end_s: float | None = None


class Panel(Upstream):
    id: str
    shot_id: str
    beat_ids: tuple[str, ...]
    image_asset_id: str | None = None
    source_sheet_asset_id: str | None = None
    asset_version_refs: dict[str, str | int] = {}


class Board(Upstream):
    panels: tuple[Panel, ...]
    synopsis_artifact_id: str | None = None


class Master(Upstream):
    asset_id: str


class Asset(Upstream):
    id: str
    version: str | int
    path: str
    sha256: str
    status: str
    source_asset_ids: tuple[str, ...] = ()
    master_asset_ref: Master | None = None


class Character(Upstream):
    id: str
    identity_sheet_asset_id: str | None = None
    ssot_artifact_id: str | None = None


class Artifact(Upstream):
    id: str
    type: str
    status: str = "draft"
    dependencies: tuple[str, ...] = ()
    asset_ids: tuple[str, ...] = ()
    required_asset_versions: dict[str, str | int] = {}


class Cue(Upstream):
    id: str
    asset_id: str | None = None
    shot_id: str | None = None
    start_s: float | None = None
    end_s: float | None = None


class Project(Upstream):
    shots: tuple[Shot, ...]
    storyboard: Board
    characters: tuple[Character, ...] = ()
    artifacts: tuple[Artifact, ...] = ()
    audio_cues: tuple[Cue, ...] = ()
    captions: tuple[Cue, ...] = ()
    asset_registry: tuple[Asset, ...] = ()
    look_asset_id: str | None = None


class AssetUse(Frozen):
    shot: str
    pin: Pin


class CoverageEnvelope(Frozen):
    format: Literal["production-coverage/1"] = "production-coverage/1"
    requirements: tuple[Requirement, ...]
    asset_uses: tuple[AssetUse, ...] = ()
    origin: Pin | None = None


def derive_coverage(path: Path) -> tuple[Requirement, ...]:
    source = TypeAdapter(CoverageEnvelope | Project).validate_json(path.read_bytes())
    match source:
        case CoverageEnvelope(requirements=requirements):
            return requirements
        case Project(shots=shots, storyboard=board):
            result: list[Requirement] = []
            ids = [s.id for s in shots]
            if len(set(ids)) != len(ids) or not ids:
                raise ContractError("coverage", "upstream shot IDs invalid")
            for shot in shots:
                panels = tuple(p.id for p in board.panels if p.shot_id == shot.id)
                if not panels:
                    raise ContractError("coverage", "shot has no approved panels")
                result.append(Requirement(id=f"shot:{shot.id}",shot=shot.id,panels=panels,locator=f"shots/{shot.id}"))
                result.extend(Requirement(id=f"cue:{shot.id}:{cue}",shot=shot.id,panels=panels,modality="audio",locator=f"shots/{shot.id}/audio_cue_ids/{cue}") for cue in shot.audio_cue_ids)
                result.extend(Requirement(id=f"speech:{sp.id}",shot=shot.id,panels=panels,modality="audio",locator=f"shots/{shot.id}/speech/{sp.id}") for sp in shot.speech)
            for panel in board.panels:
                if panel.shot_id not in ids:
                    raise ContractError("coverage", "panel has unknown shot")
                result.append(Requirement(id=f"panel:{panel.id}",shot=panel.shot_id,panels=(panel.id,),locator=f"storyboard/panels/{panel.id}"))
            for sid,beat in sorted({(p.shot_id,b) for p in board.panels for b in p.beat_ids}):
                result.append(Requirement(id=f"beat:{sid}:{beat}",shot=sid,panels=tuple(p.id for p in board.panels if p.shot_id==sid and beat in p.beat_ids),locator=f"storyboard/beats/{beat}"))
            if len({r.id for r in result}) != len(result):
                raise ContractError("coverage", "duplicate upstream coverage IDs")
            return tuple(result)
        case unreachable:
            assert_never(unreachable)


def _overlaps(cue: Cue, shot: Shot) -> bool:
    return bool(cue.shot_id == shot.id or (cue.start_s is not None and cue.end_s is not None and shot.start_s is not None and shot.end_s is not None and cue.start_s < shot.end_s and cue.end_s > shot.start_s))


def _merge_versions(existing: Mapping[str,str | int], incoming: Mapping[str,str | int]) -> Mapping[str,str | int]:
    for key,value in incoming.items():
        if key in existing and str(existing[key]) != str(value):
            raise ContractError("asset",f"conflicting dependency versions for {key}")
    return {**existing,**incoming}


def derive_asset_uses(path: Path) -> tuple[AssetUse, ...]:
    """Closure mirrors upstream project_index dependencies; retained locally, not blanket uploaded."""
    source=TypeAdapter(CoverageEnvelope | Project).validate_json(path.read_bytes())
    match source:
        case CoverageEnvelope(asset_uses=uses):
            return uses
        case Project() as project:
            result: list[AssetUse]=[]
            assets={a.id:a for a in project.asset_registry}
            artifacts={a.id:a for a in project.artifacts}
            characters={c.id:c for c in project.characters}
            if len(assets) != len(project.asset_registry) or len(artifacts) != len(project.artifacts) or len(characters) != len(project.characters):
                raise ContractError("asset","duplicate upstream asset/artifact/character IDs")
            owners: dict[str,set[str]]={}
            for art in project.artifacts:
                for aid in art.asset_ids:
                    owners.setdefault(aid,set()).add(art.id)
            for shot in project.shots:
                pending_assets=list(shot.asset_ids)
                pending_artifacts=[sp.voice_artifact_id for sp in shot.speech if sp.voice_artifact_id]
                if shot.spatial.artifact_id:
                    pending_artifacts.append(shot.spatial.artifact_id)
                if project.storyboard.synopsis_artifact_id:
                    pending_artifacts.append(project.storyboard.synopsis_artifact_id)
                if project.look_asset_id:
                    pending_assets.append(project.look_asset_id)
                for cid in shot.character_ids:
                    char=characters.get(cid)
                    if char is None or not char.identity_sheet_asset_id:
                        raise ContractError("asset", f"missing character/identity {cid}")
                    pending_assets.append(char.identity_sheet_asset_id)
                    if char.ssot_artifact_id:
                        pending_artifacts.append(char.ssot_artifact_id)
                pins: Mapping[str,str | int]={}
                for panel in project.storyboard.panels:
                    if panel.shot_id == shot.id:
                        pending_assets.extend(a for a in (panel.image_asset_id,panel.source_sheet_asset_id) if a)
                        pins=_merge_versions(pins,panel.asset_version_refs)
                pending_assets.extend(pins)
                for cue in (*project.audio_cues,*project.captions):
                    if cue.id in shot.audio_cue_ids or _overlaps(cue,shot):
                        if cue.asset_id:
                            pending_assets.append(cue.asset_id)
                seen_assets: set[str]=set()
                seen_artifacts: set[str]=set()
                while pending_assets or pending_artifacts:
                    while pending_assets:
                        aid=pending_assets.pop()
                        asset=assets.get(aid)
                        if asset is None or asset.status not in {"available","verified"}:
                            raise ContractError("asset",f"missing/current asset {aid}")
                        if aid in pins and str(pins[aid]) != str(asset.version):
                            raise ContractError("asset",f"panel/artifact asset version drift {aid}")
                        if aid in seen_assets:
                            continue
                        seen_assets.add(aid)
                        pending_assets.extend(asset.source_asset_ids)
                        if asset.master_asset_ref:
                            pending_assets.append(asset.master_asset_ref.asset_id)
                        pending_artifacts.extend(owners.get(aid,()))
                    if pending_artifacts:
                        aid=pending_artifacts.pop()
                        if aid in seen_artifacts:
                            continue
                        art=artifacts.get(aid)
                        if art is None or art.status == "stale":
                            raise ContractError("asset",f"missing/stale artifact {aid}")
                        seen_artifacts.add(aid)
                        pending_artifacts.extend(art.dependencies)
                        pending_assets.extend(art.asset_ids)
                        pins=_merge_versions(pins,art.required_asset_versions)
                        pending_assets.extend(art.required_asset_versions)
                        if art.type in {"storyboard","storyboard_sheet"}:
                            if project.look_asset_id:
                                pending_assets.append(project.look_asset_id)
                            for panel in project.storyboard.panels:
                                pending_assets.extend(a for a in (panel.image_asset_id,panel.source_sheet_asset_id) if a)
                                pins=_merge_versions(pins,panel.asset_version_refs)
                                pending_assets.extend(panel.asset_version_refs)
                result.extend(AssetUse(shot=shot.id,pin=Pin(id=aid,version=str(assets[aid].version),sha256=assets[aid].sha256,path=assets[aid].path)) for aid in sorted(seen_assets))
            return tuple(result)
        case unreachable:
            assert_never(unreachable)


def export_coverage(path: Path) -> CoverageEnvelope:
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    return CoverageEnvelope(requirements=derive_coverage(path),asset_uses=derive_asset_uses(path),origin=Pin(id="UPSTREAM-SNAPSHOT",version=digest,sha256=digest,path=path.name))


def verify_scope(state: State, root: Path) -> None:
    from production.contracts import validate_state
    validate_state(state)
    path=verified_file(root,state.coverage_source)
    if derive_coverage(path) != state.approved_coverage:
        raise ContractError("coverage","approved source differs from pinned coverage set")
    source=TypeAdapter(CoverageEnvelope | Project).validate_json(path.read_bytes())
    match source:
        case CoverageEnvelope(origin=origin_pin) if origin_pin is not None:
            origin=verified_file(root,origin_pin)
            if origin == path or derive_coverage(origin) != source.requirements or derive_asset_uses(origin) != source.asset_uses:
                raise ContractError("coverage","exported upstream closure differs from original")
        case CoverageEnvelope() | Project():
            pass
        case unreachable:
            assert_never(unreachable)
    for clip in state.batch.clips:
        for pin in (*clip.assets,*clip.dependencies):
            _=verified_file(root,pin)
    for use in derive_asset_uses(path):
        _=verified_file(root,use.pin)
        consumers=[c for c in state.batch.clips if use.shot in c.shots]
        if not consumers or any(use.pin not in (*c.assets,*c.dependencies) for c in consumers):
            raise ContractError("asset",f"mandatory design pin omitted/replaced: {use.shot}/{use.pin.id}")
