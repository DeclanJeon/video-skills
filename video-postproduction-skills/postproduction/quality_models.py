"""Reported final semantic checks, source coverage and computed gates; no installer consent or human-authentication claim."""
from enum import StrEnum
from typing import Literal

from pydantic import Field

from postproduction.common import Digest, Frozen, Nonempty, Pin, Positive, SourceRange
from postproduction.intake_models import SourceRef
from postproduction.loudness_models import LoudnessMeasurement

type GateId = Literal["PG-E","PG0","PG1","PG2","PG3","PG4","PG5","PG6"]
type CheckName = Literal["picture","composite","color","sound","captions","video_playback","audio_listening","rights","adoption"]


class QualityVerdict(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    UNVERIFIED = "unverified"
    NOT_APPLICABLE = "not_applicable"


class SemanticCheck(Frozen):
    name: CheckName
    status: QualityVerdict
    origin: Literal["reported","fixture","metadata"]
    artifact: Pin
    evidence: Pin | None = None
    covered_range: SourceRange | None = Field(alias="range",default=None)
    reason: Nonempty


class ReportedCoverage(Frozen):
    requirement_id: Nonempty
    status: QualityVerdict
    source: SourceRef
    source_hash: Digest
    source_range: SourceRange
    master_range: SourceRange
    video_observed: bool
    audio_observed: bool
    evidence: Pin


class FixTicket(Frozen):
    id: Nonempty
    source: SourceRef
    source_asset: Pin
    source_range: SourceRange
    acceptance_revision: Positive
    defects: tuple[Nonempty, ...]
    required_fix: Nonempty
    receiver: Nonempty
    acceptance_policy: Nonempty


class ResolutionRecord(Frozen):
    ticket: FixTicket
    master: Pin
    applied_artifacts: tuple[Nonempty, ...]
    status: Literal["scheduled","applied","reviewed_pass","failed"]
    reviewer: Nonempty
    evidence: Pin
    video_observed: bool
    audio_observed: bool
    side_effects_reviewed: bool


class QualitySubmission(Frozen):
    id: Nonempty
    mode: Literal["reported","technical_fixture"]
    artifact_id: Nonempty
    artifact: Pin
    receiver: Nonempty
    input_fingerprint: Digest
    timeline_digest: Digest
    checks: tuple[SemanticCheck, ...]
    coverage: tuple[ReportedCoverage, ...]
    resolutions: tuple[ResolutionRecord, ...] = ()


class QualityGate(Frozen):
    id: GateId
    status: QualityVerdict
    reason: Nonempty
    evidence_kind: Literal["native_technical","metadata","reported","technical_fixture"]


class QualityReport(Frozen):
    submission: QualitySubmission
    gates: tuple[QualityGate, ...]
    required_total: int
    covered_total: int
    scope_passed: bool
    acceptance_kind: Literal["reported_not_authenticated","technical_fixture","unverified"]
    loudness: LoudnessMeasurement | None = None
