"""Current adoption is stricter than reading durable historical facts."""
from pathlib import Path

from production.handoff import build_handoff
from production.models import ContractError as ProductionError, State
from pydantic import ValidationError

from postproduction.admission import admit_source
from postproduction.errors import ContractError
from postproduction.intake import adopt_request
from postproduction.ledger_io import document
from postproduction.jobs import validate_jobs
from postproduction.state_models import PostState
from postproduction.timeline import timeline_digest, validate_timeline


def validate_structure(state: PostState) -> None:
    """Reimported timelines cannot delete requirements, forge event maps or invent parents."""
    if not state.timelines or len({t.branch for t in state.timelines}) != len(state.timelines):
        raise ContractError("timeline", "one current timeline per nonempty approved branch set required")
    validate_jobs(state)
    known = (*state.timelines,*state.timeline_history)
    for timeline in state.timelines:
        parent = next((t for t in known if timeline_digest(t) == timeline.parent_timeline_digest),None)
        if timeline.parent_timeline_digest is not None and parent is None:
            raise ContractError("timeline", "parent timeline lineage is missing")
        validate_timeline(state.intake,timeline,parent)


def validate_current(state: PostState, path: Path) -> None:
    """Re-observe pinned inputs and current live producer selections without mutating either owner."""
    validate_structure(state)
    fresh = adopt_request(path.parent,state.intake.request,path)
    if fresh != state.intake:
        raise ContractError("revision", "adopted request/source facts are no longer exact current inputs")
    raw = document(path)
    if "production" not in raw:
        return  # Explicit separately supplied, pinned external handoff; no live producer namespace to claim.
    try:
        live = State.model_validate(raw["production"])
        old = state.intake.handoff
        current = build_handoff(live,old.flow,old.receiver,old.rights_evidence,path.parent)
        if current != old:
            raise ContractError("revision", "live production selections/scope are not the adopted handoff")
        for selected in current.selections:
            _ = admit_source(live,selected,path.parent)
    except (ProductionError,ValidationError,OSError) as exc:
        raise ContractError("currentness", f"live source cannot be currently adopted: {exc}") from exc
