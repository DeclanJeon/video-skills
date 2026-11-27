"""Independent local PNG/full decode and alpha/bounds checks, not a motion executor."""
from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Literal, assert_never

from postproduction.backends.effect_models import PixelBounds
from postproduction.errors import ContractError


@dataclass(frozen=True, slots=True)
class ImageFacts:
    width: int
    height: int
    bounds: PixelBounds
    straight_consistent: bool


def inspect_rgba(path: Path, color: str, alpha_rule: Literal["opaque","coverage"] = "opaque") -> ImageFacts:
    """Verify concrete8-bit RGBA PNG, full decode and color/transparent fringe behavior."""
    with path.open("rb") as stream:
        header = stream.read(33)
    if (len(header) != 33 or header[:8] != b"\x89PNG\r\n\x1a\n"
        or header[12:16] != b"IHDR" or header[24] != 8 or header[25] != 6):
        raise ContractError("alpha", "actual8-bit RGBA PNG required; RGB/JPEG is not an alpha plate")
    width,height = int.from_bytes(header[16:20],"big"),int.from_bytes(header[20:24],"big")
    try:
        result = subprocess.run(
            ["ffmpeg","-v","error","-xerror","-protocol_whitelist","file,pipe","-i",str(path),
             "-frames:v","1","-f","rawvideo","-pix_fmt","rgba","-"],capture_output=True,check=True,timeout=20)
    except (OSError,subprocess.CalledProcessError,subprocess.TimeoutExpired) as exc:
        raise ContractError("alpha", "independent RGBA full decode failed") from exc
    raw = result.stdout
    if len(raw) != width*height*4:
        raise ContractError("alpha", "decoded plate byte count differs from declared dimensions")
    alpha = raw[3::4]
    indices = tuple(i for i,a in enumerate(alpha) if a)
    if not indices or min(alpha) != 0:
        raise ContractError("alpha", "expected visible coverage and transparent background were not observed")
    match alpha_rule:
        case "opaque":
            if max(alpha) != 255:
                raise ContractError("alpha", "promised solid has no actual fully opaque pixel")
        case "coverage":
            pass  # Anti-aliased small glyphs can legitimately peak below255; straight RGB is still checked below.
        case _:
            assert_never(alpha_rule)
    expected = tuple(int(color[i:i+2],16) for i in (1,3,5))
    consistent = all(all(abs(raw[index*4+c]-expected[c]) <= 1 for c in range(3)) for index in indices)
    if not consistent:
        raise ContractError("alpha", "RGB/straight-alpha behavior differs from approved solid color")
    bounds = PixelBounds(left=min(i%width for i in indices),top=min(i//width for i in indices),
                         right=max(i%width for i in indices)+1,bottom=max(i//width for i in indices)+1)
    return ImageFacts(width,height,bounds,consistent)
