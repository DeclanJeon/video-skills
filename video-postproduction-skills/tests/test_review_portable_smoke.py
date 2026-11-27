"""Actual portable payload must be visible, exact siblings included, unrelated host files hidden. No install/download."""
from pathlib import Path
import shutil,subprocess
from conftest import require
from test_install_consent import plan


def test_smoke_when_existing_portable_cli_and_required_siblings_are_only_readonly_payload(tmp_path):
    target=tmp_path/"portable";target.mkdir()
    actual=target/"filmcraft-real";shutil.copy2("/usr/bin/filmcraft-cli",actual)
    resource=target/"resources"/"required.txt";resource.parent.mkdir();resource.write_text("fixture-resource")
    private=tmp_path/"unrelated-secret.txt";private.write_text("must be hidden")
    cli=target/"filmcraft-cli"
    cli.write_text("#!/usr/bin/python3\nfrom pathlib import Path\nimport os,sys\nroot=Path(__file__).parent\n"
        "assert (root/'resources'/'required.txt').read_text()=='fixture-resource'\n"
        f"if '--version' not in sys.argv and Path({str(private)!r}).exists(): sys.exit(43)\n"
        "os.execv(str(root/'filmcraft-real'),[str(root/'filmcraft-real'),*sys.argv[1:]])\n")
    cli.chmod(0o700)
    host=subprocess.run([str(cli),"--version"],capture_output=True,check=True,timeout=20)
    assert b"filmcraft-cli" in host.stdout
    result=require("environment.native_smoke","NativeSmoke")(tmp_path/"smoke").run(
        plan(tool="filmcraft",write_paths=[str(target)]),(cli,actual,resource))
    assert result.passed is True and result.network_denied is True,result.evidence


def test_backend_when_reusing_existing_self_contained_cli_outside_system_mounts_runs_it(tmp_path):
    from test_filmcraft import setup
    store,_,original,_=setup(tmp_path)
    target=tmp_path/'portable-existing';target.mkdir()
    binary=target/'filmcraft-cli';shutil.copy2('/usr/bin/filmcraft-cli',binary)
    backend=require('backends.filmcraft','FilmCraftBackend')(store,tmp_path/'portable-native',binary)
    packet=backend.prepare(original.order,backend.inspect(),store.read_recorded().intake.authority)
    job=store.record_reservation(packet,store.read_recorded().revision)
    assert backend.execute(packet).phase=='succeeded'
    result=backend.observe(store.read_recorded().jobs[0])
    assert result.technical_verified is True and result.frame_count==144
