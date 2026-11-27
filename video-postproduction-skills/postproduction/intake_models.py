"""Typed immutable production→post boundary, retaining original production identities."""
from pydantic import Field
from production.models import Handoff, State

from postproduction.audio_models import StemAsset
from postproduction.common import ClockRate, Digest, Frame, Frozen, Nonempty, Pin, Positive, SourceRange
from postproduction.edit_models import DeliveryProfile, EditAuthority, EditBrief


class SourceRef(Frozen):
    clip_id: Nonempty
    take_id: Nonempty


class SourceCaps(Frozen):
    source: SourceRef
    asset: Pin
    approved_range: SourceRange
    frame_count: Positive
    rate: ClockRate
    timebase: ClockRate
    width: Positive
    height: Positive
    has_audio: bool
    start_pts: int
    timecode: str | None
    acceptance_revision: Positive
    range_revision: Positive
    approval: Pin
    exterior_before: Frame = 0
    exterior_after: Frame = 0


class EventAnchor(Frozen):
    requirement_id: Nonempty
    source: SourceRef
    source_range: SourceRange
    asset_hash: Digest
    range_revision: Positive
    acceptance_revision: Positive
    observer: Nonempty
    evidence: Pin
    video_observed: bool
    audio_observed: bool = False


class IntakeRequest(Frozen):
    project_id: Nonempty
    snapshot: Pin
    handoff: Pin
    schema_pin: Pin = Field(alias="schema")
    brief: Pin
    authority: Pin
    profile: Pin
    upstream: tuple[Pin, ...] = ()
    anchors: tuple[EventAnchor, ...] = ()
    stems: tuple[StemAsset, ...] = ()


class PostIntake(Frozen):
    request: IntakeRequest
    snapshot: State
    handoff: Handoff
    brief: EditBrief
    authority: EditAuthority
    profile: DeliveryProfile
    sources: tuple[SourceCaps, ...]
