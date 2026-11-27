"""Physical pins are checked independently of reported QA and metadata."""
import hashlib
from pathlib import Path

from pydantic import BaseModel, ValidationError

from postproduction.common import Pin
from postproduction.errors import ContractError


def confined_path(root: Path, relative: str) -> Path:
    """Check every component, including internal symlinks, before any file operation."""
    rel = Path(relative)
    if rel.is_absolute() or ".." in rel.parts or "\\" in relative or "\0" in relative:
        raise ContractError("path", "path must be project-relative")
    if root.is_symlink():
        raise ContractError("path", "project root is a symlink")
    path = root.resolve()
    for part in rel.parts:
        path /= part
        if path.is_symlink():
            raise ContractError("path", "symlink input is not an adopted source")
    if not path.is_relative_to(root.resolve()):
        raise ContractError("path", "input escapes project")
    return path


def verified_file(root: Path, pin: Pin) -> Path:
    """Reject symlink traversal and byte drift before adopting an input."""
    path = confined_path(root, pin.path)
    if not path.is_file():
        raise ContractError("file", f"not a regular input file: {pin.id}")
    try:
        with path.open("rb") as stream:
            actual = hashlib.file_digest(stream, "sha256").hexdigest()
    except OSError as exc:
        raise ContractError("file", f"missing or unreadable input {pin.id}") from exc
    if actual != pin.sha256:
        raise ContractError("hash", f"input changed: {pin.id}")
    return path


def read_model[T: BaseModel](root: Path, pin: Pin, model: type[T]) -> T:
    """Parse a physically verified record, translating boundary parse failures."""
    path = verified_file(root, pin)
    try:
        return model.model_validate_json(path.read_bytes())
    except (OSError, ValidationError) as exc:
        raise ContractError("parse", f"invalid {model.__name__} input") from exc
