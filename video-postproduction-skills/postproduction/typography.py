"""Existing-font independent glyph/advance measurements; actual native raster bounds still need inspection."""
from pathlib import Path
import subprocess
import sys

from pydantic import ValidationError

from postproduction.common import Frozen, Nonempty
from postproduction.errors import ContractError
from postproduction.font_probe import verify_font
from postproduction.probe_models import Projection
from postproduction.style_models import StyleRecipe


class Advance(Projection):
    width: float
    height: float


class TextMeasurement(Frozen):
    font_family: Nonempty
    width: float
    height: float


MEASURE = """import sys,json
from PIL import ImageFont
font=ImageFont.truetype(sys.argv[1],int(float(sys.argv[3])),index=int(sys.argv[2]))
lines=sys.argv[4].splitlines() or ['']
boxes=[font.getbbox(line) for line in lines]
print(json.dumps({'width':max(float(font.getlength(line)) for line in lines),
 'height':sum(b[3]-b[1] for b in boxes)+max(0,len(lines)-1)*int(float(sys.argv[3]))*.2}))
"""


def measure_text(recipe: StyleRecipe, text: str, root: Path) -> TextMeasurement:
    """Charset proof plus real FreeType metrics from existing Pillow; no unknown glyph→tofu acceptance."""
    if not text or len(text)>4096 or len(text.splitlines())>recipe.max_lines or any(ord(c)<32 and c!="\n" for c in text):
        raise ContractError("text", "text/line/control range exceeds declared supported layout policy")
    facts = verify_font(recipe.font,root)
    if any(c!="\n" and not any(a<=ord(c)<=b for a,b in facts.charset) for c in text):
        raise ContractError("glyph", "actual requested font lacks required Unicode glyph; do not silently substitute")
    try:
        result = subprocess.run([sys.executable,"-c",MEASURE,str(recipe.font.path),str(recipe.font.face_index),
                                 str(recipe.font_size),text],capture_output=True,check=True,timeout=10)
        value = Advance.model_validate_json(result.stdout)
    except (OSError,ValidationError,subprocess.CalledProcessError,subprocess.TimeoutExpired) as exc:
        raise ContractError("font", "existing actual independent font metrics unavailable; no installation inferred") from exc
    if value.width <= 0 or value.height <= 0:
        raise ContractError("glyph", "actual glyph measurement empty")
    return TextMeasurement(font_family=facts.family,width=value.width,height=value.height)
