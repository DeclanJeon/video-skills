"""Canonical approved decisions are distinct from native editing artifacts and final QA."""
from typing import Literal

from production.models import JoinPlan, Requirement

from postproduction.common import ClockRate, Digest, Frame, Frozen, Nonempty, Pin, Positive, SourceRange
from postproduction.intake_models import SourceCaps, SourceRef


class CutSpec(Frozen):
    id: Nonempty
    source: SourceRef
    source_range: SourceRange
    overlap_frames: Frame = 0
    speed: ClockRate = ClockRate(num=1,den=1)
    mode: Literal["forward","reverse","freeze"] = "forward"


class EditProposal(Frozen):
    branch: Nonempty = "main"
    cuts: tuple[CutSpec, ...]


class TimelineSegment(Frozen):
    id: Nonempty
    source: SourceRef
    source_range: SourceRange
    timeline_range: SourceRange
    track: Literal["picture"] = "picture"


class EventMap(Frozen):
    requirement_id: Nonempty
    source: SourceRef
    source_anchor: SourceRange
    master_range: SourceRange
    anchor_mode: Literal["reviewed_full_source","observed_anchor"]
    evidence: Pin | None = None
    audio_sample_range: SourceRange | None = None
    audio_rounding: Literal["nearest"] | None = None
    post_verified: Literal[False] = False


class PostTimeline(Frozen):
    format: Literal["post-timeline/1"] = "post-timeline/1"
    project_id: Nonempty
    branch: Nonempty
    revision: Positive = 1
    parent_handoff_digest: Digest
    parent_timeline_digest: Digest | None
    scope_revision: Nonempty
    profile_digest: Digest
    authority: Pin
    brief: Pin
    clock: ClockRate
    required_coverage: tuple[Requirement, ...]
    source_registry: tuple[SourceCaps, ...]
    dependencies: tuple[Pin, ...]
    segments: tuple[TimelineSegment, ...]
    event_map: tuple[EventMap, ...]
    original_joins: tuple[JoinPlan, ...]
    needs_master_review: Literal[True] = True
