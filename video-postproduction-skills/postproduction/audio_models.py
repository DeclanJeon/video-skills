"""Explicit independently supplied audio inventory; a stereo mix is not fabricated component stems."""
from typing import Literal

from postproduction.common import Frozen, Nonempty, Pin, Positive


class StemAsset(Frozen):
    id: Nonempty
    role: Literal["DX","VO","MX","FX","AMBIENCE","MIX"]
    asset: Pin
    sample_rate: Positive
    channels: Positive
    sample_count: Positive
    origin: Literal["provided_separate","derived_from_mixed","mux_mix"]
    independence_evidence: Pin
