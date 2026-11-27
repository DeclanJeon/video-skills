"""Local full decode and exact PTS clocks; never a semantic quality certificate."""
from fractions import Fraction
from pathlib import Path
import subprocess

from pydantic import ValidationError

from postproduction.common import ClockRate, Pin
from postproduction.errors import ContractError
from postproduction.files import verified_file
from postproduction.probe_models import ProbeDocument, VideoFacts


def media_file(root: Path, pin: Pin) -> Path:
    """Admit concrete video containers before any decoder can follow a playlist."""
    path = verified_file(root, pin)
    with path.open("rb") as stream:
        magic = stream.read(16)
    mp4 = magic[4:8] in {b"ftyp", b"moov", b"mdat", b"wide", b"free", b"skip"}
    matroska = magic[:4] == b"\x1a\x45\xdf\xa3"
    avi = magic[:4] == b"RIFF" and magic[8:12] == b"AVI "
    if not (mp4 or matroska or avi):
        raise ContractError("decode", "unsupported concrete video container; playlists refused")
    return path


def probe_video(root: Path, pin: Pin) -> VideoFacts:
    """Count/decode actual frames and preserve rational FPS/timebase and start PTS."""
    path = media_file(root, pin)
    try:
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-protocol_whitelist", "file,pipe", "-count_frames",
             "-show_streams", "-show_frames", "-of", "json", str(path)],
            capture_output=True, check=True, timeout=120,
        )
        _ = subprocess.run(
            ["ffmpeg", "-v", "error", "-xerror", "-protocol_whitelist", "file,pipe",
             "-i", str(path), "-f", "null", "-"], capture_output=True, check=True, timeout=120,
        )
        doc = ProbeDocument.model_validate_json(probe.stdout)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError,
            ValidationError) as exc:
        raise ContractError("decode", "probe/full decode failed or required existing tool unavailable") from exc
    videos = tuple(stream for stream in doc.streams if stream.codec_type == "video")
    if len(videos) != 1:
        raise ContractError("decode", "exactly one video stream required")
    video = videos[0]
    try:
        fps = Fraction(video.avg_frame_rate)
        timebase = Fraction(video.time_base)
        count = int(video.nb_read_frames or "0")
        rate = ClockRate(num=fps.numerator, den=fps.denominator)
        tb = ClockRate(num=timebase.numerator, den=timebase.denominator)
    except (ValueError, ZeroDivisionError) as exc:
        raise ContractError("timebase", "invalid rational clock or frame count") from exc
    frames = tuple(f for f in doc.frames if f.media_type == "video")
    times = tuple(f.best_effort_timestamp for f in frames if f.best_effort_timestamp is not None)
    if count < 1 or len(frames) != count or len(times) != count or video.width < 1 or video.height < 1:
        raise ContractError("decode", "incomplete frame observation or invalid dimensions")
    cfr = all((b-a)*timebase == 1/fps for a,b in zip(times,times[1:]))
    _ = verified_file(root, pin)
    return VideoFacts(video.width, video.height, count, rate, tb, cfr,
                      any(s.codec_type == "audio" for s in doc.streams),video.start_pts,video.tags.timecode)
