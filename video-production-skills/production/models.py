"""Immutable boundary contracts. Evidence is reported, never inferred by a model."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Annotated, ClassVar, Literal, NewType, override

from pydantic import BaseModel, ConfigDict, Field, model_validator

ClipId = NewType("ClipId", str)
AttemptId = NewType("AttemptId", str)
Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
Nonempty = Annotated[str, Field(min_length=1)]
Positive = Annotated[int, Field(gt=0)]


@dataclass
class ContractError(Exception):
    """Typed exception; mutable because contextlib must attach __traceback__."""
    code: str
    detail: str

    @override
    def __str__(self) -> str:
        return f"{self.code}: {self.detail}"


class Frozen(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="forbid", allow_inf_nan=False)


class Pin(Frozen):
    id: Nonempty
    version: Nonempty
    sha256: Digest
    path: Nonempty


class SourceRange(Frozen):
    start: Annotated[int, Field(ge=0)]
    end: Positive

    @model_validator(mode="after")
    def ordered(self) -> SourceRange:
        if self.end <= self.start:
            raise ContractError("range", "end must exceed start")
        return self


class Requirement(Frozen):
    id: Nonempty
    shot: Nonempty
    panels: tuple[str, ...]
    modality: str = "video"
    locator: Nonempty


class Reference(Frozen):
    source_clip: ClipId
    role: Nonempty
    modality: Nonempty
    imports: tuple[str, ...]
    excludes: tuple[str, ...] = ()
    required: bool = True
    omission_evidence: str | None = None


class Clip(Frozen):
    id: ClipId
    shots: tuple[str, ...]
    requirements: tuple[str, ...]
    duration_s: Annotated[float, Field(gt=0)]
    prompt: Pin
    assets: tuple[Pin, ...] = ()
    dependencies: tuple[Pin, ...] = ()
    references: tuple[Reference, ...] = ()
    audio_required: bool = False


class JoinPlan(Frozen):
    id: Nonempty
    before: ClipId
    after: ClipId
    relation: Nonempty
    reveal_order: tuple[str, ...]
    allowed_changes: tuple[str, ...] = ()
    locator: Nonempty


class Batch(Frozen):
    id: Nonempty
    revision: Positive = 1
    scope_revision: Nonempty
    coverage: tuple[Requirement, ...]
    clips: tuple[Clip, ...]
    edit_order: tuple[ClipId, ...]
    joins: tuple[JoinPlan, ...] = ()


class Playback(Frozen):
    asset_hash: Digest
    source_range: SourceRange
    reviewer: Nonempty
    evidence: Nonempty
    video_watched: bool
    audio_listened: bool = False


class Take(Frozen):
    id: Nonempty
    clip_id: ClipId
    attempt_id: AttemptId | None
    origin: Literal["generated", "approved_reuse"] = "generated"
    asset: Pin
    frame_count: Positive
    fps: Annotated[float, Field(gt=0)]
    cfr: bool = True
    pts_evidence: str | None = None
    width: Positive
    height: Positive
    has_audio: bool
    decode_evidence: Nonempty
    source_range: SourceRange
    range_revision: Positive = 1
    fingerprint: Digest

    @model_validator(mode="after")
    def within_source(self) -> Take:
        if (self.origin == "generated") != (self.attempt_id is not None):
            raise ContractError("attempt", "generated takes need a real attempt; supplied takes must not invent one")
        if self.source_range.end > self.frame_count:
            raise ContractError("range", "selected range exceeds source")
        if not self.cfr and not self.pts_evidence:
            raise ContractError("timebase", "VFR needs explicit PTS/conform evidence")
        return self


class Verdict(StrEnum):
    ACCEPTED = "accepted"
    CONDITIONAL = "conditional"
    REJECTED = "rejected"


class Review(Frozen):
    verdict: Verdict
    fulfilled: tuple[str, ...]
    playback: Playback
    defects: tuple[str, ...] = ()
    post_fix: str | None = None
    post_receiver: str | None = None
    conditional_policy: str | None = None


class Selection(Frozen):
    take: Take
    review: Review
    reviewed_fingerprint: Digest
    approval: Authority
    acceptance_revision: Positive
    valid: bool = True


class Phase(StrEnum):
    SUBMITTING = "submitting"
    UNKNOWN = "unknown"
    SUBMITTED = "submitted"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "remote_failed"
    CANCELLED = "cancelled"
    NOT_RECEIVED = "not_received"
    DOWNLOADED = "downloaded"


class Capability(Frozen):
    account: Nonempty
    model: Nonempty
    transport: Nonempty
    mode: Nonempty
    roles: tuple[str, ...]
    modalities: tuple[str, ...]
    max_references: Annotated[int, Field(ge=0)]
    max_active: Positive
    durations: tuple[float, ...]
    width: Positive
    height: Positive
    audio: bool
    evidence: Pin
    observed_mode: Nonempty


class ApprovedConfig(Frozen):
    clip_id: ClipId
    scope_revision: Nonempty
    coverage_hash: Digest
    clip_hash: Digest
    duration_s: Annotated[float, Field(gt=0)]
    width: Positive
    height: Positive
    audio_requested: bool
    reuse_source: Pin | None = None
    reuse_range: SourceRange | None = None


class Authority(Frozen):
    id: Nonempty
    clips: tuple[ClipId, ...]
    allowed_hashes: tuple[str, ...]
    configurations: tuple[ApprovedConfig, ...]
    account: Nonempty
    model: Nonempty
    transport: Nonempty
    mode: Nonempty
    max_attempts: Positive = 1
    max_active: Positive = 1
    upload: bool = False
    generation: bool = False
    reuse: bool = False
    evidence: Pin


class Binding(Frozen):
    pin: Pin
    source_clip: ClipId | None = None
    source_range: SourceRange | None = None
    range_revision: int | None = None
    acceptance_revision: int | None = None
    role: Nonempty
    modality: Nonempty
    imports: tuple[str, ...]
    excludes: tuple[str, ...] = ()
    native_asset_id: Nonempty
    native_reference_id: Nonempty
    ready: bool


class Prepared(Frozen):
    clip_id: ClipId
    fingerprint: Digest
    capability: Capability
    authority: Authority
    bindings: tuple[Binding, ...]
    prompt: Pin
    prompt_text: Nonempty
    audio_requested: bool
    duration_s: Annotated[float, Field(gt=0)]
    request_hash: Digest


class Attempt(Frozen):
    id: AttemptId
    prepared: Prepared
    phase: Phase
    job_id: str | None = None
    terminal_evidence: str | None = None


class Receipt(Frozen):
    phase: Phase
    job_id: str | None = None
    evidence: Nonempty
    request_hash: Digest


class JoinReview(Frozen):
    join_id: Nonempty
    before_take: Nonempty
    after_take: Nonempty
    before_revision: Positive
    after_revision: Positive
    before_range_revision: Positive
    after_range_revision: Positive
    reveal_order: tuple[str, ...]
    passed: bool
    evidence: Nonempty
    continuous_playback: bool
    observed_changes: tuple[str, ...] = ()


class ReviewRender(Frozen):
    artifact: Pin
    manifest: Pin
    selection_hash: Digest


class FlowReview(Frozen):
    review_render: ReviewRender
    selection_hash: Digest
    clip_order: tuple[ClipId, ...]
    passed: bool
    evidence: Nonempty
    continuous_playback: bool
    audio_listened: bool


class ScopeChangeRecord(Frozen):
    evidence: Pin
    old_source: Pin
    new_source: Pin
    old_scope_revision: Nonempty
    new_scope_revision: Nonempty
    removed: tuple[str, ...]
    added: tuple[str, ...]
    changed: tuple[str, ...]
    asset_changes: tuple[str, ...]


class State(Frozen):
    revision: Annotated[int, Field(ge=0)] = 0
    batch: Batch
    approved_coverage: tuple[Requirement, ...]
    coverage_source: Pin
    attempts: tuple[Attempt, ...] = ()
    selections: tuple[Selection, ...] = ()
    history: tuple[Selection, ...] = ()
    join_reviews: tuple[JoinReview, ...] = ()
    change_evidence: tuple[str, ...] = ()
    scope_history: tuple[ScopeChangeRecord, ...] = ()
    observed_input_issues: tuple[str, ...] = ()


class Handoff(Frozen):
    batch_id: Nonempty
    scope_revision: Nonempty
    selection_hash: Digest
    selections: tuple[Selection, ...]
    joins: tuple[JoinReview, ...]
    flow: FlowReview
    receiver: Nonempty
    rights_evidence: Nonempty
    handles: tuple[tuple[str, int, int], ...]
    handle_policy: str = "No reviewed exterior handles supplied; zero certified. Raw margins remain available for separate post review."
