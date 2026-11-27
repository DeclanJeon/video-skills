"""Native literal caption layer recipe and exact renderer text settings, distinct from Adobe template binaries."""
from typing import Annotated, Literal

from pydantic import StringConstraints

from postproduction.caption_models import CaptionCue
from postproduction.common import ClockRate, Frame, Frozen, Nonempty, Pin, Positive


class TextRecipe(Frozen):
    format: Literal["post-text/1"]
    width: Positive
    height: Positive
    fps: ClockRate
    frame_count: Positive
    start_frame: Frame = 0
    style: Pin
    caption: CaptionCue
    color: Annotated[str,StringConstraints(pattern=r"^#[0-9a-fA-F]{6}$")] = "#ffffff"
    start_position: tuple[float,float]
    end_position: tuple[float,float]

    @property
    def references(self) -> tuple[Pin, ...]:
        return (self.style,self.caption.source_approval)


class TextSettings(Frozen):
    family: Nonempty
    style: Nonempty
    size: float
    color: Nonempty
