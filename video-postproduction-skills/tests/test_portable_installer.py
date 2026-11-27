"""Exercise owned portable extraction with locally-created archives, never vendor payload downloads."""
import io
import tarfile
import pytest
from conftest import require


def archive(root,members):
    path=root/"fixture.tar.gz"
    with tarfile.open(path,"w:gz") as out:
        for name,content,kind in members:
            item=tarfile.TarInfo(name);item.mode=0o700
            if kind=="symlink":item.type=tarfile.SYMTYPE;item.linkname=content;out.addfile(item)
            else:
                data=content.encode();item.size=len(data);out.addfile(item,io.BytesIO(data))
    return path


def unpack(path,target,limit=100000):
    spec=require("environment.portable","PortableSpec")(cli_name="filmcraft-cli",max_unpacked_bytes=limit)
    return require("environment.portable","unpack_portable")(path,target,spec)


def test_portable_when_archive_contains_owned_relative_program(tmp_path):
    source=archive(tmp_path,[("bin/filmcraft-cli","#!/bin/sh\necho fixture\n","file")])
    files=unpack(source,tmp_path/"new-tool")
    assert files==(tmp_path/"new-tool/bin/filmcraft-cli",)
    assert files[0].read_text()=="#!/bin/sh\necho fixture\n"
    assert files[0].stat().st_mode & 0o111


@pytest.mark.parametrize("members",[
    [("../outside","bad","file")],[("/outside","bad","file")],
    [("escape","../../outside","symlink"),("escape/filmcraft-cli","bad","file")],
    [("bin/filmcraft-cli","/usr/bin/python3","symlink")],
    [("one/filmcraft-cli","first","file"),("two/filmcraft-cli","second","file")],
    [("no-cli.txt","not a native program","file")],
])
def test_portable_when_payload_escapes_or_cannot_supply_unique_cli(tmp_path,members):
    source=archive(tmp_path,members)
    with pytest.raises(require("errors","ContractError")):
        unpack(source,tmp_path/"new-tool")
    assert not (tmp_path/"new-tool").exists()
    assert not (tmp_path/"outside").exists()


def test_portable_when_unpacked_bytes_exceed_the_approved_bound(tmp_path):
    source=archive(tmp_path,[("filmcraft-cli","X"*100,"file")])
    with pytest.raises(require("errors","ContractError"),match="limit"):
        unpack(source,tmp_path/"new-tool",limit=20)
    assert not (tmp_path/"new-tool").exists()


def test_portable_when_target_already_belongs_to_someone_else(tmp_path):
    target=tmp_path/"existing";target.mkdir();(target/"project").write_text("owned by another terminal")
    source=archive(tmp_path,[("filmcraft-cli","new","file")])
    with pytest.raises(require("errors","ContractError"),match="existing"):
        unpack(source,target)
    assert (target/"project").read_text()=="owned by another terminal"
