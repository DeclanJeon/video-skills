"""Exact decoded source clocks; no network playlists or false metadata adoption."""
import hashlib
import subprocess
import pytest
from conftest import require


def pinned(root,name):
    return require("models","Pin")(id=name,version="1",path=name,sha256=hashlib.sha256((root/name).read_bytes()).hexdigest())


def test_probe_when_fractional_clock_must_not_be_upstream_float(tmp_path):
    subprocess.run(["ffmpeg","-v","error","-f","lavfi","-i","color=blue:s=64x64:r=24000/1001","-frames:v","48","-c:v","libx264",str(tmp_path/"fraction.mp4")],check=True,capture_output=True,timeout=30)
    value=require("media","probe_video")(tmp_path,pinned(tmp_path,"fraction.mp4"))
    assert (value.rate.num,value.rate.den)==(24000,1001)
    assert value.frame_count==48
    assert value.cfr is True


def test_probe_when_local_name_hides_network_playlist(tmp_path,monkeypatch):
    (tmp_path/"fake.mp4").write_text("#EXTM3U\nhttp://127.0.0.1:1/not-permitted\n")
    calls=[]
    def forbidden(*args,**kwargs):
        calls.append(args)
        pytest.fail("unrecognized media must be rejected before tool dispatch")
    monkeypatch.setattr(subprocess,"run",forbidden)
    with pytest.raises(require("errors","ContractError")):
        require("media","probe_video")(tmp_path,pinned(tmp_path,"fake.mp4"))
    assert calls==[]


def test_probe_when_media_bytes_do_not_match_pin(tmp_path):
    (tmp_path/"wrong.mp4").write_bytes(b"not media")
    value=pinned(tmp_path,"wrong.mp4")
    (tmp_path/"wrong.mp4").write_bytes(b"replacement")
    with pytest.raises(require("errors","ContractError")):
        require("media","probe_video")(tmp_path,value)
