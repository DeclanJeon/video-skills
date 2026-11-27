"""Meaningful work fingerprints omit unrelated polling/root revision and unconsumed sources."""
import hashlib
from pathlib import Path

from production.contracts import clip_for, selection_for, validate_state
from production.models import ContractError as ProductionError, State as ProductionState
from pydantic import ValidationError

from postproduction.admission import admit_source, local_pin
from postproduction.adoption_scope import verify_adopted_decisions
from postproduction.files import verified_file
from postproduction.ledger_io import document

from postproduction.common import Frozen, Pin
from postproduction.edit_models import DeliveryProfile
from postproduction.errors import ContractError
from postproduction.intake_models import SourceCaps
from postproduction.invalidation_models import Invalidation
from postproduction.job_models import ArtifactRef, JobPhase
from postproduction.backends.base import JobObservation
from postproduction.state_models import PostState
from postproduction.timeline_models import TimelineSegment
from postproduction.work_models import WorkOrder
from postproduction.timeline import timeline_digest, validate_timeline


def verify_work_inputs(state: PostState, order: WorkOrder, project: Path) -> None:
    """A consumed derived artifact consumes its producer inputs, not just currently unchanged output bytes."""
    pending: list[tuple[WorkOrder,tuple[str, ...]]] = [(order,())]
    verified: set[str] = set()
    while pending:
        current,ancestors = pending.pop()
        if current.id in ancestors:
            raise ContractError("dependency", "derived work dependency cycle")
        if current.id in verified:
            continue
        _verify_order_inputs(state,current,project)
        verified.add(current.id)
        for dep in current.dependencies:
            artifact = next((a for a in state.artifacts if (a.pin.id,a.pin.path)==(dep.id,dep.path)),None)
            if artifact is None:
                continue  # Actual externally supplied inputs retain their explicit pin/authority contract.
            job = next((j for j in state.jobs if j.id==artifact.job_id),None)
            if (artifact.pin != dep or artifact.proof is None or job is None or job.phase != JobPhase.SUCCEEDED
                or artifact.input_fingerprint != job.packet.input_fingerprint
                or work_fingerprint(state,job.packet.order) != artifact.input_fingerprint):
                raise ContractError("dependency", "consumed artifact is not exact current known producer work")
            for pin in (artifact.pin,artifact.proof,*artifact.related):
                _ = verified_file(project.parent,pin)
            proof = JobObservation.model_validate_json(verified_file(project.parent,artifact.proof).read_bytes())
            required = (*((proof.native_project,) if proof.native_project is not None else ()),*proof.frames,*proof.related_assets)
            if (not proof.technical_verified or proof.artifact != artifact.pin
                or proof.receipt.request_hash != job.request_hash or any(p not in artifact.related for p in required)):
                raise ContractError("dependency", "consumed artifact native/source/sidecar technical proof incomplete")
            pending.append((job.packet.order,(*ancestors,current.id)))


def _verify_order_inputs(state: PostState, order: WorkOrder, project: Path) -> None:
    """Re-admit exact consumed live sources/pins without invalidating independent unrelated work."""
    if any(order.id in value.order_ids for value in state.invalidations):
        raise ContractError("invalidation", "work explicitly invalidated; retain facts and prepare a revised work identity")
    root = project.parent
    verify_adopted_decisions(state.intake,root)
    timeline = next((t for t in state.timelines if t.branch == order.branch),None)
    if timeline is None:
        raise ContractError("branch", "consumed work branch is not adopted")
    known = (*state.timelines,*state.timeline_history)
    parent = next((t for t in known if timeline_digest(t)==timeline.parent_timeline_digest),None)
    if timeline.parent_timeline_digest is not None and parent is None:
        raise ContractError("timeline", "consumed work timeline parent is missing")
    validate_timeline(state.intake,timeline,parent)
    for anchor in state.intake.request.anchors:
        if anchor.source in order.source_refs:
            _ = verified_file(root,anchor.evidence)
    for pin in (*order.dependencies,*((order.recipe,) if order.recipe is not None else ()),
                state.intake.request.authority,state.intake.authority.evidence):
        _ = verified_file(root,pin)
    raw = document(project)
    try:
        live = ProductionState.model_validate(raw["production"]) if "production" in raw else state.intake.snapshot
        validate_state(live)
        expected = state.intake.snapshot
        if (live.batch.scope_revision,live.approved_coverage,live.coverage_source) != (
            expected.batch.scope_revision,expected.approved_coverage,expected.coverage_source):
            raise ContractError("scope", "live required coverage differs from adopted source scope")
        _ = verified_file(root,local_pin(live.coverage_source))
        for ref in order.source_refs:
            source = next((s for s in state.intake.sources if s.source == ref),None)
            selected = selection_for(live,ref.clip_id)
            if source is None or selected is None or selected.take.id != ref.take_id:
                raise ContractError("source", "consumed live source identity was replaced or removed")
            clip = clip_for(live,ref.clip_id)
            for pin in (clip.prompt,*clip.assets,*clip.dependencies):
                _ = verified_file(root,local_pin(pin))
            if admit_source(live,selected,root) != source:
                raise ContractError("revision", "consumed source bytes/approval/range/QA revision changed")
    except (ProductionError,ValidationError,OSError) as exc:
        raise ContractError("currentness", f"consumed work input cannot be currently adopted: {exc}") from exc


