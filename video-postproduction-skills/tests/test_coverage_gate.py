"""Pure mapped-event coverage denominator: every required occurrence, not any passing occurrence."""
from conftest import require
from test_ledger import built,project,prepare
from support import json_pin


def test_coverage_when_one_of_multiple_required_occurrences_is_hidden_cannot_count_requirement_complete(project):
    path,store,state,production=prepare(project)
    timeline=state.timelines[0];first=timeline.event_map[0]
    another=timeline.event_map[1].model_copy(update={"requirement_id":first.requirement_id})
    timeline=timeline.model_copy(update={"event_map":(*timeline.event_map,another)})
    evidence=require("admission","local_pin")(json_pin(path.parent,"coverage-evidence.json",{"scope":"pure reported coverage fixture"}))
    rows=[]
    for event in timeline.event_map:
        cap=next(s for s in state.intake.sources if s.source==event.source)
        rows.append(require("quality_models","ReportedCoverage")(requirement_id=event.requirement_id,status=require("quality_models","QualityVerdict").PASS,
            source=event.source,source_hash=cap.asset.sha256,source_range=event.source_anchor,master_range=event.master_range,
            video_observed=event is not another,audio_observed=False,evidence=evidence))
    report=require("quality_models","QualitySubmission")(id="COVERAGE",mode="technical_fixture",artifact_id="pure-mapping",artifact=state.intake.sources[0].asset,
        receiver="fixture",input_fingerprint="a"*64,timeline_digest="b"*64,checks=(),coverage=tuple(rows))
    actual=require("quality_checks","coverage_count")(report,timeline,path.parent)
    assert actual==len(timeline.required_coverage)-1
