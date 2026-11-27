"""Pure coverage, dependency and input-revision contracts."""
import hashlib
import json
from typing import Final

from production.models import Batch, Clip, ClipId, ContractError, Phase, Selection, State, Verdict

ACTIVE: Final = frozenset({Phase.SUBMITTING, Phase.UNKNOWN, Phase.SUBMITTED, Phase.RUNNING})


def validate_batch(batch: Batch) -> None:
    """Reject incomplete coverage and ambiguous or cyclic dependency graphs."""
    ids = [c.id for c in batch.clips]
    req_ids = [r.id for r in batch.coverage]
    join_ids = [j.id for j in batch.joins]
    if not ids or not req_ids:
        raise ContractError("coverage", "approved coverage and clip list must be nonempty")
    if len(set(ids)) != len(ids) or len(set(req_ids)) != len(req_ids) or len(set(join_ids)) != len(join_ids):
        raise ContractError("duplicate", "clip, coverage and join IDs must be unique")
    if len(batch.edit_order) != len(ids) or set(batch.edit_order) != set(ids):
        raise ContractError("order", "edit order must cover every clip exactly once")
    reqs = {r.id: r for r in batch.coverage}
    mapped: set[str] = set()
    graph: dict[str, set[str]] = {}
    for clip in batch.clips:
        pins: dict[str, str] = {}
        for pin in (*clip.assets,*clip.dependencies):
            signature = pin.model_dump_json()
            if pin.id in pins and pins[pin.id] != signature:
                raise ContractError("asset", f"conflicting pins for {pin.id}")
            pins[pin.id] = signature
        if not clip.shots or not clip.requirements:
            raise ContractError("coverage", f"empty allocation for {clip.id}")
        for rid in clip.requirements:
            if rid not in reqs or reqs[rid].shot not in clip.shots:
                raise ContractError("coverage", f"invalid mapping {clip.id}/{rid}")
            mapped.add(rid)
        if set(clip.shots) != {reqs[rid].shot for rid in clip.requirements}:
            raise ContractError("coverage", f"unmapped shot inside {clip.id}")
        graph[clip.id] = set()
        for ref in clip.references:
            if ref.source_clip not in ids or not ref.imports:
                raise ContractError("reference", f"invalid source/imports for {clip.id}")
            graph[clip.id].add(ref.source_clip)
    if mapped != set(req_ids):
        raise ContractError("coverage", f"unmapped requirements: {set(req_ids) - mapped}")
    resolved: set[str] = set()
    while len(resolved) < len(ids):
        ready = {key for key, deps in graph.items() if key not in resolved and deps <= resolved}
        if not ready:
            raise ContractError("cycle", "active reference graph is cyclic")
        resolved |= ready
    pairs = {(j.before, j.after) for j in batch.joins}
    required_pairs = set(zip(batch.edit_order, batch.edit_order[1:]))
    if not required_pairs <= pairs:
        # Single clips need no join. Multi-clip plans must explicitly declare even intentional cuts.
        raise ContractError("join", "every adjacent edit pair needs a relation")
    for join in batch.joins:
        if join.before not in ids or join.after not in ids or join.before == join.after:
            raise ContractError("join", f"invalid endpoint {join.id}")


def validate_state(state: State) -> None:
    validate_batch(state.batch)
    if state.batch.coverage != state.approved_coverage:
        raise ContractError("coverage", "batch coverage differs from approved source set")
    if len({a.id for a in state.attempts}) != len(state.attempts):
        raise ContractError("duplicate", "attempt IDs must be unique")
    if len({s.take.clip_id for s in state.selections}) != len(state.selections):
        raise ContractError("duplicate", "one current selection per clip")
    if len({j.join_id for j in state.join_reviews}) != len(state.join_reviews):
        raise ContractError("duplicate", "one current report per join")


def clip_for(state: State, clip_id: str) -> Clip:
    for clip in state.batch.clips:
        if clip.id == clip_id:
            return clip
    raise ContractError("clip", f"unknown clip {clip_id}")


def selection_for(state: State, clip_id: str) -> Selection | None:
    return next((s for s in state.selections if s.take.clip_id == clip_id), None)


def fingerprint(state: State, clip_id: str) -> str:
    """Pin only consumed design/asset/source revisions, not unrelated batch edits."""
    clip = clip_for(state, clip_id)
    payload = {
        "scope": state.batch.scope_revision,
        "coverage_source": state.coverage_source.model_dump(mode="json"),
        "clip": clip.model_dump(mode="json"),
        "coverage": [r.model_dump(mode="json") for r in state.batch.coverage if r.id in clip.requirements],
        "sources": [source.model_dump(mode="json") if (source := selection_for(state, ref.source_clip)) is not None else None for ref in clip.references],
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def usable(selection: Selection | None, imports: tuple[str, ...] = ()) -> bool:
    if selection is None or not selection.valid:
        return False
    match selection.review.verdict:
        case Verdict.ACCEPTED:
            return True
        case Verdict.CONDITIONAL:
            return bool(selection.review.conditional_policy and selection.review.post_receiver and selection.review.post_fix and not set(imports) & set(selection.review.defects))
        case Verdict.REJECTED:
            return False
        case unreachable:
            from typing import assert_never
            assert_never(unreachable)


def ready_clips(state: State) -> tuple[ClipId, ...]:
    validate_state(state)
    reviewed_attempts = {s.take.attempt_id for s in (*state.selections, *state.history)}
    busy = {a.prepared.clip_id for a in state.attempts if a.phase in ACTIVE or (a.phase in {Phase.SUCCEEDED, Phase.DOWNLOADED} and a.id not in reviewed_attempts)}
    ready: list[ClipId] = []
    for clip in state.batch.clips:
        own = selection_for(state, clip.id)
        if clip.id in busy or usable(own):
            continue
        # A stale selection must be explicitly revalidated, not silently rescheduled.
        if own is not None and not own.valid:
            continue
        satisfied = True
        for ref in clip.references:
            source = selection_for(state, ref.source_clip)
            source_current = source is not None and source.reviewed_fingerprint == fingerprint(state, ref.source_clip)
            if not (source_current and usable(source, ref.imports)) and (ref.required or not ref.omission_evidence):
                satisfied = False
        if satisfied:
            ready.append(clip.id)
    return tuple(ready)
