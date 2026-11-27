"""Host observations are separate from permission, installation and functional readiness."""
from enum import StrEnum
from typing import Literal, Self

from pydantic import AwareDatetime, model_validator

from postproduction.common import Digest, Frame, Frozen, Nonempty
from postproduction.errors import ContractError


class Tool(StrEnum):
    FILMCRAFT = "filmcraft"
    EFFECTCRAFT = "effectcraft"
    SOUNDCRAFT = "soundcraft"
    AUTOCLIP = "autoclip"
    RESOLVE = "resolve"
    PREMIERE = "premiere"
    AFTER_EFFECTS = "after_effects"
    FFMPEG = "ffmpeg"
    FFPROBE = "ffprobe"


class System(StrEnum):
    LINUX = "Linux"
    WINDOWS = "Windows"
    MACOS = "Darwin"


class Discovery(StrEnum):
    PATH = "path"
    PACKAGE = "package_db"
    DESKTOP = "desktop"
    LOCATIONS = "known_locations"
    CLI = "required_cli"


class EnvStatus(StrEnum):
    INSPECTING = "inspecting"
    REUSABLE = "reusable"
    MISSING = "missing"
    UNKNOWN = "unknown"
    INCOMPATIBLE = "incompatible"
    PLANNED = "planned"
    AWAITING_CONSENT = "awaiting_consent"
    APPROVED = "approved"
    FETCHING = "fetching"
    INSTALLING = "installing"
    INSTALLED = "installed"
    CONFIGURING = "configuring"
    VERIFYING = "verifying"
    READY = "ready"
    DECLINED = "declined"
    NEEDS_USER_ACTION = "needs_user_action"
    UNSUPPORTED = "unsupported"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    NOT_REQUIRED = "not_required"


class ToolRequirement(Frozen):
    tool: Tool
    feature: Nonempty
    versions: tuple[Nonempty, ...] = ()
    needs_cli: bool = True
    required: bool = True
    omission_reason: Nonempty | None = None
    systems: tuple[System, ...] = (System.LINUX,System.WINDOWS,System.MACOS)
    architectures: tuple[Nonempty, ...] = ("x86_64","aarch64","AMD64","arm64")
    min_disk_bytes: Frame = 0
    min_memory_bytes: Frame = 0
    requires_verified_gpu: bool = False

    @model_validator(mode="after")
    def omitted_reason(self) -> Self:
        if not self.required and self.omission_reason is None:
            raise ContractError("environment", "unselected optional tool needs an explicit omission reason")
        return self


class InstalledPackage(Frozen):
    name: Nonempty
    version: Nonempty


class ToolObservation(Frozen):
    tool: Tool
    cli_path: Nonempty | None = None
    cli_sha256: Digest | None = None
    version: Nonempty | None = None
    package_name: Nonempty | None = None
    desktop_entries: tuple[Nonempty, ...] = ()
    known_app_locations: tuple[Nonempty, ...] = ()
    checked: tuple[Discovery, ...] = ()
    errors: tuple[Nonempty, ...] = ()


class HostSnapshot(Frozen):
    host_id: Digest
    system: System
    architecture: Nonempty
    programs: tuple[ToolObservation, ...]
    packages: tuple[InstalledPackage, ...]
    disk_available_bytes: Frame | None
    memory_available_bytes: Frame | None
    gpu_status: Literal["unknown","identified","verified"]
    gpu_info: tuple[Nonempty, ...]
    evidence_kind: Literal["read_only_host","contract_fixture"]
    inspected_at: AwareDatetime
    active_tools: tuple[Tool, ...] = ()
    package_lock_status: Literal["free","busy","unknown"] = "unknown"
    requirements: tuple[ToolRequirement, ...] = ()


class ToolDecision(Frozen):
    tool: Tool
    status: EnvStatus
    installation: ToolObservation | None
    reason: Nonempty
    ready: Literal[False] = False


class EnvironmentDecision(Frozen):
    host_id: Digest
    status: EnvStatus
    tools: tuple[ToolDecision, ...]
    ready: Literal[False] = False
