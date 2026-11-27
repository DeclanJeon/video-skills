"""Frozen trust-boundary primitives shared by all postproduction domains."""
from pathlib import PurePosixPath, PureWindowsPath
from typing import Annotated, ClassVar, NewType, Self

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator, model_validator

from postproduction.errors import ContractError

SourceId = NewType("SourceId", str)
type Nonempty = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
type Digest = Annotated[str, StringConstraints(pattern=r"^[a-f0-9]{64}$")]
type Positive = Annotated[int, Field(strict=True, gt=0)]
type Frame = Annotated[int, Field(strict=True, ge=0)]


class Frozen(BaseModel):
    """Parsed immutable records, with no unrecognized fields or nonfinite numbers."""

    model_config: ClassVar[ConfigDict] = ConfigDict(
        frozen=True, extra="forbid", strict=True, allow_inf_nan=False,
        str_strip_whitespace=True, validate_default=True, serialize_by_alias=True,
    )


class Pin(Frozen):
    """Versioned exact bytes at a safe project-relative POSIX path."""

    id: Annotated[SourceId, StringConstraints(min_length=1)]
    version: Nonempty
    path: Nonempty
    sha256: Digest

    @field_validator("path")
    @classmethod
    def relative_path(cls, value: str) -> str:
        if (PurePosixPath(value).is_absolute() or PureWindowsPath(value).drive
            or "\\" in value or "\0" in value or ":" in value
            or ".." in value.split("/") or value == "."):
            raise ContractError("path", "pin must stay within a project-relative path")
        return value


class SourceRange(Frozen):
    """Half-open source frame interval, never an invented exterior handle."""

    start: Frame
    end: Positive

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if self.end <= self.start:
            raise ContractError("range", "source interval must contain frames")
        return self

    @property
    def length(self) -> int:
        return self.end-self.start


class ClockRate(Frozen):
    """Exact positive rational units per second (frames, ticks or samples)."""

    num: Positive
    den: Positive
