"""Independently decode exact final bytes through existing EBU R128/oversampled true-peak scanner; never auto-normalize."""
from pathlib import Path
from decimal import Decimal
import re
import subprocess

from postproduction.common import Pin
from postproduction.errors import ContractError
from postproduction.files import verified_file
from postproduction.loudness_models import LoudnessMeasurement, LoudnessPolicy
from postproduction.media import media_file


def measure_loudness(root: Path, artifact: Pin) -> LoudnessMeasurement:
    path = verified_file(root,artifact)
    with path.open("rb") as stream:
        magic = stream.read(12)
    if not (magic[:4]==b"fLaC" or magic[:4] in {b"RIFF",b"RF64"} and magic[8:12]==b"WAVE"):
        _ = media_file(root,artifact)
    try:
        measured = subprocess.run(["ffmpeg","-hide_banner","-nostdin","-v","info","-xerror",
            "-protocol_whitelist","file,pipe","-i",str(path),"-map","0:a:0",
            "-af","ebur128=peak=true","-f","null","-"],
            capture_output=True,check=True,timeout=120)
    except (OSError,subprocess.CalledProcessError,subprocess.TimeoutExpired) as exc:
        raise ContractError("loudness","independent EBU R128/true-peak full decode failed") from exc
    summary = measured.stderr.decode(errors="replace").rpartition("Summary:")[2]
    integrated = re.search(r"\bI:\s*(-?\d+(?:\.\d+)?)\s*LUFS",summary)
    peak = re.search(r"\bPeak:\s*(-inf|-?\d+(?:\.\d+)?)\s*dBFS",summary)
    if integrated is None or peak is None:
        raise ContractError("loudness","required integrated loudness/true-peak summary unavailable")
    _ = verified_file(root,artifact)
    return LoudnessMeasurement(artifact=artifact,integrated_lufs=float(integrated.group(1)),
                              true_peak_dbtp=None if peak.group(1)=="-inf" else float(peak.group(1)))


def verify_loudness(actual: LoudnessMeasurement, policy: LoudnessPolicy) -> None:
    deviation = abs(Decimal(str(actual.integrated_lufs))-Decimal(str(policy.integrated_lufs)))
    if deviation>Decimal(str(policy.tolerance_lu)):
        raise ContractError("loudness","actual final integrated LUFS differs from explicit project target/tolerance")
    if actual.true_peak_dbtp is not None and actual.true_peak_dbtp>policy.max_true_peak_dbtp:
        raise ContractError("loudness","actual final oversampled true peak exceeds explicit project ceiling")
