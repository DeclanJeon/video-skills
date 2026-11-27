"""Known native job facts persist without mutable input readiness; observations are not QA gates."""
import json
import pytest
from conftest import require
from test_ledger import built,project,prepare


def active(project):
    path,store,state,production=prepare(project)
    store.initialize(state)
    order=require("work_models","WorkOrder").model_validate_json(json.dumps({
        "id":"W1","domain":"picture","branch":"main","backend":"filmcraft",
        "source_refs":[{"clip_id":"C1","take_id":"T1"}],"output":"renders/picture.mp4"}))
    fp=require("revisions","work_fingerprint")(state,order)
    packet=require("work_models","RequestPacket")(order=order,input_fingerprint=fp,payload="synthetic native packet; no actual tool dispatch")
    with store.transaction(0) as tx:tx.state=require("jobs","reserve_work")(tx.state,packet)
    return path,store,packet


def receipt(packet,phase="running",job_id="synthetic-process-1",**changes):
    raw={"phase":phase,"job_id":job_id,"request_hash":require("jobs","request_digest")(packet),
        "evidence":"synthetic local observation; NOT actual native execution",**changes}
    return require("job_models","JobReceipt").model_validate_json(json.dumps(raw))


def test_reserve_when_existing_uncertain_work_cannot_be_dispatched_again(project):
    path,store,packet=active(project)
    state=store.read_recorded()
    with pytest.raises(require("errors","ContractError"),match="reserved"):
        require("jobs","reserve_work")(state,packet)
    assert len(state.jobs)==1


def test_observation_when_required_media_is_lost_still_persists_known_process(project):
    path,store,packet=active(project)
    (path.parent/"source1.mp4").unlink()
    status=store.record_observation("W1-A1",receipt(packet),1)
    assert status.inputs_ready is False
    assert status.new_work is False
    assert status.jobs[0].job_id=="synthetic-process-1"
    assert status.jobs[0].phase=="running"
    assert store.read_recorded().jobs[0].job_id=="synthetic-process-1"


def test_observation_when_diagnostic_crashes_facts_were_published_first(project,monkeypatch):
    path,store,packet=active(project)
    def fail(state):raise RuntimeError("diagnostic interrupted after facts")
    monkeypatch.setattr(store,"input_issues",fail)
    with pytest.raises(RuntimeError,match="diagnostic"):
        store.record_observation("W1-A1",receipt(packet),1)
    known=store.read_recorded()
    assert known.jobs[0].phase=="running"
    assert known.jobs[0].job_id=="synthetic-process-1"
    assert known.revision==2


@pytest.mark.parametrize("change",[{"request_hash":"a"*64},{"phase":"materialized"},{"phase":"dispatching"}])
def test_observation_when_receipt_is_wrong_request_or_local_gate_cannot_publish(project,change):
    path,store,packet=active(project);before=path.read_bytes()
    with pytest.raises(require("errors","ContractError")):
        store.record_observation("W1-A1",receipt(packet,**change),1)
    assert path.read_bytes()==before


def test_observation_when_known_process_cannot_be_replaced_or_unreceived(project):
    path,store,packet=active(project)
    status=store.record_observation("W1-A1",receipt(packet),1)
    for bad in (receipt(packet,job_id="another-process"),receipt(packet,phase="not_started",job_id=None)):
        with pytest.raises(require("errors","ContractError")):
            store.record_observation("W1-A1",bad,status.revision)


def test_observation_when_terminal_fact_can_skip_missing_intermediate_poll(project):
    path,store,packet=active(project)
    status=store.record_observation("W1-A1",receipt(packet,phase="succeeded"),1)
    assert status.jobs[0].phase=="succeeded"
    assert not store.read_recorded().artifacts  # Native exit is not materialized/accepted output.


def test_transaction_when_historical_job_fact_is_forged_or_removed_cannot_publish(project):
    path,store,packet=active(project)
    before=path.read_bytes()
    for removed in (False,True):
        with pytest.raises(require("errors","ContractError")):
            with store.transaction(1) as tx:
                job=tx.state.jobs[0]
                forged=job.model_copy(update={"phase":require("job_models","JobPhase").SUCCEEDED,"job_id":"invented-process"})
                tx.state=tx.state.model_copy(update={"jobs":() if removed else (forged,)})
        assert path.read_bytes()==before


def test_initialization_when_known_job_facts_are_not_a_clean_new_namespace(project):
    path,store,packet=active(project)
    state=store.read_recorded().model_copy(update={"revision":0})
    raw=json.loads(path.read_text());raw.pop("postproduction");path.write_text(json.dumps(raw))
    with pytest.raises(require("errors","ContractError"),match="initial"):
        store.initialize(state)
    assert "postproduction" not in json.loads(path.read_text())


def test_historical_read_when_duplicate_attempt_ids_in_stored_data_are_rejected(project):
    path,store,packet=active(project)
    raw=json.loads(path.read_text());job=raw["postproduction"]["jobs"][0]
    raw["postproduction"]["jobs"].append(job)
    path.write_text(json.dumps(raw))
    with pytest.raises(require("errors","ContractError"),match="duplicate"):
        store.read_recorded()


def test_work_fingerprint_when_unrelated_ledger_polling_does_not_stale_inputs(project):
    path,store,packet=active(project)
    state=store.read_recorded()
    altered=state.model_copy(update={"revision":100,"notes":("unrelated status note",)})
    assert require("revisions","work_fingerprint")(altered,packet.order)==packet.input_fingerprint
