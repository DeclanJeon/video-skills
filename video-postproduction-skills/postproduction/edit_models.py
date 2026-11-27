"""Per-project edit authority and delivery inputs are not installation grants."""
from enum import StrEnum
from typing import Literal

from postproduction.common import ClockRate, Digest, Frozen, Nonempty, Pin, Positive
from postproduction.loudness_models import LoudnessPolicy


class Change(StrEnum):
    TRIM = "trim"
    REORDER = "reorder"
    OVERLAP = "overlap"
    RETIME = "retime"
    COMPOSITE = "composite"
    AUDIO = "audio"
    CAPTIONS = "captions"
    COLOR = "color"
    BRANCH = "branch"


class DeliveryProfile(Frozen):
    id: Nonempty
    width: Positive
    height: Positive
    fps: ClockRate
    sample_rate: Positive
    channels: Positive
    container: Literal["mp4", "mov", "mkv"]
    video_codec: Nonempty
    audio_codec: Nonempty
    loudness: LoudnessPolicy | None = None


class EditBrief(Frozen):
    project_id: Nonempty
    intent: Nonempty
    required_assets: tuple[Nonempty, ...] = ()
    required_stems: tuple[Nonempty, ...] = ()


class EditAuthority(Frozen):
    id: Nonempty
    project_id: Nonempty
    receiver: Nonempty
    handoff_digest: Digest
    scope_revision: Nonempty
    brief_digest: Digest
    profile_digest: Digest
    allowed_changes: tuple[Change, ...] = ()
    assets: tuple[Pin, ...] = ()
    evidence: Pin
