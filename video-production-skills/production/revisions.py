"""Invalidate consumed revisions without rewriting historical remote facts."""
from production.models import ContractError, Selection, State
from production.contracts import clip_for, selection_for


def invalidate_selection(state: State, clip_id: str, evidence: str) -> State:
    if not evidence:
        raise ContractError("evidence", "invalidation needs an observed reason")
    previous = selection_for(state, clip_id)
    if previous is None:
        raise ContractError("selection", "no current selection")
    invalid = previous.model_copy(update={"valid": False, "acceptance_revision": previous.acceptance_revision + 1})
    updated = replace_selection(state, invalid)
    return updated.model_copy(update={"change_evidence": (*state.change_evidence, evidence)})


def replace_selection(state: State, selection: Selection) -> State:
    """Publish a new reviewed selection and invalidate affected descendants/joins.

    Admission QA belongs to quality.accept_take; this primitive is also used to
    explicitly invalidate or revalidate existing selections.
    """
    _ = clip_for(state, selection.take.clip_id)
    old = selection_for(state, selection.take.clip_id)
    if old is not None and selection.acceptance_revision <= old.acceptance_revision:
        raise ContractError("revision", "acceptance revision must increase")
    affected = {selection.take.clip_id}
    while True:
        more = {c.id for c in state.batch.clips if any(r.source_clip in affected for r in c.references)}
        if more <= affected:
            break
        affected |= more
    kept = tuple(s.model_copy(update={"valid": False}) if s.take.clip_id in affected else s
        for s in state.selections if s.take.clip_id != selection.take.clip_id)
    affected_joins = {j.id for j in state.batch.joins if j.before in affected or j.after in affected}
    return state.model_copy(update={
        "selections": (*kept, selection),
        "history": (*state.history, *((old,) if old is not None else ())),
        "join_reviews": tuple(j for j in state.join_reviews if j.join_id not in affected_joins),
    })
