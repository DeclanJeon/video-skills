"""Actual local technical fixture bundle, receiver/rights/current QA, missing stems/fonts and no implicit release/upload."""
import hashlib,json
import pytest
from conftest import require
from quality_support import ready,submission
from support import json_pin


@pytest.fixture(scope="module")
def actual(tmp_path_factory):
    require("delivery_models","DeliveryContract")
    store,artifact=ready(tmp_path_factory.mktemp("actual-native-delivery"))
    report=submission(store,artifact,id="DELIVERY-QA")
    store.record_review(report,store.read_recorded().revision)
    return store,artifact


def contract(store,artifact,**changes):
    evidence=json_pin(store.path.parent,"delivery-rights.json",{"scope":"contract_fixture declared receiver/source access only, not authenticated rights or human final approval"})
    pins=[]
    for a in store.read_recorded().artifacts:
        pins.extend([a.pin,*a.related,*((a.proof,) if a.proof is not None else ())])
    pins.extend(s.asset for s in store.read_recorded().intake.sources)
    raw={"id":"BUNDLE-1","mode":"technical_fixture","kind":"master_only","artifact_id":artifact.id,"receiver":"fixture-local-receiver",
        "output":"deliveries/technical-bundle","variants":[],"include_mix":True,"required_stems":[],"font_permissions":[],
        "rights":{"status":"reported_allowed","origin":"fixture","evidence":evidence.model_dump(),"permitted":[p.model_dump() for p in pins]},**changes}
    return require("delivery_models","DeliveryContract").model_validate_json(json.dumps(raw))


def test_delivery_when_real_technical_bundle_checksums_and_no_false_human_release(actual):
    store,artifact=actual;c=contract(store,artifact)
    bundle=require("delivery","build_delivery")(store.read_recorded(),c,store.path)
    assert bundle.mode=="technical_fixture" and bundle.formal_release is False
    assert bundle.receiver==c.receiver
    for file in bundle.files:
        path=store.path.parent/bundle.path/file.path
        assert hashlib.sha256(path.read_bytes()).hexdigest()==file.sha256
    assert not any("/home/" in p.read_text() or "signed_url" in p.read_text().lower() for p in (store.path.parent/bundle.path).rglob("*.json"))


@pytest.mark.parametrize("change",[{"receiver":"another-receiver"},{"required_stems":["nonexistent-DX"]},{"kind":"editable"}])
def test_delivery_when_receiver_or_real_stem_or_editable_font_dependency_missing_blocks(actual,change):
    store,artifact=actual;c=contract(store,artifact,output="deliveries/blocked",**change)
    with pytest.raises(require("errors","ContractError")):
        require("delivery","build_delivery")(store.read_recorded(),c,store.path)
    assert not (store.path.parent/c.output).exists()


def test_delivery_when_editable_native_projects_relink_with_exact_receiver_font_receipt(actual):
    store,artifact=actual
    fonts=require("delivery_scope","required_fonts")(store.read_recorded(),contract(store,artifact),store.path.parent)
    evidence=json_pin(store.path.parent,"receiver-fonts.json",{"scope":"fixture receiver acknowledges exact existing fonts, not remote machine authentication"})
    permissions=[{"font_sha256":f.sha256,"receiver_present":True,"redistribute":False,"evidence":evidence.model_dump()} for f in fonts]
    c=contract(store,artifact,id="EDITABLE",kind="editable",font_permissions=permissions,output="deliveries/editable")
    bundle=require("delivery","build_delivery")(store.read_recorded(),c,store.path)
    assert bundle.native_relink_verified is True
    natives=[p for p in (store.path.parent/bundle.path/"native").iterdir() if p.suffix in {".fcproj",".ecproj",".scraft"}]
    assert len(natives)==5
    assert all(str(store.path.parent) not in p.read_text() for p in natives)


def test_delivery_when_fixture_report_cannot_be_laundered_into_real_final_master(actual):
    store,artifact=actual;c=contract(store,artifact,mode="reported_release",output="deliveries/not-a-real-master")
    with pytest.raises(require("errors","ContractError")):
        require("delivery","build_delivery")(store.read_recorded(),c,store.path)


def test_delivery_when_narrow_commit_records_actual_package_without_changing_native_job_facts(actual):
    store,artifact=actual;c=contract(store,artifact,id="RECORDED",output="deliveries/recorded")
    before=store.read_recorded()
    record=store.record_delivery(c,before.revision)
    assert store.read_recorded().deliveries[-1]==record
    assert record.bundle.formal_release is False
    assert store.read_recorded().jobs==before.jobs


def test_delivery_when_generic_transaction_cannot_forge_delivered_status(actual):
    store,artifact=actual;c=contract(store,artifact,id="FAKE-GENERIC",output="deliveries/generic-data")
    bundle=require("delivery","build_delivery")(store.read_recorded(),c,store.path)
    record=require("delivery_models","DeliveryRecord")(contract=c,bundle=bundle)
    before=store.read_recorded()
    with pytest.raises(require("errors","ContractError")):
        with store.transaction(before.revision) as tx:
            tx.state=tx.state.model_copy(update={"deliveries":(*before.deliveries,record)})


def test_delivery_when_source_replaced_after_render_blocks_local_package(actual):
    store,artifact=actual;c=contract(store,artifact,output="deliveries/stale")
    source=store.path.parent/"source1.mp4";data=source.read_bytes();source.write_bytes((store.path.parent/"source3.mp4").read_bytes())
    try:
        with pytest.raises(require("errors","ContractError")):
            require("delivery","build_delivery")(store.read_recorded(),c,store.path)
    finally:source.write_bytes(data)
