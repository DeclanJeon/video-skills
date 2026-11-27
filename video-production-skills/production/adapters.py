"""Read-only seams for existing ledger, storyboard and prepared-call formats.

Nothing here calls a provider. Native IDs and receipts are observed evidence
supplied by an operator; they are not authenticated by this offline adapter.
"""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
from typing import ClassVar, Literal, assert_never

from pydantic import BaseModel, ConfigDict, JsonValue

from production.files import verified_file
from production.models import ContractError, Pin, Prepared


class Upstream(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")


class LegacyVersion(Upstream):
    version: int
    path: str
    sha256: str
    consumes: tuple[str, ...]
    status: str


class LegacyLedger(Upstream):
    schema_version: Literal[1]
    artifacts: dict[str, tuple[LegacyVersion, ...]]


def resolve_legacy(path: Path, ref: str) -> Pin:
    ledger = LegacyLedger.model_validate_json(path.read_bytes())
    match = re.fullmatch(r"([A-Z][A-Z0-9-]*)@v([1-9][0-9]*)", ref)
    if match is None:
        raise ContractError("pin", "explicit legacy ID@vN required")
    aid, version = match.groups()
    history = ledger.artifacts.get(aid, ())
    item = next((x for x in history if x.version == int(version)), None)
    if item is None or item.status != "current" or not history or history[-1] != item:
        raise ContractError("current", "legacy artifact is missing/stale/superseded")
    pin = Pin(id=aid, version=str(item.version), sha256=item.sha256, path=item.path)
    _ = verified_file(path.parent, pin)
    return pin


from production.upstream import (
    derive_coverage as derive_coverage,
    derive_asset_uses as derive_asset_uses,
    export_coverage as export_coverage,
    verify_scope as verify_scope,
)


class NativeCall(Upstream):
    format: Literal["sequence-generation-call/1"]
    tool: str
    arguments: dict[str, JsonValue]
    call_sha256: str
    submitted: Literal[False]


@dataclass(frozen=True, slots=True)
class NativeAudit:
    submitted: bool
    reference_ids: tuple[str, ...]
    call_sha256: str
    limits: str = "Local supplied-call comparison only, no provider authenticity/conditioning/quality proof."


def pointer(document: JsonValue, path: str) -> JsonValue:
    if not path.startswith("/"):
        raise ContractError("pointer", "absolute JSON pointer required")
    current = document
    for token in path[1:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        match current:
            case dict() as mapping:
                if token not in mapping:
                    raise ContractError("pointer", path)
                current = mapping[token]
            case list() as values:
                if not token.isdigit() or int(token) >= len(values):
                    raise ContractError("pointer", path)
                current = values[int(token)]
            case str() | int() | float() | bool() | None:
                raise ContractError("pointer", path)
            case unreachable:
                assert_never(unreachable)
    return current


def audit_native(packet: Prepared, native: JsonValue, tool: str,
                 model_pointer: str, prompt_pointer: str,
                 references_pointer: str, duration_pointer: str) -> NativeAudit:
    from production.files import packet_hash
    call = NativeCall.model_validate(native)
    digest = hashlib.sha256(json.dumps({"tool": call.tool, "arguments": call.arguments}, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if digest != call.call_sha256 or packet_hash(packet) != packet.request_hash:
        raise ContractError("request", "native/prepared request digest changed")
    if call.tool != tool or pointer(call.arguments, model_pointer) != packet.capability.model:
        raise ContractError("model", "native tool/model differs from checked contract")
    if pointer(call.arguments, prompt_pointer) != packet.prompt_text or pointer(call.arguments, duration_pointer) != packet.duration_s:
        raise ContractError("request", "native prompt/duration differs")
    refs = tuple(b.native_reference_id for b in packet.bindings)
    if pointer(call.arguments, references_pointer) != list(refs):
        raise ContractError("selection", "actual selected references differ from bound receipts")
    return NativeAudit(submitted=False, reference_ids=refs, call_sha256=digest)
