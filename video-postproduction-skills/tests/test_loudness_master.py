"""Explicit actual pinned project policy must gate independently measured final native AAC, not only a helper."""
import json
import pytest
from conftest import require
from finishing_support import build
from quality_support import submission
from test_delivery import contract


def test_loudness_when_public_profile_accepts_explicit_policy_without_imposing_a_platform_preset():
    raw={"id":"local","width":160,"height":90,"fps":{"num":24,"den":1},"sample_rate":48000,"channels":2,
         "container":"mp4","video_codec":"h264","audio_codec":"aac",
         "loudness":{"integrated_lufs":-20.0,"tolerance_lu":0.5,"max_true_peak_dbtp":-1.0}}
    value=require("edit_models","DeliveryProfile").model_validate_json(json.dumps(raw))
    assert value.loudness.integrated_lufs==-20.0


@pytest.fixture(scope="module")
def mismatched(tmp_path_factory):
    root=tmp_path_factory.mktemp("native-final-loudness")
    # A real declared/pinned target deliberately incompatible with actual synthetic tone mix.
    policy={"integrated_lufs":-60.0,"tolerance_lu":0.5,"max_true_peak_dbtp":-1.0}
    store,backend,packet,value=build(root,loudness=policy)
    state=store.read_recorded();artifact=store.record_materialization(state.jobs[-1].id,state.revision)
    result=store.record_review(submission(store,artifact,id="LOUDNESS-QA"),store.read_recorded().revision)
    return store,artifact,result


def test_loudness_when_actual_final_misses_profile_cannot_pass_pg5(mismatched):
    store,artifact,result=mismatched
    assert next(g for g in result.gates if g.id=="PG5").status=="fail"
    assert result.loudness.artifact==artifact.pin and result.loudness.integrated_lufs>-50
    assert result.scope_passed is False


def test_delivery_when_actual_final_loudness_fails_cannot_publish_bundle(mismatched):
    store,artifact,result=mismatched
    c=contract(store,artifact,output="deliveries/loudness-denied")
    with pytest.raises(require("errors","ContractError")):
        require("delivery","build_delivery")(store.read_recorded(),c,store.path)
    assert not (store.path.parent/c.output).exists()


def test_loudness_when_actual_final_meets_explicit_policy_pg5_retains_measurement(tmp_path):
    policy={"integrated_lufs":-30.0,"tolerance_lu":10.0,"max_true_peak_dbtp":-1.0}
    store,backend,packet,value=build(tmp_path,loudness=policy)
    state=store.read_recorded();artifact=store.record_materialization(state.jobs[-1].id,state.revision)
    report=store.record_review(submission(store,artifact,id="MATCHING-LUFS"),store.read_recorded().revision)
    assert next(g for g in report.gates if g.id=="PG5").status=="pass"
    assert report.scope_passed is True and report.loudness.artifact==artifact.pin
    assert -40<report.loudness.integrated_lufs<-20
