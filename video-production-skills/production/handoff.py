"""Coverage, exact join revisions and whole-flow evidence gate local post handoff."""
from dataclasses import dataclass
from pathlib import Path
from production.files import verified_file
import hashlib
import json

from production.contracts import fingerprint, selection_for, usable, validate_state
from production.models import (
    ContractError, FlowReview, Handoff, JoinReview, Selection, State, Verdict,
)


@dataclass(frozen=True, slots=True)
class Progress:
    required: int
    accepted: int
    conditional: int
    coverage_required: int
    coverage_fulfilled: int
    joins_required: int
    joins_passed: int


def current(state: State, selection: Selection | None) -> bool:
    return bool(selection and usable(selection) and selection.reviewed_fingerprint == fingerprint(state, selection.take.clip_id))


def selection_hash(state: State) -> str:
    data = {"batch": state.batch.model_dump(mode="json"),
        "selections": [source.model_dump(mode="json") if (source := selection_for(state, cid)) is not None else None for cid in state.batch.edit_order],
        "joins": [r.model_dump(mode="json") for r in state.join_reviews]}
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def check_join(state: State, review: JoinReview) -> None:
    plan = next((j for j in state.batch.joins if j.id == review.join_id), None)
    if plan is None:
        raise ContractError("join", "unknown boundary")
    before, after = selection_for(state, plan.before), selection_for(state, plan.after)
    if not current(state, before) or not current(state, after) or before is None or after is None:
        raise ContractError("revision", "boundary has no valid current selections")
    expected = (before.take.id, after.take.id, before.acceptance_revision, after.acceptance_revision,
        before.take.range_revision, after.take.range_revision)
    actual = (review.before_take, review.after_take, review.before_revision, review.after_revision,
        review.before_range_revision, review.after_range_revision)
    if actual != expected:
        raise ContractError("revision", "boundary report is for other take/range revisions")
    if not set(review.observed_changes) <= set(plan.allowed_changes):
        raise ContractError("change", "observed state change is not permitted by approved edit")
    if review.reveal_order != plan.reveal_order:
        raise ContractError("reveal", "observed reveal violates approved board order")
    if not review.passed or not review.continuous_playback:
        raise ContractError("join", "actual continuous boundary review is missing")


def progress(state: State) -> Progress:
    valid = [s for s in state.selections if current(state, s)]
    fulfilled = {rid for s in valid for rid in s.review.fulfilled}
    passed = 0
    for review in state.join_reviews:
        try:
            check_join(state, review)
        except ContractError:
            continue
        passed += 1
    return Progress(required=len(state.batch.clips),
        accepted=sum(s.review.verdict == Verdict.ACCEPTED for s in valid),
        conditional=sum(s.review.verdict == Verdict.CONDITIONAL for s in valid),
        coverage_required=len(state.batch.coverage),
        coverage_fulfilled=len(fulfilled & {r.id for r in state.batch.coverage}),
        joins_required=len(state.batch.joins), joins_passed=passed)


def build_handoff(state: State, flow: FlowReview, receiver: str, rights_evidence: str, root: Path) -> Handoff:
    validate_state(state)
    from production.upstream import verify_scope
    verify_scope(state,root)
    selections: list[Selection] = []
    for clip in state.batch.clips:
        selection = selection_for(state, clip.id)
        if not current(state, selection) or selection is None or set(selection.review.fulfilled) != set(clip.requirements):
            raise ContractError("coverage", f"unfulfilled required source {clip.id}")
        _ = verified_file(root, selection.take.asset)
        _ = verified_file(root, selection.approval.evidence)
        selections.append(selection)
    if {rid for s in selections for rid in s.review.fulfilled} != {r.id for r in state.batch.coverage}:
        raise ContractError("coverage", "required coverage is incomplete")
    if len(state.join_reviews) != len(state.batch.joins) or {j.join_id for j in state.join_reviews} != {j.id for j in state.batch.joins}:
        raise ContractError("join", "all required boundaries need current reports")
    for review in state.join_reviews:
        check_join(state, review)
    if (not flow.passed or not flow.continuous_playback or flow.selection_hash != selection_hash(state)
        or flow.review_render.selection_hash != flow.selection_hash
        or flow.clip_order != state.batch.edit_order
        or (any(s.take.has_audio for s in selections) and not flow.audio_listened)):
        raise ContractError("flow", "missing/current full-sequence playback evidence")
    if not receiver or not rights_evidence:
        raise ContractError("handoff", "post recipient and rights record required")
    ordered = tuple(next(s for s in selections if s.take.clip_id == cid) for cid in state.batch.edit_order)
    return Handoff(batch_id=state.batch.id, scope_revision=state.batch.scope_revision,
        selection_hash=selection_hash(state), selections=ordered, joins=state.join_reviews, flow=flow,
        receiver=receiver, rights_evidence=rights_evidence,
        handles=tuple((s.take.clip_id, 0, 0) for s in ordered))
