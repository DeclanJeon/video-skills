"""Independent AAC output waveform/sample/offset verification against actual native WAV mix; not listening QA."""
from array import array
import math
from pathlib import Path
import subprocess
import sys

from pydantic import ValidationError

from postproduction.audio import probe_audio
from postproduction.common import Pin
from postproduction.errors import ContractError
from postproduction.files import verified_file
from postproduction.finishing_models import FinishingPlan
from postproduction.probe_models import Projection


class MixStream(Projection):
    codec_type: str
    channels: int = 0
    sample_rate: int = 0
    duration: float = 0
    start_time: float = 0


class MixStreams(Projection):
    streams: tuple[MixStream, ...]


def verify_mix(plan: FinishingPlan, output: Pin, root: Path) -> None:
    reference = probe_audio(root,plan.inputs.mix.pin)
    profile = plan.inputs.profile
    duration = plan.inputs.total_frames*profile.fps.den/profile.fps.num
    path = verified_file(root,output)
    try:
        metadata = subprocess.run(["ffprobe","-v","error","-show_streams","-of","json",str(path)],
                                  capture_output=True,check=True,timeout=20)
        audios = tuple(s for s in MixStreams.model_validate_json(metadata.stdout).streams if s.codec_type=="audio")
        if len(audios)!=1 or (audios[0].sample_rate,audios[0].channels)!=(reference.sample_rate,reference.channels):
            raise ContractError("audio", "actual final mix channel/rate differs from approved native WAV")
        if abs(audios[0].start_time)>1/reference.sample_rate or abs(audios[0].duration-duration)>2048/reference.sample_rate:
            raise ContractError("audio", "actual final audio start/sample extent differs from picture lock")
        data = subprocess.run(["ffmpeg","-v","error","-xerror","-i",str(path),"-map","0:a:0",
            "-t",str(duration+2048/reference.sample_rate),"-f","f32le","-acodec","pcm_f32le","-"],
            capture_output=True,check=True,timeout=30).stdout
    except (OSError,ValidationError,subprocess.CalledProcessError,subprocess.TimeoutExpired) as exc:
        raise ContractError("audio", "independent final mix full decode failed") from exc
    values: array[float] = array("f")
    values.frombytes(data)
    if sys.byteorder!="little":
        values.byteswap()
    count = reference.sample_count*reference.channels
    if not count<=len(values)<=count+2048*reference.channels or not all(math.isfinite(v) for v in values):
        raise ContractError("audio", "actual final decoded sample count/nonfinite output differs")
    error = math.fsum((values[i]-v)**2 for i,v in enumerate(reference.samples))
    energy = math.fsum(v*v for v in reference.samples)
    if (energy and math.sqrt(error/energy)>0.1) or (not energy and max(abs(v) for v in values)>0.0001):
        raise ContractError("audio", "actual final waveform/gain/sample offset differs from real native mix, not just meters")
