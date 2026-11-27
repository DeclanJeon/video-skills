"""Atomic production namespace in the existing project ledger; no competing registry."""
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
import fcntl
import json
import os
from pathlib import Path
import tempfile
from typing import assert_never

from pydantic import JsonValue, TypeAdapter, ValidationError

from production.models import AttemptId, ContractError, Phase, Receipt, State
from production.contracts import ACTIVE


@dataclass(frozen=True, slots=True)
class AttemptStatus:
    id: AttemptId
    phase: Phase
    job_id: str | None
    reserved: bool


@dataclass(frozen=True, slots=True)
class RecordedStatus:
    revision: int
    attempts: tuple[AttemptStatus, ...]
    inputs_ready: bool
    issues: tuple[str, ...]
    new_submission: bool = False


@dataclass
class Transaction:
    """Mutable transaction buffer, owned by one locked writer until publication."""
    state: State


class ProjectStore:
    """Preserve all existing ledger fields, adding only the production namespace."""

    def __init__(self, path: Path) -> None:
        self.path: Path = path.absolute()
        self.lock_path: Path = self.path.with_name(self.path.name + ".production.lock")

    def _check_paths(self) -> None:
        for item in (self.path, self.lock_path):
            if item.is_symlink() or any(p.is_symlink() for p in item.parents):
                raise ContractError("path", "ledger/lock symlink refused")
        if not self.path.parent.is_dir():
            raise ContractError("path", "project directory must already exist")

    @contextmanager
    def _lock(self) -> Generator[None, None, None]:
        self._check_paths()
        with self.lock_path.open("a+") as lock:
            try:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise ContractError("lock", "another project writer owns the lock") from exc
            try:
                yield
            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)

    def _document(self) -> dict[str, JsonValue]:
        if not self.path.exists():
            return {}
        return TypeAdapter(dict[str, JsonValue]).validate_json(self.path.read_bytes())

    def _publish(self, document: dict[str, JsonValue], state: State) -> bytes:
        payload = {**document, "production": json.loads(state.model_dump_json())}
        encoded = (json.dumps(payload,ensure_ascii=False,indent=2)+"\n").encode("utf-8")
        temp_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(mode="wb", dir=self.path.parent, prefix=".production-", delete=False) as out:
                temp_path = Path(out.name)
                _ = out.write(encoded)
                out.flush()
                os.fsync(out.fileno())
            os.replace(temp_path, self.path)
            temp_path = None
            with _directory(self.path.parent) as fd:
                os.fsync(fd)
            return encoded
        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)

    def _check_scope_storage(self, state: State) -> None:
        """A mutable ledger cannot be its own immutable preproduction/source pin."""
        from production.upstream import CoverageEnvelope, Project
        source_path = (self.path.parent/state.coverage_source.path).resolve()
        if source_path == self.path.resolve():
            raise ContractError("scope","approved source must be an immutable snapshot separate from the mutable ledger")
        source = TypeAdapter(CoverageEnvelope | Project).validate_json(source_path.read_bytes())
        match source:
            case CoverageEnvelope(origin=origin) if origin is not None:
                if (self.path.parent/origin.path).resolve() == self.path.resolve():
                    raise ContractError("scope","exported origin must not be the mutable ledger; snapshot it first")
            case CoverageEnvelope() | Project():
                pass
            case unreachable:
                assert_never(unreachable)

    def initialize(self, state: State) -> None:
        from production.adapters import verify_scope
        verify_scope(state, self.path.parent)
        self._check_scope_storage(state)
        if state.revision != 0 or state.attempts or state.selections or state.history or state.join_reviews or state.scope_history:
            raise ContractError("initial", "init accepts only a clean initial plan; resume known attempts instead")
        with self._lock():
            document = self._document()
            if "production" in document:
                raise ContractError("exists", "production state already exists; resume instead")
            _ = self._publish(document, state)

    def read_recorded(self) -> State:
        """Read model-validated historical facts without granting current-input readiness."""
        self._check_paths()
        document = self._document()
        if "production" not in document:
            raise ContractError("state", "production namespace missing")
        return State.model_validate(document["production"])

    def read(self) -> State:
        state = self.read_recorded()
        from production.adapters import verify_scope
        verify_scope(state, self.path.parent)
        return state

    def _input_issues(self, state: State) -> tuple[str, ...]:
        from production.upstream import verify_scope
        try:
            verify_scope(state, self.path.parent)
            self._check_scope_storage(state)
        except (ContractError, OSError, ValidationError, UnicodeError) as exc:
            return (str(exc),)
        return ()

    def _status(self, state: State, issues: tuple[str, ...]) -> RecordedStatus:
        return RecordedStatus(revision=state.revision,
            attempts=tuple(AttemptStatus(a.id,a.phase,a.job_id,a.phase in ACTIVE) for a in state.attempts),
            inputs_ready=not issues,issues=issues)

    def status(self) -> RecordedStatus:
        """Expose known jobs plus fresh input diagnostics, never a new-work permission."""
        state = self.read_recorded()
        return self._status(state,self._input_issues(state))

    def record_observation(self, attempt_id: str, receipt: Receipt, expected_revision: int) -> RecordedStatus:
        """Persist only a known attempt's remote facts, independent of mutable media readiness.

        This is deliberately NOT a generic transaction bypass: no callback or replacement
        State is accepted. Model/lock/CAS/receipt/request/job/transition checks remain.
        """
        from production.execution import observe
        if receipt.phase in {Phase.SUBMITTING,Phase.DOWNLOADED}:
            raise ContractError("observation","local submit/download gates are not remote observations")
        with self._lock():
            original_bytes = self.path.read_bytes()
            document = TypeAdapter(dict[str,JsonValue]).validate_json(original_bytes)
            state = State.model_validate(document.get("production"))
            if state.revision != expected_revision:
                raise ContractError("revision","compare-and-swap failed")
            updated = observe(state,attempt_id,receipt)
            validated = State.model_validate_json(updated.model_dump_json())
            # Persist facts first: slow/broken diagnostics must never discard a known job ID.
            facts = validated.model_copy(update={"revision":state.revision+1,
                "observed_input_issues":("scope readiness diagnosis pending; not a new-work permission",)})
            if self.path.read_bytes() != original_bytes:
                raise ContractError("conflict","ledger changed outside the cooperating writer lock")
            fact_bytes = self._publish(document,facts)
            issues = self._input_issues(facts)
            diagnosed = facts.model_copy(update={"revision":facts.revision+1,"observed_input_issues":issues})
            if self.path.read_bytes() != fact_bytes:
                raise ContractError("conflict","remote fact saved, but ledger changed before diagnostic publication; inspect status")
            _ = self._publish(document,diagnosed)
            return self._status(diagnosed,issues)

    @contextmanager
    def transaction(self, expected_revision: int) -> Generator[Transaction, None, None]:
        with self._lock():
            original_bytes = self.path.read_bytes()
            document = TypeAdapter(dict[str, JsonValue]).validate_json(original_bytes)
            state = State.model_validate(document.get("production"))
            if state.revision != expected_revision:
                raise ContractError("revision", "compare-and-swap failed")
            tx = Transaction(state)
            yield tx
            # Re-parse model_copy updates at persistence boundary.
            validated = State.model_validate_json(tx.state.model_dump_json())
            from production.adapters import verify_scope
            verify_scope(validated, self.path.parent)
            self._check_scope_storage(validated)
            if self.path.read_bytes() != original_bytes:
                raise ContractError("conflict", "ledger changed outside the cooperating writer lock")
            _ = self._publish(document, validated.model_copy(update={"revision": state.revision + 1}))


@contextmanager
def _directory(path: Path) -> Generator[int, None, None]:
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        yield fd
    finally:
        os.close(fd)
