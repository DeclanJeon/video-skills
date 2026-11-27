"""Explicit project-specific final delivery loudness, not a universal platform preset or listening certificate."""
from typing import Annotated, Literal

from pydantic import Field

from postproduction.common import Frozen, Pin


class LoudnessPolicy(Frozen):
    integrated_lufs: Annotated[float,Field(ge=-70,le=0)]
    tolerance_lu: Annotated[float,Field(ge=0,le=10)]
    max_true_peak_dbtp: Annotated[float,Field(ge=-60,le=0)]


class LoudnessMeasurement(Frozen):
    artifact: Pin
    method: Literal["ffmpeg_ebur128_true_peak"] = "ffmpeg_ebur128_true_peak"
    integrated_lufs: Annotated[float,Field(ge=-70,le=20)]
    true_peak_dbtp: Annotated[float,Field(ge=-200,le=50)] | None
