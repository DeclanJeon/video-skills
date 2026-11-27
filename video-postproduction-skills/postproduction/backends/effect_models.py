"""EffectCraft native recipe, actual property readback, and measured sequence manifest."""
from pathlib import Path
from typing import Annotated, Literal, Self

from pydantic import Field, JsonValue, RootModel, StringConstraints, model_validator

from postproduction.backends.base import CapabilitySnapshot
from postproduction.backends.text_models import TextRecipe, TextSettings
from postproduction.common import ClockRate, Digest, Frame, Frozen, Nonempty, Pin, Positive
from postproduction.errors import ContractError
from postproduction.intake_models import SourceCaps
from postproduction.probe_models import Projection


class MotionRecipe(Frozen):
    format: Literal["post-motion/1"]
    width: Positive
    height: Positive
    fps: ClockRate
    frame_count: Positive
    start_frame: Frame = 0
    box_width: Positive
    box_height: Positive
    color: Annotated[str,StringConstraints(pattern=r"^#[0-9a-fA-F]{6}$")]
    start_position: tuple[float,float]
    end_position: tuple[float,float]
    references: tuple[Pin, ...] = ()

    @model_validator(mode="after")
    def visible_box(self) -> Self:
        for x,y in (self.start_position,self.end_position):
            if (x-self.box_width/2 < 0 or x+self.box_width/2 > self.width
                or y-self.box_height/2 < 0 or y+self.box_height/2 > self.height):
                raise ContractError("recipe", "the approved linear graphic must stay inside its declared canvas")
        return self


class CompositionRecipe(RootModel[MotionRecipe | TextRecipe]):
    """Both actual native recipes parse through their literal versioned formats."""


class EffectPlan(Frozen):
    workspace: Path
    owner: Nonempty
    capability: CapabilitySnapshot
    recipe: MotionRecipe | TextRecipe
    text_settings: TextSettings | None = None
    recipe_pin: Pin
    sources: tuple[SourceCaps, ...]


class EffectEvidence(Frozen):
    stage: Positive
    pid: Positive
    returncode: int
    timed_out: bool
    stdout_sha256: Digest
    project_sha256: Digest | None = None
    frames: tuple[Pin, ...] = ()
    comp_id: Positive | None = None
    layer_id: Positive | None = None


class PixelBounds(Frozen):
    left: Frame
    top: Frame
    right: Positive
    bottom: Positive


class PlateManifest(Frozen):
    format: Literal["post-rgba-sequence/1"] = "post-rgba-sequence/1"
    width: Positive
    height: Positive
    fps: ClockRate
    frame_count: Positive
    frames: tuple[Pin, ...]
    bounds: tuple[PixelBounds, ...]
    alpha_mode: Literal["straight"]
    color_assignment: Literal["unassigned"] = "unassigned"
    font_family: Nonempty | None = None
    source_text: Nonempty | None = None


class EffectStep(Projection):
    command: str
    result: JsonValue


class EffectRun(Projection):
    result: tuple[EffectStep, ...]


class LayerInfo(Projection):
    id: int


class CompInfo(Projection):
    id: int
    name: str
    width: int
    height: int
    frameRate: float
    duration: float
    layers: tuple[LayerInfo, ...]


class KeyValue(Projection):
    time: float
    value: tuple[float,float,float]


class PositionInfo(Projection):
    layer: int
    animated: bool
    keys: tuple[KeyValue, ...]
    value: tuple[float,float,float]


class EffectHeader(Projection):
    schema_version: Literal[2] = Field(alias="schema")
    savedBy: str
