"""Read projections of tool metadata; irrelevant vendor fields are explicitly ignored."""
from dataclasses import dataclass
from typing import ClassVar

from pydantic import BaseModel, ConfigDict

from postproduction.common import ClockRate


class Projection(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore", allow_inf_nan=False)


class Tags(Projection):
    timecode: str | None = None


class Stream(Projection):
    codec_type: str
    width: int = 0
    height: int = 0
    avg_frame_rate: str = "0/0"
    time_base: str = "0/0"
    nb_read_frames: str | None = None
    start_pts: int = 0
    tags: Tags = Tags()


class Frame(Projection):
    media_type: str
    best_effort_timestamp: int | None = None


class ProbeDocument(Projection):
    streams: tuple[Stream, ...]
    frames: tuple[Frame, ...]


@dataclass(frozen=True, slots=True)
class VideoFacts:
    width: int
    height: int
    frame_count: int
    rate: ClockRate
    timebase: ClockRate
    cfr: bool
    has_audio: bool
    start_pts: int
    timecode: str | None
