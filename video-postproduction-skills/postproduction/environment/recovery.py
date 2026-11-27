"""Explicit consent-bound recovery inspects live effects under the same lease before reusing bytes or smoke."""
from collections.abc import Callable
from dataclasses import dataclass
import hashlib
import subprocess

from postproduction.environment.consent import plan_digest, verify_install_consent
from postproduction.environment.consent_models import InstallAuthority, InstallationPlan
from postproduction.environment.install_journal import write_journal
from postproduction.environment.install_lease import HostToolLease
from postproduction.environment.install_models import InstallEvent, InstallJournal, InstallReceipt, SmokeResult
from postproduction.environment.install_scope import contained_regular_file, installed_files_valid
from postproduction.environment.models import EnvStatus, HostSnapshot
from postproduction.environment.probe import inspect_host
from postproduction.environment.provision import InstallUncertain, Provisioner
from postproduction.environment.recovery_models import RecoverableDriver
from postproduction.errors import ContractError


@dataclass(frozen=True, slots=True)
class InstallRecovery:
    driver: RecoverableDriver
    record: Callable[[InstallEvent],None]

    def fresh_vendor_scope(self, plan: InstallationPlan, host: HostSnapshot, authority: InstallAuthority) -> None:
        """Recovery cannot turn fixture approval into real installation or quietly expand a changed host."""
        if self.driver.evidence_kind == "contract_fixture":
            return
        if (host.evidence_kind != "read_only_host" or not host.requirements
            or plan.source_evidence_kind == "contract_fixture" or authority.question is None
            or authority.question.channel == "contract_fixture"):
            raise ContractError("fixture", "real recovery requires actual host/question/source scope")
        fresh = inspect_host(host.requirements)
        if fresh.host_id != host.host_id or fresh.evidence_kind != "read_only_host":
            raise ContractError("host", "fresh recovery inspection did not identify this host")
        if not self.driver.target.exists():
            _ = verify_install_consent(plan,fresh,authority)  # Any new write still requires unchanged exact scope.

    def resume(self, plan: InstallationPlan, host: HostSnapshot, authority: InstallAuthority) -> InstallReceipt:
        """No refetch; absent target may install verified cache only after a fresh no-process/scope inspection."""
        verdict = verify_install_consent(plan,host,authority)
        events: list[InstallEvent] = []
        installed: bool | None = None
        smoke: SmokeResult | None = None
        digest = plan_digest(plan)

        def receipt(status: EnvStatus) -> InstallReceipt:
            return InstallReceipt(host_id=host.host_id,tool=plan.tool,plan_digest=digest,status=status,
                                  installed=installed,evidence_kind=self.driver.evidence_kind,
                                  events=tuple(events),smoke=smoke)
        if verdict != EnvStatus.APPROVED:
            return receipt(verdict)
        self.fresh_vendor_scope(plan,host,authority)
        if self.driver.uses_package_manager or plan.license_steps or plan.cost is None or plan.cost > 0:
            return receipt(EnvStatus.NEEDS_USER_ACTION)
        Provisioner(self.driver,self.record).scope(plan,existing_reconciled=True)
        with HostToolLease(self.driver.lease_root,host.host_id,plan.tool) as journal:
            if not journal.exists():
                raise ContractError("reconcile", "no owned historical installation attempt exists")
            previous = InstallJournal.model_validate_json(journal.read_bytes())
            if (previous.host_id,previous.tool,previous.plan_digest) != (host.host_id,plan.tool,digest):
                raise ContractError("reconcile", "prior attempt belongs to another host/tool/plan")
            installed = previous.installed

            def fact(phase: EnvStatus, detail: str) -> None:
                write_journal(journal,InstallJournal(host_id=host.host_id,tool=plan.tool,plan_digest=digest,
                                                    phase=phase,installed=installed,detail=detail))
                event = InstallEvent(phase=phase,detail=detail,installed=installed)
                events.append(event)
                self.record(event)
            fact(EnvStatus.INSPECTING,"explicit fresh owned-scope/process/files reconciliation dispatch")
            try:
                actual = self.driver.inspect_installation(plan)
                if actual.process_state != "not_running" or not actual.scope_verified:
                    fact(EnvStatus.UNKNOWN,"process or actual effect scope remains uncertain; no replay")
                    return receipt(EnvStatus.UNKNOWN)
                files = actual.files
                if files:
                    if not installed_files_valid(files,self.driver.target):
                        fact(EnvStatus.UNKNOWN,"found target is not a verified scoped executable")
                        return receipt(EnvStatus.UNKNOWN)
                    installed = True
                    fact(EnvStatus.INSTALLED,"fresh source-scoped target confirmed; skip reinstall/configure")
                else:
                    if self.driver.target.exists():
                        fact(EnvStatus.UNKNOWN,"unrecognized existing/partial/user target; preserve and ask")
                        return receipt(EnvStatus.UNKNOWN)
                    artifact = actual.artifact
                    if artifact is None or not contained_regular_file(artifact,self.driver.cache):
                        fact(EnvStatus.NEEDS_USER_ACTION,"no verified cached artifact; no guessed download/replay")
                        return receipt(EnvStatus.NEEDS_USER_ACTION)
                    with artifact.open("rb") as stream:
                        actual_hash = hashlib.file_digest(stream,"sha256").hexdigest()
                    if actual_hash != plan.source_sha256:
                        raise ContractError("hash", "cached installer bytes changed; ask/reconcile again")
                    fact(EnvStatus.INSTALLING,"fresh no-process/absent-target proof; use exact previously fetched bytes")
                    files = self.driver.install(plan,artifact)
                    if not installed_files_valid(files,self.driver.target):
                        installed = None
                        fact(EnvStatus.UNKNOWN,"resume returned no actual scoped executable")
                        return receipt(EnvStatus.UNKNOWN)
                    installed = True
                    fact(EnvStatus.INSTALLED,"actual bounded resume effects known; readiness unverified")
                    fact(EnvStatus.CONFIGURING,"new bounded target configuration dispatch")
                    self.driver.configure(plan,files)
                fact(EnvStatus.VERIFYING,"fresh isolated smoke; no inference from old timeout or exit status")
                smoke = self.driver.smoke(plan,files)
                if not smoke.passed or not smoke.network_denied:
                    fact(EnvStatus.FAILED,"installed but current smoke/security proof did not pass")
                    return receipt(EnvStatus.FAILED)
                fact(EnvStatus.READY,"fresh scoped native smoke passed; not real-media or perceptual certification")
                return receipt(EnvStatus.READY)
            except (InstallUncertain,subprocess.TimeoutExpired,OSError,subprocess.CalledProcessError) as exc:
                fact(EnvStatus.UNKNOWN,f"recovery dispatch uncertain: {exc}; retain actual paths/facts and inspect again")
                return receipt(EnvStatus.UNKNOWN)
