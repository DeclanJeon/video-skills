"""Local synthetic portable archives only, plus readonly own-process inspection. No vendor downloads."""
import hashlib
from conftest import require
from test_portable_installer import archive
from test_installer_routes import release_plan


def setup(root):
    cache=root/"cache";cache.mkdir()
    payload=archive(cache,[("bin/filmcraft-cli","#!/bin/sh\necho local-fixture\n","file")])
    canonical=cache/"artifact.tar";payload.rename(canonical)
    p=release_plan(root,source_sha256=hashlib.sha256(canonical.read_bytes()).hexdigest())
    driver=require("environment.craft_installer","CraftPortableDriver")(root,root/"leases",cache,root/"target",lambda p,f:None)
    return driver,p,canonical


def test_portable_reconcile_when_exact_cache_and_absent_target_are_physically_inspected(tmp_path):
    driver,p,artifact=setup(tmp_path)
    actual=driver.inspect_installation(p)
    assert actual.process_state=="not_running"
    assert actual.scope_verified is True
    assert actual.artifact==artifact
    assert actual.files==()


def test_portable_reconcile_when_complete_matching_payload_does_not_install_again(tmp_path):
    driver,p,artifact=setup(tmp_path);files=driver.install(p,artifact)
    actual=driver.inspect_installation(p)
    assert actual.scope_verified is True
    assert actual.files==files


def test_portable_reconcile_when_existing_or_extra_user_bytes_are_preserved_as_unknown(tmp_path):
    driver,p,artifact=setup(tmp_path);driver.install(p,artifact)
    (driver.target/"user-file.txt").write_text("keep me")
    actual=driver.inspect_installation(p)
    assert actual.scope_verified is False
    assert (driver.target/"user-file.txt").read_text()=="keep me"


def test_portable_reconcile_when_own_scope_process_is_live_leaves_it_running(tmp_path):
    import subprocess,sys
    driver,p,artifact=setup(tmp_path)
    process=subprocess.Popen([sys.executable,"-c","import time; time.sleep(30)",str(driver.target)])
    try:
        actual=driver.inspect_installation(p)
        assert actual.process_state=="running"
        assert actual.scope_verified is False
        assert process.poll() is None
    finally:
        process.terminate();process.wait(timeout=5)


def test_portable_reconcile_when_source_binary_changed_cannot_claim_ready(tmp_path):
    driver,p,artifact=setup(tmp_path);files=driver.install(p,artifact)
    files[0].write_text("#!/bin/sh\necho replaced\n")
    actual=driver.inspect_installation(p)
    assert actual.scope_verified is False
