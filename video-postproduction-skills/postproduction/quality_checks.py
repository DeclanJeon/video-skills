"""Scope-bound reported checks/coverage; metadata and screenshots cannot become reported full playback."""
from pathlib import Path

from postproduction.common import SourceRange
from postproduction.errors import ContractError
from postproduction.files import verified_file
from postproduction.quality_models import CheckName, QualitySubmission, QualityVerdict
from postproduction.timeline_models import PostTimeline


def check_status(report: QualitySubmission, names: tuple[CheckName, ...], root: Path) -> QualityVerdict:
    statuses: list[QualityVerdict] = []
    for name in names:
        checks = tuple(c for c in report.checks if c.name==name)
        if len(checks)!=1:
            return QualityVerdict.UNVERIFIED
        check = checks[0]
        if check.artifact!=report.artifact:
            return QualityVerdict.FAIL
        allowed_origin = "reported" if report.mode=="reported" else "fixture"
        if check.origin!=allowed_origin:
            return QualityVerdict.UNVERIFIED
        if check.status==QualityVerdict.PASS:
            if check.evidence is None:
                return QualityVerdict.UNVERIFIED
            try:
                _ = verified_file(root,check.evidence)
            except (ContractError,OSError):
                return QualityVerdict.FAIL
        statuses.append(check.status)
    if QualityVerdict.FAIL in statuses:
        return QualityVerdict.FAIL
    return QualityVerdict.PASS if all(s==QualityVerdict.PASS for s in statuses) else QualityVerdict.UNVERIFIED


def playback_status(report: QualitySubmission, extent: tuple[int,int], root: Path) -> QualityVerdict:
    status = check_status(report,("video_playback","audio_listening"),root)
    if status!=QualityVerdict.PASS:
        return status
    for name,end in zip(("video_playback","audio_listening"),extent):
        check = next(c for c in report.checks if c.name==name)
        if check.covered_range!=SourceRange(start=0,end=end):
            return QualityVerdict.UNVERIFIED
    return QualityVerdict.PASS


def coverage_count(report: QualitySubmission, timeline: PostTimeline, root: Path) -> int:
    """Exact complete original denominator and mapped anchors; no dropping required events to improve percentage."""
    expected = {(e.requirement_id,e.source.clip_id,e.source.take_id):e for e in timeline.event_map}
    rows = {(r.requirement_id,r.source.clip_id,r.source.take_id):r for r in report.coverage}
    if len(expected)!=len(timeline.event_map) or len(rows)!=len(report.coverage) or rows.keys()!=expected.keys():
        return 0
    covered = {e.requirement_id for e in expected.values()} & {r.id for r in timeline.required_coverage}
    for key,event in expected.items():
        row = rows[key]
        source = next(s for s in timeline.source_registry if s.source==event.source)
        requirement = next(r for r in timeline.required_coverage if r.id==row.requirement_id)
        if (row.status!=QualityVerdict.PASS or not row.video_observed
            or (requirement.modality=="audio" and not row.audio_observed)
            or row.source_range!=event.source_anchor or row.master_range!=event.master_range
            or row.source_hash!=source.asset.sha256):
            covered.discard(row.requirement_id)
            continue
        try:
            _ = verified_file(root,row.evidence)
        except (ContractError,OSError):
            covered.discard(row.requirement_id)
    return len(covered)
