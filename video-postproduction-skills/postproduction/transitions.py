"""Generic locked edits cannot manufacture/remove historical process facts or adopt artifacts."""
from postproduction.errors import ContractError
from postproduction.job_models import JobPhase
from postproduction.revisions import work_fingerprint
from postproduction.state_models import PostState


def validate_edit_transition(before: PostState, after: PostState) -> None:
    """Only narrow observation/materialization APIs may publish those kinds of known facts."""
    if before.intake!=after.intake or before.intake_history!=after.intake_history:
        raise ContractError("intake", "source scope changes require explicit actual re-adoption revision")
    if before.deliveries != after.deliveries:
        raise ContractError("delivery", "generic edits cannot forge/remove local delivered package facts")
    if before.reviews != after.reviews:
        raise ContractError("review", "generic edits cannot import/erase local computed QA gates")
    if before.invalidations != after.invalidations:
        raise ContractError("invalidation", "generic edits cannot forge/remove explicit revocation history")
    if before.environment_events != after.environment_events:
        raise ContractError("environment", "generic edits cannot forge/remove historical installation observations")
    for prior in before.jobs:
        current = next((j for j in after.jobs if j.id == prior.id),None)
        if current != prior:
            raise ContractError("fact", "generic edits cannot replace/remove a known native process fact")
    for job in after.jobs:
        if any(j.id == job.id for j in before.jobs):
            continue
        if (job.phase != JobPhase.DISPATCHING or job.job_id is not None or job.observations
            or job.packet.input_fingerprint != work_fingerprint(after,job.packet.order)):
            raise ContractError("fact", "new jobs must be current unexecuted reservations, not invented results")
        others = tuple(j for j in after.jobs if j.packet.order.id == job.packet.order.id)
        if len(others) > job.packet.order.max_attempts:
            raise ContractError("attempt", "new reservation exceeds explicit bounded attempt scope")
    for order in before.orders:
        if next((o for o in after.orders if o.id == order.id),None) != order:
            raise ContractError("work", "known work needs an explicit revision path, not silent replacement")
    if before.artifacts != after.artifacts:
        raise ContractError("artifact", "generic edits cannot materialize/adopt native artifacts")
