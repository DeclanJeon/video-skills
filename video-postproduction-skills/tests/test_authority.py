"""Per-edit scope/format/brief grants do not become install or provider consent."""
import json
import shutil
import pytest
from conftest import require
from support import fixture,modify_authority


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    path=tmp_path_factory.mktemp("authority-source");fixture(path);return path


@pytest.mark.parametrize("field,value",[
    ("project_id","another-project"),("receiver","another-team"),
    ("handoff_digest","a"*64),("scope_revision","scope-other"),
    ("brief_digest","b"*64),("profile_digest","c"*64),
])
def test_authority_when_grant_is_for_other_exact_input(built,tmp_path,field,value):
    shutil.copytree(built,tmp_path,dirs_exist_ok=True)
    request=json.loads((tmp_path/"request.json").read_text())
    modify_authority(tmp_path,request,**{field:value})
    with pytest.raises(require("errors","ContractError"),match="authority"):
        require("intake","load_intake")(tmp_path,tmp_path/"request.json")


def test_authority_when_evidence_bytes_changed(built,tmp_path):
    shutil.copytree(built,tmp_path,dirs_exist_ok=True)
    (tmp_path/"edit-grant.txt").write_text("changed grant")
    with pytest.raises(require("errors","ContractError")):
        require("intake","load_intake")(tmp_path,tmp_path/"request.json")
