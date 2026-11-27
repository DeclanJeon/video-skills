"""Source→master coverage is not inferred from a retained fraction of an unknown event."""
import json
import shutil
import pytest
from conftest import require
from support import fixture,modify_authority,pin


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    root=tmp_path_factory.mktemp("timeline-source");fixture(root);return root


def prepared(root,built,allowed=(),anchors=False):
    shutil.copytree(built,root,dirs_exist_ok=True)
    request=json.loads((root/"request.json").read_text())
    modify_authority(root,request,allowed_changes=list(allowed))
    if anchors:
        state=json.loads((root/"snapshot.json").read_text())
        evidence=pin(root,"event-observations.txt","Synthetic source observation: each required event at frames16:32. Not master perceptual QA.")
        request["anchors"]=[{"requirement_id":s["review"]["fulfilled"][0],
            "source":{"clip_id":s["take"]["clip_id"],"take_id":s["take"]["id"]},
            "source_range":{"start":16,"end":32},"asset_hash":s["take"]["asset"]["sha256"],
            "range_revision":s["take"]["range_revision"],"acceptance_revision":s["acceptance_revision"],
            "observer":"synthetic-source-observer","evidence":evidence.model_dump(),"video_observed":True}
            for s in state["selections"]]
        (root/"request.json").write_text(json.dumps(request))
    return require("intake","load_intake")(root,root/"request.json")


def proposal(intake,order=(0,1,2),trim=None,overlap=0,branch="main"):
    Cut=require("timeline_models","CutSpec")
    cuts=[]
    for pos,index in enumerate(order):
        s=intake.sources[index]
        sr=s.approved_range if trim is None or index!=0 else require("models","SourceRange")(start=trim[0],end=trim[1])
        cuts.append(Cut(id=f"S{index+1}",source=s.source,source_range=sr,overlap_frames=overlap if pos==1 else 0))
    return require("timeline_models","EditProposal")(branch=branch,cuts=tuple(cuts))


def test_initial_timeline_when_no_precise_event_anchors(tmp_path,built):
    intake=prepared(tmp_path,built)
    timeline=require("timeline","build_timeline")(intake)
    assert tuple(s.source.clip_id for s in timeline.segments)==("C1","C2","C3")
    assert timeline.segments[-1].timeline_range.end==1524096000000
    assert timeline.required_coverage==intake.snapshot.approved_coverage
    assert all(e.anchor_mode=="reviewed_full_source" for e in timeline.event_map)
    assert all(not e.post_verified for e in timeline.event_map)


def test_trim_when_authorized_but_no_observed_anchor(tmp_path,built):
    intake=prepared(tmp_path,built,allowed=("trim",))
    with pytest.raises(require("errors","ContractError"),match="anchor"):
        require("timeline","build_timeline")(intake,proposal(intake,trim=(0,47)))


def test_trim_when_observed_anchor_exists_but_authority_does_not(tmp_path,built):
    intake=prepared(tmp_path,built,anchors=True)
    with pytest.raises(require("errors","ContractError"),match="authority"):
        require("timeline","build_timeline")(intake,proposal(intake,trim=(10,40)))


def test_trim_when_exact_anchor_survives_and_scope_is_approved(tmp_path,built):
    intake=prepared(tmp_path,built,allowed=("trim",),anchors=True)
    result=require("timeline","build_timeline")(intake,proposal(intake,trim=(10,40)))
    event=next(e for e in result.event_map if e.requirement_id=="R1")
    assert (event.master_range.start,event.master_range.end)==(63504000000,232848000000)
    assert result.segments[-1].timeline_range.end==1333584000000
    assert len(result.required_coverage)==3
    assert event.anchor_mode=="observed_anchor"


@pytest.mark.parametrize("trim",[(0,49),(17,48)])
def test_trim_when_outside_reviewed_handles_or_cutting_required_event(tmp_path,built,trim):
    intake=prepared(tmp_path,built,allowed=("trim",),anchors=True)
    with pytest.raises(require("errors","ContractError")):
        require("timeline","build_timeline")(intake,proposal(intake,trim=trim))


def test_coverage_when_clip_with_required_event_is_omitted(tmp_path,built):
    intake=prepared(tmp_path,built)
    with pytest.raises(require("errors","ContractError"),match="coverage"):
        require("timeline","build_timeline")(intake,proposal(intake,order=(0,1)))


