"""Narrow verified local materialization is separate from execution facts and reported final QA."""
import pytest
from conftest import require
from test_filmcraft import rendered


def test_materialization_when_actual_native_output_is_reverified_and_registered_once(tmp_path):
    store,backend,packet,value=rendered(tmp_path)
    state=store.read_recorded();job=state.jobs[0]
    artifact=store.record_materialization(job.id,state.revision)
    known=store.read_recorded()
    assert len(known.artifacts)==1
    assert artifact.pin==value.artifact
    assert artifact.adopted is False
    assert artifact.proof is not None
    assert artifact.kind=="video"
    assert value.native_project in artifact.related
    require("materialization","verify_artifact_current")(known,artifact,store.path)
    again=store.record_materialization(job.id,known.revision)
    assert again==artifact
    assert len(store.read_recorded().artifacts)==1


def test_materialization_when_current_source_lost_does_not_adopt_output_or_lose_job(tmp_path):
    store,backend,packet,value=rendered(tmp_path)
    state=store.read_recorded();job=state.jobs[0]
    (tmp_path/"source1.mp4").unlink()
    with pytest.raises(require("errors","ContractError")):
        store.record_materialization(job.id,state.revision)
    assert store.read_recorded().jobs[0].phase=="succeeded"
    assert not store.read_recorded().artifacts


def test_materialization_when_unknown_attempt_cannot_claim_current_file(tmp_path):
    store,backend,packet,value=rendered(tmp_path)
    state=store.read_recorded()
    with pytest.raises(require("errors","ContractError"),match="job"):
        store.record_materialization("not-a-reserved-job",state.revision)
    assert not store.read_recorded().artifacts
