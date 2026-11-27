"""Small native backend contracts; metadata, process facts and technical artifacts are separate."""
from typing import Literal, Protocol

from postproduction.common import Digest, Frozen, Nonempty, Pin, Positive, SourceRange
from postproduction.edit_models import EditAuthority
from postproduction.environment.models import Tool
from postproduction.intake_models import SourceRef
from postproduction.job_models import JobReceipt, PostJob
from postproduction.work_models import RequestPacket, WorkOrder


class CapabilitySnapshot(Frozen):
    tool: Tool
    binary_path: Nonempty
    binary_sha256: Digest
    version: Nonempty
    command_ids: tuple[Nonempty, ...]
    evidence_tier: Literal["E2"] = "E2"


class NativeMapping(Frozen):
    source: SourceRef
    native_item: Positive
    native_clip: Positive
    source_range: SourceRange
    timeline_range: SourceRange
    relation: Literal["source_media","work_context"] = "source_media"


class ArtifactMapping(Frozen):
    source: Pin
    native_item: Positive
    native_clip: Positive
    source_unit: Literal["frames","samples","still"]
    source_range: SourceRange
    timeline_range: SourceRange


class AudioMapping(Frozen):
    stem_id: Nonempty
    native_source: Positive
    native_track: Positive
    native_clip: Positive
    source_samples: SourceRange
    mix_samples: SourceRange


class JobObservation(Frozen):
    receipt: JobReceipt
    artifact: Pin | None
    native_project: Pin | None
    mapping: tuple[NativeMapping, ...]
    frame_count: Positive
    technical_verified: bool
    frames: tuple[Pin, ...] = ()
    media_kind: Literal["video","rgba_sequence","audio"] = "video"
    sample_count: Positive | None = None
    sample_rate: Positive | None = None
    channels: Positive | None = None
    audio_mapping: tuple[AudioMapping, ...] = ()
    related_assets: tuple[Pin, ...] = ()
    artifact_mapping: tuple[ArtifactMapping, ...] = ()
    evidence_kind: Literal["native_technical_fixture"] = "native_technical_fixture"


class Backend(Protocol):
    def inspect(self) -> CapabilitySnapshot: ...
    def prepare(self, order: WorkOrder, capability: CapabilitySnapshot, authority: EditAuthority) -> RequestPacket: ...
    def execute(self, packet: RequestPacket) -> JobReceipt: ...
    def observe(self, job: PostJob) -> JobObservation: ...
