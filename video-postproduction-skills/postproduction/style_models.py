"""Concept-only style vocabulary is distinct from licensed asset pixels and native template interchange."""
from pathlib import Path
from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from postproduction.backends.effect_models import PixelBounds
from postproduction.common import ClockRate, Digest, Frame, Frozen, Nonempty, Pin, Positive
from postproduction.errors import ContractError


class ExistingFont(Frozen):
    path: Path
    sha256: Digest
    family: Nonempty
    style: Nonempty
    version: Positive
    face_index: Frame
    license_evidence: Pin

    @model_validator(mode="after")
    def actual_file(self) -> Self:
        if not self.path.is_absolute():
            raise ContractError("font", "existing exact absolute font file required; no install/fallback inference")
        return self


class DisplayMetric(Frozen):
    name: Nonempty
    value: Nonempty
    scope: Literal["actual","synthetic_demo"]
    evidence: Pin
    display_label: Nonempty


class StyleRecipe(Frozen):
    format: Literal["post-style/1"]
    id: Nonempty
    family: Nonempty
    reference_use: Literal["concept_only","licensed_pixels"]
    references: tuple[Pin, ...] = ()
    asset_license_evidence: Pin | None = None
    attribution: tuple[Nonempty, ...] = ()
    attribution_presentation: Literal["receiver_record","on_screen"] = "receiver_record"
    width: Positive
    height: Positive
    fps: ClockRate
    font: ExistingFont
    font_size: Annotated[int,Field(gt=0,le=1000)]
    safe_bounds: PixelBounds
    protected_bounds: tuple[PixelBounds, ...]
    max_lines: Positive
    max_characters_per_second: Annotated[float,Field(gt=0,le=1000)]
    metrics: tuple[DisplayMetric, ...]

    @model_validator(mode="after")
    def scoped_design(self) -> Self:
        if self.safe_bounds.right > self.width or self.safe_bounds.bottom > self.height:
            raise ContractError("bounds", "safe mask extends beyond actual recipe canvas")
        if self.reference_use == "licensed_pixels" and (not self.references or self.asset_license_evidence is None):
            raise ContractError("rights", "actual reference pixels need explicit package-specific permission/evidence")
        return self
