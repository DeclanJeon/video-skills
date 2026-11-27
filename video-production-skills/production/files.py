"""Shared safe-file and canonical prepared-packet digests."""
import hashlib
import json
from pathlib import Path

from production.models import ContractError, Pin, Prepared


def verified_file(root: Path, pin: Pin) -> Path:
    relative = Path(pin.path)
    if relative.is_absolute() or ".." in relative.parts:
        raise ContractError("path", pin.path)
    current = root.resolve()
    for part in relative.parts:
        current /= part
        if current.is_symlink():
            raise ContractError("path", "symlink reference is not managed")
    if not current.is_relative_to(root.resolve()) or not current.is_file():
        raise ContractError("path", f"missing regular file {pin.path}")
    if hashlib.sha256(current.read_bytes()).hexdigest() != pin.sha256:
        raise ContractError("hash", pin.path)
    return current


def packet_hash(packet: Prepared) -> str:
    data = packet.model_dump(mode="json", exclude={"request_hash"})
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
