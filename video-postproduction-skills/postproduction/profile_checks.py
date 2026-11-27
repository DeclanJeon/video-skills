"""Independent exact final encoding/profile inspection, not native export flags or reported playback."""
from pathlib import Path
import subprocess
from typing import Literal, assert_never

from pydantic import ValidationError

from postproduction.common import Pin
from postproduction.edit_models import DeliveryProfile
from postproduction.errors import ContractError
from postproduction.files import verified_file
from postproduction.media import media_file
from postproduction.probe_models import Projection


class EncodingStream(Projection):
    codec_type: str
    codec_name: str = ""
    sample_rate: int = 0
    channels: int = 0


class ContainerTags(Projection):
    major_brand: str = ""


class Container(Projection):
    format_name: str
    tags: ContainerTags = ContainerTags()


class EncodingDocument(Projection):
    streams: tuple[EncodingStream, ...]
    format: Container


def container_matches(expected: Literal["mp4","mov","mkv"], actual: Container) -> bool:
    names = actual.format_name.split(",")
    match expected:
        case "mp4":
            return "mp4" in names and actual.tags.major_brand.strip() in {"isom","iso2","iso4","iso5","iso6","mp41","mp42","avc1"}
        case "mov":
            return "mov" in names and actual.tags.major_brand.strip()=="qt"
        case "mkv":
            return "matroska" in names
    assert_never(expected)


def require_native_export_profile(profile: DeliveryProfile) -> None:
    if (profile.container,profile.video_codec,profile.audio_codec,profile.channels)!=("mp4","h264","aac",2):
        raise ContractError("format","qualified native export is H264 MP4/stereo AAC; unsupported profiles cannot dispatch")


def verify_encoding(root: Path, artifact: Pin, profile: DeliveryProfile, *, audio_required: bool = True) -> None:
    path = media_file(root,artifact)
    try:
        result = subprocess.run(["ffprobe","-v","error","-protocol_whitelist","file,pipe",
            "-show_streams","-show_format","-of","json",str(path)],
            capture_output=True,check=True,timeout=30)
        actual = EncodingDocument.model_validate_json(result.stdout)
    except (OSError,ValidationError,subprocess.CalledProcessError,subprocess.TimeoutExpired) as exc:
        raise ContractError("encoding","independent final container/codec probe failed") from exc
    videos = tuple(s for s in actual.streams if s.codec_type=="video")
    audios = tuple(s for s in actual.streams if s.codec_type=="audio")
    if not container_matches(profile.container,actual.format) or len(videos)!=1 or videos[0].codec_name!=profile.video_codec:
        raise ContractError("encoding","actual container/video codec differs from explicit profile")
    if audio_required:
        if len(audios)!=1 or (audios[0].codec_name,audios[0].sample_rate,audios[0].channels)!=(
            profile.audio_codec,profile.sample_rate,profile.channels):
            raise ContractError("encoding","actual audio codec/rate/channels differs from explicit profile")
    elif audios:
        raise ContractError("encoding","unexpected output audio outside the approved source picture")
    _ = verified_file(root,artifact)
