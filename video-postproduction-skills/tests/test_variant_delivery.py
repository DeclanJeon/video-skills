"""Actual main-with-text and clean native branch, separately current QA and local bundle records. No human/E4 claim."""
import json
import pytest
from conftest import require
from finishing_support import build
from quality_support import submission
from test_delivery import contract
from support import json_pin


@pytest.fixture(scope="module")
def branched(tmp_path_factory):
    root=tmp_path_factory.mktemp("native-branch-delivery")
    store,backend,packet,value=build(root,variants=True)
    state=store.read_recorded();main=store.record_materialization(state.jobs[-1].id,state.revision)
    state=store.read_recorded();parent=state.timelines[0]
    proposal=require("timeline_models","EditProposal").model_validate_json(json.dumps({"branch":"clean","cuts":[
        {"id":s.id,"source":s.source.model_dump(),"source_range":s.source_range.model_dump()} for s in parent.segments]}))
    clean=require("timeline","build_timeline")(state.intake,proposal,parent)
    with store.transaction(state.revision) as tx:
        tx.state=tx.state.model_copy(update={"timelines":(*state.timelines,clean)})
    state=store.read_recorded()
    picture=next(a for a in state.artifacts if a.id.startswith("PICTURE-"))
    mix=next(a for a in state.artifacts if a.id.startswith("SOUND-"))
    recipe=require("admission","local_pin")(json_pin(root,"clean-finishing.json",
        {"format":"post-finishing/1","id":"CLEAN","branch":"clean","picture":picture.id,"plates":[],"mix":mix.id}))
    order=require("finishing","prepare_finishing")(state,recipe,root)
    adapter=require("backends.finishing","FinishingBackend")(store,root/"clean-native")
    planned=adapter.prepare(order,adapter.inspect(),state.intake.authority)
    job=store.record_reservation(planned,store.read_recorded().revision)
    assert adapter.execute(planned).phase=="succeeded"
    variant=store.record_materialization(job.id,store.read_recorded().revision)
    for artifact,id in ((main,"MAIN-QA"),(variant,"CLEAN-QA")):
        review=store.record_review(submission(store,artifact,id=id),store.read_recorded().revision)
        assert review.scope_passed is True
    return store,main,variant


def test_variant_when_native_clean_branch_is_actual_distinct_current_output(branched):
    store,main,variant=branched
    assert variant.pin.sha256!=main.pin.sha256
    assert [len(t.required_coverage) for t in store.read_recorded().timelines]==[3,3]
    require("materialization","verify_artifact_current")(store.read_recorded(),variant,store.path)


def test_variant_when_bundle_includes_each_distinct_final_has_its_own_qa_and_lineage(branched):
    store,main,variant=branched
    c=contract(store,main,id="BRANCH-BUNDLE",output="deliveries/branched",variants=[variant.id])
    bundle=require("delivery","build_delivery")(store.read_recorded(),c,store.path)
    root=store.path.parent/bundle.path
    assert len(list((root/"variants").glob("*.mp4")))==1
    records=[json.loads(p.read_text()) for p in (root/"records").rglob("*.json")]
    assert any(isinstance(v,dict) and v.get("submission",{}).get("artifact_id")==variant.id for v in records)
    assert any(isinstance(v,list) and any(row.get("artifact_id")==variant.id for row in v) for v in records)


def test_variant_when_editable_inventory_must_include_own_native_project_not_just_main(branched):
    store,main,variant=branched
    c=contract(store,main,id="EDITABLE-VARIANTS",kind="editable",variants=[variant.id])
    inventory=require("editable_inventory","editable_inventory")(store.read_recorded(),c,store.path.parent)
    assert len(inventory.projects)==6


def test_variant_when_editable_bundle_reopens_all_six_actual_native_projects(branched):
    store,main,variant=branched
    c=contract(store,main,id="EDITABLE-BRANCHES",kind="editable",variants=[variant.id],output="deliveries/editable-branches")
    fonts=require("delivery_scope","required_fonts")(store.read_recorded(),c,store.path.parent)
    evidence=json_pin(store.path.parent,"variant-receiver-fonts.json",{"scope":"fixture exact font receiver receipt, not issuer authentication"})
    permissions=[{"font_sha256":f.sha256,"receiver_present":True,"redistribute":False,"evidence":evidence.model_dump()} for f in fonts]
    c=c.model_copy(update={"font_permissions":tuple(require("delivery_models","FontPermission").model_validate_json(json.dumps(p)) for p in permissions)})
    bundle=require("delivery","build_delivery")(store.read_recorded(),c,store.path)
    assert bundle.native_relink_verified is True
    assert len(list((store.path.parent/bundle.path/"native").iterdir()))==6


def test_variant_when_its_own_output_changes_main_qa_cannot_cover_it(branched):
    store,main,variant=branched
    c=contract(store,main,id="STALE-BRANCH",variants=[variant.id],output="deliveries/stale-branch")
    path=store.path.parent/variant.pin.path;before=path.read_bytes()
    path.write_bytes(before+b"changed native output")
    try:
        with pytest.raises(require("errors","ContractError")):
            require("delivery","build_delivery")(store.read_recorded(),c,store.path)
        assert not (store.path.parent/c.output).exists()
    finally:path.write_bytes(before)
