"""Temporary installer-driver contracts; never actual Craft/vendor-installation certification."""
import hashlib
from pathlib import Path
import subprocess
import pytest
from conftest import require
from test_install_consent import authority,missing_host,plan


class FixtureDriver:
    evidence_kind="contract_fixture"
    uses_package_manager=False
    def __init__(self,root,smoke=True,interrupt=None):
        self.root=root;self.lease_root=root/"leases";self.cache=root/"cache"
        self.target=root/"new-tool";self.calls=[];self.smoke_ok=smoke;self.interrupt=interrupt
    def fetch(self,p):
        self.calls.append("fetch")
        self.cache.mkdir();path=self.cache/"artifact.bin";path.write_bytes(b"temporary fixture artifact")
        return path
    def install(self,p,artifact):
        self.calls.append("install")
        if self.interrupt=="install":
            raise require("environment.provision","InstallUncertain")("fixture interruption after dispatch; reconcile first")
        self.target.mkdir();program=self.target/"fixture-program"
        program.write_text("#!/bin/sh\nprintf 'fixture-ready\\n'\n");program.chmod(0o700)
        return (program,)
    def configure(self,p,files):
        self.calls.append("configure")
    def smoke(self,p,files):
        self.calls.append("smoke")
        value=subprocess.run([str(files[0])],capture_output=True,text=True,check=True,timeout=5)
        return require("environment.install_models","SmokeResult")(passed=self.smoke_ok,evidence="temporary stub stdout="+value.stdout.strip(),network_denied=True)


def prepared(root,**driver_kw):
    h=missing_host()
    driver=FixtureDriver(root,**driver_kw)
    p=plan(h,write_paths=[str(driver.target),str(driver.cache),str(driver.lease_root)],source_sha256=hashlib.sha256(b"temporary fixture artifact").hexdigest())
    events=[]
    runner=require("environment.provision","Provisioner")(driver,events.append)
    return h,p,driver,events,runner


def test_installer_when_consent_is_missing_has_zero_fetch_or_install_effects(tmp_path):
    h,p,driver,events,runner=prepared(tmp_path)
    result=runner.execute(p,h,require("environment.consent_models","InstallAuthority")())
    assert result.status=="awaiting_consent"
    assert driver.calls==[]
    assert not driver.lease_root.exists()
    assert not driver.cache.exists()


def test_installer_when_user_declines_never_fetches(tmp_path):
    h,p,driver,events,runner=prepared(tmp_path)
    result=runner.execute(p,h,authority(p,h,"decline"))
    assert result.status=="declined"
    assert driver.calls==[]


def test_installer_when_scope_changed_does_not_start_driver(tmp_path):
    h,p,driver,events,runner=prepared(tmp_path)
    changed=p.model_copy(update={"version":"changed-version"})
    with pytest.raises(require("errors","ContractError")):
        runner.execute(changed,h,authority(p,h))
    assert driver.calls==[]


def test_installer_when_exact_fixture_scope_is_approved_and_smoke_runs(tmp_path):
    h,p,driver,events,runner=prepared(tmp_path)
    (tmp_path/"other-users-project.txt").write_text("keep")
    result=runner.execute(p,h,authority(p,h))
    assert result.status=="ready"
    assert result.installed is True
    assert result.evidence_kind=="contract_fixture"
    assert result.real_media_ready is False
    assert driver.calls==["fetch","install","configure","smoke"]
    assert (tmp_path/"other-users-project.txt").read_text()=="keep"
    assert any(e.phase=="installed" for e in events)


def test_installer_when_exit_zero_but_smoke_fails_is_not_ready(tmp_path):
    h,p,driver,events,runner=prepared(tmp_path,smoke=False)
    result=runner.execute(p,h,authority(p,h))
    assert result.status=="failed"
    assert result.installed is True
    assert result.real_media_ready is False
    assert any(e.phase=="installed" for e in events)


def test_installer_when_dispatch_result_is_unknown_never_blindly_replays(tmp_path):
    h,p,driver,events,runner=prepared(tmp_path,interrupt="install")
    a=authority(p,h)
    result=runner.execute(p,h,a)
    assert result.status=="unknown"
    assert driver.calls==["fetch","install"]
    with pytest.raises(require("errors","ContractError"),match="reconcil"):
        runner.execute(p,h,a)
    assert driver.calls==["fetch","install"]


def test_installer_when_artifact_bytes_fail_expected_hash_stops_before_install(tmp_path):
    h,p,driver,events,runner=prepared(tmp_path)
    changed=p.model_copy(update={"source_sha256":"a"*64})
    result=runner.execute(changed,h,authority(changed,h))
    assert result.status=="failed"
    assert driver.calls==["fetch"]
    assert not driver.target.exists()


