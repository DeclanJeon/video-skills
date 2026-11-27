"""Reservations survive ambiguous submits; no network is exercised."""
import pytest
from production.models import AttemptId, ContractError, Phase, Receipt
from conftest import require
from test_bindings import prepare


def reserved(seed, capability, authority, tmp_path):
    packet = prepare(seed, capability, authority, tmp_path)
    state = require("execution", "reserve")(seed, packet, AttemptId("ATT-1"), 0, tmp_path)
    return state, packet


def test_unknown_slot_when_submit_response_lost(seed, capability, authority, tmp_path):
    # Given: reserved A plus one other account job; capacity is two.
    state, packet = reserved(seed, capability, authority, tmp_path)
    state = require("execution", "observe")(state, "ATT-1", Receipt(phase=Phase.UNKNOWN, evidence="fixture-timeout", request_hash=packet.request_hash))
    # When: asking for additional capacity.
    available = require("execution", "available_slots")(state, capability, authority, 1)
    # Then: unknown still reserves a slot.
    assert available == 0


def test_external_job_when_capacity_two(seed, capability, authority, tmp_path):
    # Given: one job outside this project is observed.
    # When: computing headroom.
    result = require("execution", "available_slots")(seed, capability, authority, 1)
    # Then: only one slot is available.
    assert result == 1


def test_duplicate_when_attempt_already_reserved(seed, capability, authority, tmp_path):
    # Given: submit identity has already been journaled.
    state, packet = reserved(seed, capability, authority, tmp_path)
    # When / Then: neither same identity nor active clip is submitted twice.
    with pytest.raises(ContractError, match="attempt"):
        require("execution", "reserve")(state, packet, AttemptId("ATT-1"), 0, tmp_path)


def test_terminal_when_download_not_completed(seed, capability, authority, tmp_path):
    # Given: a known remote job succeeded.
    state, packet = reserved(seed, capability, authority, tmp_path)
    observe = require("execution", "observe")
    state = observe(state, "ATT-1", Receipt(phase=Phase.SUBMITTED, job_id="fixture-job", evidence="fixture-accepted", request_hash=packet.request_hash))
    # When: remote termination is confirmed, before local download.
    state = observe(state, "ATT-1", Receipt(phase=Phase.SUCCEEDED, job_id="fixture-job", evidence="fixture-finished", request_hash=packet.request_hash))
    # Then: remote slot is free, but there is still no accepted take.
    assert require("execution", "available_slots")(state, capability, authority, 0) == 2
    assert not state.selections


def test_cancel_when_only_request_without_confirmation(seed, capability, authority, tmp_path):
    # Given: submitting does not yet identify a remote job.
    state, packet = reserved(seed, capability, authority, tmp_path)
    # When / Then: an unbound cancellation cannot free capacity.
    with pytest.raises(ContractError, match="job"):
        require("execution", "observe")(state, "ATT-1", Receipt(phase=Phase.CANCELLED, evidence="cancel requested only", request_hash=packet.request_hash))


def test_receipt_when_request_hash_wrong(seed, capability, authority, tmp_path):
    # Given: remote event belongs to a different payload.
    state, packet = reserved(seed, capability, authority, tmp_path)
    # When / Then: refuse incorrect reconciliation.
    with pytest.raises(ContractError, match="request"):
        require("execution", "observe")(state, "ATT-1", Receipt(phase=Phase.SUBMITTED, job_id="fixture-job", evidence="receipt", request_hash="a"*64))


def test_result_when_job_id_changed(seed, capability, authority, tmp_path):
    # Given: a bound job.
    state, packet = reserved(seed, capability, authority, tmp_path)
    observe = require("execution", "observe")
    state = observe(state, "ATT-1", Receipt(phase=Phase.SUBMITTED, job_id="J1", evidence="receipt", request_hash=packet.request_hash))
    # When / Then: another history entry is not treated as this result.
    with pytest.raises(ContractError, match="job"):
        observe(state, "ATT-1", Receipt(phase=Phase.SUCCEEDED, job_id="J2", evidence="result", request_hash=packet.request_hash))


def test_reservation_when_packet_tampered(seed, capability, authority, tmp_path):
    # Given: text changed after inspection.
    packet = prepare(seed, capability, authority, tmp_path).model_copy(update={"prompt_text": "DIFFERENT"})
    # When / Then: exact request digest is checked again.
    with pytest.raises(ContractError, match="request"):
        require("execution", "reserve")(seed, packet, AttemptId("X"), 0, tmp_path)


def test_available_when_account_occupancy_unknown(seed, capability, authority):
    # Given: account occupancy is unavailable rather than zero.
    # When / Then: do not guess free capacity.
    with pytest.raises(ContractError, match="occupancy"):
        require("execution", "available_slots")(seed, capability, authority, None)


def test_observation_when_recorded_payload_hash_corrupted(seed,capability,authority,tmp_path):
    # Given: recorded immutable request bytes no longer match their stored digest.
    state,packet=reserved(seed,capability,authority,tmp_path)
    attempt=state.attempts[0]
    corrupt=attempt.prepared.model_copy(update={"prompt_text":"tampered recorded payload"})
    state=state.model_copy(update={"attempts":(attempt.model_copy(update={"prepared":corrupt}),)})
    # When / Then: a supplied receipt cannot authenticate a corrupted local request record.
    with pytest.raises(ContractError,match="request"):
        require("execution","observe")(state,"ATT-1",Receipt(phase=Phase.SUBMITTED,job_id="fixture-job",evidence="receipt",request_hash=packet.request_hash))


def test_not_received_when_job_identity_was_already_acknowledged(seed,capability,authority,tmp_path):
    # Given: a known remote job became temporarily unobservable.
    state,packet=reserved(seed,capability,authority,tmp_path)
    observe=require("execution","observe")
    state=observe(state,"ATT-1",Receipt(phase=Phase.SUBMITTED,job_id="fixture-job",evidence="ack",request_hash=packet.request_hash))
    state=observe(state,"ATT-1",Receipt(phase=Phase.UNKNOWN,evidence="temporary lookup failure",request_hash=packet.request_hash))
    # When / Then: absence cannot rewrite the known identity into a never-received request.
    with pytest.raises(ContractError,match="job"):
        observe(state,"ATT-1",Receipt(phase=Phase.NOT_RECEIVED,evidence="absence is not terminal proof",request_hash=packet.request_hash))
