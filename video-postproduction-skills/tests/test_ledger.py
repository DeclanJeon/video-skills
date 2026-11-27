"""Actual production lock inode/CAS seam; post writes cannot steal the root/production namespace."""
import fcntl
import json
import shutil
import pytest
from conftest import require
from support import fixture
from production.store import ProjectStore


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    root=tmp_path_factory.mktemp("post-ledger-source");fixture(root);return root


@pytest.fixture
def project(tmp_path,built):
    shutil.copytree(built,tmp_path,dirs_exist_ok=True)
    production=json.loads((tmp_path/"snapshot.json").read_text())
    path=tmp_path/"project.json"
    path.write_text(json.dumps({"production":production,"foreign":{"owner":"other-terminal","items":[1,2,3]}}))
    return path,production


def prepare(project):
    path,production=project
    intake=require("intake","load_intake")(path.parent,path.parent/"request.json",path)
    timeline=require("timeline","build_timeline")(intake)
    state=require("state_models","PostState")(intake=intake,timelines=(timeline,))
    store=require("ledger","PostStore")(path)
    return path,store,state,production


def test_post_store_when_initializing_preserves_actual_other_namespaces(project):
    path,store,state,production=prepare(project)
    store.initialize(state)
    assert store.read_recorded()==state
    raw=json.loads(path.read_text())
    assert raw["production"]==production
    assert raw["foreign"]=={"owner":"other-terminal","items":[1,2,3]}
    assert ProjectStore(path).read_recorded().model_dump(mode="json")==production


def test_post_store_when_transaction_changes_only_post_revision(project):
    path,store,state,production=prepare(project)
    store.initialize(state)
    with store.transaction(0) as tx:
        tx.state=tx.state.model_copy(update={"notes":("typed post change",)})
    assert store.read_recorded().revision==1
    assert store.read_recorded().notes==("typed post change",)
    assert json.loads(path.read_text())["production"]==production


def test_post_store_when_original_production_writer_holds_public_lock_inode(project):
    path,store,state,production=prepare(project)
    original=ProjectStore(path)
    with original.lock_path.open("a+") as stream:
        fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
        try:
            with pytest.raises(require("errors","ContractError"),match="lock"):
                store.initialize(state)
        finally:
            fcntl.flock(stream,fcntl.LOCK_UN)
    assert "postproduction" not in json.loads(path.read_text())


def test_post_store_when_stale_namespace_revision_cannot_publish(project):
    path,store,state,production=prepare(project)
    store.initialize(state)
    with store.transaction(0) as tx:tx.state=tx.state.model_copy(update={"notes":("first",)})
    before=path.read_bytes()
    with pytest.raises(require("errors","ContractError"),match="revision"):
        with store.transaction(0):pytest.fail("stale writer entered")
    assert path.read_bytes()==before


def test_post_store_when_external_owner_changes_bytes_during_transaction(project):
    path,store,state,production=prepare(project)
    store.initialize(state)
    with pytest.raises(require("errors","ContractError"),match="conflict"):
        with store.transaction(0) as tx:
            value=json.loads(path.read_text());value["foreign"]["owner"]="new-owner"
            path.write_text(json.dumps(value))
            tx.state=tx.state.model_copy(update={"notes":("must not overwrite",)})
    assert json.loads(path.read_text())["foreign"]["owner"]=="new-owner"
    assert store.read_recorded().revision==0


def test_post_store_when_model_copy_bypassed_types_is_reparsed_at_publication(project):
    path,store,state,production=prepare(project)
    store.initialize(state);before=path.read_bytes()
    with pytest.raises(require("errors","ContractError")):
        with store.transaction(0) as tx:tx.state=tx.state.model_copy(update={"revision":"not-an-integer"})
    assert path.read_bytes()==before


def test_post_store_when_input_bytes_are_lost_historical_facts_remain_readable(project):
    path,store,state,production=prepare(project)
    store.initialize(state)
    (path.parent/"source1.mp4").unlink()
    assert store.read_recorded().revision==0
    with pytest.raises(require("errors","ContractError")):
        store.read()


def test_post_store_when_ledger_or_lock_is_a_symlink_is_refused(project):
    path,store,state,production=prepare(project)
    target=path.parent/"external-lock";target.write_text("other writer")
    ProjectStore(path).lock_path.symlink_to(target)
    with pytest.raises(require("errors","ContractError"),match="path"):
        store.initialize(state)
    assert target.read_text()=="other writer"
