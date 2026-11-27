"""Pure current conditional ticket contract; scheduled effects/unknown tickets are not actual resolved fixes."""
from production.models import Verdict
from conftest import require
from test_ledger import built,project,prepare
from support import json_pin


def conditional(state):
    selected=state.intake.handoff.selections[0]
    review=selected.review.model_copy(update={"verdict":Verdict.CONDITIONAL,"defects":("lighting",),"post_fix":"adjust current lighting","post_receiver":state.intake.handoff.receiver,"conditional_policy":"verify before/after and effects on current master"})
    selected=selected.model_copy(update={"review":review})
    handoff=state.intake.handoff.model_copy(update={"selections":(selected,*state.intake.handoff.selections[1:])})
    return state.model_copy(update={"intake":state.intake.model_copy(update={"handoff":handoff})})


def packet(path,state,ticket):
    evidence=require("admission","local_pin")(json_pin(path.parent,"resolution-evidence.json",{"scope":"pure conditional fixture; no actual resolved work"}))
    resolution=require("quality_models","ResolutionRecord")(ticket=ticket,master=state.intake.sources[0].asset,
        applied_artifacts=("scheduled-work",),status="scheduled",reviewer="fixture",evidence=evidence,
        video_observed=True,audio_observed=False,side_effects_reviewed=True)
    return require("quality_models","QualitySubmission")(id="FIX-CLAIM",mode="technical_fixture",artifact_id="not-an-adopted-master",
        artifact=state.intake.sources[0].asset,receiver="fixture",input_fingerprint="a"*64,timeline_digest="b"*64,
        checks=(),coverage=(),resolutions=(resolution,))


def test_condition_when_scheduled_native_effect_does_not_close_current_ticket(project):
    path,store,state,production=prepare(project);state=conditional(state)
    ticket=require("conditions","fix_tickets")(state.intake)[0]
    report=packet(path,state,ticket)
    assert require("conditions","resolutions_ready")(state,report,path) is False


def test_condition_when_unknown_or_old_ticket_cannot_be_laundered_as_resolution(project):
    path,store,state,production=prepare(project)
    ticket=require("conditions","fix_tickets")(conditional(state).intake)[0]
    report=packet(path,state,ticket)
    assert require("conditions","resolutions_ready")(state,report,path) is False
