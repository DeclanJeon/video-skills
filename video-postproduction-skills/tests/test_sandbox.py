"""Real existing bwrap: network denial, private prefs, read-only media, no user app bridge."""
import json
from pathlib import Path
import pytest
from conftest import require


def runner(tmp_path,read_roots=()):
    scope=require("backends.process","SandboxScope")(workspace=tmp_path/"work",owner="synthetic-owned-job",read_roots=read_roots)
    return require("backends.process","IsolatedProcess")(scope)


def test_sandbox_when_home_is_private_and_stdin_stdout_are_preserved(tmp_path):
    value=runner(tmp_path).run(("/usr/bin/python3","-c","import os,sys,json; print(json.dumps({'home':os.environ['HOME'],'input':sys.stdin.read()}))"),stdin=b"owned synthetic bytes")
    assert value.returncode==0
    assert value.timed_out is False
    data=json.loads(value.stdout)
    assert data["home"].startswith(str(tmp_path/"work"))
    assert data["input"]=="owned synthetic bytes"


def test_sandbox_when_external_network_is_unreachable_before_app_first_run(tmp_path):
    code="import socket,sys\ns=socket.socket();s.settimeout(1)\ntry:s.connect(('1.1.1.1',443))\nexcept OSError:sys.exit(0)\nsys.exit(7)"
    result=runner(tmp_path).run(("/usr/bin/python3","-c",code))
    assert result.returncode==0
    assert result.network_denied is True


def test_sandbox_when_source_media_is_readonly_and_unapproved_file_is_hidden(tmp_path):
    sources=tmp_path/"sources";sources.mkdir();source=sources/"approved.txt";source.write_text("approved source")
    hidden=tmp_path/"other-terminal.txt";hidden.write_text("do not expose")
    code=f"from pathlib import Path\np=Path({str(source)!r})\nassert p.read_text()=='approved source'\ntry:p.write_text('changed')\nexcept OSError:pass\nelse:raise RuntimeError('source was writable')\nassert not Path({str(hidden)!r}).exists()"
    result=runner(tmp_path,(sources,)).run(("/usr/bin/python3","-c",code))
    assert result.returncode==0
    assert source.read_text()=="approved source"
    assert hidden.read_text()=="do not expose"


def test_sandbox_when_workspace_is_unowned_nonempty_refuses_before_dispatch(tmp_path):
    work=tmp_path/"work";work.mkdir();(work/"user-project").write_text("preserve")
    with pytest.raises(require("errors","ContractError"),match="owner"):
        runner(tmp_path).run(("/usr/bin/true",))
    assert (work/"user-project").read_text()=="preserve"
