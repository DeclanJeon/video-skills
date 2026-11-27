"""Actual stream tag inspection never certifies pixel gamut, shader transforms, faces or perceptual matching."""
from pathlib import Path
import subprocess

from pydantic import ValidationError

from postproduction.color_models import ColorAssignment, ColorFacts, ColorState, ColorTarget
from postproduction.common import Pin
from postproduction.errors import ContractError
from postproduction.files import verified_file
from postproduction.probe_models import Projection


class ColorStream(Projection):
    codec_type: str
    pix_fmt: str = ""
    bits_per_raw_sample: int = 0
    color_primaries: str | None = None
    color_transfer: str | None = None
    color_space: str | None = None
    color_range: str | None = None


class ColorDocument(Projection):
    streams: tuple[ColorStream, ...]


def known(value: str | None) -> str | None:
    return None if value in {None,"","unknown","unspecified","reserved"} else value


def probe_color(root: Path, pin: Pin) -> ColorFacts:
    path = verified_file(root,pin)
    try:
        process = subprocess.run(["ffprobe","-v","error","-protocol_whitelist","file,pipe",
            "-show_streams","-of","json",str(path)],capture_output=True,check=True,timeout=30)
        doc = ColorDocument.model_validate_json(process.stdout)
    except (OSError,ValidationError,subprocess.CalledProcessError,subprocess.TimeoutExpired) as exc:
        raise ContractError("color", "actual color stream metadata unavailable") from exc
    video = tuple(s for s in doc.streams if s.codec_type=="video")
    if len(video) != 1:
        raise ContractError("color", "one actual video stream required")
    v = video[0]
    formats = {"yuv420p":8,"yuv422p":8,"yuv444p":8,"rgb24":8,"rgba":8,"bgra":8,"gbrp":8,
               "yuv420p10le":10,"yuv422p10le":10,"yuv444p10le":10,"yuva444p10le":10,"rgba64le":16}
    depth = v.bits_per_raw_sample or formats.get(v.pix_fmt)
    _ = verified_file(root,pin)
    return ColorFacts(primaries=known(v.color_primaries),transfer=known(v.color_transfer),matrix=known(v.color_space),
                      range=known(v.color_range),pixel_format=v.pix_fmt,bit_depth=depth)


def resolve_color(root: Path, source: Pin, assignment: ColorAssignment | None) -> ColorState:
    """An explicit source assignment retains original unknowns; it does not pretend an output transform happened."""
    facts = probe_color(root,source)
    if assignment is not None:
        if assignment.source != source:
            raise ContractError("color", "source assignment belongs to another exact physical source")
        _ = verified_file(root,assignment.evidence)
        expected_transfer = "bt709" if assignment.space=="Rec709" else "iec61966-2-1"
        if (facts.primaries not in {None,"bt709"} or facts.transfer not in {None,expected_transfer}):
            raise ContractError("color", "assignment conflicts with actual existing tags; explicit reviewed override route required")
    return ColorState(detected=facts,assignment=assignment)


def verify_color_output(root: Path, pin: Pin, target: ColorTarget) -> ColorFacts:
    facts = probe_color(root,pin)
    if (facts.primaries,facts.transfer,facts.matrix,facts.range,facts.bit_depth) != (
        target.primaries,target.transfer,target.matrix,target.range,target.bit_depth):
        raise ContractError("color", "actual output color tags/bit depth unknown or differ from requested target")
    return facts
