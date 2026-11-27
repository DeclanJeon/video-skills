"""Actual upstream handoff/currentness and physically decoded source admission."""
import json
import shutil
import pytest
from conftest import require
from support import fixture,update_request


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    path=tmp_path_factory.mktemp("intake-source")
    fixture(path)
    return path


@pytest.fixture
def bundle(tmp_path,built):
    shutil.copytree(built,tmp_path,dirs_exist_ok=True)
    return tmp_path,json.loads((tmp_path/"request.json").read_text())


def load(root):
    return require("intake","load_intake")(root,root/"request.json")


def test_intake_when_real_local_sources_and_actual_production_handoff_match(bundle):
    root,request=bundle
    value=load(root)
    assert len(value.sources)==3
    assert value.sources[0].rate.num==24
    assert value.sources[0].frame_count==48
    assert value.handoff.handles == (("C1",0,0),("C2",0,0),("C3",0,0))
    assert value.snapshot.approved_coverage==value.snapshot.batch.coverage
    assert value.request.handoff.sha256==request["handoff"]["sha256"]


@pytest.mark.parametrize("key",["snapshot","handoff","schema","brief","authority","profile"])
def test_intake_when_required_physical_input_drifts(bundle,key):
    root,request=bundle
    (root/request[key]["path"]).write_text("changed")
    with pytest.raises(require("errors","ContractError")):
        load(root)


@pytest.mark.parametrize("mutation",["invalid","missing_source","approval","stale_review","scope","handles","missing_rough","missing_stem","schema","malformed"])
def test_intake_when_source_or_contract_cannot_be_adopted(bundle,mutation):
    root,request=bundle
    state=json.loads((root/"snapshot.json").read_text())
    if mutation=="missing_source":
        (root/"source1.mp4").unlink()
    elif mutation=="approval":
        (root/"reuse-approval.txt").write_text("replacement")
    elif mutation=="missing_rough":
        (root/"review-only.mp4").unlink()
    elif mutation=="missing_stem":
        brief=json.loads((root/"brief.json").read_text());brief["required_stems"]=["clean-dialogue"]
        update_request(root,request,"brief","brief.json",brief)
    elif mutation=="schema":
        update_request(root,request,"schema","upstream-schema.py.txt",{"not":"the active schema"})
    elif mutation=="malformed":
        update_request(root,request,"snapshot","snapshot.json",{"batch":"wrong"})
    elif mutation=="handles":
        handoff=json.loads((root/"handoff.json").read_text());handoff["handles"][0][1]=1
        update_request(root,request,"handoff","handoff.json",handoff)
    else:
        match mutation:
            case "invalid":state["selections"][0]["valid"]=False
            case "stale_review":state["selections"][0]["reviewed_fingerprint"]="a"*64
            case "scope":state["batch"]["scope_revision"]="unapproved-scope"
        update_request(root,request,"snapshot","snapshot.json",state)
    with pytest.raises(require("errors","ContractError")):
        load(root)


def test_intake_when_strict_record_is_serialized_and_reloaded(bundle):
    root,request=bundle
    value=load(root)
    restored=require("intake_models","PostIntake").model_validate_json(value.model_dump_json())
    assert restored==value
    assert restored.request.schema_pin.sha256==request["schema"]["sha256"]


def test_intake_when_namespace_snapshot_has_other_owners_fields(bundle):
    root,request=bundle
    original=json.loads((root/"snapshot.json").read_text())
    update_request(root,request,"snapshot","snapshot.json",{"production":original,"foreign":{"owner":"other-terminal"}})
    before=(root/"snapshot.json").read_bytes()
    value=load(root)
    assert value.snapshot.batch.id=="B1"
    assert (root/"snapshot.json").read_bytes()==before


def test_intake_when_request_parent_is_an_internal_symlink(bundle):
    root,request=bundle
    folder=root/"nested";folder.mkdir()
    shutil.copyfile(root/"request.json",folder/"request.json")
    (root/"alias").symlink_to(folder,target_is_directory=True)
    with pytest.raises(require("errors","ContractError")):
        require("intake","load_intake")(root,root/"alias/request.json")


def test_intake_when_mutable_ledger_is_proposed_as_snapshot(bundle):
    root,request=bundle
    with pytest.raises(require("errors","ContractError"),match="snapshot"):
        require("intake","load_intake")(root,root/"request.json",root/"snapshot.json")


def test_intake_when_source_is_a_symlink_even_with_matching_hash(bundle,tmp_path_factory):
    root,request=bundle
    outside=tmp_path_factory.mktemp("external-source")/"source.mp4"
    shutil.copyfile(root/"source1.mp4",outside)
    (root/"source1.mp4").unlink();(root/"source1.mp4").symlink_to(outside)
    with pytest.raises(require("errors","ContractError")):
        load(root)
