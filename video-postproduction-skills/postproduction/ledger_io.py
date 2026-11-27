"""Typed project JSON and atomic post-only publication, using the existing production lock inode."""
from collections.abc import Generator
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import tempfile

from production.store import ProjectStore
from pydantic import JsonValue, TypeAdapter, ValidationError

from postproduction.errors import ContractError
from postproduction.state_models import PostState


def check_paths(path: Path) -> Path:
    """Reuse the actual public production lock_path, never a second invented post lock."""
    lock = ProjectStore(path).lock_path
    for item in (path,lock):
        if any(p.is_symlink() for p in (item,*item.parents)):
            raise ContractError("path", "ledger/production lock symlink refused")
    if not path.parent.is_dir():
        raise ContractError("path", "existing project directory required")
    return lock


@contextmanager
def shared_lock(path: Path) -> Generator[None]:
    """Use the exact same inode/flock protocol as the actual production writer."""
    lock = check_paths(path)
    with lock.open("a+") as stream:
        try:
            fcntl.flock(stream.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ContractError("lock", "another project writer owns the shared production lock") from exc
        try:
            yield
        finally:
            fcntl.flock(stream.fileno(),fcntl.LOCK_UN)


def document(path: Path) -> dict[str,JsonValue]:
    """Keep every foreign/root field; validate JSON rather than carrying Any across boundaries."""
    try:
        return TypeAdapter(dict[str,JsonValue]).validate_json(path.read_bytes()) if path.exists() else {}
    except (OSError,ValidationError) as exc:
        raise ContractError("state", "project document is unreadable or malformed") from exc


def publish(path: Path, source: dict[str,JsonValue], state: PostState) -> bytes:
    """Atomic publication owns only the postproduction namespace and fsyncs the directory."""
    post = TypeAdapter(JsonValue).validate_json(state.model_dump_json())
    encoded = (json.dumps({**source,"postproduction":post},ensure_ascii=False,indent=2)+"\n").encode()
    temp: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb",dir=path.parent,prefix=".postproduction-",delete=False) as stream:
            temp = Path(stream.name)
            _ = stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp,path)
        temp = None
        directory = os.open(path.parent,os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
        return encoded
    finally:
        if temp is not None:
            temp.unlink(missing_ok=True)
