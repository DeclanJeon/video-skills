"""Current artifact work graph and native finishing projection; a working master is not final reported QA."""
from pathlib import Path
from typing import Literal

from postproduction.backends.base import CapabilitySnapshot
from postproduction.backends.effect_models import PlateManifest
from postproduction.common import Frame, Frozen, Nonempty, Pin, Positive, SourceRange
from postproduction.edit_models import DeliveryProfile
from postproduction.job_models import ArtifactRef


class FinishingRecipe(Frozen):
    format: Literal["post-finishing/1"]
    id: Nonempty
    branch: Nonempty
    picture: Nonempty
    plates: tuple[Nonempty, ...]
    mix: Nonempty


class PlatePlacement(Frozen):
    artifact: ArtifactRef
    manifest: PlateManifest
    start_frame: Frame


class FinishingInputs(Frozen):
    picture: ArtifactRef
    plates: tuple[PlatePlacement, ...]
    mix: ArtifactRef
    profile: DeliveryProfile
    total_frames: Positive

    @property
    def pins(self) -> tuple[Pin, ...]:
        return (self.picture.pin,*(f for p in self.plates for f in p.manifest.frames),self.mix.pin)


class NativePlacement(Frozen):
    source: Pin
    track: Nonempty
    start_tick: Frame
    duration_ticks: Positive
    source_range: SourceRange
    source_unit: Literal["frames","samples","still"]


class FinishingPlan(Frozen):
    workspace: Path
    owner: Nonempty
    capability: CapabilitySnapshot
    recipe: FinishingRecipe
    recipe_pin: Pin
    inputs: FinishingInputs
