"""Local receiver-scoped bundle contract; technical fixtures cannot be relabeled formal human-approved releases."""
from typing import Literal

from pydantic import field_validator

from postproduction.common import Digest, Frozen, Nonempty, Pin


class FontPermission(Frozen):
    font_sha256: Digest
    redistribute: bool = False
    receiver_present: bool = False
    evidence: Pin


class DeliveryRights(Frozen):
    status: Literal["reported_allowed","unknown","denied"]
    origin: Literal["reported","fixture"]
    evidence: Pin
    permitted: tuple[Pin, ...]


class DeliveryContract(Frozen):
    id: Nonempty
    mode: Literal["technical_fixture","reported_release"]
    kind: Literal["master_only","editable"]
    artifact_id: Nonempty
    receiver: Nonempty
    output: Nonempty
    variants: tuple[Nonempty, ...]
    include_mix: bool
    required_stems: tuple[Nonempty, ...]
    font_permissions: tuple[FontPermission, ...]
    rights: DeliveryRights

    @field_validator("output")
    @classmethod
    def local_directory(cls, value: str) -> str:
        return Pin.relative_path(value)


class DeliveryFile(Frozen):
    path: Nonempty
    sha256: Digest
    source_sha256: Digest | None
    role: Nonempty


class DeliveryBundle(Frozen):
    id: Nonempty
    mode: Literal["technical_fixture","reported_release"]
    receiver: Nonempty
    path: Nonempty
    artifact_id: Nonempty
    input_fingerprint: Digest
    manifest_sha256: Digest
    files: tuple[DeliveryFile, ...]
    formal_release: bool
    native_relink_verified: bool = False


class DeliveryRecord(Frozen):
    contract: DeliveryContract
    bundle: DeliveryBundle
