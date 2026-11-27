"""Independent full RGBA sequence verification: numeric solid motion or exact-font literal text in safe masks."""
from math import ceil, floor
from pathlib import Path
from typing import Literal, assert_never

from postproduction.backends.effect_models import EffectEvidence, EffectPlan, MotionRecipe, PixelBounds, PlateManifest
from postproduction.backends.image_probe import inspect_rgba
from postproduction.backends.text_models import TextRecipe
from postproduction.backends.text_readback import text_readback
from postproduction.errors import ContractError
from postproduction.files import verified_file
from postproduction.templates import load_recipe, verify_style_bounds


def verify_frames(plan: EffectPlan, evidence: EffectEvidence, root: Path) -> PlateManifest:
    """No missing/extra frames or hidden glyph fallback; source color assignment remains explicitly unassigned."""
    recipe = plan.recipe
    expected = tuple(f"plate_{i:05d}.png" for i in range(recipe.frame_count))
    if tuple(p.name for p in sorted(plan.workspace.glob("plate_*.png"))) != expected or len(evidence.frames) != len(expected):
        raise ContractError("frame", "partial/missing/extra sequence frames cannot materialize")
    font_family,source_text = None,None
    alpha_rule: Literal["opaque","coverage"]
    match recipe:
        case MotionRecipe():
            alpha_rule = "opaque"
            style = None
        case TextRecipe():
            alpha_rule = "coverage"
            if evidence.comp_id is None or evidence.layer_id is None:
                raise ContractError("readback", "actual text resources missing")
            actual = text_readback(plan,(evidence.comp_id,evidence.layer_id))
            font_family,source_text = actual.font,actual.text
            style = load_recipe(root/recipe.style.path,root)
        case _:
            assert_never(recipe)
    bounds: list[PixelBounds] = []
    for index,pin in enumerate(evidence.frames):
        facts = inspect_rgba(verified_file(root,pin),recipe.color,alpha_rule)
        if (facts.width,facts.height) != (recipe.width,recipe.height):
            raise ContractError("motion", "independent canvas differs from approved recipe")
        match recipe:
            case MotionRecipe():
                x = recipe.start_position[0]+(recipe.end_position[0]-recipe.start_position[0])*index/recipe.frame_count
                y = recipe.start_position[1]+(recipe.end_position[1]-recipe.start_position[1])*index/recipe.frame_count
                want = (floor(x-recipe.box_width/2),floor(y-recipe.box_height/2),
                        ceil(x+recipe.box_width/2),ceil(y+recipe.box_height/2))
                actual_bounds = (facts.bounds.left,facts.bounds.top,facts.bounds.right,facts.bounds.bottom)
                if actual_bounds != want:
                    raise ContractError("motion", "independent alpha/motion bounds differ from native timing plan")
            case TextRecipe():
                if style is None:
                    raise ContractError("style", "text style unavailable")
                verify_style_bounds(style,facts.bounds)
            case _:
                assert_never(recipe)
        bounds.append(facts.bounds)
    return PlateManifest(width=recipe.width,height=recipe.height,fps=recipe.fps,frame_count=recipe.frame_count,
                         frames=evidence.frames,bounds=tuple(bounds),alpha_mode="straight",
                         font_family=font_family,source_text=source_text)
