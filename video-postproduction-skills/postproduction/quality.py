"""PG-E/PG0–PG6 are computed from current native bytes/lineage and scoped reported checks, never claimed by job status."""
from pathlib import Path

from pydantic import ValidationError

from postproduction.artifact_graph import artifact_closure
from postproduction.backends.base import CapabilitySnapshot, JobObservation
from postproduction.backends.film_native import digest_file
from postproduction.clock import map_frame
from postproduction.common import ClockRate
from postproduction.conditions import resolutions_ready
from postproduction.delivery_attribution import attribution_records
from postproduction.currentness import validate_current, validate_structure
from postproduction.errors import ContractError
from postproduction.files import read_model
from postproduction.materialization import verify_artifact_current
from postproduction.loudness import measure_loudness, verify_loudness
from postproduction.loudness_models import LoudnessMeasurement
from postproduction.media import probe_video
from postproduction.probe_models import Projection
from postproduction.profile_checks import verify_encoding
from postproduction.quality_checks import check_status, coverage_count, playback_status
from postproduction.quality_models import GateId, QualityGate, QualityReport, QualitySubmission, QualityVerdict
from postproduction.state_models import PostState
from postproduction.timeline import timeline_digest
from postproduction.timeline_map import FILM_CLOCK


class PlanCapability(Projection):
    capability: CapabilitySnapshot


def evaluate_submission(state: PostState, report: QualitySubmission, project: Path) -> QualityReport:
    """Current source/proof and final-file reported semantics are separate checks; fixture never adopts a real master."""
    artifact = next((a for a in state.artifacts if a.id==report.artifact_id),None)
    job = next((j for j in state.jobs if artifact is not None and j.id==artifact.job_id),None)
    if artifact is None or job is None:
        raise ContractError("artifact", "actual known materialized artifact required for review")
    timeline = next((t for t in state.timelines if t.branch==job.packet.order.branch),None)
    if timeline is None:
        raise ContractError("branch", "review refers to an archived/replaced branch; no current final adoption")
    profile = state.intake.profile
    frames = map_frame(timeline.segments[-1].timeline_range.end,FILM_CLOCK,profile.fps,rounding="exact")
    samples = map_frame(frames,profile.fps,ClockRate(num=profile.sample_rate,den=1),rounding="exact")
    root = project.parent
    gates: list[QualityGate] = []
    reported_kind = "reported" if report.mode=="reported" else "technical_fixture"
    def add(id: GateId, status: QualityVerdict, reason: str, technical: bool = False) -> None:
        gates.append(QualityGate(id=id,status=status,reason=reason,
                                evidence_kind="native_technical" if technical else reported_kind))
    header_current = (report.artifact==artifact.pin and report.input_fingerprint==artifact.input_fingerprint
                      and report.timeline_digest==timeline_digest(timeline))
    try:
        closure = artifact_closure(state,artifact.id)
        for item in closure:
            producer = next(j for j in state.jobs if j.id==item.job_id)
            cap = PlanCapability.model_validate_json(producer.packet.payload).capability
            if digest_file(Path(cap.binary_path))!=cap.binary_sha256:
                raise ContractError("environment", "actual producer binary changed since native qualification")
        add("PG-E",QualityVerdict.PASS,"actual consumed native producer binaries/technical lineage present",True)
    except (ContractError,OSError,ValidationError):
        add("PG-E",QualityVerdict.FAIL,"required current native producer environment missing/changed",True)
    try:
        validate_current(state,project)
        add("PG0",QualityVerdict.PASS,"actual full source/schema/scope/approval pins current",True)
    except (ContractError,OSError,ValidationError):
        add("PG0",QualityVerdict.FAIL,"full source/approval/current handoff input is stale or missing",True)
    try:
        validate_structure(state)
        add("PG1",QualityVerdict.PASS if header_current else QualityVerdict.FAIL,"exact current edit map/denominator/report scope",True)
    except (ContractError,OSError,ValidationError):
        add("PG1",QualityVerdict.FAIL,"current canonical edit map is invalid",True)
    add("PG2",check_status(report,("picture",),root),"final-picture reported acting/event/order/pacing scope")
    add("PG3",check_status(report,("composite","color","sound","captions"),root),"final combined field results reported, not metadata-only PASS")
    add("PG4",playback_status(report,(frames,samples),root),"whole exact final file reported playback/listening, not contact sheet or earlier preview")
    loudness: LoudnessMeasurement | None = None
    try:
        verify_artifact_current(state,artifact,project)
        if artifact.proof is None:
            raise ContractError("proof", "native master proof missing")
        native = read_model(root,artifact.proof,JobObservation)
        verify_encoding(root,artifact.pin,profile)
        facts = probe_video(root,artifact.pin)
        if (facts.width,facts.height,facts.rate,facts.frame_count,facts.cfr,facts.has_audio,native.technical_verified)!=(
            profile.width,profile.height,profile.fps,frames,True,True,True):
            raise ContractError("master", "actual final master full decode differs from required profile")
        if profile.loudness is not None:
            loudness = measure_loudness(root,artifact.pin)
            verify_loudness(loudness,profile.loudness)
        add("PG5",QualityVerdict.PASS,"actual final decode/current lineage and explicitly requested loudness policy",True)
    except (ContractError,OSError,ValidationError):
        add("PG5",QualityVerdict.FAIL,"actual master/source/native proof or final technical validation failed",True)
    covered = coverage_count(report,timeline,root)
    total = len(timeline.required_coverage)
    try:
        fixed = resolutions_ready(state,report,project)
    except (ContractError,OSError,ValidationError):
        fixed = False
    final = check_status(report,("rights","adoption"),root)
    try:
        _ = attribution_records(state,(artifact.id,),root)
    except (ContractError,OSError,ValidationError):
        final = QualityVerdict.FAIL
    prior = all(g.status==QualityVerdict.PASS for g in gates)
    status = QualityVerdict.PASS if header_current and prior and covered==total and fixed and final==QualityVerdict.PASS else QualityVerdict.UNVERIFIED
    if covered!=total or not header_current or final==QualityVerdict.FAIL:
        status = QualityVerdict.FAIL
    add("PG6",status,"complete original coverage/current fix closure/final-file reported adoption/rights; issuer not authenticated")
    passed = all(g.status==QualityVerdict.PASS for g in gates)
    kind = ("reported_not_authenticated" if report.mode=="reported" else "technical_fixture") if passed else "unverified"
    result = QualityReport(submission=report,gates=tuple(gates),required_total=total,covered_total=covered,
                           scope_passed=passed,acceptance_kind=kind,loudness=loudness)
    return result


def review_artifact(state: PostState, report: QualitySubmission, project: Path) -> PostState:
    """Append only a newly evaluated review; delivery may reevaluate an old submission without rewriting history."""
    if any(r.submission.id==report.id for r in state.reviews):
        raise ContractError("review", "immutable review identity already exists; submit a new review revision")
    result = evaluate_submission(state,report,project)
    artifacts = tuple(a.model_copy(update={"adopted":result.scope_passed and report.mode=="reported"})
                      if a.id==report.artifact_id else a for a in state.artifacts)
    return state.model_copy(update={"reviews":(*state.reviews,result),"artifacts":artifacts})
