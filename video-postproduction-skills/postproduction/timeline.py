"""Canonical timeline construction never edits a native file or certifies a final playback."""
import hashlib

from postproduction.clock import map_frame
from postproduction.edit_models import Change
from postproduction.errors import ContractError
from postproduction.intake_models import PostIntake
from postproduction.timeline_map import FILM_CLOCK, event_maps, layout
from postproduction.timeline_models import CutSpec, EditProposal, PostTimeline


def timeline_digest(timeline: PostTimeline) -> str:
    """Pin the typed decision serialization, not an unrelated mutable ledger revision."""
    return hashlib.sha256(timeline.model_dump_json().encode()).hexdigest()


def validate_timeline(intake: PostIntake, timeline: PostTimeline, parent: PostTimeline | None = None) -> None:
    """Reconstruct decisions at reimport/persistence; a native edit cannot forge maps or coverage."""
    cuts: list[CutSpec] = []
    position = 0
    for segment in timeline.segments:
        overlap = position-segment.timeline_range.start
        if overlap < 0:
            raise ContractError("timeline", "unapproved/generic gaps are not represented by this initial route")
        frames = map_frame(overlap,FILM_CLOCK,intake.profile.fps,rounding="exact")
        cuts.append(CutSpec(id=segment.id,source=segment.source,source_range=segment.source_range,
                            overlap_frames=frames))
        position = segment.timeline_range.end
    expected = build_timeline(intake,EditProposal(branch=timeline.branch,cuts=tuple(cuts)),parent)
    expected = expected.model_copy(update={"revision":timeline.revision})
    if expected != timeline:
        raise ContractError("timeline", "external/native decisions do not match exact approved source/event map")


def build_timeline(intake: PostIntake, proposal: EditProposal | None = None,
                   parent: PostTimeline | None = None) -> PostTimeline:
    """Preserve the full denominator and explicit source identity through approved edits."""
    selected = tuple(s.source for s in intake.sources)
    if proposal is None:
        proposal = EditProposal(cuts=tuple(CutSpec(id=f"S{i}",source=s.source,source_range=s.approved_range)
                                          for i,s in enumerate(intake.sources,1)))
    actual = tuple(c.source for c in proposal.cuts)
    if len(actual) != len(selected) or set(actual) != set(selected):
        raise ContractError("coverage", "one explicit cut per admitted source is required in this initial route")
    if len({c.id for c in proposal.cuts}) != len(proposal.cuts):
        raise ContractError("duplicate", "timeline segment IDs must be stable and unique")
    if actual != selected and Change.REORDER not in intake.authority.allowed_changes:
        raise ContractError("authority", "changed reveal/edit order is not approved")
    if proposal.branch != "main":
        if Change.BRANCH not in intake.authority.allowed_changes or parent is None:
            raise ContractError("authority", "derived branch needs a current parent and explicit branch grant")
    if parent is not None and (parent.project_id != intake.request.project_id
                              or parent.parent_handoff_digest != intake.request.handoff.sha256
                              or parent.scope_revision != intake.snapshot.batch.scope_revision):
        raise ContractError("branch", "parent belongs to a different source/scope/project")
    segments = layout(intake,proposal.cuts)
    maps = event_maps(intake,segments)
    return PostTimeline(
        project_id=intake.request.project_id,branch=proposal.branch,
        parent_handoff_digest=intake.request.handoff.sha256,
        parent_timeline_digest=timeline_digest(parent) if parent is not None else None,
        scope_revision=intake.snapshot.batch.scope_revision,profile_digest=intake.request.profile.sha256,
        authority=intake.request.authority,brief=intake.request.brief,clock=FILM_CLOCK,
        required_coverage=intake.snapshot.approved_coverage,source_registry=intake.sources,
        dependencies=tuple(p for p in intake.request.upstream if p.id in intake.brief.required_assets),
        segments=segments,event_map=maps,original_joins=intake.snapshot.batch.joins,
    )
