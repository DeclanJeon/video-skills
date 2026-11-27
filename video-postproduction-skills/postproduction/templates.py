"""Local conceptual style intake and actual measured safe/masked bounds. No MOGRT/JSX execution or binary copying."""
from pathlib import Path

from pydantic import ValidationError

from postproduction.backends.effect_models import PixelBounds
from postproduction.errors import ContractError
from postproduction.files import confined_path, verified_file
from postproduction.font_probe import verify_font
from postproduction.style_models import StyleRecipe


def load_recipe(path: Path, root: Path) -> StyleRecipe:
    """Validate exact installed font/assets/rights references; absence requests setup/approval, never fallback."""
    absolute = path.absolute()
    try:
        relative = absolute.relative_to(root.absolute()).as_posix()
        file = confined_path(root,relative)
        recipe = StyleRecipe.model_validate_json(file.read_bytes())
    except (OSError,ValueError,ValidationError) as exc:
        raise ContractError("recipe", "invalid actual local conceptual recipe or missing attribution/metric evidence") from exc
    _ = verify_font(recipe.font,root)
    for pin in (*recipe.references,*(m.evidence for m in recipe.metrics)):
        _ = verified_file(root,pin)
    if recipe.asset_license_evidence is not None:
        _ = verified_file(root,recipe.asset_license_evidence)
    return recipe


def verify_style_bounds(recipe: StyleRecipe, bounds: PixelBounds) -> None:
    """Safe masks are declared project evidence, not invented universal platform UI guidelines."""
    safe = recipe.safe_bounds
    if not (safe.left <= bounds.left < bounds.right <= safe.right and safe.top <= bounds.top < bounds.bottom <= safe.bottom):
        raise ContractError("bounds", "actual glyph/graphic bounds overflow supplied safe mask")
    for mask in recipe.protected_bounds:
        if bounds.left < mask.right and mask.left < bounds.right and bounds.top < mask.bottom and mask.top < bounds.bottom:
            raise ContractError("bounds", "actual glyph/graphic bounds occlude supplied protected face/action/UI mask")
