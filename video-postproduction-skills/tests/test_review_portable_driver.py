"""Actual local synthetic archive -> CraftPortableDriver -> recovered inventory -> native smoke. No fetch/vendor install."""
import hashlib,io,shutil,tarfile
from pathlib import Path
import pytest
from conftest import require
from test_installer_routes import release_plan
from test_portable_installer import unpack


@pytest.fixture(scope="module")
def portable(tmp_path_factory):
    root=tmp_path_factory.mktemp("actual-portable-inventory")
    source=root/"source"/"bundle";(source/"bin").mkdir(parents=True);(source/"resources").mkdir()
    shutil.copy2("/usr/bin/filmcraft-cli",source/"bin"/"filmcraft-real")
    (source/"resources"/"required.txt").write_text("fixture-resource")
    secret=root/"unrelated-secret";secret.write_text("must remain hidden")
    cli=source/"bin"/"filmcraft-cli"
    cli.write_text("#!/usr/bin/python3\nfrom pathlib import Path\nimport os,sys\nroot=Path(__file__).parent\n"
        "assert (root.parent/'resources'/'required.txt').read_text()=='fixture-resource'\n"
        f"assert not Path({str(secret)!r}).exists()\n"
        "os.execv(str(root/'filmcraft-real'),[str(root/'filmcraft-real'),*sys.argv[1:]])\n")
    cli.chmod(0o700)
    cache=root/"cache";cache.mkdir();payload=cache/"artifact.tar"
    with tarfile.open(payload,"w:gz") as out:out.add(source,arcname="bundle")
    p=release_plan(root,source_sha256=hashlib.sha256(payload.read_bytes()).hexdigest())
    smoke=require("environment.native_smoke","NativeSmoke")(root/"smoke")
    driver=require("environment.craft_installer","CraftPortableDriver")(root,root/"leases",cache,root/"target",smoke.run)
    files=driver.install(p,payload)
    return driver,p,files


def test_portable_when_actual_driver_install_inventory_reaches_native_smoke(portable):
    driver,p,files=portable
    driver.configure(p,files)
    actual=driver.smoke(p,files)  # Intentionally use EXACT producer result, no expanded fixture tuple.
    assert actual.passed is True and actual.network_denied is True,actual.evidence
    assert files[0].name=="filmcraft-cli" and len(files)==3


def test_portable_when_actual_recovery_audit_inventory_reaches_native_smoke(portable):
    driver,p,files=portable
    recovered=driver.inspect_installation(p)
    assert recovered.scope_verified is True and recovered.files==files
    actual=driver.smoke(p,recovered.files)
    assert actual.passed is True and actual.network_denied is True,actual.evidence


def test_portable_when_recovery_sees_foreign_file_never_adds_it_to_payload(portable):
    driver,p,files=portable;extra=driver.target/"user-file";extra.write_text("preserve")
    try:
        recovered=driver.inspect_installation(p)
        assert recovered.scope_verified is False and recovered.files==() and extra.read_text()=="preserve"
    finally:extra.unlink()


@pytest.mark.parametrize("link",["symlink","hardlink"])
def test_portable_when_internal_links_need_unverified_runtime_layout_no_publish(tmp_path,link):
    source=tmp_path/"linked.tar"
    with tarfile.open(source,"w") as out:
        data=b"#!/bin/sh\nexit 0\n";item=tarfile.TarInfo("bin/filmcraft-cli");item.mode=0o700;item.size=len(data)
        out.addfile(item,io.BytesIO(data))
        item=tarfile.TarInfo("bin/alias");item.type=tarfile.SYMTYPE if link=="symlink" else tarfile.LNKTYPE
        item.linkname="filmcraft-cli" if link=="symlink" else "bin/filmcraft-cli";out.addfile(item)
    with pytest.raises(require("errors","ContractError")):
        unpack(source,tmp_path/"unsupported-target")
    assert not (tmp_path/"unsupported-target").exists()
