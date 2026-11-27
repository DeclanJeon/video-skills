"""Local role package manifest, not a global skill installation or automatic invocation grant."""
from typing import Literal

from postproduction.common import Frozen, Nonempty

ROLE_IDS = ("postproduction-supervisor","picture-editor","motion-compositor","color-finisher",
            "sound-editor-mixer","caption-editor","finishing-operator","postproduction-qa")


class RoleEntry(Frozen):
    id: Nonempty
    path: Nonempty


class PackageManifest(Frozen):
    format: Literal["video-postproduction-package/1"]
    name: Literal["video-postproduction-skills"]
    version: Nonempty
    entry: Literal["SKILL.md"]
    automatic_invocation: Literal[False]
    installed_globally: Literal[False]
    roles: tuple[RoleEntry, ...]
    schemas: tuple[Nonempty, ...]
    examples: tuple[Nonempty, ...]
    validation_scope: tuple[Nonempty, ...]
    unverified: tuple[Nonempty, ...]


class PackageCheck(Frozen):
    ok: bool
    roles: int
    issues: tuple[str, ...]
