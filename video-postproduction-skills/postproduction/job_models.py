"""Native job facts cannot by themselves certify materialization, current adoption or QA."""
from enum import StrEnum
import hashlib
from typing import Literal, Self

from pydantic import model_validator

from postproduction.common import Digest, Frame, Frozen, Nonempty, Pin
from postproduction.errors import ContractError
from postproduction.work_models import RequestPacket


class JobPhase(StrEnum):
    DISPATCHING = "dispatching"
    UNKNOWN = "unknown"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    NOT_STARTED = "not_started"
    MATERIALIZED = "materialized"


class JobReceipt(Frozen):
    phase: JobPhase
    request_hash: Digest
    job_id: Nonempty | None
    evidence: Nonempty


class PostJob(Frozen):
    id: Nonempty
    packet: RequestPacket
    request_hash: Digest
    phase: JobPhase
    job_id: Nonempty | None = None
    observations: tuple[JobReceipt, ...] = ()

    @model_validator(mode="after")
    def packet_bound(self) -> Self:
        if hashlib.sha256(self.packet.model_dump_json().encode()).hexdigest() != self.request_hash:
            raise ContractError("request", "canonical stored native packet and request digest differ")
        return self


class ArtifactRef(Frozen):
    id: Nonempty
    job_id: Nonempty
    pin: Pin
    input_fingerprint: Digest
    adopted: bool = False
    proof: Pin | None = None
    related: tuple[Pin, ...] = ()
    kind: Literal["video","rgba_sequence","audio"] = "video"


class PostStatus(Frozen):
    revision: Frame
    jobs: tuple[PostJob, ...]
    inputs_ready: bool
    issues: tuple[Nonempty, ...]
    new_work: Literal[False] = False
