"""Independent review F1-F4 regressions; operator/semantic records are fixtures."""
import json

import pytest

from conftest import pin, require
from production.models import ContractError
from test_bindings import prepare
from test_handoff import all_selected, flow_for, joins_for
from test_quality import candidate


@pytest.mark.parametrize("mutation", ["delete", "replace"])
def test_library_handoff_when_delivered_source_changes(seed,tmp_path,mutation):
    # Given: matching current reports, then a source disappears or changes on disk.
    state=all_selected(seed,tmp_path)
    state=state.model_copy(update={"join_reviews":joins_for(state)})
    flow=flow_for(state)
    path=tmp_path/state.selections[0].take.asset.path
    if mutation == "delete":
        path.unlink()
    else:
        path.write_text("unexpected replacement bytes")
    # When / Then: successful reports cannot deliver nonexistent/unpinned originals.
    with pytest.raises(ContractError,match="path|hash"):
        require("handoff","build_handoff")(state,flow,"post","rights", tmp_path)


def upstream_identity(tmp_path):
    identity=pin(tmp_path,"identity.dat","synthetic identity asset")
    source={"shots":[{"id":"SH1","character_ids":["CHR1"],"asset_ids":[]}],"characters":[{"id":"CHR1","identity_sheet_asset_id":identity.id}],"storyboard":{"panels":[{"id":"P1","shot_id":"SH1","beat_ids":["B1"]}]},"asset_registry":[{**identity.model_dump(),"status":"verified"}]}
    return source,identity


def test_character_identity_when_upstream_relation_not_in_direct_assets(seed,tmp_path):
    # Given: identity is mandatory through shot.character_ids, not shot.asset_ids.
    source,identity=upstream_identity(tmp_path)
    source_pin=pin(tmp_path,"character-project.json",json.dumps(source))
    coverage=require("adapters","derive_coverage")(tmp_path/source_pin.path)
    clip=seed.batch.clips[0].model_copy(update={"assets":(),"shots":("SH1",),"requirements":tuple(r.id for r in coverage)})
    batch=seed.batch.model_copy(update={"coverage":coverage,"clips":(clip,),"edit_order":(clip.id,),"joins":()})
    state=seed.model_copy(update={"batch":batch,"coverage_source":source_pin,"approved_coverage":coverage})
    # When / Then: source projection cannot silently discard the character dependency.
    with pytest.raises(ContractError,match="asset"):
        require("adapters","verify_scope")(state,tmp_path)


@pytest.mark.parametrize("change", ["duration", "aspect", "scope"])
def test_approval_when_settings_exceed_same_grant(seed,capability,authority,tmp_path,change):
    # Given: capability can support more than the original approval.
    cap=capability
    state=seed
    if change == "duration":
        clip=seed.batch.clips[0].model_copy(update={"duration_s":20})
        state=seed.model_copy(update={"batch":seed.batch.model_copy(update={"clips":(clip,*seed.batch.clips[1:])})})
        cap=capability.model_copy(update={"durations":(2,20)})
    elif change == "aspect":
        cap=capability.model_copy(update={"width":720,"height":1280})
    else:
        state=seed.model_copy(update={"batch":seed.batch.model_copy(update={"scope_revision":"not-approved"})})
    # When / Then: same authority does not silently authorize a longer/different configuration.
    with pytest.raises(ContractError,match="authority"):
        prepare(state,cap,authority,tmp_path)


def test_commit_when_approval_evidence_changed(seed,capability,authority,tmp_path):
    # Given: successful fixture receipt and real decodable candidate; approval pin then drifts.
    state,take,review=candidate(seed,capability,authority,tmp_path)
    (tmp_path/authority.evidence.path).write_text("APPROVAL REVOKED / REPLACED")
    # When / Then: historical remote success is retained, but current QA cannot publish.
    with pytest.raises(ContractError,match="hash|approval"):
        require("quality","accept_take")(state,take,review,take.fingerprint,tmp_path)


