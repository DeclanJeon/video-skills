"""Bounded owned portable extraction, without maintainer scripts or implicit dependencies."""
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tarfile
import tempfile
from typing import Self

from pydantic import model_validator

from postproduction.common import Frozen, Nonempty, Positive
from postproduction.errors import ContractError


class PortableSpec(Frozen):
    cli_name: Nonempty
    max_unpacked_bytes: Positive
    max_members: Positive = 10000

    @model_validator(mode="after")
    def basename(self) -> Self:
        if PurePosixPath(self.cli_name).name != self.cli_name or any(c in self.cli_name for c in "\\:\0"):
            raise ContractError("portable", "expected CLI is a concrete basename, not a path")
        return self


def safe_members(archive: tarfile.TarFile, spec: PortableSpec) -> tuple[tarfile.TarInfo, ...]:
    """Constrain all members before extraction; data_filter checks again while writing."""
    members: list[tarfile.TarInfo] = []
    total = 0
    for item in archive:
        path = PurePosixPath(item.name)
        if (path.is_absolute() or ".." in path.parts or "\\" in item.name or ":" in item.name
            or "\0" in item.name or len(item.name) > 4096):
            raise ContractError("portable", "archive path escapes or is not portable")
        if not (item.isfile() or item.isdir() or item.issym() or item.islnk()):
            raise ContractError("portable", "device/special archive member refused")
        if item.issym() or item.islnk():
            raise ContractError("portable", "link-dependent portable layouts need a separately verified adapter; regular-file payload required")
        total += item.size
        if total > spec.max_unpacked_bytes or len(members) >= spec.max_members:
            raise ContractError("limit", "archive exceeds approved unpack byte/member limit")
        members.append(item)
    return tuple(members)


def payload_inventory(root: Path, spec: PortableSpec) -> tuple[Path, ...]:
    """Complete verified regular-file mount inventory, unique executable CLI first."""
    if any(p.is_symlink() for p in (root,*root.parents)):
        raise ContractError("portable", "symlink payload root refused")
    entries = tuple(sorted(root.rglob("*")))
    if any(p.is_symlink() or not (p.is_dir() or p.is_file()) for p in entries):
        raise ContractError("portable", "unsupported link/special runtime payload layout")
    files = tuple(p for p in entries if p.is_file())
    programs = tuple(p for p in files if p.name==spec.cli_name and os.access(p,os.X_OK))
    if len(programs)!=1:
        raise ContractError("portable", "payload must supply exactly one real executable CLI")
    return (programs[0],*(p for p in files if p!=programs[0]))


def unpack_portable(archive: Path, target: Path, spec: PortableSpec) -> tuple[Path, ...]:
    """Extract only owned staging; publish with existing GNU mv no-clobber on supported Linux."""
    if sys.platform != "linux":
        raise ContractError("portable", "non-Linux no-clobber publish needs a verified adapter")
    for path in (target,*target.parents,archive,*archive.parents):
        if path.is_symlink():
            raise ContractError("portable", "symlink source/target parent refused")
    if target.exists():
        raise ContractError("existing", "existing installation target cannot be replaced")
    if not target.parent.is_dir():
        raise ContractError("portable", "approved target parent must already exist")
    try:
        with tempfile.TemporaryDirectory(dir=archive.parent,prefix=".portable-stage-") as temp:
            stage = Path(temp)/"payload"
            stage.mkdir()
            with tarfile.open(archive,"r:*") as source:
                members = safe_members(source,spec)
                source.extractall(stage,members=members,filter="data")
            relative = tuple(p.relative_to(stage) for p in payload_inventory(stage,spec))
            if stage.stat().st_dev != target.parent.stat().st_dev:
                raise ContractError("portable", "owned no-clobber publication requires one filesystem")
            _ = subprocess.run(["mv","--no-clobber","--no-target-directory","--",str(stage),str(target)],
                               capture_output=True,check=True,timeout=30)
            if stage.exists():
                raise ContractError("existing", "another writer created the target; no-clobber publish skipped")
            return tuple(target/p for p in relative)
    except (tarfile.TarError,OSError,subprocess.CalledProcessError,subprocess.TimeoutExpired) as exc:
        raise ContractError("portable", "archive extraction/publish failed; inspect owned paths before retry") from exc