def consumed_pins(state: PostState, order: WorkOrder) -> tuple[Pin, ...]:
    """Stable entity/path identities for actual source/dependency and global editing decisions."""
    request = state.intake.request
    pins = [request.snapshot,request.handoff,request.schema_pin,request.brief,request.profile,request.authority,
            state.intake.authority.evidence,*order.dependencies]
    if order.recipe is not None:
        pins.append(order.recipe)
    for source in state.intake.sources:
        if source.source in order.source_refs:
            pins.extend((source.asset,source.approval))
            clip = clip_for(state.intake.snapshot,source.source.clip_id)
            pins.extend(local_pin(p) for p in (clip.prompt,*clip.assets,*clip.dependencies))
    pins.extend(a.evidence for a in request.anchors if a.source in order.source_refs)
    return tuple(pins)


def invalidate_dependents(state: PostState, changed_pins: tuple[Pin, ...]) -> PostState:
    """Revoke only direct/transitive consumers; explicit invalidation never deletes receipts or grants current QA."""
    if not changed_pins:
        raise ContractError("invalidation", "actual changed pin identities required")
    keys = {(p.id,p.path) for p in changed_pins}
    affected: set[str] = set()
    while True:
        before = (len(keys),len(affected))
        for order in state.orders:
            if any((p.id,p.path) in keys for p in consumed_pins(state,order)):
                affected.add(order.id)
        for artifact in state.artifacts:
            job = next((j for j in state.jobs if j.id==artifact.job_id),None)
            if job is not None and ((artifact.pin.id,artifact.pin.path) in keys or job.packet.order.id in affected):
                affected.add(job.packet.order.id)
                keys.add((artifact.pin.id,artifact.pin.path))
        if before == (len(keys),len(affected)):
            break
    artifacts: list[ArtifactRef] = []
    for artifact in state.artifacts:
        job = next((j for j in state.jobs if j.id==artifact.job_id),None)
        artifacts.append(artifact.model_copy(update={"adopted":False}) if job is not None and job.packet.order.id in affected else artifact)
    record = Invalidation(id=f"INV-{len(state.invalidations)+1}",changed_pins=changed_pins,
                          order_ids=tuple(o.id for o in state.orders if o.id in affected))
    return state.model_copy(update={"artifacts":tuple(artifacts),"invalidations":(*state.invalidations,record)})


class WorkInputs(Frozen):
    order: WorkOrder
    segments: tuple[TimelineSegment, ...]
    sources: tuple[SourceCaps, ...]
    profile: DeliveryProfile
    authority: Pin


def work_fingerprint(state: PostState, order: WorkOrder) -> str:
    """Bind only actually consumed source/range/review and work/profile/authority decisions."""
    timeline = next((t for t in state.timelines if t.branch == order.branch),None)
    if timeline is None:
        raise ContractError("branch", "work has no adopted branch timeline")
    sources = tuple(s for s in state.intake.sources if s.source in order.source_refs)
    if len(sources) != len(order.source_refs):
        raise ContractError("source", "work references a source absent from adopted intake")
    segments = tuple(s for s in timeline.segments if s.source in order.source_refs)
    value = WorkInputs(order=order,segments=segments,sources=sources,profile=state.intake.profile,
                       authority=state.intake.request.authority)
    return hashlib.sha256(value.model_dump_json().encode()).hexdigest()
