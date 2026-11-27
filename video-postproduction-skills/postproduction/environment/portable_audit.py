"""Readonly archive-to-target verification for the synchronous no-clobber portable driver, not package managers."""
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import tarfile

from postproduction.environment.catalog import tool_spec
from postproduction.environment.consent_models import InstallationPlan
from postproduction.environment.install_scope import contained_regular_file, installed_files_valid
from postproduction.environment.portable import PortableSpec, safe_members, payload_inventory
from postproduction.environment.process_scope import owned_process_state
from postproduction.environment.recovery_models import InstallInspection
from postproduction.environment.release_evidence import verify_release_evidence
from postproduction.errors import ContractError


@dataclass(frozen=True, slots=True)
class PortableScope:
    root: Path
    cache: Path
    target: Path


def matches_payload(archive: Path, target: Path, spec: PortableSpec) -> bool:
    """Every payload file/link matches known archive; foreign/changed files block adoption and removal."""
    expected: set[Path] = set()
    with tarfile.open(archive,"r:*") as source:
        members = safe_members(source,spec)
        for member in members:
            path = target/member.name
            expected.add(path)
            expected.update(p for p in path.parents if p.is_relative_to(target) and p != target)
            if not path.resolve().is_relative_to(target.resolve()):
                return False
            if member.isdir():
                if not path.is_dir() or path.is_symlink():
                    return False
            elif member.issym():
                if not path.is_symlink() or os.readlink(path) != member.linkname:
                    return False
            else:
                if not path.is_file() or path.is_symlink():
                    return False
                stream = source.extractfile(member)
                if stream is None:
                    return False
                with stream, path.open("rb") as actual:
                    checksum = hashlib.sha256()
                    while block := stream.read(1048576):
                        checksum.update(block)
                    if checksum.digest() != hashlib.file_digest(actual,"sha256").digest():
                        return False
        return set(target.rglob("*")) == expected


def inspect_portable(scope: PortableScope, plan: InstallationPlan) -> InstallInspection:
    """Called under host/tool lease; derive process/file facts, never clear unknowns by caller assertion."""
    _ = verify_release_evidence(scope.root,plan)
    state = owned_process_state((scope.cache,scope.target))
    artifact = scope.cache/"artifact.tar"
    def report(verified: bool, files: tuple[Path, ...] = ()) -> InstallInspection:
        return InstallInspection(process_state=state,files=files,artifact=artifact,
            scope_verified=verified,evidence="readonly same-user process argv, exact cached archive SHA, complete payload/foreign file audit")
    if state != "not_running" or not contained_regular_file(artifact,scope.cache):
        return report(False)
    with artifact.open("rb") as stream:
        if hashlib.file_digest(stream,"sha256").hexdigest() != plan.source_sha256:
            raise ContractError("hash", "owned cached portable changed before reconciliation")
    if not scope.target.exists():
        return report(True)
    names = tool_spec(plan.tool).cli_names
    if len(names) != 1 or scope.target.is_symlink():
        return report(False)
    spec = PortableSpec(cli_name=names[0],max_unpacked_bytes=plan.max_unpacked_bytes)
    try:
        if not matches_payload(artifact,scope.target,spec):
            return report(False)
        files = payload_inventory(scope.target,spec)
    except ContractError:
        return report(False)
    if not installed_files_valid(files,scope.target):
        return report(False)
    return report(True,files)
