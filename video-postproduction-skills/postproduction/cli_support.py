"""Strict local CLI boundaries; file/help parsing never grants install/upload authority."""
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel
import typer

from postproduction.common import Frozen
from postproduction.errors import ContractError
from postproduction.files import confined_path
from postproduction.ledger import PostStore

M = TypeVar("M",bound=BaseModel)


class CliError(Frozen):
    error: str
    stage: str


def emit(value: BaseModel) -> None:
    typer.echo(value.model_dump_json(indent=2))


def input_model(path: Path, root: Path, model: type[M]) -> M:
    absolute = path.absolute() if path.is_absolute() else root/path
    try:
        relative = absolute.relative_to(root.absolute()).as_posix()
    except ValueError as exc:
        raise ContractError("path", "CLI input must be inside the selected project/plan root") from exc
    file = confined_path(root,relative)
    return model.model_validate_json(file.read_bytes())


def store_for(project: Path) -> PostStore:
    return PostStore(project)
