"""Exact FilmCraft plan and read projections for the actually inspected schema17."""
from pathlib import Path
from typing import Literal

from pydantic import Field, JsonValue

from postproduction.backends.base import CapabilitySnapshot
from postproduction.common import ClockRate, Digest, Frozen, Nonempty, Positive
from postproduction.edit_models import DeliveryProfile
from postproduction.intake_models import SourceCaps
from postproduction.probe_models import Projection
from postproduction.timeline_models import PostTimeline


class FilmPlan(Frozen):
    workspace: Path
    owner: Nonempty
    capability: CapabilitySnapshot
    timeline: PostTimeline
    sources: tuple[SourceCaps, ...]
    profile: DeliveryProfile


class StageEvidence(Frozen):
    stage: Positive
    pid: Positive
    returncode: int
    timed_out: bool
    stdout_sha256: Digest
    stderr_sha256: Digest
    project_sha256: Digest | None
    output_sha256: Digest | None


class NativeSettings(Projection):
    width: int
    height: int
    frame_rate: ClockRate
    sample_rate: int


class NativeClip(Projection):
    id: int
    item: int
    start: int
    duration: int
    source_in: int
    speed: float
    reverse: bool
    enabled: bool


class NativeTrack(Projection):
    items: tuple[NativeClip, ...]


class NativeSequence(Projection):
    settings: NativeSettings
    video_tracks: tuple[NativeTrack, ...]
    audio_tracks: tuple[NativeTrack, ...]


class NativeFile(Projection):
    path: str


class NativeLocation(Projection):
    file: NativeFile = Field(alias="File")


class NativeVideo(Projection):
    has_alpha: bool = False
    width: int
    height: int
    frame_rate: ClockRate


class NativeInfo(Projection):
    kind: str = "Movie"
    duration: int
    video: NativeVideo | None
    audio_streams: tuple[JsonValue, ...]


class NativeMedia(Projection):
    media: NativeLocation
    info: NativeInfo
    offline: bool


class NativeKind(Projection):
    sequence: NativeSequence | None = Field(default=None,alias="Sequence")
    media: NativeMedia | None = Field(default=None,alias="Media")


class NativeItem(Projection):
    id: int
    kind: NativeKind


class ProjectData(Projection):
    items: dict[str,NativeItem]


class FilmProject(Projection):
    format: Literal["filmcraft.project"]
    schema_version: Literal[17]
    project: ProjectData


class ExportDetails(Projection):
    bytes: int
    frames: int
    path: str


class FilmExport(Projection):
    job: int
    path: str
    offlineMedia: tuple[JsonValue, ...]
    result: ExportDetails
    warnings: tuple[str, ...]
