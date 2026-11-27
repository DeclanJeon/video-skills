"""Selected Craft Linux portable adapter; actual vendor execution still requires external exact consent."""
from collections.abc import Callable
from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Literal

from postproduction.environment.catalog import tool_spec
from postproduction.environment.consent_models import InstallationPlan
from postproduction.environment.download import fetch_artifact
from postproduction.environment.install_models import SmokeResult
from postproduction.environment.install_scope import contained_regular_file, installed_files_valid
from postproduction.environment.installers import select_route
from postproduction.environment.models import EnvStatus
from postproduction.environment.portable import PortableSpec, unpack_portable
from postproduction.environment.portable_audit import PortableScope, inspect_portable
from postproduction.environment.recovery_models import InstallInspection
from postproduction.environment.release_evidence import verify_release_evidence
from postproduction.errors import ContractError


@dataclass(frozen=True, slots=True)
class CraftPortableDriver:
    root: Path
    lease_root: Path
    cache: Path
    target: Path
    smoke_runner: Callable[[InstallationPlan,tuple[Path, ...]],SmokeResult]
    @property
    def evidence_kind(self) -> Literal["vendor_installation"]:
        return "vendor_installation"

    @property
    def uses_package_manager(self) -> bool:
        return False

    def inspect_installation(self, plan: InstallationPlan) -> InstallInspection:
        """Readonly real process/archive/entire target audit; no package-manager or implicit retry support."""
        return inspect_portable(PortableScope(self.root,self.cache,self.target),plan)

    def fetch(self, plan: InstallationPlan) -> Path:
        """Use verified exact repository/record, never a guessed latest URL or extra dependency install."""
        route = select_route(plan)
        if route.status != EnvStatus.PLANNED or route.kind != "linux_portable_tar":
            raise ContractError("installer-route",route.reason)
        _ = verify_release_evidence(self.root,plan)
        if plan.dependencies:
            raise ContractError("dependency", "separate exact dependency verification/provision plan required")
        return fetch_artifact(plan,self.cache)

    def install(self, plan: InstallationPlan, artifact: Path) -> tuple[Path, ...]:
        """Recheck both mutable evidence and cached bytes before an owned no-clobber extraction."""
        _ = verify_release_evidence(self.root,plan)
        if not contained_regular_file(artifact,self.cache):
            raise ContractError("install-scope", "installer source is not actual owned cache bytes")
        with artifact.open("rb") as stream:
            actual = hashlib.file_digest(stream,"sha256").hexdigest()
        if actual != plan.source_sha256:
            raise ContractError("hash", "cached package changed after verification")
        names = tool_spec(plan.tool).cli_names
        if len(names) != 1:
            raise ContractError("installer-route", "actual required Craft CLI is not established")
        spec = PortableSpec(cli_name=names[0],max_unpacked_bytes=plan.max_unpacked_bytes)
        return unpack_portable(artifact,self.target,spec)

    def configure(self, plan: InstallationPlan, files: tuple[Path, ...]) -> None:
        """Portable route does not mutate user PATH/preferences/shared libraries or download plugins."""
        _ = plan
        if not installed_files_valid(files,self.target):
            raise ContractError("configure", "installed executable is missing or outside owned target")

    def smoke(self, plan: InstallationPlan, files: tuple[Path, ...]) -> SmokeResult:
        """Delegate to actual per-tool native fixture; callback success is scoped, not artistic certification."""
        if not installed_files_valid(files,self.target):
            raise ContractError("smoke", "native executable changed/disappeared before isolated fixture")
        return self.smoke_runner(plan,files)
