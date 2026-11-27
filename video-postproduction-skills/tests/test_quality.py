"""Current reported-semantic gates, never job-success/metadata-based playback or human authentication."""
import pytest
from conftest import require
from quality_support import ready,submission


@pytest.fixture(scope="module")
def actual(tmp_path_factory):
    return ready(tmp_path_factory.mktemp("current-quality-native"))


def test_quality_when_actual_technical_master_and_reported_fixture_checks_are_current(actual):
    store,artifact=actual
    report=submission(store,artifact)
    result=require("quality","review_artifact")(store.read_recorded(),report,store.path)
    assert result.reviews[-1].scope_passed is True
    assert result.reviews[-1].acceptance_kind=="technical_fixture"
    assert next(a for a in result.artifacts if a.id==artifact.id).adopted is False


@pytest.mark.parametrize("name",["video_playback","audio_listening"])
def test_quality_when_playback_or_listening_unverified_cannot_be_final_pass(actual,name):
    store,artifact=actual;report=submission(store,artifact,id="NO-"+name)
    checks=tuple(c.model_copy(update={"status":require("quality_models","QualityVerdict").UNVERIFIED}) if c.name==name else c for c in report.checks)
    report=report.model_copy(update={"checks":checks})
    result=require("quality","review_artifact")(store.read_recorded(),report,store.path)
    assert result.reviews[-1].scope_passed is False
    assert next(g for g in result.reviews[-1].gates if g.id=="PG4").status=="unverified"


def test_quality_when_original_required_denominator_is_reduced_cannot_pass(actual):
    store,artifact=actual;report=submission(store,artifact,id="DROPPED")
    report=report.model_copy(update={"coverage":report.coverage[:-1]})
    result=require("quality","review_artifact")(store.read_recorded(),report,store.path)
    assert result.reviews[-1].scope_passed is False
    assert result.reviews[-1].required_total==len(store.read_recorded().timelines[0].required_coverage)


def test_quality_when_reencoded_or_other_preview_pin_cannot_cover_current_final(actual):
    store,artifact=actual;report=submission(store,artifact,id="OLD-PREVIEW")
    old=artifact.pin.model_copy(update={"sha256":"a"*64})
    report=report.model_copy(update={"checks":tuple(c.model_copy(update={"artifact":old}) for c in report.checks)})
    result=require("quality","review_artifact")(store.read_recorded(),report,store.path)
    assert result.reviews[-1].scope_passed is False


def test_quality_when_generic_transaction_cannot_forge_local_gate_reports(actual):
    store,artifact=actual;report=submission(store,artifact,id="FORGED-GENERIC")
    state=store.read_recorded()
    result=require("quality","review_artifact")(state,report,store.path)
    with pytest.raises(require("errors","ContractError")):
        with store.transaction(state.revision) as tx:tx.state=result


def test_quality_when_narrow_review_commit_preserves_foreign_and_job_facts(actual):
    import json
    store,artifact=actual;report=submission(store,artifact,id="NARROW-REVIEW")
    before=store.read_recorded()
    result=store.record_review(report,before.revision)
    assert result.scope_passed is True
    assert store.read_recorded().jobs==before.jobs
    assert json.loads(store.path.read_text())["foreign"]=={"owner":"preserve"}


def test_quality_when_source_lost_retains_succeeded_history_but_no_current_adoption(actual):
    store,artifact=actual;report=submission(store,artifact,id="LOST-SOURCE")
    source=store.path.parent/"source1.mp4";data=source.read_bytes();source.unlink()
    try:
        result=require("quality","review_artifact")(store.read_recorded(),report,store.path)
        assert result.reviews[-1].scope_passed is False
        assert result.jobs[-1].phase=="succeeded"
    finally:source.write_bytes(data)
