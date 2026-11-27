"""Primary-source route checks; hypothetical fixture URLs are never fetched or claimed live."""
import json
import pytest
from conftest import require
from support import json_pin
from test_install_consent import missing_host,plan


def release_plan(root,**changes):
    artifact_hash=changes.pop("source_sha256","c"*64)
    record={"tool":"filmcraft","version":"0.20.1","asset_url":"https://github.com/storytold/filmcraft/releases/download/v0.20.1/FIXTURE-NOT-A-LIVE-ASSET.tar.gz",
        "asset_sha256":artifact_hash,"verification":"official_checksum",
        "source_document_url":"https://github.com/storytold/filmcraft/releases/tag/v0.20.1"}
    evidence=json_pin(root,"release-evidence.json",record)
    p=plan(missing_host(),version="0.20.1",source_url=record["asset_url"],source_sha256=artifact_hash,source_evidence=evidence.model_dump(),source_evidence_kind="official_checksum",network_hosts=["github.com","release-assets.githubusercontent.com"],**changes)
    return p


def test_installer_route_when_craft_linux_portable_source_is_exactly_pinned(tmp_path):
    p=release_plan(tmp_path)
    route=require("environment.installers","select_route")(p)
    assert route.status=="planned"
    assert route.kind=="linux_portable_tar"
    assert route.evidence=="installed local README release inventory; actual vendor installation unperformed"
    value=require("environment.release_evidence","verify_release_evidence")(tmp_path,p)
    assert value.asset_sha256==p.source_sha256


@pytest.mark.parametrize("changes",[
    {"source_url":"https://evil.invalid/tool.tar.gz","network_hosts":["evil.invalid"]},
    {"source_url":"https://github.com/unrelated/filmcraft/releases/download/v1/tool.tar.gz"},
    {"source_sha256":"f"*64},{"version":"different-version"},
])
def test_installer_route_when_publisher_or_release_pin_does_not_match(tmp_path,changes):
    p=release_plan(tmp_path).model_copy(update=changes)
    with pytest.raises(require("errors","ContractError")):
        require("environment.release_evidence","verify_release_evidence")(tmp_path,p)


def test_installer_route_when_self_hash_is_not_publisher_proof(tmp_path):
    p=release_plan(tmp_path).model_copy(update={"source_evidence_kind":"self_hash_unverified"})
    with pytest.raises(require("errors","ContractError"),match="publisher"):
        require("environment.release_evidence","verify_release_evidence")(tmp_path,p)


def test_craft_portable_driver_when_local_synthetic_archive_is_installed_and_callback_checked(tmp_path):
    import hashlib
    from test_portable_installer import archive
    cache=tmp_path/"cache";cache.mkdir()
    payload=archive(cache,[("bin/filmcraft-cli","#!/bin/sh\\necho synthetic\\n","file")])
    p=release_plan(tmp_path,source_sha256=hashlib.sha256(payload.read_bytes()).hexdigest())
    calls=[]
    def smoke(plan,files):
        calls.append(files)
        return require("environment.install_models","SmokeResult")(passed=True,evidence="synthetic callback only, no real vendor certification",network_denied=True)
    driver=require("environment.craft_installer","CraftPortableDriver")(tmp_path,tmp_path/"leases",cache,tmp_path/"new-tool",smoke)
    files=driver.install(p,payload)
    driver.configure(p,files)
    result=driver.smoke(p,files)
    assert files[0].is_file()
    assert result.passed is True
    assert calls==[files]


def test_craft_portable_driver_when_cached_payload_changed_before_install(tmp_path):
    from test_portable_installer import archive
    cache=tmp_path/"cache";cache.mkdir()
    payload=archive(cache,[("bin/filmcraft-cli","not the approved bytes","file")])
    p=release_plan(tmp_path)
    driver=require("environment.craft_installer","CraftPortableDriver")(tmp_path,tmp_path/"leases",cache,tmp_path/"new-tool",lambda p,f:None)
    with pytest.raises(require("errors","ContractError"),match="hash"):
        driver.install(p,payload)
    assert not driver.target.exists()


def test_installer_route_when_missing_or_changed_source_document_cannot_be_used(tmp_path):
    p=release_plan(tmp_path)
    (tmp_path/p.source_evidence.path).write_text("changed")
    with pytest.raises(require("errors","ContractError")):
        require("environment.release_evidence","verify_release_evidence")(tmp_path,p)


@pytest.mark.parametrize("tool,status,fragment",[
    ("autoclip","needs_user_action","diagnostics"),
    ("resolve","needs_user_action","Free/Studio"),
    ("premiere","unsupported","Linux"),
    ("after_effects","unsupported","Linux"),
])
def test_optional_vendor_route_when_real_limit_or_required_human_step_is_specific(tmp_path,tool,status,fragment):
    p=plan(missing_host(),tool=tool)
    route=require("environment.installers","select_route")(p)
    assert route.status==status
    assert fragment in route.reason
    assert route.ready is False
