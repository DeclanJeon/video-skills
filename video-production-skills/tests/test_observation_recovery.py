"""Historical remote receipts must survive loss of mutable local preparation inputs."""
import json

import pytest

from conftest import configurations, pin, require
from production.models import AttemptId, Phase, Receipt, State
from test_bindings import native
from test_cli import cli


def live_reservations(seed,capability,authority,tmp_path,submitted=False):
    dependency=pin(tmp_path,"unrelated-local-dependency.txt","only clip C3 uses this")
    third=seed.batch.clips[2].model_copy(update={"dependencies":(dependency,)})
    initial=seed.model_copy(update={"batch":seed.batch.model_copy(update={"clips":(*seed.batch.clips[:2],third)})})
    authority=authority.model_copy(update={"configurations":configurations(initial,capability)})
    state=initial
    packets=[]
    for cid,aid in (("C1","A1"),("C2","A2")):
        packet=require("bindings","prepare_request")(state,cid,capability,authority,(native(state),),tmp_path)
        state=require("execution","reserve")(state,packet,AttemptId(aid),0,tmp_path)
        packets.append(packet)
    state=require("execution","observe")(state,"A2",Receipt(phase=Phase.UNKNOWN,evidence="synthetic timeout; second job unresolved",request_hash=packets[1].request_hash))
    if submitted:
        state=require("execution","observe")(state,"A1",Receipt(phase=Phase.SUBMITTED,job_id="fixture-confirmed-remote-id",evidence="synthetic acknowledged job",request_hash=packets[0].request_hash))
    store=require("store","ProjectStore")(tmp_path/"ledger.json")
    store.initialize(initial)
    with store.transaction(0) as tx:
        tx.state=state
    return store,packets[0],dependency


@pytest.mark.parametrize("damage",["missing-input","hash-drift","unrelated-dependency","coverage-missing"])
def test_observe_ack_when_mutable_inputs_unavailable(seed,capability,authority,tmp_path,damage):
    # Given: C1 reserved and C2 unknown; a mutable local input then becomes unusable.
    store,packet,dependency=live_reservations(seed,capability,authority,tmp_path)
    if damage == "missing-input":
        (tmp_path/seed.batch.clips[0].assets[0].path).unlink()
    elif damage == "hash-drift":
        (tmp_path/seed.batch.clips[0].assets[0].path).write_text("changed bytes")
    elif damage == "unrelated-dependency":
        (tmp_path/dependency.path).unlink()
    else:
        (tmp_path/seed.coverage_source.path).unlink()
    receipt=tmp_path/"ack.json"
    receipt.write_text(Receipt(phase=Phase.SUBMITTED,job_id="fixture-confirmed-remote-id",evidence="synthetic exact acknowledgement",request_hash=packet.request_hash).model_dump_json())
    # When: recording a known historical remote fact through the actual CLI.
    result=cli("observe",tmp_path/"ledger.json","A1",receipt,1)
    # Then: acknowledged job ID is durable; unavailable inputs do not open new work.
    assert result.returncode == 0,result.stdout+result.stderr
    persisted=State.model_validate(json.loads((tmp_path/"ledger.json").read_text())["production"])
    assert persisted.revision == 3  # durable fact commit, then separate diagnostic commit
    assert persisted.attempts[0].job_id == "fixture-confirmed-remote-id"
    assert persisted.attempts[0].phase == Phase.SUBMITTED
    assert persisted.attempts[1].phase == Phase.UNKNOWN
    assert persisted.observed_input_issues
    assert json.loads(result.stdout)["inputs_ready"] is False
    assert require("execution","available_slots")(persisted,capability,authority,0) == 0
    assert cli("ready",tmp_path/"ledger.json").returncode != 0
    status=cli("status",tmp_path/"ledger.json")
    assert status.returncode == 0,status.stdout+status.stderr
    assert json.loads(status.stdout)["inputs_ready"] is False
    packet_file=tmp_path/"original-packet.json";packet_file.write_text(packet.model_dump_json())
    assert cli("reserve",tmp_path/"ledger.json",packet_file,"NEW-A1",3,0).returncode != 0
    assert len(json.loads((tmp_path/"ledger.json").read_text())["production"]["attempts"]) == 2


