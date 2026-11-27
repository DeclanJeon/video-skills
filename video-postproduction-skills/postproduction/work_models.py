"""Scoped work declarations and immutable opaque native bytes; each backend owns its packet parser."""
from enum import StrEnum
from typing import Self

from pydantic import field_validator, model_validator

from postproduction.common import Digest, Frozen, Nonempty, Pin, Positive
from postproduction.environment.models import Tool
from postproduction.errors import ContractError
from postproduction.intake_models import SourceRef


class Domain(StrEnum):
    PICTURE = "picture"
    MOTION = "motion"
    COLOR = "color"
    SOUND = "sound"
    CAPTIONS = "captions"
    FINISHING = "finishing"
    QA = "qa"
    DELIVERY = "delivery"
    ENVIRONMENT = "environment"


class WorkOrder(Frozen):
    id: Nonempty
    domain: Domain
    branch: Nonempty
    backend: Tool
    source_refs: tuple[SourceRef, ...]
    dependencies: tuple[Pin, ...] = ()
    recipe: Pin | None = None
    output: Nonempty
    max_attempts: Positive = 1

    @field_validator("output")
    @classmethod
    def confined_output(cls, value: str) -> str:
        return Pin.relative_path(value)

    @model_validator(mode="after")
    def scope(self) -> Self:
        if not self.source_refs and self.domain != Domain.ENVIRONMENT:
            raise ContractError("work", "non-environment work needs explicit consumed source identities")
        if len(set(self.source_refs)) != len(self.source_refs):
            raise ContractError("work", "duplicate consumed source identity")
        expected = {Domain.PICTURE:Tool.FILMCRAFT,Domain.MOTION:Tool.EFFECTCRAFT,Domain.SOUND:Tool.SOUNDCRAFT}
        if self.domain in expected and self.backend != expected[self.domain]:
            raise ContractError("backend", "work cannot substitute a different editor for native execution")
        return self


class RequestPacket(Frozen):
    order: WorkOrder
    input_fingerprint: Digest
    payload: Nonempty  # Exact backend-native serialization, not a guessed common Craft command schema.
