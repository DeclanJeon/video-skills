"""Typed JSON native projection path relink only; never change canonical decisions or copy an unknown private dependency."""
from dataclasses import dataclass
import os
from pathlib import Path
from typing import assert_never

from pydantic import JsonValue

from postproduction.errors import ContractError


@dataclass(frozen=True,slots=True)
class RelinkContext:
    source_parent: Path
    destination_parent: Path
    destinations: dict[Path,Path]


def referenced_paths(value: JsonValue) -> tuple[str, ...]:
    """Only native file-path fields are inputs; dialogue strings are not opportunistically opened as filenames."""
    found: list[str] = []
    match value:
        case dict():
            for key,item in value.items():
                if key in {"path","filename"} and isinstance(item,str) and item:
                    found.append(item)
                else:
                    found.extend(referenced_paths(item))
        case list():
            for item in value:
                found.extend(referenced_paths(item))
        case str() | bool() | int() | float() | None:
            pass
        case _:
            assert_never(value)
    return tuple(found)


def relink_value(value: JsonValue, context: RelinkContext) -> JsonValue:
    """Known exact paths become relative to each native file; unexpected absolute strings fail closed."""
    match value:
        case str():
            candidate = Path(value)
            resolved = candidate if candidate.is_absolute() else context.source_parent/candidate
            destination = context.destinations.get(resolved.absolute())
            if destination is not None:
                return os.path.relpath(destination,context.destination_parent)
            if candidate.is_absolute():
                raise ContractError("privacy", "native project has an unapproved/unmapped absolute dependency or private path")
            return value
        case list():
            return [relink_value(item,context) for item in value]
        case dict():
            return {key:relink_value(item,context) for key,item in value.items()}
        case bool() | int() | float() | None:
            return value
        case _:
            assert_never(value)