@pytest.mark.parametrize("allowed",[(),("reorder",)])
def test_reorder_when_it_is_or_is_not_explicitly_authorized(tmp_path,built,allowed):
    intake=prepared(tmp_path,built,allowed=allowed)
    if not allowed:
        with pytest.raises(require("errors","ContractError"),match="authority"):
            require("timeline","build_timeline")(intake,proposal(intake,order=(2,0,1)))
    else:
        result=require("timeline","build_timeline")(intake,proposal(intake,order=(2,0,1)))
        assert tuple(s.source.clip_id for s in result.segments)==("C3","C1","C2")
        assert len(result.required_coverage)==3
        assert result.needs_master_review is True


def test_non_linear_when_already_approved_upstream_order_is_not_corrected(tmp_path):
    fixture(tmp_path,order=(3,1,2))
    intake=require("intake","load_intake")(tmp_path,tmp_path/"request.json")
    result=require("timeline","build_timeline")(intake)
    assert tuple(s.source.clip_id for s in result.segments)==("C3","C1","C2")
    assert result.original_joins[0].reveal_order==("R3","R1")


@pytest.mark.parametrize("anchors,allowed",[(False,("overlap",)),(True,())])
def test_overlap_when_anchor_or_permission_is_missing(tmp_path,built,anchors,allowed):
    intake=prepared(tmp_path,built,allowed=allowed,anchors=anchors)
    with pytest.raises(require("errors","ContractError")):
        require("timeline","build_timeline")(intake,proposal(intake,overlap=6))


def test_overlap_when_interior_frames_and_protected_events_survive(tmp_path,built):
    intake=prepared(tmp_path,built,allowed=("overlap",),anchors=True)
    result=require("timeline","build_timeline")(intake,proposal(intake,overlap=6))
    assert result.segments[-1].timeline_range.end==1460592000000
    assert result.segments[0].source_range==intake.sources[0].approved_range
    assert len(result.event_map)==3
    assert result.needs_master_review is True


def test_overlap_when_important_anchor_would_be_covered(tmp_path,built):
    intake=prepared(tmp_path,built,allowed=("overlap",),anchors=True)
    with pytest.raises(require("errors","ContractError"),match="anchor"):
        require("timeline","build_timeline")(intake,proposal(intake,overlap=25))


def test_branch_when_new_variant_does_not_delete_original_denominator(tmp_path,built):
    intake=prepared(tmp_path,built,allowed=("branch",))
    initial=require("timeline","build_timeline")(intake)
    variant=require("timeline","build_timeline")(intake,proposal(intake,branch="short"),initial)
    assert variant.required_coverage==initial.required_coverage
    assert variant.parent_timeline_digest==require("timeline","timeline_digest")(initial)
    assert variant.branch=="short"
    assert initial.branch=="main"


def test_speech_map_when_reviewed_mux_audio_is_preserved_in_target_sample_clock(tmp_path):
    fixture(tmp_path,with_audio=True)
    intake=require("intake","load_intake")(tmp_path,tmp_path/"request.json")
    result=require("timeline","build_timeline")(intake)
    event=next(e for e in result.event_map if e.requirement_id=="R2")
    assert (event.audio_sample_range.start,event.audio_sample_range.end)==(96000,192000)
    assert event.audio_rounding=="nearest"
    assert event.post_verified is False


def test_timeline_reimport_when_valid_decisions_roundtrip(tmp_path,built):
    intake=prepared(tmp_path,built)
    timeline=require("timeline","build_timeline")(intake)
    assert require("timeline","validate_timeline")(intake,timeline) is None


@pytest.mark.parametrize("change",["event_map","denominator","interval"])
def test_timeline_reimport_when_native_or_external_change_forged_canonical_decisions(tmp_path,built,change):
    intake=prepared(tmp_path,built)
    timeline=require("timeline","build_timeline")(intake)
    if change=="event_map":
        event=timeline.event_map[0].model_copy(update={"master_range":require("models","SourceRange")(start=1,end=2)})
        timeline=timeline.model_copy(update={"event_map":(event,*timeline.event_map[1:])})
    elif change=="denominator":timeline=timeline.model_copy(update={"required_coverage":timeline.required_coverage[:-1]})
    else:
        segment=timeline.segments[0].model_copy(update={"timeline_range":require("models","SourceRange")(start=1,end=2)})
        timeline=timeline.model_copy(update={"segments":(segment,*timeline.segments[1:])})
    with pytest.raises(require("errors","ContractError")):
        require("timeline","validate_timeline")(intake,timeline)


def test_branch_when_parent_or_authority_is_missing(tmp_path,built):
    intake=prepared(tmp_path,built)
    initial=require("timeline","build_timeline")(intake)
    with pytest.raises(require("errors","ContractError")):
        require("timeline","build_timeline")(intake,proposal(intake,branch="short"),initial)
