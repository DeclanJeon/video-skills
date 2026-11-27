"""Explicit only-new-target rollback with exact current source audit; never recursive delete of unknown/user files."""
from collections.abc import Callable
from dataclasses import dataclass

from postproduction.environment.consent import plan_digest, verify_install_consent
from postproduction.environment.consent_models import InstallAuthority, InstallationPlan
from postproduction.environment.install_journal import write_journal
from postproduction.environment.install_lease import HostToolLease
from postproduction.environment.install_models import InstallEvent, InstallJournal, InstallReceipt
from postproduction.environment.models import EnvStatus, HostSnapshot
from postproduction.environment.provision import Provisioner
from postproduction.environment.recovery import InstallRecovery
from postproduction.environment.recovery_models import RecoverableDriver
from postproduction.errors import ContractError


@dataclass(frozen=True, slots=True)
class InstallRollback:
    driver: RecoverableDriver
    record: Callable[[InstallEvent],None]

    def execute(self, plan: InstallationPlan, host: HostSnapshot, authority: InstallAuthority) -> InstallReceipt:
        """Original exact rollback scope must be approved; only known installed new target can be removed."""
        verdict = verify_install_consent(plan,host,authority)
        installed: bool | None = None
        events: list[InstallEvent] = []
        digest = plan_digest(plan)
        def receipt(status: EnvStatus) -> InstallReceipt:
            return InstallReceipt(host_id=host.host_id,tool=plan.tool,plan_digest=digest,status=status,
                installed=installed,evidence_kind=self.driver.evidence_kind,events=tuple(events))
        if verdict != EnvStatus.APPROVED:
            return receipt(verdict)
        if plan.existing_change != "new" or self.driver.uses_package_manager:
            return receipt(EnvStatus.NEEDS_USER_ACTION)  # Repair/upgrade needs separately known originals, never delete.
        InstallRecovery(self.driver,self.record).fresh_vendor_scope(plan,host,authority)
        Provisioner(self.driver,self.record).scope(plan,existing_reconciled=True)
        with HostToolLease(self.driver.lease_root,host.host_id,plan.tool) as journal:
            if not journal.exists():
                raise ContractError("rollback", "missing owned installation history")
            previous = InstallJournal.model_validate_json(journal.read_bytes())
            if ((previous.host_id,previous.tool,previous.plan_digest) != (host.host_id,plan.tool,digest)
                or previous.installed is not True):
                raise ContractError("rollback", "cannot delete target without exact known own new-install facts")
            installed = previous.installed
            def fact(status: EnvStatus, detail: str) -> None:
                write_journal(journal,InstallJournal(host_id=host.host_id,tool=plan.tool,plan_digest=digest,
                                                    phase=status,installed=installed,detail=detail))
                event = InstallEvent(phase=status,detail=detail,installed=installed)
                events.append(event)
                self.record(event)
            fact(EnvStatus.INSPECTING,"explicit rollback current process/source/entire target audit")
            actual = self.driver.inspect_installation(plan)
            if actual.process_state != "not_running" or not actual.scope_verified or not actual.files:
                fact(EnvStatus.UNKNOWN,"live/unverified/changed/foreign target preserved; explicit operator reconciliation needed")
                return receipt(EnvStatus.UNKNOWN)
            try:
                for path in sorted(self.driver.target.rglob("*"),key=lambda p:len(p.parts),reverse=True):
                    if path.is_symlink() or path.is_file():
                        path.unlink()
                    else:
                        path.rmdir()
                self.driver.target.rmdir()
            except OSError as exc:
                installed = None
                fact(EnvStatus.UNKNOWN,f"owned rollback interrupted: {exc}; preserve remaining paths/cache/journal")
                return receipt(EnvStatus.UNKNOWN)
            installed = False
            fact(EnvStatus.ROLLED_BACK,"only exact source-matching new target removed; cache/source/history retained")
            return receipt(EnvStatus.ROLLED_BACK)
