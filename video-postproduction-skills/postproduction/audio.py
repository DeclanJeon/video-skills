"""Independent concrete audio full decode/sample/layout/level measurement, not listening or source authenticity."""
from array import array
from dataclasses import dataclass
import math
from pathlib import Path
import subprocess
import sys

from pydantic import ValidationError

from postproduction.audio_models import StemAsset
from postproduction.common import Pin
from postproduction.errors import ContractError
from postproduction.files import verified_file
from postproduction.probe_models import Projection


class AudioStream(Projection):
    codec_type: str
    sample_rate: int = 0
    channels: int = 0


class AudioDocument(Projection):
    streams: tuple[AudioStream, ...]


@dataclass(frozen=True, slots=True)
class AudioFacts:
    sample_rate: int
    channels: int
    sample_count: int
    sample_peak: float
    rms: float
    samples: tuple[float, ...]


def probe_audio(root: Path, pin: Pin) -> AudioFacts:
    """Read existing local WAV/FLAC only; verify exact bytes before and after full float decode."""
    path = verified_file(root,pin)
    with path.open("rb") as stream:
        magic = stream.read(12)
    if not ((magic[:4] in {b"RIFF",b"RF64"} and magic[8:12] == b"WAVE") or magic[:4] == b"fLaC"):
        raise ContractError("audio", "concrete WAV/FLAC source required; no playlist or invented mux stems")
    try:
        probe = subprocess.run(["ffprobe","-v","error","-protocol_whitelist","file,pipe","-show_streams",
                                "-of","json",str(path)],capture_output=True,check=True,timeout=60)
        decoded = subprocess.run(["ffmpeg","-v","error","-xerror","-protocol_whitelist","file,pipe",
                                  "-i",str(path),"-f","f32le","-acodec","pcm_f32le","-"],
                                 capture_output=True,check=True,timeout=60)
        metadata = AudioDocument.model_validate_json(probe.stdout)
    except (OSError,ValidationError,subprocess.CalledProcessError,subprocess.TimeoutExpired) as exc:
        raise ContractError("audio", "audio probe/full decode failed") from exc
    if len(metadata.streams) != 1 or metadata.streams[0].codec_type != "audio":
        raise ContractError("audio", "exactly one actual audio stream required")
    stream = metadata.streams[0]
    if stream.channels < 1 or stream.sample_rate < 1 or len(decoded.stdout)%4:
        raise ContractError("audio", "invalid decoded audio layout/rate")
    values: array[float] = array("f")
    values.frombytes(decoded.stdout)
    if sys.byteorder != "little":
        values.byteswap()
    samples = tuple(values)
    if not samples or len(samples)%stream.channels or not all(math.isfinite(v) for v in samples):
        raise ContractError("audio", "empty/nonfinite/incomplete decoded audio")
    _ = verified_file(root,pin)
    return AudioFacts(stream.sample_rate,stream.channels,len(samples)//stream.channels,
                      max(abs(v) for v in samples),math.sqrt(math.fsum(v*v for v in samples)/len(samples)),samples)


def verify_stem(root: Path, stem: StemAsset) -> AudioFacts:
    """Validate physical provenance/declared layout; supplied declarations are not legal issuer certification."""
    if stem.origin != "provided_separate" and stem.role != "MIX":
        raise ContractError("stem", "derived stereo/mux mix cannot become fabricated DX/MX/FX component stems")
    _ = verified_file(root,stem.independence_evidence)
    actual = probe_audio(root,stem.asset)
    if (actual.sample_rate,actual.channels,actual.sample_count) != (
        stem.sample_rate,stem.channels,stem.sample_count):
        raise ContractError("stem", "declared stem inventory differs from actual decoded samples/channels/rate")
    return actual
