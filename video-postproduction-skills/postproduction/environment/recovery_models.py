"""Fresh driver inspection, not a caller checkbox clearing an unknown dispatch."""
from pathlib import Path
from typing import Literal, Protocol

from postproduction.common import Frozen, Nonempty
from postproduction.environment.consent_models import InstallationPlan
from postproduction.environment.install_driver import InstallerDriver


class InstallInspection(Frozen):
    process_state: Literal["not_running","running","unknown"]
    files: tuple[Path, ...] = ()
    artifact: Path | None = None
    scope_verified: bool = False
    evidence: Nonempty


class RecoverableDriver(InstallerDriver,Protocol):
    def inspect_installation(self, plan: InstallationPlan) -> InstallInspection: ...
