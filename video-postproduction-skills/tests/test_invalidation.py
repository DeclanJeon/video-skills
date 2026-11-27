"""Pure consumed-pin dependency graph fixtures, not native artifact adoption or perceptual certification."""
import json
import pytest
from conftest import require
from test_ledger import built,project,prepare
from test_revisions import order_for
from support import pin


def graph(project):
    path,store,state,production=prepare(project)
    a=order_for(state,id="A")
    b=order_for(state,id="B",source_refs=[state.intake.sources[1].source.model_dump()])
    derived=pin(path.parent,"derived-graph-only.txt","pure graph fixture, not actual native output")
    c=order_for(state,id="C",source_refs=[state.intake.sources[1].source.model_dump()],dependencies=[derived.model_dump()])
    state=state.model_copy(update={"orders":(a,b,c)})
    fp=require("revisions","work_fingerprint")(state,a)
    packet=require("work_models","RequestPacket")(order=a,input_fingerprint=fp,payload="pure graph, no native dispatch")
    state=require("jobs","reserve_work")(state,packet)
    artifact=require("job_models","ArtifactRef")(id="GRAPH-A",job_id=state.jobs[-1].id,pin=require("admission","local_pin")(derived),input_fingerprint=fp,adopted=True)
    return path,store,state.model_copy(update={"artifacts":(artifact,)}),a,b,c,artifact


def test_invalidation_when_changed_consumed_source_does_not_erase_history_or_block_independent_work(project):
    path,store,state,a,b,c,artifact=graph(project)
    before=require("revisions","work_fingerprint")(state,b)
    changed=require("revisions","invalidate_dependents")(state,(state.intake.sources[0].asset,))
    assert changed.artifacts[0].adopted is False
    assert changed.artifacts[0].pin==artifact.pin
    assert changed.orders==state.orders and changed.jobs==state.jobs
    assert changed.invalidations[-1].order_ids==("A","C")
    assert require("revisions","work_fingerprint")(changed,b)==before
    require("revisions","verify_work_inputs")(changed,b,path)
    with pytest.raises(require("errors","ContractError"),match="invalidat"):
        require("revisions","verify_work_inputs")(changed,a,path)


def test_invalidation_when_unknown_unconsumed_pin_has_no_false_coverage_or_fingerprint_effect(project):
    path,store,state,a,b,c,artifact=graph(project)
    other=pin(path.parent,"unconsumed.txt","unrelated")
    changed=require("revisions","invalidate_dependents")(state,(require("admission","local_pin")(other),))
    assert changed.invalidations[-1].order_ids==()
    assert changed.artifacts==state.artifacts


def test_invalidation_when_actual_store_uses_narrow_path_preserving_reservations_and_foreign_data(project):
    path,store,state,production=prepare(project);store.initialize(state)
    order=order_for(state,id="RESERVED-A")
    packet=require("work_models","RequestPacket")(order=order,input_fingerprint=require("revisions","work_fingerprint")(state,order),payload="unexecuted pure graph fixture")
    with store.transaction(0) as tx:tx.state=require("jobs","reserve_work")(tx.state,packet)
    before=store.read_recorded()
    store.record_invalidation((state.intake.sources[0].asset,),before.revision)
    assert store.read_recorded().jobs==before.jobs
    assert store.read_recorded().invalidations[-1].order_ids==("RESERVED-A",)
    assert json.loads(path.read_text())["production"]==production
    assert json.loads(path.read_text())["foreign"]["owner"]=="other-terminal"
