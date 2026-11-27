"""Explicit current source/edit adoption revision retains old facts and snapshots; generic changes cannot swap intake."""
import hashlib,json
import pytest
from conftest import require
from test_ledger import built,project,prepare
from test_revisions import order_for
from support import json_pin


def adoption(path,state):
    request=json.loads(state.intake.request.model_dump_json())
    brief=json.loads((path.parent/request['brief']['path']).read_text());brief['intent']='Explicit new approved edit brief version'
    bp=json_pin(path.parent,'brief-v2.json',brief);request['brief']=bp.model_dump()
    grant=json.loads((path.parent/request['authority']['path']).read_text());grant['brief_digest']=bp.sha256
    ap=json_pin(path.parent,'authority-v2.json',grant);request['authority']=ap.model_dump()
    newfile=path.parent/'request-v2.json';newfile.write_text(json.dumps(request))
    intake=require('intake','load_intake')(path.parent,newfile,path)
    timeline=require('timeline','build_timeline')(intake)
    return require('adoption_models','IntakeRevision')(previous_intake_digest=hashlib.sha256(state.intake.model_dump_json().encode()).hexdigest(),
        intake=intake,timelines=(timeline,),evidence=intake.authority.evidence)


def test_adoption_when_explicit_revision_archives_old_source_and_preserves_reserved_history(project):
    path,store,state,production=prepare(project);store.initialize(state)
    order=order_for(state)
    packet=require('work_models','RequestPacket')(order=order,input_fingerprint=require('revisions','work_fingerprint')(state,order),payload='unexecuted reservation')
    store.record_reservation(packet,0);before=store.read_recorded()
    revision=adoption(path,before)
    store.record_revision(revision,before.revision)
    result=store.read()
    assert result.intake==revision.intake
    assert result.intake_history[-1]==before.intake
    assert result.jobs==before.jobs and result.orders==before.orders
    assert result.timeline_history[-1]==before.timelines[0]
    assert require('revisions','work_fingerprint')(result,order)!=packet.input_fingerprint


def test_adoption_when_previous_source_fingerprint_wrong_cannot_replace_current_namespace(project):
    path,store,state,production=prepare(project);store.initialize(state)
    revision=adoption(path,state).model_copy(update={'previous_intake_digest':'a'*64})
    before=path.read_bytes()
    with pytest.raises(require('errors','ContractError')):store.record_revision(revision,0)
    assert path.read_bytes()==before


def test_adoption_when_generic_transaction_cannot_replace_intake_or_forge_history(project):
    path,store,state,production=prepare(project);store.initialize(state)
    revision=adoption(path,state)
    with pytest.raises(require('errors','ContractError')):
        with store.transaction(0) as tx:tx.state=tx.state.model_copy(update={'intake':revision.intake,'timelines':revision.timelines})
