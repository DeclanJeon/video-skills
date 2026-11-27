"""Delete only exact known newly-created owned target; preserve cache/protected inputs/user/changed/live paths."""
from test_portable_recovery import setup as portable
from test_install_consent import authority,missing_host
from conftest import require


def setup(root):
    driver,p,artifact=portable(root)
    class FixturePortable(type(driver)):
        evidence_kind="contract_fixture"
    driver=FixturePortable(root,driver.lease_root,driver.cache,driver.target,driver.smoke_runner)
    p=p.model_copy(update={"write_paths":tuple(str(x) for x in (driver.target,driver.cache,driver.lease_root))})
    h=missing_host()
    driver.install(p,artifact)
    with require("environment.install_lease","HostToolLease")(driver.lease_root,h.host_id,p.tool) as journal:
        require("environment.install_journal","write_journal")(journal,require("environment.install_models","InstallJournal")(
            host_id=h.host_id,tool=p.tool,plan_digest=require("environment.consent","plan_digest")(p),
            phase=require("environment.models","EnvStatus").FAILED,installed=True,detail="synthetic known installation; smoke not ready"))
    rollback=require("environment.rollback","InstallRollback")(driver,lambda e:None)
    return h,p,driver,rollback


def test_rollback_when_known_new_exact_payload_and_no_live_process_removes_only_owned_target(tmp_path):
    h,p,driver,rollback=setup(tmp_path)
    result=rollback.execute(p,h,authority(p,h))
    assert result.status=="rolled_back"
    assert result.installed is False
    assert not driver.target.exists()
    assert (driver.cache/"artifact.tar").is_file()
    assert (tmp_path/p.source_evidence.path).is_file()


def test_rollback_when_extra_user_file_is_detected_does_not_delete_any_target(tmp_path):
    h,p,driver,rollback=setup(tmp_path)
    user=driver.target/"my-project";user.write_text("keep")
    result=rollback.execute(p,h,authority(p,h))
    assert result.status=="unknown"
    assert user.read_text()=="keep"
    assert (driver.target/"bin/filmcraft-cli").is_file()


def test_rollback_when_owned_binary_was_edited_is_preserved_for_operator(tmp_path):
    h,p,driver,rollback=setup(tmp_path)
    binary=driver.target/"bin/filmcraft-cli";binary.write_text("user-edited")
    result=rollback.execute(p,h,authority(p,h))
    assert result.status=="unknown"
    assert binary.read_text()=="user-edited"
