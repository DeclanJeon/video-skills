"""Narrow native observation transitions, separate from current-input and materialization gates."""
import hashlib

from postproduction.errors import ContractError
from postproduction.job_models import JobPhase, JobReceipt, PostJob
from postproduction.revisions import work_fingerprint
from postproduction.state_models import PostState
from postproduction.work_models import RequestPacket

ACTIVE = frozenset({JobPhase.DISPATCHING,JobPhase.UNKNOWN,JobPhase.RUNNING,JobPhase.SUCCEEDED})
TERMINAL = frozenset({JobPhase.SUCCEEDED,JobPhase.FAILED,JobPhase.CANCELLED,JobPhase.NOT_STARTED})


def request_digest(packet: RequestPacket) -> str:
    """Hash the entire immutable typed header and exact backend-native bytes."""
    return hashlib.sha256(packet.model_dump_json().encode()).hexdigest()


def validate_jobs(state: PostState) -> None:
    """Retain historical packets without requiring their inputs still be adoptable."""
    if len({o.id for o in state.orders}) != len(state.orders) or len({j.id for j in state.jobs}) != len(state.jobs):
        raise ContractError("duplicate", "work and attempt IDs must be unique")
    for job in state.jobs:
        if job.request_hash != request_digest(job.packet) or not any(o.id == job.packet.order.id for o in state.orders):
            raise ContractError("request", "stored job is not bound to an immutable known work packet")


def reserve_work(state: PostState, packet: RequestPacket) -> PostState:
    """Reserve before dispatch; uncertain or succeeded-but-unadopted work is not rerun."""
    validate_jobs(state)
    prior = tuple(j for j in state.jobs if j.packet.order.id == packet.order.id)
    if any(j.phase in ACTIVE for j in prior):
        raise ContractError("reserved", "known work remains reserved; observe/reconcile before another dispatch")
    if len(prior) >= packet.order.max_attempts:
        raise ContractError("attempt", "approved bounded local attempt count exhausted")
    old = next((o for o in state.orders if o.id == packet.order.id),None)
    if old is not None and old != packet.order:
        raise ContractError("work", "existing work identity needs an explicit revision, not silent replacement")
    if packet.input_fingerprint != work_fingerprint(state,packet.order):
        raise ContractError("revision", "prepared native packet no longer matches current consumed inputs")
    job = PostJob(id=f"{packet.order.id}-A{len(prior)+1}",packet=packet,
                  request_hash=request_digest(packet),phase=JobPhase.DISPATCHING)
    return state.model_copy(update={"orders":state.orders if old is not None else (*state.orders,packet.order),
                                    "jobs":(*state.jobs,job)})


def observe_job(state: PostState, job_id: str, receipt: JobReceipt) -> PostState:
    """Record only observed process facts; no caller-declared local materialization/QA gate."""
    validate_jobs(state)
    job = next((j for j in state.jobs if j.id == job_id),None)
    if job is None:
        raise ContractError("job", "unknown reserved attempt")
    if receipt.phase in {JobPhase.DISPATCHING,JobPhase.MATERIALIZED}:
        raise ContractError("observation", "local dispatch/materialization gates are not process observations")
    if receipt.request_hash != job.request_hash or job.request_hash != request_digest(job.packet):
        raise ContractError("request", "observation differs from the canonical reserved packet")
    if job.job_id is not None and receipt.job_id is not None and job.job_id != receipt.job_id:
        raise ContractError("job", "observation cannot replace the known process identity")
    if receipt.phase == JobPhase.NOT_STARTED and (job.job_id is not None or receipt.job_id is not None):
        raise ContractError("job", "known process cannot be declared never started")
    if receipt.phase in {JobPhase.RUNNING,JobPhase.SUCCEEDED,JobPhase.FAILED,JobPhase.CANCELLED} and not receipt.job_id:
        raise ContractError("job", "observed native process phase needs a concrete process identity")
    if job.phase in TERMINAL and receipt.phase != job.phase:
        raise ContractError("transition", "a known terminal fact cannot regress or contradict itself")
    updated = job.model_copy(update={"phase":receipt.phase,"job_id":receipt.job_id or job.job_id,
                                    "observations":(*job.observations,receipt)})
    return state.model_copy(update={"jobs":tuple(updated if j.id == job.id else j for j in state.jobs)})
