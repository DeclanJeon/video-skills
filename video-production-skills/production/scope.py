"""Explicit approved scope revisions preserve remote history and invalidate prior QA."""
from pathlib import Path

from production.files import verified_file
from production.models import Batch, ContractError, Digest, Frozen, Nonempty, Pin, ScopeChangeRecord, State
from production.upstream import derive_asset_uses, derive_coverage, verify_scope


class ScopeGrant(Frozen):
    old_source_hash: Digest
    old_scope_revision: Nonempty
    new_source: Pin
    new_scope_revision: Nonempty
    removed: tuple[str, ...]
    added: tuple[str, ...]
    changed: tuple[str, ...]
    asset_changes: tuple[str, ...]
    evidence: Pin


def revise_scope(state: State, batch: Batch, grant: ScopeGrant, root: Path) -> State:
    """Apply exact approved coverage/asset deltas; never reset attempts or slot reservations."""
    old_path=verified_file(root,state.coverage_source)
    new_path=verified_file(root,grant.new_source)
    _=verified_file(root,grant.evidence)
    if (grant.old_source_hash != state.coverage_source.sha256 or grant.old_scope_revision != state.batch.scope_revision
        or batch.scope_revision != grant.new_scope_revision or batch.scope_revision == state.batch.scope_revision
        or batch.id != state.batch.id or batch.revision <= state.batch.revision):
        raise ContractError("scope","scope grant does not bind exact old/new batch revisions")
    coverage=derive_coverage(new_path)
    old={r.id:r for r in state.approved_coverage}
    new={r.id:r for r in coverage}
    changed={rid for rid in old.keys() & new.keys() if old[rid] != new[rid]}
    if (set(grant.removed) != old.keys()-new.keys() or set(grant.added) != new.keys()-old.keys()
        or set(grant.changed) != changed):
        raise ContractError("scope","removed/added/replaced coverage differs from explicit approval")
    old_assets={(u.shot,u.pin.id):u.pin for u in derive_asset_uses(old_path)}
    new_assets={(u.shot,u.pin.id):u.pin for u in derive_asset_uses(new_path)}
    asset_changes={f"{shot}:{aid}" for shot,aid in old_assets.keys() | new_assets.keys() if old_assets.get((shot,aid)) != new_assets.get((shot,aid))}
    if set(grant.asset_changes) != asset_changes:
        raise ContractError("scope","mandatory asset changes were not explicitly approved")
    current_ids={c.id for c in batch.clips}
    retained=tuple(s.model_copy(update={"valid":False}) for s in state.selections if s.take.clip_id in current_ids)
    removed=tuple(s for s in state.selections if s.take.clip_id not in current_ids)
    updated=state.model_copy(update={"batch":batch,"coverage_source":grant.new_source,"approved_coverage":coverage,
        "selections":retained,"history":(*state.history,*removed),"join_reviews":(),
        "change_evidence":(*state.change_evidence,grant.evidence.path),
        "scope_history":(*state.scope_history,ScopeChangeRecord(evidence=grant.evidence,old_source=state.coverage_source,new_source=grant.new_source,old_scope_revision=state.batch.scope_revision,new_scope_revision=grant.new_scope_revision,removed=grant.removed,added=grant.added,changed=grant.changed,asset_changes=grant.asset_changes))})
    verify_scope(updated,root)
    return updated
