"""Consent-first bounded installer coordination; fixture success is never vendor certification."""
from collections.abc import Callable
from dataclasses import dataclass
import hashlib
from pathlib import Path
import subprocess

from postproduction.environment.consent import plan_digest, verify_install_consent
from postproduction.environment.consent_models import InstallAuthority, InstallationPlan
from postproduction.environment.install_driver import InstallerDriver
from postproduction.environment.install_journal import reconcile_required, write_journal
from postproduction.environment.install_lease import HostToolLease
from postproduction.environment.install_models import InstallEvent, InstallJournal, InstallReceipt, SmokeResult
from postproduction.environment.install_scope import contained_regular_file, installed_files_valid
from postproduction.environment.models import EnvStatus, HostSnapshot
from postproduction.environment.policy import decide_tool
from postproduction.environment.probe import inspect_host
from postproduction.errors import ContractError


class InstallUncertain(Exception):
    """Installer dispatch may have had effects; do not retry without fresh reconciliation."""


@dataclass(frozen=True, slots=True)
class Provisioner:
    driver: InstallerDriver
    record: Callable[[InstallEvent],None]

    def scope(self, plan: InstallationPlan, *, existing_reconciled: bool = False) -> None:
        """Only declared, nonsymlink cache/target/lease paths may be used."""
        allowed = {Path(p).absolute() for p in plan.write_paths}
        for path in (self.driver.target,self.driver.cache,self.driver.lease_root):
            if path.absolute() not in allowed:
                raise ContractError("install-scope", "driver path is outside exact approved write set")
            for parent in (path,*path.parents):
                if parent.is_symlink():
                    raise ContractError("install-scope", "symlink installation path refused")
        if not existing_reconciled and (self.driver.target.exists() or self.driver.cache.exists()):
            raise ContractError("existing", "existing target/cache needs reconciliation; never overwrite blindly")

    def execute(self, plan: InstallationPlan, host: HostSnapshot, authority: InstallAuthority) -> InstallReceipt:
        """No lease/fetch/install effects occur before exact actual question-response scope checks."""
        verdict = verify_install_consent(plan,host,authority)
        digest = plan_digest(plan)
        events: list[InstallEvent] = []
        installed: bool | None = False
        smoke: SmokeResult | None = None

        def receipt(status: EnvStatus) -> InstallReceipt:
            return InstallReceipt(host_id=host.host_id,tool=plan.tool,plan_digest=digest,
                                  status=status,installed=installed,evidence_kind=self.driver.evidence_kind,
                                  events=tuple(events),smoke=smoke)

        if verdict != EnvStatus.APPROVED:
            return receipt(verdict)
        if self.driver.evidence_kind == "vendor_installation":
            if (host.evidence_kind == "contract_fixture" or plan.source_evidence_kind == "contract_fixture"
                or authority.question is None or authority.question.channel == "contract_fixture"):
                raise ContractError("fixture", "simulated host/question/source cannot authorize a real vendor driver")
            if not host.requirements:
                raise ContractError("host", "actual original inspection requirements are needed for fresh reinspection")
            fresh = inspect_host(host.requirements)
            if fresh.host_id != host.host_id or fresh.evidence_kind != "read_only_host":
                raise ContractError("host", "fresh actual inspection did not identify this host")
            needed = next((r for r in host.requirements if r.tool == plan.tool),None)
            if needed is None:
                raise ContractError("host", "target tool is not in the actual inspected requirement scope")
            if decide_tool(needed,fresh).status == EnvStatus.REUSABLE:
                installed = True
                return receipt(EnvStatus.REUSABLE)
            _ = verify_install_consent(plan,fresh,authority)
            host = fresh
        if plan.license_steps or plan.cost is None or plan.cost > 0:
            return receipt(EnvStatus.NEEDS_USER_ACTION)
        if self.driver.uses_package_manager and host.package_lock_status != "free":
            return receipt(EnvStatus.NEEDS_USER_ACTION)
        self.scope(plan)
        def current_phase() -> EnvStatus:
            return events[-1].phase if events else EnvStatus.APPROVED

        with HostToolLease(self.driver.lease_root,host.host_id,plan.tool) as journal:
            reconcile_required(journal)

            def fact(status: EnvStatus, detail: str) -> None:
                write_journal(journal,InstallJournal(host_id=host.host_id,tool=plan.tool,plan_digest=digest,
                                                    phase=status,installed=installed,detail=detail))
                event = InstallEvent(phase=status,detail=detail,installed=installed)
                events.append(event)
                self.record(event)

            fact(EnvStatus.APPROVED,"exact captured approval matched; owned host/tool lease")
            try:
                fact(EnvStatus.FETCHING,"fetch dispatch")
                artifact = self.driver.fetch(plan)
                if not contained_regular_file(artifact,self.driver.cache):
                    fact(EnvStatus.FAILED,"download receipt is outside approved cache or is not actual regular bytes")
                    return receipt(EnvStatus.FAILED)
                with artifact.open("rb") as stream:
                    actual = hashlib.file_digest(stream,"sha256").hexdigest()
                if actual != plan.source_sha256:
                    fact(EnvStatus.FAILED,"artifact does not match planned exact checksum")
                    return receipt(EnvStatus.FAILED)
                fact(EnvStatus.INSTALLING,"verified bytes; installation dispatch")
                files = self.driver.install(plan,artifact)
                if not installed_files_valid(files,self.driver.target):
                    installed = None
                    fact(EnvStatus.UNKNOWN,"install returned no verified scoped executable; inspect partial effects")
                    return receipt(EnvStatus.UNKNOWN)
                installed = True
                fact(EnvStatus.INSTALLED,"driver returned actual installed paths; readiness unverified")
                fact(EnvStatus.CONFIGURING,"bounded configuration dispatch")
                self.driver.configure(plan,files)
                if not installed_files_valid(files,self.driver.target):
                    fact(EnvStatus.UNKNOWN,"configuration left missing/unscoped executable; reconcile first")
                    return receipt(EnvStatus.UNKNOWN)
                fact(EnvStatus.VERIFYING,"isolated smoke dispatch")
                smoke = self.driver.smoke(plan,files)
                if not smoke.passed or not smoke.network_denied:
                    fact(EnvStatus.FAILED,"installed but independent smoke/security readiness did not pass")
                    return receipt(EnvStatus.FAILED)
                fact(EnvStatus.READY,"driver-scoped smoke passed; no real-media or vendor-perceptual certification")
                return receipt(EnvStatus.READY)
            except (InstallUncertain,subprocess.TimeoutExpired) as exc:
                phase = current_phase()
                installed = None if phase == EnvStatus.INSTALLING else installed
                fact(EnvStatus.UNKNOWN,f"uncertain dispatch: {exc}; reconcile before retry")
                return receipt(EnvStatus.UNKNOWN)
            except (OSError,subprocess.CalledProcessError) as exc:
                phase = current_phase()
                if phase in {EnvStatus.INSTALLING,EnvStatus.CONFIGURING,EnvStatus.VERIFYING}:
                    installed = None if phase == EnvStatus.INSTALLING else installed
                    fact(EnvStatus.UNKNOWN,f"partial operation requires reconciliation: {exc}")
                    return receipt(EnvStatus.UNKNOWN)
                fact(EnvStatus.FAILED,f"pre-install operation failed: {exc}")
                return receipt(EnvStatus.FAILED)
