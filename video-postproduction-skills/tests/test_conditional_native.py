"""Actual native final incorporation versus an equally current unused correction. Semantics remain reported fixtures."""
import pytest
from conftest import require
from finishing_support import build
from quality_support import submission
from support import json_pin


@pytest.fixture(scope="module")
def corrected(tmp_path_factory):
    root=tmp_path_factory.mktemp("conditional-native")
    store,backend,packet,value=build(root,conditional=True)
    state=store.read_recorded()
    master=store.record_materialization(state.jobs[-1].id,state.revision)
    return store,master


def resolution(store,master,application):
    state=store.read_recorded()
    ticket=require("conditions","fix_tickets")(state.intake)[0]
    evidence=require("admission","local_pin")(json_pin(store.path.parent,"conditional-review.json",
        {"scope":"reported fixture before-after native caption and side effects, not actual human certification"}))
    record=require("quality_models","ResolutionRecord")(ticket=ticket,master=master.pin,
        applied_artifacts=(application,),status="reviewed_pass",reviewer="fixture",evidence=evidence,
        video_observed=True,audio_observed=False,side_effects_reviewed=True)
    return submission(store,master).model_copy(update={"resolutions":(record,)})


@pytest.mark.parametrize("application,want",[("TEXT",True),("UNUSED",False),("FINISH",False)])
def test_condition_when_only_actual_final_consumed_native_correction_can_resolve(corrected,application,want):
    # Given: two current real rendered captions, only TEXT incorporated in this final master.
    store,master=corrected
    state=store.read_recorded()
    artifact=next(a for a in state.artifacts if a.id.startswith(application+"-"))
    require("materialization","verify_artifact_current")(state,artifact,store.path)
    report=resolution(store,master,artifact.id)
    # When: a reported corrective application claims resolution on the exact master.
    actual=require("conditions","resolutions_ready")(state,report,store.path)
    # Then: unused application cannot resolve a defect even with unchanged current bytes.
    assert actual is want
