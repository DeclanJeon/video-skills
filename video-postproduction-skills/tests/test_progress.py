"""Separate real technical, reported full QA and delivery denominators; reservation is not quality completion."""
from conftest import require
from test_ledger import built,project,prepare
from test_revisions import order_for


def setup(project):
    path,store,state,production=prepare(project);store.initialize(state)
    order=order_for(state)
    packet=require("work_models","RequestPacket")(order=order,input_fingerprint=require("revisions","work_fingerprint")(state,order),payload="unexecuted progress fixture")
    store.record_reservation(packet,0)
    return path,store


def test_progress_when_reserved_only_has_distinct_zero_completion_denominators(project):
    path,store=setup(project)
    progress=require("progress","project_progress")(store.read_recorded(),path)
    branch=progress.branches[0]
    assert branch.work.total==1 and branch.work.complete==0
    assert branch.coverage.total==3 and branch.coverage.complete==0
    assert branch.final_qa.complete==0
    assert branch.formal_deliveries==0


def test_progress_when_native_success_receipt_without_artifact_or_playback_is_not_quality(project):
    path,store=setup(project);state=store.read_recorded();job=state.jobs[0]
    receipt=require("job_models","JobReceipt")(phase=require("job_models","JobPhase").SUCCEEDED,
        request_hash=job.request_hash,job_id="contract-progress-process",evidence="reported process receipt, not verified native artifact")
    store.record_observation(job.id,receipt,state.revision)
    branch=require("progress","project_progress")(store.read_recorded(),path).branches[0]
    assert branch.work.complete==0 and branch.final_qa.complete==0
    assert branch.historical_succeeded==1


def test_progress_when_missing_source_cannot_shrink_original_coverage_denominator(project):
    path,store=setup(project);(path.parent/"source3.mp4").unlink()
    branch=require("progress","project_progress")(store.read_recorded(),path).branches[0]
    assert branch.coverage.total==3 and branch.coverage.complete==0
    assert branch.final_qa.complete==0
