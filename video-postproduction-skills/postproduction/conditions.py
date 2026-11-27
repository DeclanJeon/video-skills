"""Production conditional verdict is preserved; only current actual application plus reported side-effect review closes a ticket."""
from pathlib import Path

from production.models import Verdict

from postproduction.artifact_graph import artifact_closure
from postproduction.errors import ContractError
from postproduction.files import verified_file
from postproduction.intake_models import PostIntake, SourceRef
from postproduction.materialization import verify_artifact_current
from postproduction.quality_models import FixTicket, QualitySubmission
from postproduction.state_models import PostState


def fix_tickets(intake: PostIntake) -> tuple[FixTicket, ...]:
    result: list[FixTicket] = []
    for selected in intake.handoff.selections:
        if selected.review.verdict!=Verdict.CONDITIONAL:
            continue
        review,take = selected.review,selected.take
        source = next(s for s in intake.sources if s.source==SourceRef(clip_id=take.clip_id,take_id=take.id))
        if review.post_fix is None or review.post_receiver is None or review.conditional_policy is None:
            raise ContractError("conditional", "current conditional source has no exact accepted repair contract")
        result.append(FixTicket(id=f"FIX-{take.clip_id}-{selected.acceptance_revision}",source=source.source,
            source_asset=source.asset,source_range=source.approved_range,acceptance_revision=source.acceptance_revision,
            defects=review.defects,required_fix=review.post_fix,receiver=review.post_receiver,acceptance_policy=review.conditional_policy))
    return tuple(result)


def resolutions_ready(state: PostState, report: QualitySubmission, project: Path) -> bool:
    tickets = fix_tickets(state.intake)
    if (len({r.ticket.id for r in report.resolutions})!=len(report.resolutions)
        or {r.ticket.id for r in report.resolutions}!={t.id for t in tickets}):
        return False
    for ticket in tickets:
        resolution = next((r for r in report.resolutions if r.ticket==ticket),None)
        if (resolution is None or resolution.status!="reviewed_pass" or resolution.master!=report.artifact
            or not resolution.applied_artifacts or not resolution.video_observed or not resolution.side_effects_reviewed):
            return False
        source = next(s for s in state.intake.sources if s.source==ticket.source)
        if source.has_audio and not resolution.audio_observed:
            return False
        try:
            master = next((a for a in state.artifacts if a.id==report.artifact_id and a.pin==report.artifact),None)
            if master is None:
                return False
            verify_artifact_current(state,master,project)
            incorporated = {a.id for a in artifact_closure(state,master.id) if a.id!=master.id}
            _ = verified_file(project.parent,resolution.evidence)
            for id in resolution.applied_artifacts:
                artifact = next((a for a in state.artifacts if a.id==id),None)
                if artifact is None or id not in incorporated:
                    return False
                verify_artifact_current(state,artifact,project)
                job = next(j for j in state.jobs if j.id==artifact.job_id)
                if ticket.source not in job.packet.order.source_refs:
                    return False
        except (ContractError,OSError):
            return False
    return True
