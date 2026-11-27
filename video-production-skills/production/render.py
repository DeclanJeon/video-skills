"""Deterministic local review-only montage and source-range lineage."""
import hashlib
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Literal

from production.files import verified_file
from production.handoff import current, selection_hash
from production.media import probe_media
from production.models import ClipId, ContractError, Frozen, Pin, ReviewRender, SourceRange, State


class Slice(Frozen):
    clip_id: ClipId
    take_id: str
    source: Pin
    source_range: SourceRange
    acceptance_revision: int
    range_revision: int


class RenderManifest(Frozen):
    format: Literal["production-review-render/1"] = "production-review-render/1"
    selection_hash: str
    artifact: Pin
    sources: tuple[Slice, ...]


def slices(state: State) -> tuple[Slice, ...]:
    result: list[Slice] = []
    for cid in state.batch.edit_order:
        selected = next((s for s in state.selections if s.take.clip_id == cid), None)
        if selected is None or not current(state, selected):
            raise ContractError("coverage", "review montage needs every current source")
        result.append(Slice(clip_id=cid,take_id=selected.take.id,source=selected.take.asset,
            source_range=selected.take.source_range,acceptance_revision=selected.acceptance_revision,
            range_revision=selected.take.range_revision))
    return tuple(result)


def _output(root: Path, relative: str) -> Path:
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts:
        raise ContractError("path", "review output must stay inside project")
    path = root.resolve()
    for part in rel.parts:
        path /= part
        if path.is_symlink():
            raise ContractError("path", "output symlink refused")
    if path.exists():
        raise ContractError("exists", "review outputs are immutable; choose a new version")
    return path


def _pin(root: Path, path: Path, name: str) -> Pin:
    return Pin(id=name,version="1",path=path.relative_to(root.resolve()).as_posix(),sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def render_review(state: State, root: Path, output: str) -> ReviewRender:
    source_slices = slices(state)
    target = _output(root, output)
    manifest_path = _output(root, output + ".sources.json")
    sources = [verified_file(root,s.source) for s in source_slices]
    probes = [probe_media(root,s.source) for s in source_slices]
    if len({(p.width,p.height,p.fps,p.has_audio) for p in probes}) != 1 or not all(p.cfr for p in probes):
        raise ContractError("conform", "mixed formats/audio/VFR need an explicitly approved conform route")
    target.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=root,prefix=".review-render-") as temp:
        work = Path(temp)
        try:
            for i,(source,sl,probe) in enumerate(zip(sources,source_slices,probes)):
                args = ["ffmpeg","-v","error","-xerror","-i",str(source),"-vf",f"trim=start_frame={sl.source_range.start}:end_frame={sl.source_range.end},setpts=PTS-STARTPTS"]
                if probe.has_audio:
                    args += ["-af",f"atrim=start={sl.source_range.start/probe.fps}:end={sl.source_range.end/probe.fps},asetpts=PTS-STARTPTS","-c:a","aac"]
                else:
                    args += ["-an"]
                args += ["-c:v","libx264","-preset","ultrafast","-pix_fmt","yuv420p",str(work/f"part{i}.mp4")]
                _ = subprocess.run(args,capture_output=True,check=True,timeout=90)
            listing=work/"concat.txt"
            _ = listing.write_text("".join(f"file 'part{i}.mp4'\n" for i in range(len(sources))))
            rendered=work/"review.mp4"
            _ = subprocess.run(["ffmpeg","-v","error","-xerror","-f","concat","-safe","1","-i",str(listing),"-c","copy",str(rendered)],capture_output=True,check=True,timeout=90)
            with target.open("xb") as out, rendered.open("rb") as inp:
                shutil.copyfileobj(inp,out)
        except (subprocess.CalledProcessError,subprocess.TimeoutExpired,FileNotFoundError) as exc:
            raise ContractError("render", "local review render failed; no remote jobs started") from exc
    artifact = _pin(root,target,"REVIEW-VIDEO")
    manifest = RenderManifest(selection_hash=selection_hash(state),artifact=artifact,sources=source_slices)
    with manifest_path.open("x") as out:
        _ = out.write(manifest.model_dump_json(indent=2))
    proof=ReviewRender(artifact=artifact,manifest=_pin(root,manifest_path,"REVIEW-LINEAGE"),selection_hash=selection_hash(state))
    verify_render(state,root,proof)
    return proof


def verify_render(state: State, root: Path, proof: ReviewRender) -> None:
    path=verified_file(root,proof.manifest)
    manifest=RenderManifest.model_validate_json(path.read_bytes())
    if (proof.selection_hash != selection_hash(state) or manifest.selection_hash != proof.selection_hash
        or manifest.sources != slices(state) or manifest.artifact != proof.artifact):
        raise ContractError("flow", "review montage lineage is stale/mismatched")
    result=probe_media(root,proof.artifact)
    expected=sum((s.take.source_range.end-s.take.source_range.start)/s.take.fps for s in state.selections)
    if abs(result.frame_count/result.fps-expected) > 1/result.fps:
        raise ContractError("flow", "review artifact does not cover full selected duration")
