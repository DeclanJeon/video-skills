"""Mock HTTPS transport only: no network/payload download is authorized or performed by these tests."""
import hashlib
import pytest
from conftest import require
from test_install_consent import missing_host,plan


class Response:
    def __init__(self,body=b"fixture artifact",status=200,location=None):
        self.body=body;self.status=status;self.location=location
    def getheader(self,name):return self.location if name=="Location" else None
    def read(self,size):value=self.body[:size];self.body=self.body[size:];return value


def transport(monkeypatch,responses):
    import postproduction.environment.download as mod
    calls=[]
    class Connection:
        def __init__(self,host,**kwargs):self.host=host;calls.append(host)
        def request(self,method,path,headers):assert method=="GET"
        def getresponse(self):return responses[self.host]
        def close(self):pass
    monkeypatch.setattr(mod,"HTTPSConnection",Connection)
    return calls


def test_download_when_exact_allowed_host_and_expected_bytes_match(tmp_path,monkeypatch):
    fn=require("environment.download","fetch_artifact")
    p=plan(missing_host(),source_sha256=hashlib.sha256(b"fixture artifact").hexdigest())
    calls=transport(monkeypatch,{"fixture.invalid":Response()})
    path=fn(p,tmp_path/"cache")
    assert path.read_bytes()==b"fixture artifact"
    assert calls==["fixture.invalid"]


def test_download_when_redirect_would_escape_approved_host_never_connects(tmp_path,monkeypatch):
    fn=require("environment.download","fetch_artifact")
    calls=transport(monkeypatch,{"fixture.invalid":Response(status=302,location="https://unapproved.invalid/data")})
    with pytest.raises(require("errors","ContractError")):
        fn(plan(),tmp_path/"cache")
    assert calls==["fixture.invalid"]
    assert not (tmp_path/"cache/artifact.tar").exists()


def test_download_when_archive_hash_is_not_expected_has_no_published_artifact(tmp_path,monkeypatch):
    fn=require("environment.download","fetch_artifact")
    transport(monkeypatch,{"fixture.invalid":Response()})
    with pytest.raises(require("errors","ContractError"),match="hash"):
        fn(plan(),tmp_path/"cache")
    assert not (tmp_path/"cache/artifact.tar").exists()


def test_download_when_byte_budget_is_exceeded_stops_and_cleans_owned_partial(tmp_path,monkeypatch):
    fn=require("environment.download","fetch_artifact")
    transport(monkeypatch,{"fixture.invalid":Response(body=b"X"*30)})
    p=plan().model_copy(update={"max_download_bytes":10})
    with pytest.raises(require("errors","ContractError"),match="limit"):
        fn(p,tmp_path/"cache")
    assert not (tmp_path/"cache/artifact.tar").exists()
    assert not (tmp_path/"cache/.download.part").exists()


def test_download_when_existing_cache_belongs_to_prior_work_is_not_overwritten(tmp_path,monkeypatch):
    fn=require("environment.download","fetch_artifact")
    calls=transport(monkeypatch,{"fixture.invalid":Response()})
    cache=tmp_path/"cache";cache.mkdir();(cache/"evidence").write_text("preserve")
    with pytest.raises(require("errors","ContractError"),match="existing"):
        fn(plan(),cache)
    assert calls==[]
    assert (cache/"evidence").read_text()=="preserve"
