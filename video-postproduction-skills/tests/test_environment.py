"""Discovery is read-only; missing PATH is neither absence nor install permission."""
import json
import pytest
from conftest import require

CHECKS=["path","package_db","desktop","known_locations","required_cli"]


def requirement(tool="filmcraft",**changes):
    data={"tool":tool,"feature":"native-edit","versions":["0.20.1-1"],**changes}
    return require("environment.models","ToolRequirement").model_validate_json(json.dumps(data))


def host(**changes):
    observation={"tool":"filmcraft","cli_path":"/fixture/filmcraft-cli","cli_sha256":"a"*64,
        "version":"0.20.1-1","package_name":"filmcraft","desktop_entries":[],
        "known_app_locations":[],"checked":CHECKS,"errors":[]}
    observed=changes.pop("observation",None)
    if observed is not None:observation.update(observed)
    data={"host_id":"b"*64,"system":"Linux","architecture":"x86_64",
        "programs":[observation],"packages":[],"disk_available_bytes":10**10,
        "memory_available_bytes":10**10,"gpu_status":"unknown","gpu_info":[],
        "evidence_kind":"contract_fixture","inspected_at":"2026-11-26T00:00:00+00:00",**changes}
    return require("environment.models","HostSnapshot").model_validate_json(json.dumps(data))


def decide(h=None,r=None):
    return require("environment.probe","plan_environment")((r or requirement(),),h or host())


def test_environment_when_compatible_installation_can_be_reused():
    value=decide()
    assert value.status=="reusable"
    assert value.tools[0].installation.cli_path=="/fixture/filmcraft-cli"
    assert value.ready is False  # Metadata is not native smoke or real-media readiness.


def test_environment_when_only_path_is_missing_but_known_location_has_cli():
    value=decide(host(observation={"cli_path":"/opt/existing/filmcraft-cli","known_app_locations":["/opt/existing"]}))
    assert value.status=="reusable"
    assert value.tools[0].installation.cli_path=="/opt/existing/filmcraft-cli"


def test_environment_when_gui_package_exists_without_required_cli():
    value=decide(host(observation={"cli_path":None,"cli_sha256":None,"desktop_entries":["/fixture/filmcraft.desktop"]}))
    assert value.status=="needs_user_action"
    assert "existing" in value.tools[0].reason.lower()


def test_environment_when_launcher_does_not_supply_editor_cli():
    value=decide(host(observation={"cli_path":None,"cli_sha256":None,"version":None,"package_name":None},packages=[{"name":"artcraft-launcher","version":"0.20.0-1"}]))
    assert value.status=="missing"
    assert value.ready is False


@pytest.mark.parametrize("unchecked",CHECKS)
def test_environment_when_discovery_channel_was_not_inspected(unchecked):
    snapshot=host(observation={"cli_path":None,"cli_sha256":None,"version":None,"package_name":None,"checked":[c for c in CHECKS if c!=unchecked]})
    assert decide(snapshot).status=="unknown"


def test_environment_when_package_or_location_probe_failed():
    snapshot=host(observation={"cli_path":None,"cli_sha256":None,"version":None,"package_name":None,"errors":["package DB permission denied"]})
    assert decide(snapshot).status=="unknown"


def test_environment_when_present_cli_version_cannot_be_proved():
    assert decide(host(observation={"version":None})).status=="needs_user_action"


def test_environment_when_existing_version_is_incompatible():
    assert decide(host(observation={"version":"0.1.0"})).status=="incompatible"


@pytest.mark.parametrize("changes,req_changes,status",[
    ({"system":"Darwin"},{"systems":["Linux"]},"unsupported"),
    ({"architecture":"armv7l"},{"architectures":["x86_64"]},"unsupported"),
    ({"disk_available_bytes":10},{"min_disk_bytes":100},"needs_user_action"),
    ({"memory_available_bytes":None},{"min_memory_bytes":100},"needs_user_action"),
    ({"gpu_status":"identified"},{"requires_verified_gpu":True},"needs_user_action"),
])
def test_environment_when_platform_or_resources_are_not_ready(changes,req_changes,status):
    assert decide(host(**changes),requirement(**req_changes)).status==status


def test_environment_when_optional_tool_was_explicitly_not_selected():
    value=decide(host(programs=[]),requirement(tool="autoclip",required=False,omission_reason="current work order uses native editors, no derived Shorts module"))
    assert value.status=="not_required"
    assert value.ready is False


def test_discovery_when_desktop_directory_is_not_readable(tmp_path,monkeypatch):
    from pathlib import Path
    blocked=tmp_path/".local/share/applications";blocked.mkdir(parents=True)
    monkeypatch.setattr(Path,"home",classmethod(lambda cls:tmp_path))
    blocked.chmod(0)
    try:
        entries,complete=require("environment.discovery","desktop_entries")("filmcraft")
        assert complete is False
    finally:
        blocked.chmod(0o700)


def test_discovery_when_path_directory_cannot_be_searched(tmp_path,monkeypatch):
    from postproduction.environment.catalog import ToolSpec
    import postproduction.environment.discovery as discovery
    blocked=tmp_path/"blocked-bin";blocked.mkdir();blocked.chmod(0)
    monkeypatch.setenv("PATH",str(blocked))
    monkeypatch.setattr(discovery,"tool_spec",lambda tool:ToolSpec(("synthetic-missing-cli",),(),"absent-app",()))
    try:
        observed=require("environment.discovery","inspect_program")(requirement(),(),True)
        snapshot=host(programs=[json.loads(observed.model_dump_json())])
        assert decide(snapshot).status=="unknown"
    finally:
        blocked.chmod(0o700)


def test_environment_when_actual_current_host_is_inspected_without_app_launch():
    reqs=tuple(requirement(tool=t,versions=[]) for t in ("filmcraft","effectcraft","soundcraft"))
    snapshot=require("environment.probe","inspect_host")(reqs)
    assert snapshot.evidence_kind=="read_only_host"
    assert any(p.name=="artcraft-launcher" for p in snapshot.packages)
    assert len(snapshot.programs)==3
    assert all(p.cli_path and p.cli_sha256 and p.version for p in snapshot.programs)
    decision=require("environment.probe","plan_environment")(reqs,snapshot)
    assert decision.status=="reusable"
    assert decision.ready is False