def test_revalidate_when_approval_evidence_changed(seed,capability,authority,tmp_path):
    # Given: accepted selection whose approval evidence is replaced.
    state,take,review=candidate(seed,capability,authority,tmp_path)
    state=require("quality","accept_take")(state,take,review,take.fingerprint,tmp_path)
    (tmp_path/authority.evidence.path).write_text("APPROVAL REVOKED / REPLACED")
    # When / Then: revalidation cannot bypass the applicable current approval pin.
    with pytest.raises(ContractError,match="hash|approval"):
        require("quality","revalidate_take")(state,"C1",review,take.fingerprint,tmp_path)


@pytest.mark.parametrize("mutation", ["delete", "replace"])
def test_cli_handoff_when_source_changes_after_render(seed,tmp_path,mutation):
    # Given: an actual local montage, then source bytes drift after its render.
    from test_media import make_video
    from test_cli import cli
    from production.store import ProjectStore
    from production.render import render_review
    state=all_selected(seed,tmp_path)
    selected=[]
    for i,s in enumerate(state.selections):
        asset=make_video(tmp_path,f"handoff-original-{i}.mp4",color=("blue","green","red")[i])
        selected.append(s.model_copy(update={"take":s.take.model_copy(update={"asset":asset}),"review":s.review.model_copy(update={"playback":s.review.playback.model_copy(update={"asset_hash":asset.sha256})})}))
    state=state.model_copy(update={"selections":tuple(selected)})
    state=state.model_copy(update={"join_reviews":joins_for(state)})
    proof=render_review(state,tmp_path,"qa/handoff-review.mp4")
    store=ProjectStore(tmp_path/"ledger.json");store.initialize(seed)
    with store.transaction(0) as tx:
        tx.state=state
    state=store.read()
    flow=flow_for(state).model_copy(update={"review_render":proof})
    report=tmp_path/"flow.json";report.write_text(flow.model_dump_json())
    target=tmp_path/state.selections[0].take.asset.path
    if mutation == "delete":
        target.unlink()
    else:
        target.write_bytes(b"replaced after render")
    # When: the public delivery boundary runs against the preserved montage.
    result=cli("handoff",tmp_path/"ledger.json",report,"fixture-post","fixture-rights")
    # Then: G5 blocks rather than delivering records for missing/replaced media.
    assert result.returncode != 0
    assert json.loads(result.stdout)["status"] == "blocked"


def test_coverage_export_when_identity_and_lineage_are_mandatory(seed,tmp_path):
    # Given: identity, panel version, and master/source lineage in upstream schema.
    from test_cli import cli
    source,identity=upstream_identity(tmp_path)
    origin=pin(tmp_path,"identity-master.dat","original master")
    prop=pin(tmp_path,"prop.dat","prop fixture")
    source["asset_registry"][0]["source_asset_ids"]=[origin.id]
    source["asset_registry"] += [{**origin.model_dump(),"status":"verified"},{**prop.model_dump(),"status":"verified"}]
    source["storyboard"]["panels"][0]["asset_version_refs"]={prop.id:"1"}
    project=tmp_path/"upstream.json";project.write_text(json.dumps(source))
    # When: exporting the public coverage envelope.
    result=cli("coverage",project)
    assert result.returncode == 0,result.stdout+result.stderr
    envelope=json.loads(result.stdout)
    # Then: ID-only projection no longer drops closure; local dependencies need not all be uploaded.
    assert {u["pin"]["id"] for u in envelope["asset_uses"]} == {identity.id,origin.id,prop.id}
    scope=pin(tmp_path,"exported-scope.json",result.stdout)
    coverage=require("adapters","derive_coverage")(tmp_path/scope.path)
    clip=seed.batch.clips[0].model_copy(update={"assets":(),"dependencies":(identity,origin,prop),"shots":("SH1",),"requirements":tuple(r.id for r in coverage)})
    batch=seed.batch.model_copy(update={"coverage":coverage,"clips":(clip,),"edit_order":(clip.id,),"joins":()})
    state=seed.model_copy(update={"batch":batch,"coverage_source":scope,"approved_coverage":coverage})
    require("adapters","verify_scope")(state,tmp_path)


