"""Local full decode/probe. This proves technical media properties, not semantics."""
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import ClassVar
import subprocess

from pydantic import BaseModel, ConfigDict

from production.files import verified_file
from production.models import ContractError, Pin


class Stream(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(extra="ignore", frozen=True)
    codec_type: str
    width: int = 0
    height: int = 0
    avg_frame_rate: str = "0/0"
    nb_read_frames: str | None = None


class Frame(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(extra="ignore", frozen=True)
    media_type: str
    best_effort_timestamp_time: str | None = None


class ProbeDocument(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(extra="ignore", frozen=True)
    streams: tuple[Stream, ...]
    frames: tuple[Frame, ...]


@dataclass(frozen=True, slots=True)
class MediaProbe:
    width: int
    height: int
    frame_count: int
    fps: float
    has_audio: bool
    cfr: bool


def probe_media(root: Path, pin: Pin) -> MediaProbe:
    path = verified_file(root, pin)
    try:
        probe = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-show_streams", "-show_frames", "-of", "json", str(path)], capture_output=True, check=True, timeout=60)
        _ = subprocess.run(["ffmpeg", "-v", "error", "-xerror", "-i", str(path), "-f", "null", "-"], capture_output=True, check=True, timeout=60)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as exc:
        raise ContractError("decode", "media probe/full decode failed or tool unavailable") from exc
    doc = ProbeDocument.model_validate_json(probe.stdout)
    videos = [s for s in doc.streams if s.codec_type == "video"]
    if len(videos) != 1:
        raise ContractError("decode", "exactly one video stream required")
    video = videos[0]
    try:
        fps = float(Fraction(video.avg_frame_rate))
        frames = int(video.nb_read_frames or "0")
    except (ValueError, ZeroDivisionError) as exc:
        raise ContractError("decode", "unknown frame count/timebase") from exc
    if fps <= 0 or frames < 1:
        raise ContractError("decode", "empty video/timebase")
    times = [float(f.best_effort_timestamp_time) for f in doc.frames if f.media_type == "video" and f.best_effort_timestamp_time is not None]
    if len(times) != frames:
        raise ContractError("decode", "frame PTS observation incomplete")
    cfr = all(abs((b-a) - 1/fps) <= 0.00002 for a,b in zip(times,times[1:]))
    return MediaProbe(video.width, video.height, frames, fps, any(s.codec_type == "audio" for s in doc.streams), cfr)
