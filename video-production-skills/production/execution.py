"""Pure attempt transitions. Calling these functions never sends a remote request."""
from typing import Final

from production.bindings import prepare_request
from production.files import packet_hash
from production.contracts import ACTIVE, fingerprint
from production.models import (
    Attempt, AttemptId, Authority, Capability, ContractError, Phase, Prepared,
    Receipt, State,
)
from pathlib import Path

TRANSITIONS: Final[dict[Phase, set[Phase]]] = {
    Phase.SUBMITTING: {Phase.UNKNOWN, Phase.SUBMITTED, Phase.RUNNING, Phase.SUCCEEDED, Phase.NOT_RECEIVED, Phase.FAILED, Phase.CANCELLED},
    Phase.UNKNOWN: {Phase.SUBMITTED, Phase.RUNNING, Phase.SUCCEEDED, Phase.FAILED, Phase.CANCELLED, Phase.NOT_RECEIVED},
    Phase.SUBMITTED: {Phase.RUNNING, Phase.UNKNOWN, Phase.SUCCEEDED, Phase.FAILED, Phase.CANCELLED},
    Phase.RUNNING: {Phase.UNKNOWN, Phase.SUCCEEDED, Phase.FAILED, Phase.CANCELLED},
    Phase.SUCCEEDED: {Phase.DOWNLOADED},
    Phase.FAILED: set(),
    Phase.CANCELLED: set(),
    Phase.NOT_RECEIVED: set(),
    Phase.DOWNLOADED: set(),
}


def available_slots(state: State, capability: Capability, authority: Authority,
                    external_active: int | None) -> int:
    if external_active is None or external_active < 0:
        raise ContractError("occupancy", "observed account occupancy required")
    own = sum(a.phase in ACTIVE and a.prepared.capability.account == capability.account for a in state.attempts)
    return max(0, min(capability.max_active, authority.max_active) - own - external_active)


def reserve(state: State, packet: Prepared, attempt_id: AttemptId,
            external_active: int | None, root: Path) -> State:
    """Journal a reservation before any external side effect; safe to persist atomically."""
    if any(a.id == attempt_id for a in state.attempts):
        raise ContractError("attempt", "attempt identity already journaled")
    if packet_hash(packet) != packet.request_hash:
        raise ContractError("request", "prepared packet has been modified")
    if fingerprint(state, packet.clip_id) != packet.fingerprint:
        raise ContractError("revision", "prepared inputs changed")
    refreshed = prepare_request(state, packet.clip_id, packet.capability, packet.authority, packet.bindings, root)
    if refreshed != packet:
        raise ContractError("request", "current payload differs")
    if available_slots(state, packet.capability, packet.authority, external_active) < 1:
        raise ContractError("slot", "no confirmed remote capacity")
    attempts = sum(a.prepared.clip_id == packet.clip_id for a in state.attempts)
    if attempts >= packet.authority.max_attempts:
        raise ContractError("authority", "attempt allowance exhausted")
    attempt = Attempt(id=attempt_id, prepared=packet, phase=Phase.SUBMITTING)
    return state.model_copy(update={"attempts": (*state.attempts, attempt)})


def observe(state: State, attempt_id: str, receipt: Receipt) -> State:
    """Import an operator-observed receipt, never infer failure from an absent response."""
    if len({a.id for a in state.attempts}) != len(state.attempts):
        raise ContractError("attempt", "ambiguous duplicate attempt identities")
    previous = next((a for a in state.attempts if a.id == attempt_id), None)
    if previous is None:
        raise ContractError("attempt", "unknown attempt identity")
    if packet_hash(previous.prepared) != previous.prepared.request_hash:
        raise ContractError("request", "recorded request payload digest is corrupt")
    if receipt.request_hash != previous.prepared.request_hash:
        raise ContractError("request", "receipt belongs to another payload")
    if (previous.job_id is not None or receipt.job_id is not None) and receipt.phase in {Phase.NOT_RECEIVED}:
        raise ContractError("job", "known remote identity requires terminal confirmation, not a non-receipt claim")
    if receipt.phase not in {Phase.UNKNOWN, Phase.NOT_RECEIVED, Phase.FAILED} and not receipt.job_id:
        raise ContractError("job", "confirmed remote job ID required")
    if receipt.phase not in TRANSITIONS[previous.phase]:
        raise ContractError("transition", f"{previous.phase} -> {receipt.phase} not permitted")
    if previous.job_id and receipt.job_id and previous.job_id != receipt.job_id:
        raise ContractError("job", "receipt remote identity changed")
    job_id = receipt.job_id or previous.job_id
    updated = previous.model_copy(update={"phase": receipt.phase, "job_id": job_id,
        "terminal_evidence": receipt.evidence})
    return state.model_copy(update={"attempts": tuple(updated if a.id == attempt_id else a for a in state.attempts)})
