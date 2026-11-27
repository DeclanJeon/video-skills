"""Container/stream color tags, explicit source assignment and requested output tag/bit depth are separate."""
from typing import Literal

from postproduction.common import Frozen, Pin, Positive


class ColorFacts(Frozen):
    primaries: str | None
    transfer: str | None
    matrix: str | None
    range: str | None
    pixel_format: str
    bit_depth: Positive | None
    method: Literal["stream_tags_not_gamut_measurement"] = "stream_tags_not_gamut_measurement"


class ColorAssignment(Frozen):
    source: Pin
    space: Literal["Rec709","sRGB"]
    evidence: Pin
    origin: Literal["assigned"]


class ColorState(Frozen):
    detected: ColorFacts
    assignment: ColorAssignment | None = None


class ColorTarget(Frozen):
    primaries: str
    transfer: str
    matrix: str
    range: str
    bit_depth: Positive