def test_installer_when_existing_target_must_not_be_overwritten(tmp_path):
    h,p,driver,events,runner=prepared(tmp_path)
    driver.target.mkdir();(driver.target/"user-file").write_text("preserve")
    with pytest.raises(require("errors","ContractError"),match="existing"):
        runner.execute(p,h,authority(p,h))
    assert driver.calls==[]
    assert (driver.target/"user-file").read_text()=="preserve"


def test_installer_when_simulated_question_cannot_authorize_real_vendor_driver(tmp_path):
    h,p,driver,events,runner=prepared(tmp_path)
    driver.evidence_kind="vendor_installation"
    with pytest.raises(require("errors","ContractError"),match="fixture"):
        runner.execute(p,h,authority(p,h))
    assert driver.calls==[]


def test_installer_when_driver_reports_empty_installed_paths_cannot_claim_readiness(tmp_path):
    h,p,driver,events,runner=prepared(tmp_path)
    driver.install=lambda p,artifact:()
    driver.smoke=lambda p,files:require("environment.install_models","SmokeResult")(passed=True,evidence="simulated false success",network_denied=True)
    result=runner.execute(p,h,authority(p,h))
    assert result.status!="ready"
    assert result.installed is not True


def test_installer_when_download_receipt_is_outside_approved_cache(tmp_path):
    h,p,driver,events,runner=prepared(tmp_path)
    outside=tmp_path/"unapproved-artifact";outside.write_bytes(b"temporary fixture artifact")
    driver.fetch=lambda p:outside
    result=runner.execute(p,h,authority(p,h))
    assert result.status!="ready"
    assert "install" not in driver.calls


def test_host_lease_when_same_resource_owner_is_reentered_must_not_release_first_lock(tmp_path):
    Lease=require("environment.install_lease","HostToolLease")
    h=missing_host();p=plan(h)
    owner=Lease(tmp_path/"leases",h.host_id,p.tool)
    with owner:
        with pytest.raises(require("errors","ContractError")):
            owner.__enter__()
        with pytest.raises(require("errors","ContractError"),match="lease"):
            with Lease(tmp_path/"leases",h.host_id,p.tool):
                pytest.fail("reentrant ownership must not silently drop the first lock")


def operator_shape(root):
    from test_environment import requirement
    h,p,driver,events,runner=prepared(root)
    h=h.model_copy(update={"evidence_kind":"read_only_host","requirements":(requirement(),)})
    driver.evidence_kind="vendor_installation"
    p=p.model_copy(update={"host_fingerprint":require("environment.consent","host_fingerprint")(h),"source_evidence_kind":"official_checksum"})
    a=authority(p,h)
    a=a.model_copy(update={"question":a.question.model_copy(update={"channel":"operator_message"}),"consent":a.consent.model_copy(update={"channel":"operator_message"})})
    return h,p,driver,events,runner,a


def test_installer_when_real_driver_must_reinspect_host_before_any_fetch(tmp_path,monkeypatch):
    import postproduction.environment.provision as module
    h,p,driver,events,runner,a=operator_shape(tmp_path)
    changed=h.model_copy(update={"architecture":"aarch64"})
    monkeypatch.setattr(module,"inspect_host",lambda reqs:changed,raising=False)
    with pytest.raises(require("errors","ContractError"),match="host"):
        runner.execute(p,h,a)
    assert driver.calls==[]


def test_installer_when_another_terminal_completed_compatible_install_reuses_it(tmp_path,monkeypatch):
    import postproduction.environment.provision as module
    h,p,driver,events,runner,a=operator_shape(tmp_path)
    observed=h.programs[0].model_copy(update={"cli_path":"/already/installed/filmcraft-cli","cli_sha256":"e"*64,"version":"0.20.1-1","package_name":"filmcraft"})
    changed=h.model_copy(update={"programs":(observed,)})
    monkeypatch.setattr(module,"inspect_host",lambda reqs:changed,raising=False)
    result=runner.execute(p,h,a)
    assert result.status=="reusable"
    assert driver.calls==[]
    assert not driver.cache.exists()


def test_installer_when_ownership_lock_is_busy_never_fetches_or_removes_foreign_lock(tmp_path):
    import fcntl
    h,p,driver,events,runner=prepared(tmp_path)
    Lease=require("environment.install_lease","HostToolLease")
    with Lease(driver.lease_root,h.host_id,p.tool):
        with pytest.raises(require("errors","ContractError"),match="lease"):
            runner.execute(p,h,authority(p,h))
    assert driver.calls==[]
