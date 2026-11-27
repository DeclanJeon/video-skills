"""Actual EffectCraft comp/layer/linear keys/RGBA sequence; no MOGRT or artist-quality claims."""
import json
import pytest
from conftest import require
from support import fixture,modify_authority,json_pin


def setup(root,**recipe_changes):
    request,production,handoff=fixture(root)
    modify_authority(root,request,allowed_changes=["composite"])
    path=root/"project.json";path.write_text(json.dumps({"production":production.model_dump(mode="json")}))
    intake=require("intake","load_intake")(root,root/"request.json",path)
    timeline=require("timeline","build_timeline")(intake)
    state=require("state_models","PostState")(intake=intake,timelines=(timeline,))
    store=require("ledger","PostStore")(path);store.initialize(state)
    recipe={"format":"post-motion/1","width":160,"height":90,"fps":{"num":24,"den":1},"frame_count":12,
        "start_frame":0,"box_width":40,"box_height":30,"color":"#ff0000","start_position":[40,45],"end_position":[120,45],**recipe_changes}
    rp=json_pin(root,"motion-recipe.json",recipe)
    order=require("work_models","WorkOrder").model_validate_json(json.dumps({"id":"NATIVE-MOTION","domain":"motion","branch":"main","backend":"effectcraft","source_refs":[intake.sources[0].source.model_dump()],"recipe":rp.model_dump(),"output":"plates/motion-manifest.json"}))
    backend=require("backends.effectcraft","EffectCraftBackend")(store,root/"effect-native")
    cap=backend.inspect()
    return store,backend,order,cap


def rendered(root):
    store,backend,order,cap=setup(root)
    packet=backend.prepare(order,cap,store.read_recorded().intake.authority)
    with store.transaction(0) as tx:tx.state=require("jobs","reserve_work")(tx.state,packet)
    receipt=backend.execute(packet);assert receipt.phase=="succeeded"
    return store,backend,packet,backend.observe(store.read_recorded().jobs[0])


def test_effectcraft_when_actual_rgba_sequence_and_keys_are_independently_verified(tmp_path):
    store,backend,packet,value=rendered(tmp_path)
    assert value.technical_verified is True
    assert value.frame_count==12
    assert len(value.frames)==12
    manifest=require("backends.effect_models","PlateManifest").model_validate_json((tmp_path/value.artifact.path).read_bytes())
    assert manifest.alpha_mode=="straight"
    assert manifest.color_assignment=="unassigned"
    assert manifest.bounds[0].left==20 and manifest.bounds[0].right==60
    assert manifest.bounds[-1].left==93 and manifest.bounds[-1].right==134
    assert all(m.relation=="work_context" for m in value.mapping)
    assert not store.read_recorded().artifacts


@pytest.mark.parametrize("changes",[{"fps":{"num":30,"den":1}},{"width":200},{"authorApp":"ppro"},{"frame_count":0}])
def test_effectcraft_when_unapproved_format_or_guessed_template_compatibility_is_rejected(tmp_path,changes):
    store,backend,order,cap=setup(tmp_path,**changes)
    with pytest.raises(require("errors","ContractError")):
        backend.prepare(order,cap,store.read_recorded().intake.authority)


def test_effectcraft_when_any_plate_frame_is_missing_cannot_materialize(tmp_path):
    store,backend,packet,value=rendered(tmp_path)
    (tmp_path/value.frames[3].path).unlink()
    with pytest.raises(require("errors","ContractError")):
        backend.observe(store.read_recorded().jobs[0])


def test_effectcraft_when_native_comp_or_keys_were_edited_requires_reimport(tmp_path):
    store,backend,packet,value=rendered(tmp_path)
    path=tmp_path/value.native_project.path
    raw=json.loads(path.read_text());raw["settings"]["linearize"]=True;path.write_text(json.dumps(raw))
    with pytest.raises(require("errors","ContractError"),match="readback"):
        backend.observe(store.read_recorded().jobs[0])