def test_panel_pin_when_registered_version_drifted(seed,tmp_path):
    # Given: panel requires version 1, registry silently supplies version 2.
    source,identity=upstream_identity(tmp_path)
    source["storyboard"]["panels"][0]["asset_version_refs"]={identity.id:"wrong-version"}
    project=tmp_path/"drift.json";project.write_text(json.dumps(source))
    # When / Then: closure must preserve exact version pins, not just asset IDs.
    with pytest.raises(ContractError,match="version"):
        require("adapters","derive_asset_uses")(project)


def test_panel_pins_when_two_views_disagree_on_same_asset(tmp_path):
    # Given: last-wins parsing would hide the first panel's incompatible version.
    source,identity=upstream_identity(tmp_path)
    source["asset_registry"][0]["version"]="2"
    source["storyboard"]["panels"][0]["asset_version_refs"]={identity.id:"1"}
    source["storyboard"]["panels"].append({"id":"P2","shot_id":"SH1","beat_ids":["B1"],"asset_version_refs":{identity.id:"2"}})
    project=tmp_path/"conflicting-panels.json";project.write_text(json.dumps(source))
    # When / Then: conflicting pinned versions are rejected rather than overwritten.
    with pytest.raises(ContractError,match="version"):
        require("adapters","derive_asset_uses")(project)


def test_scope_projection_when_existing_upstream_closure_agrees(tmp_path):
    # Given: representative upstream character, panels, source lineage, voice and cue dependencies.
    import os,subprocess,sys
    from pathlib import Path
    source,identity=upstream_identity(tmp_path)
    records={identity.id:source["asset_registry"][0]}
    for name in ("MASTER","LOOK","PROP","BOARD","SSOTDOC","STORYDOC","VOICEAUDIO","AMB","CAPTION"):
        asset=pin(tmp_path,f"{name}.dat",f"local dependency {name}")
        records[name]={**asset.model_dump(),"id":name,"status":"verified"}
    records[identity.id]["source_asset_ids"]=["MASTER"]
    source["asset_registry"]=list(records.values())
    source["look_asset_id"]="LOOK"
    source["characters"][0]["ssot_artifact_id"]="SSOT"
    source["shots"][0].update(scene_id="S1",start_s=0,end_s=2,audio_cue_ids=["AMB1"],speech=[{"id":"D1","voice_artifact_id":"VOICE"}])
    source["storyboard"]["synopsis_artifact_id"]="STORY"
    source["storyboard"]["panels"][0].update(image_asset_id="BOARD",asset_version_refs={"PROP":"1"})
    source["artifacts"]=[{"id":"SSOT","type":"character_sheet","asset_ids":["SSOTDOC"],"dependencies":["STORY"]},{"id":"STORY","type":"synopsis","asset_ids":["STORYDOC"]},{"id":"VOICE","type":"voice","asset_ids":["VOICEAUDIO"]}]
    for artifact in source["artifacts"]:
        artifact["version"]="v1"
    source["audio_cues"]=[{"id":"AMB1","shot_id":"SH1","start_s":0,"end_s":2,"asset_id":"AMB"}]
    source["captions"]=[{"id":"CAP1","shot_id":"SH1","start_s":0,"end_s":2,"asset_id":"CAPTION"}]
    path=tmp_path/"closure-project.json";path.write_text(json.dumps(source))
    upstream=Path.home()/".pi/agent/skills/video-production-assets/scripts"
    code="import json,sys;from project_index import build_index;p=json.load(open(sys.argv[1]));print(json.dumps(sorted(a['id'] for a in build_index(p,['SH1'])['asset_registry'])))"
    result=subprocess.run([sys.executable,"-c",code,str(path)],capture_output=True,text=True,env={**os.environ,"PYTHONPATH":str(upstream),"PYTHONDONTWRITEBYTECODE":"1"})
    assert result.returncode == 0,result.stderr
    # When: our typed projection resolves the same concrete upstream source.
    uses=require("adapters","derive_asset_uses")(path)
    # Then: closure is not reduced to only direct shot.asset_ids.
    assert sorted(u.pin.id for u in uses) == json.loads(result.stdout)
