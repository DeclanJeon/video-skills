"""Public raw finishing packet must carry the same exact work/recipe/branch/dependency authority at every seam."""
import json
from uuid import uuid4
import pytest
from conftest import require
from finishing_support import build
from support import json_pin


@pytest.fixture(scope='module')
def raw_context(tmp_path_factory):
    root=tmp_path_factory.mktemp('raw-finishing-admission')
    store,backend,packet,value=build(root,variants=True,reorder=True)
    state=store.read_recorded();parent=state.timelines[0]
    proposal=require('timeline_models','EditProposal').model_validate_json(json.dumps({'branch':'reverse','cuts':[
        {'id':s.id,'source':s.source.model_dump(),'source_range':s.source_range.model_dump()} for s in reversed(parent.segments)]}))
    reverse=require('timeline','build_timeline')(state.intake,proposal,parent)
    with store.transaction(state.revision) as tx:tx.state=tx.state.model_copy(update={'timelines':(*state.timelines,reverse)})
    return store,backend,packet


def raw_packet(context,mismatch):
    store,backend,original=context;root=store.path.parent;owner=uuid4().hex
    plan=require('finishing_models','FinishingPlan').model_validate_json(original.payload)
    plan=plan.model_copy(update={'workspace':(backend.workspace/('run-'+owner)).absolute(),'owner':owner})
    order=json.loads(original.order.model_dump_json());order['id']='RAW-'+mismatch+'-'+owner
    if mismatch=='branch':order['branch']='reverse'
    elif mismatch=='recipe-pin':order['recipe']=json_pin(root,owner+'-recipe.json',plan.recipe.model_dump(mode='json')).model_dump()
    elif mismatch=='dependencies':order['dependencies']=[]
    elif mismatch=='domain':order['domain']='picture'
    elif mismatch=='capability':plan=plan.model_copy(update={'capability':plan.capability.model_copy(update={'tool':require('environment.models','Tool').EFFECTCRAFT})})
    parsed=require('work_models','WorkOrder').model_validate_json(json.dumps(order))
    packet=require('work_models','RequestPacket')(order=parsed,
        input_fingerprint=require('revisions','work_fingerprint')(store.read_recorded(),parsed),payload=plan.model_dump_json())
    return packet,plan


@pytest.mark.parametrize('mismatch',['branch','recipe-pin','dependencies','domain','capability'])
def test_finishing_when_raw_reserved_packet_mismatches_order_rejects_before_any_native_effect(raw_context,mismatch):
    store,backend,original=raw_context;packet,plan=raw_packet(raw_context,mismatch)
    store.record_reservation(packet,store.read_recorded().revision)
    with pytest.raises(require('errors','ContractError')):
        backend.execute(packet)
    assert not plan.workspace.exists()


@pytest.mark.parametrize('mismatch',['branch','recipe-pin','dependencies','capability'])
def test_quality_when_actual_historical_raw_packet_is_mismatched_rejects_current_proof(raw_context,monkeypatch,mismatch):
    from quality_support import submission
    store,backend,original=raw_context;packet,plan=raw_packet(raw_context,mismatch)
    # Capture ONLY the earlier missing admission contract; binary/path checks, native commands,
    # reservations, output readback and materialization remain real. This is fixture history, not QA.
    with monkeypatch.context() as patch:
        patch.setattr('postproduction.finishing_admission.verify_finishing_packet',
            lambda state,packet,project:require('finishing_models','FinishingPlan').model_validate_json(packet.payload))
        job=store.record_reservation(packet,store.read_recorded().revision)
        assert backend.execute(packet).phase=='succeeded'
        artifact=store.record_materialization(job.id,store.read_recorded().revision)
    # Real CURRENT validator restored. Do not erase historical succeeded facts or their bytes.
    before=store.path.read_bytes()
    with pytest.raises(require('errors','ContractError')):
        store.record_materialization(job.id,store.read_recorded().revision)
    assert store.path.read_bytes()==before
    result=require('quality','evaluate_submission')(store.read_recorded(),submission(store,artifact,id='RAW-QA-'+mismatch),store.path)
    assert next(g for g in result.gates if g.id=='PG5').status=='fail' and result.scope_passed is False
    assert (store.path.parent/artifact.pin.path).is_file()
    assert next(j for j in store.read_recorded().jobs if j.id==job.id).phase=='succeeded'


def test_finishing_when_only_input_adoption_registry_flags_change_native_projection_still_matches(raw_context):
    store,backend,packet=raw_context
    state=store.read_recorded()
    state=state.model_copy(update={'artifacts':tuple(a.model_copy(update={'adopted':True}) for a in state.artifacts)})
    plan=require('finishing_admission','verify_finishing_packet')(state,packet,store.path)
    assert plan.recipe.branch==packet.order.branch

