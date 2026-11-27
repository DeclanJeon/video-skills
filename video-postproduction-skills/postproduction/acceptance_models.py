"""Traceable executed-case evidence, explicitly distinct from perceptual/vendor installation certification."""
from typing import Literal

from pydantic import field_validator
from postproduction.common import Digest, Frozen, Nonempty, Pin


class SourceFile(Frozen):
    path: Nonempty
    sha256: Digest

    @field_validator("path")
    @classmethod
    def confined(cls,value: str) -> str:
        return Pin.relative_path(value)


class SourceSnapshot(Frozen):
    format: Literal["post-test-scope/1"] = "post-test-scope/1"
    files: tuple[SourceFile, ...]


class Scenario(Frozen):
    id: Nonempty
    purpose: Nonempty
    cases: tuple[Nonempty, ...]
    scopes: tuple[Nonempty, ...]
    unverified: tuple[Nonempty, ...]


class AcceptanceMap(Frozen):
    format: Literal["post-acceptance-map/1"]
    scenarios: tuple[Scenario, ...]


class AcceptanceCheck(Frozen):
    ok: bool
    mapped_scenarios: int
    passed_cases: int
    fully_perceptually_verified: Literal[False] = False
    issues: tuple[str, ...]
    scenarios: tuple[Scenario, ...] = ()
