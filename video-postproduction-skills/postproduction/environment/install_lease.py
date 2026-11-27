"""Per-host/tool process lock; never steal/unlink a different writer's lock."""
from collections.abc import Generator
from contextlib import AbstractContextManager, contextmanager
from pathlib import Path
import sys
from types import TracebackType

from postproduction.environment.models import Tool
from postproduction.errors import ContractError


class HostToolLease:
    """Mutable resource owner for a live context, not an immutable domain/boundary record."""

    def __init__(self, root: Path, host_id: str, tool: Tool) -> None:
        self.root: Path = root
        self.host_id: str = host_id
        self.tool: Tool = tool
        self.context: AbstractContextManager[Path] | None = None

    @contextmanager
    def acquire(self) -> Generator[Path]:
        """Acquire a known tool lock after authorization; retain uncertain state for reconciliation."""
        if sys.platform == "win32":
            raise ContractError("lease", "Windows host-wide installer locking needs a verified adapter")
        import fcntl
        for parent in (self.root,*self.root.parents):
            if parent.is_symlink():
                raise ContractError("lease", "symlink lock directory refused")
        if not self.root.parent.is_dir():
            raise ContractError("lease", "lock parent must already exist within approved scope")
        self.root.mkdir(mode=0o700,exist_ok=True)
        stem = f"{self.host_id}-{self.tool.value}"
        path = self.root/f"{stem}.lock"
        state = self.root/f"{stem}.state.json"
        if path.is_symlink() or state.is_symlink():
            raise ContractError("lease", "symlink lock/state refused")
        with path.open("a+",encoding="utf-8") as stream:
            try:
                fcntl.flock(stream.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise ContractError("lease", "another process owns this host/tool lease") from exc
            try:
                yield state
            finally:
                fcntl.flock(stream.fileno(),fcntl.LOCK_UN)

    def __enter__(self) -> Path:
        if self.context is not None:
            raise ContractError("lease", "this resource owner is already holding its host/tool lease")
        context = self.acquire()
        value = context.__enter__()
        self.context = context
        return value

    def __exit__(self, kind: type[BaseException] | None, exc: BaseException | None,
                 traceback: TracebackType | None) -> bool | None:
        context = self.context
        self.context = None
        if context is not None:
            return context.__exit__(kind,exc,traceback)
        return None
