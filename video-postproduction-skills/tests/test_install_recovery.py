"""Explicit bounded reconciliation/resume contracts; never replay an unknown installer without inspection."""
from pathlib import Path
import pytest
from conftest import require
from test_installers import FixtureDriver
from test_install_consent import missing_host,plan,authority
import hashlib


class RecoverableFixture(FixtureDriver):
    def inspect_installation(self,p):
        self.calls.append("inspect")
        files=tuple(self.target.glob("fixture-program"))
        return require("environment.recovery_models","InstallInspection")(
            process_state="unknown" if self.interrupt=="still-unknown" else "not_running",
            files=files,artifact=self.cache/"artifact.bin",scope_verified=True,
            evidence="contract fixture inspect actual owned files; NOT a real vendor inspection")


def setup(root):
    h=missing_host();driver=RecoverableFixture(root,interrupt="install")
    p=plan(h,write_paths=[str(driver.target),str(driver.cache),str(driver.lease_root)],source_sha256=hashlib.sha256(b"temporary fixture artifact").hexdigest())
    events=[];a=authority(p,h)
    start=require("environment.provision","Provisioner")(driver,events.append).execute(p,h,a)
    assert start.status=="unknown"
    recovery=require("environment.recovery","InstallRecovery")(driver,events.append)
    return h,p,a,driver,recovery


def test_recovery_when_known_scoped_no_process_and_no_target_reuses_verified_artifact(tmp_path):
    h,p,a,driver,recovery=setup(tmp_path);driver.interrupt=None
    result=recovery.resume(p,h,a)
    assert result.status=="ready"
    assert result.evidence_kind=="contract_fixture"
    assert driver.calls==["fetch","install","inspect","install","configure","smoke"]


def test_recovery_when_completed_target_exists_does_not_repeat_install(tmp_path):
    h,p,a,driver,recovery=setup(tmp_path);driver.interrupt=None
    driver.install(p,driver.cache/"artifact.bin")
    before=driver.calls.count("install")
    result=recovery.resume(p,h,a)
    assert result.status=="ready"
    assert driver.calls.count("install")==before
    assert driver.calls[-2:]==["inspect","smoke"]


def test_recovery_when_process_or_effect_scope_is_unknown_never_replays(tmp_path):
    h,p,a,driver,recovery=setup(tmp_path);driver.interrupt="still-unknown"
    result=recovery.resume(p,h,a)
    assert result.status=="unknown"
    assert driver.calls==["fetch","install","inspect"]


def test_recovery_when_old_approval_cannot_cover_new_version_or_paths(tmp_path):
    h,p,a,driver,recovery=setup(tmp_path)
    with pytest.raises(require("errors","ContractError")):
        recovery.resume(p.model_copy(update={"version":"2"}),h,a)
    assert driver.calls==["fetch","install"]
