"""Recompute current meaningful completion from actual sources/outputs/QA/package hashes, not mutable job counts."""
import hashlib
from pathlib import Path

from pydantic import ValidationError

from postproduction.conditions import fix_tickets, resolutions_ready
from postproduction.errors import ContractError
from postproduction.delivery_scope import preflight
from postproduction.files import confined_path
from postproduction.job_models import JobPhase
from postproduction.materialization import verify_artifact_current
from postproduction.progress_models import BranchProgress, Completion, ProjectProgress
from postproduction.quality import evaluate_submission
from postproduction.state_models import PostState


def project_progress(state: PostState, project: Path) -> ProjectProgress:
    branches: list[BranchProgress] = []
    for timeline in state.timelines:
        orders = tuple(o for o in state.orders if o.branch==timeline.branch)
        jobs = tuple(j for j in state.jobs if j.packet.order.branch==timeline.branch)
        current_orders: set[str] = set()
        for artifact in state.artifacts:
            job = next((j for j in jobs if j.id==artifact.job_id),None)
            if job is None:
                continue
            try:
                verify_artifact_current(state,artifact,project)
                current_orders.add(job.packet.order.id)
            except (ContractError,OSError,ValidationError):
                continue
        reports = tuple(r for r in state.reviews if any(j.id==a.job_id and j.packet.order.branch==timeline.branch
            for a in state.artifacts if a.id==r.submission.artifact_id for j in jobs))
        covered,formal_qa,fixture_qa,fixed = 0,0,0,0
        latest = reports[-1] if reports else None
        if latest is not None:
            try:
                current = evaluate_submission(state,latest.submission,project)
                if current.scope_passed:
                    covered = current.covered_total
                    formal_qa = int(current.acceptance_kind=="reported_not_authenticated")
                    fixture_qa = int(current.acceptance_kind=="technical_fixture")
                    fixed = len(fix_tickets(state.intake)) if resolutions_ready(state,latest.submission,project) else 0
            except (ContractError,OSError,ValidationError):
                pass
        formal_deliveries,fixture_deliveries = 0,0
        for record in state.deliveries:
            if not any(a.id==record.bundle.artifact_id and a.job_id in {j.id for j in jobs} for a in state.artifacts):
                continue
            report = next((r for r in reversed(reports) if r.submission.artifact_id==record.bundle.artifact_id),None)
            if report is None:
                continue
            try:
                _ = preflight(state,record.contract,project)
                for variant_id in record.contract.variants:
                    _ = preflight(state,record.contract.model_copy(update={"artifact_id":variant_id}),project)
                path = confined_path(project.parent,record.bundle.path)
                if hashlib.sha256((path/"manifest.json").read_bytes()).hexdigest()!=record.bundle.manifest_sha256:
                    continue
                if any(hashlib.sha256((path/f.path).read_bytes()).hexdigest()!=f.sha256 for f in record.bundle.files):
                    continue
                formal_deliveries += int(record.bundle.formal_release)
                fixture_deliveries += int(not record.bundle.formal_release)
            except (ContractError,OSError,ValidationError):
                continue
        branches.append(BranchProgress(branch=timeline.branch,work=Completion(complete=len(current_orders),total=len(orders)),
            coverage=Completion(complete=covered,total=len(timeline.required_coverage)),
            fixes=Completion(complete=fixed,total=len(fix_tickets(state.intake))),
            final_qa=Completion(complete=formal_qa,total=1),technical_fixture_qa=Completion(complete=fixture_qa,total=1),
            historical_succeeded=sum(j.phase==JobPhase.SUCCEEDED for j in jobs),
            formal_deliveries=formal_deliveries,technical_fixture_deliveries=fixture_deliveries))
    return ProjectProgress(revision=state.revision,branches=tuple(branches))
