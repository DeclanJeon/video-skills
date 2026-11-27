"""Exact sample cues and actual SoundCraft source/track/session projections."""
from pathlib import Path
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from postproduction.audio_models import StemAsset
from postproduction.backends.base import CapabilitySnapshot
from postproduction.common import ClockRate, Digest, Frozen, Nonempty, Pin, Positive, Frame
from postproduction.errors import ContractError
from postproduction.intake_models import SourceCaps
from postproduction.probe_models import Projection


class SoundCue(Frozen):
    id: Nonempty
    stem_id: Nonempty
    at_sample: Frame
    gain_db: Annotated[float,Field(ge=-144,le=12)]


class SoundRecipe(Frozen):
    format: Literal["post-sound/1"]
    sample_rate: Positive
    channels: Positive
    sample_count: Positive
    picture: Pin
    picture_fps: ClockRate
    cues: tuple[SoundCue, ...]
    mono_center_db: float = -3.0

    @model_validator(mode="after")
    def nonempty_unique(self) -> Self:
        if not self.cues or len({c.id for c in self.cues}) != len(self.cues):
            raise ContractError("cue", "actual unique sample-offset cues required")
        return self


class SoundPlan(Frozen):
    workspace: Path
    owner: Nonempty
    capability: CapabilitySnapshot
    recipe: SoundRecipe
    recipe_pin: Pin
    stems: tuple[StemAsset, ...]
    sources: tuple[SourceCaps, ...]


class SoundEvidence(Frozen):
    stage: Positive
    pid: Positive
    returncode: int
    timed_out: bool
    stdout_sha256: Digest
    project_sha256: Digest | None = None
    output_sha256: Digest | None = None
    related_assets: tuple[Pin, ...] = ()


class NativeAudioImport(Projection):
    channels: int
    clip: int
    frames: int
    source: int
    track: int


class AudioImports(Projection):
    imported: tuple[NativeAudioImport, ...]


class NativeSource(Projection):
    id: int
    channels: int
    frames: int
    loaded: bool
    path: str


class NativeSoundClip(Projection):
    id: int
    start: int
    end: int
    offset: int
    length: int
    source: int | None = None
    video: int | None = None
    muted: bool
    gain_db: float


class NativeSoundTrack(Projection):
    id: int
    kind: str
    format: str
    record_arm: bool
    mute: bool
    inactive: bool
    volume_db: float
    pan: tuple[float, ...]
    clips: tuple[NativeSoundClip, ...]


class Transport(Projection):
    playing: bool
    recording: bool


class SoundSummary(Projection):
    sample_rate: int
    frame_rate: str
    length_samples: int
    main_format: str
    sources: tuple[NativeSource, ...]
    tracks: tuple[NativeSoundTrack, ...]
    transport: Transport