@pytest.mark.parametrize("phase",[Phase.SUCCEEDED,Phase.FAILED,Phase.CANCELLED])
def test_observe_terminal_when_local_asset_missing(seed,capability,authority,tmp_path,phase):
    # Given: acknowledged C1 plus unresolved C2, then asset loss.
    store,packet,dependency=live_reservations(seed,capability,authority,tmp_path,submitted=True)
    (tmp_path/seed.batch.clips[0].assets[0].path).unlink()
    receipt=tmp_path/"terminal.json"
    receipt.write_text(Receipt(phase=phase,job_id="fixture-confirmed-remote-id",evidence="synthetic confirmed terminal receipt",request_hash=packet.request_hash).model_dump_json())
    # When: reconciling only C1's known terminal fact.
    result=cli("observe",tmp_path/"ledger.json","A1",receipt,1)
    # Then: only C1's reservation is freed, even though preparation remains blocked.
    assert result.returncode == 0,result.stdout+result.stderr
    state=State.model_validate(json.loads((tmp_path/"ledger.json").read_text())["production"])
    assert state.attempts[0].phase == phase
    assert state.attempts[1].phase == Phase.UNKNOWN
    assert require("execution","available_slots")(state,capability,authority,0) == 1
    assert state.observed_input_issues
    assert cli("ready",tmp_path/"ledger.json").returncode != 0


def test_historical_observation_when_receipt_identity_wrong(seed,capability,authority,tmp_path):
    # Given: unavailable inputs do not relax exact receipt identity checks.
    store,packet,dependency=live_reservations(seed,capability,authority,tmp_path)
    (tmp_path/seed.batch.clips[0].assets[0].path).unlink()
    before=(tmp_path/"ledger.json").read_bytes()
    receipt=tmp_path/"wrong.json"
    receipt.write_text(Receipt(phase=Phase.SUBMITTED,job_id="unrelated-job",evidence="synthetic wrong receipt",request_hash="f"*64).model_dump_json())
    # When: attempting reconciliation with a mismatched request hash.
    result=cli("observe",tmp_path/"ledger.json","A1",receipt,1)
    # Then: no bypass endpoint can rewrite the original attempt or current plan.
    assert result.returncode != 0
    assert "request" in result.stdout
    assert (tmp_path/"ledger.json").read_bytes() == before


def test_remote_observation_when_download_state_would_skip_source_admission(seed,capability,authority,tmp_path):
    # Given: remote generation succeeded, but no source has been admitted/decoded by QA.
    store,packet,dependency=live_reservations(seed,capability,authority,tmp_path,submitted=True)
    with store.transaction(1) as tx:
        tx.state=require("execution","observe")(tx.state,"A1",Receipt(phase=Phase.SUCCEEDED,job_id="fixture-confirmed-remote-id",evidence="synthetic remote success",request_hash=packet.request_hash))
    before=(tmp_path/"ledger.json").read_bytes()
    report=tmp_path/"fake-downloaded.json"
    report.write_text(Receipt(phase=Phase.DOWNLOADED,job_id="fixture-confirmed-remote-id",evidence="no local file/probe supplied",request_hash=packet.request_hash).model_dump_json())
    # When: the historical-remote endpoint is misused to claim a local data gate.
    result=cli("observe",tmp_path/"ledger.json","A1",report,2)
    # Then: this narrow persistence route cannot bypass local source admission.
    assert result.returncode != 0
    assert (tmp_path/"ledger.json").read_bytes() == before


def test_historical_observation_when_writer_revision_is_stale(seed,capability,authority,tmp_path):
    # Given: record is at revision 1, and local preparation inputs are unavailable.
    store,packet,dependency=live_reservations(seed,capability,authority,tmp_path)
    (tmp_path/dependency.path).unlink()
    before=(tmp_path/"ledger.json").read_bytes()
    receipt=tmp_path/"ack.json";receipt.write_text(Receipt(phase=Phase.SUBMITTED,job_id="fixture-job",evidence="synthetic exact ack",request_hash=packet.request_hash).model_dump_json())
    # When: a stale writer attempts the specialized receipt route.
    result=cli("observe",tmp_path/"ledger.json","A1",receipt,0)
    # Then: scope-readiness decoupling does not remove CAS or ownership checks.
    assert result.returncode != 0
    assert "revision" in result.stdout
    assert (tmp_path/"ledger.json").read_bytes() == before


