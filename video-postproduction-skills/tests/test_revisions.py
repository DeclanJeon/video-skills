"""Current adoption checks actual consumed inputs, not mutable root revision or unrelated work."""
import json
import pytest
from conftest import require
from test_ledger import built,project,prepare
from support import pin


def order_for(state,**changes):
    raw={"id":"SCOPED-WORK","domain":"picture","branch":"main","backend":"filmcraft",
        "source_refs":[state.intake.sources[0].source.model_dump()],"output":"renders/scoped.mp4",**changes}
    return require("work_models","WorkOrder").model_validate_json(json.dumps(raw))


def test_work_when_consumed_dependency_bytes_changed_cannot_be_current(project):
    path,store,state,production=prepare(project)
    dep=pin(path.parent,"consumed-recipe-dependency.txt","selected concept/license fixture")
    order=order_for(state,dependencies=[dep.model_dump()])
    require("revisions","verify_work_inputs")(state,order,path)
    (path.parent/dep.path).write_text("replaced")
    with pytest.raises(require("errors","ContractError")):
        require("revisions","verify_work_inputs")(state,order,path)


@pytest.mark.parametrize("which,blocked",[(0,True),(2,False)])
def test_work_when_live_producer_invalidates_consumed_or_unrelated_source(project,which,blocked):
    path,store,state,production=prepare(project)
    order=order_for(state)
    raw=json.loads(path.read_text());raw["production"]["selections"][which]["valid"]=False
    path.write_text(json.dumps(raw))
    if blocked:
        with pytest.raises(require("errors","ContractError")):
            require("revisions","verify_work_inputs")(state,order,path)
    else:
        require("revisions","verify_work_inputs")(state,order,path)


def test_work_when_unconsumed_source_caps_change_does_not_invalidate_independent_work(project):
    path,store,state,production=prepare(project)
    order=order_for(state)
    before=require("revisions","work_fingerprint")(state,order)
    source=state.intake.sources[-1].model_copy(update={"acceptance_revision":99})
    changed=state.model_copy(update={"intake":state.intake.model_copy(update={"sources":(*state.intake.sources[:-1],source)})})
    assert require("revisions","work_fingerprint")(changed,order)==before