def test_job_identity_when_diagnostic_process_is_interrupted(seed,capability,authority,tmp_path,monkeypatch):
    # Given: diagnostic work can fail after an actual remote acknowledgement is available.
    store,packet,dependency=live_reservations(seed,capability,authority,tmp_path)
    def interrupted(state):
        raise RuntimeError("fixture interruption during mutable-input diagnostics")
    monkeypatch.setattr(store,"_input_issues",interrupted)
    receipt=Receipt(phase=Phase.SUBMITTED,job_id="fixture-confirmed-remote-id",evidence="synthetic acknowledgement",request_hash=packet.request_hash)
    # When: the process is interrupted while computing readiness diagnostics.
    with pytest.raises(RuntimeError):
        store.record_observation("A1",receipt,1)
    # Then: remote identity is already durable, before any mutable-file verification.
    persisted=State.model_validate(json.loads((tmp_path/"ledger.json").read_text())["production"])
    assert persisted.attempts[0].job_id == "fixture-confirmed-remote-id"
    assert persisted.attempts[0].phase == Phase.SUBMITTED
    assert persisted.attempts[1].phase == Phase.UNKNOWN
    assert persisted.observed_input_issues


def test_fact_commit_when_second_diagnostic_publication_fails(seed,capability,authority,tmp_path,monkeypatch):
    # Given: a real first publication can succeed while the second diagnostic update fails.
    import os
    store,packet,dependency=live_reservations(seed,capability,authority,tmp_path)
    original=os.replace
    calls=0
    def replace(src,dst):
        nonlocal calls
        calls+=1
        if calls == 2:
            raise OSError("fixture diagnostic disk failure")
        original(src,dst)
    monkeypatch.setattr(os,"replace",replace)
    receipt=Receipt(phase=Phase.SUBMITTED,job_id="fixture-confirmed-remote-id",evidence="synthetic acknowledgement",request_hash=packet.request_hash)
    # When: diagnostics fail after the historical fact was durably published.
    with pytest.raises(OSError):
        store.record_observation("A1",receipt,1)
    # Then: callers inspect status and never treat the exception as no remote job.
    restored=store.read_recorded()
    assert restored.attempts[0].job_id == "fixture-confirmed-remote-id"
    assert restored.attempts[1].phase == Phase.UNKNOWN
    assert restored.revision == 2
    assert restored.observed_input_issues


def test_fact_commit_when_other_owner_changes_document_before_diagnostics(seed,capability,authority,tmp_path,monkeypatch):
    # Given: a non-cooperating writer changes an unrelated root field after fact publication.
    store,packet,dependency=live_reservations(seed,capability,authority,tmp_path)
    def external_writer(state):
        data=json.loads((tmp_path/"ledger.json").read_text())
        data["other_owner"]=42
        (tmp_path/"ledger.json").write_text(json.dumps(data))
        return ()
    monkeypatch.setattr(store,"_input_issues",external_writer)
    receipt=Receipt(phase=Phase.SUBMITTED,job_id="fixture-confirmed-remote-id",evidence="synthetic acknowledgement",request_hash=packet.request_hash)
    # When / Then: diagnostic publication refuses to clobber the observed other-owner change.
    from production.models import ContractError
    with pytest.raises(ContractError,match="conflict"):
        store.record_observation("A1",receipt,1)
    data=json.loads((tmp_path/"ledger.json").read_text())
    assert data["other_owner"] == 42
    assert data["production"]["attempts"][0]["job_id"] == "fixture-confirmed-remote-id"


@pytest.mark.parametrize("phase",[Phase.RUNNING,Phase.SUCCEEDED,Phase.FAILED,Phase.CANCELLED])
def test_first_recovered_receipt_when_intermediate_status_was_not_observed(seed,capability,authority,tmp_path,phase):
    # Given: interruption left the record submitting; later lookup already sees running/terminal.
    store,packet,dependency=live_reservations(seed,capability,authority,tmp_path)
    (tmp_path/dependency.path).unlink()
    receipt=tmp_path/"first-recovered.json"
    receipt.write_text(Receipt(phase=phase,job_id="fixture-confirmed-remote-id",evidence="synthetic exact recovered remote status",request_hash=packet.request_hash).model_dump_json())
    # When: saving the actual observed status, without inventing intermediate events.
    result=cli("observe",tmp_path/"ledger.json","A1",receipt,1)
    # Then: a known remote identity/status is durable even if acknowledgement was missed.
    assert result.returncode == 0,result.stdout+result.stderr
    state=store.read_recorded()
    assert state.attempts[0].phase == phase
    assert state.attempts[0].job_id == "fixture-confirmed-remote-id"
    assert state.attempts[1].phase == Phase.UNKNOWN
