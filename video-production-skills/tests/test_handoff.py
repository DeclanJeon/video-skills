"""All required coverage, joins and full playback precede post delivery."""
import pytest
from production.models import ContractError, FlowReview, JoinReview, Pin, ReviewRender, Verdict
from conftest import require
from test_revisions import selection


def all_selected(seed, tmp_path):
    return seed.model_copy(update={"selections": tuple(selection(seed, tmp_path, f"C{i}") for i in (1,2,3))})


def joins_for(state):
    sels = {s.take.clip_id: s for s in state.selections}
    return tuple(JoinReview(join_id=j.id, before_take=sels[j.before].take.id, after_take=sels[j.after].take.id, before_revision=sels[j.before].acceptance_revision, after_revision=sels[j.after].acceptance_revision, before_range_revision=sels[j.before].take.range_revision, after_range_revision=sels[j.after].take.range_revision, reveal_order=j.reveal_order, passed=True, evidence="fixture-boundary-viewing", continuous_playback=True) for j in state.batch.joins)


def flow_for(state):
    digest = require("handoff", "selection_hash")(state)
    proof = ReviewRender(artifact=Pin(id="fixture-rough",version="1",path="fixture-rough.mp4",sha256="a"*64),manifest=Pin(id="fixture-manifest",version="1",path="fixture-manifest.json",sha256="b"*64),selection_hash=digest)
    return FlowReview(review_render=proof,selection_hash=digest, clip_order=state.batch.edit_order, passed=True, evidence="fixture-full-playback", continuous_playback=True, audio_listened=True)


def test_delivery_when_all_sources_and_flow_checked(seed, tmp_path):
    # Given: all sources and exact joins reviewed.
    state = all_selected(seed, tmp_path)
    state = state.model_copy(update={"join_reviews": joins_for(state)})
    # When: preparing local post handoff.
    package = require("handoff", "build_handoff")(state, flow_for(state), "post-receiver", "rights-record", tmp_path)
    # Then: every required source is included, with explicit handles.
    assert len(package.selections) == 3
    assert package.handles == (("C1",0,0),("C2",0,0),("C3",0,0))


def test_delivery_when_clip_is_missing(seed, tmp_path):
    # Given: two of three clips exist.
    state = all_selected(seed, tmp_path)
    state = state.model_copy(update={"selections": state.selections[:-1]})
    # When / Then: missing clip is not a black placeholder.
    with pytest.raises(ContractError, match="coverage"):
        require("handoff", "build_handoff")(state, flow_for(state), "receiver", "rights", tmp_path)


def test_join_when_other_take_revision_reviewed(seed, tmp_path):
    # Given: stale boundary report.
    state = all_selected(seed, tmp_path)
    join = joins_for(state)[0].model_copy(update={"before_revision": 99})
    # When / Then: same clip IDs cannot hide different selected takes.
    with pytest.raises(ContractError, match="revision"):
        require("handoff", "check_join")(state, join)


def test_reaction_first_when_approved_reveal_order(seed, tmp_path):
    # Given: board intentionally reveals the reaction before its cause.
    j = seed.batch.joins[0].model_copy(update={"relation": "reaction", "reveal_order": ("reaction", "cause")})
    state = all_selected(seed.model_copy(update={"batch": seed.batch.model_copy(update={"joins": (j, *seed.batch.joins[1:])})}), tmp_path)
    # When: checking matching observed order.
    result = require("handoff", "check_join")(state, joins_for(state)[0])
    # Then: non-linear reveal is preserved.
    assert result is None


def test_reveal_when_observed_order_violates_board(seed, tmp_path):
    # Given: actual reveal reverses the approved order.
    state = all_selected(seed, tmp_path)
    join = joins_for(state)[0].model_copy(update={"reveal_order": ("unauthorized",)})
    # When / Then: unapproved narrative inversion is rejected.
    with pytest.raises(ContractError, match="reveal"):
        require("handoff", "check_join")(state, join)


def test_flow_when_only_frames_were_seen(seed, tmp_path):
    # Given: complete sources, but only stills were inspected.
    state = all_selected(seed, tmp_path)
    state = state.model_copy(update={"join_reviews": joins_for(state)})
    flow = flow_for(state).model_copy(update={"continuous_playback": False})
    # When / Then: partial viewing cannot certify overall flow.
    with pytest.raises(ContractError, match="flow"):
        require("handoff", "build_handoff")(state, flow, "receiver", "rights", tmp_path)


def test_progress_when_selection_stale(seed, tmp_path):
    # Given: stale result is still on disk.
    state = all_selected(seed, tmp_path)
    state = state.model_copy(update={"selections": (state.selections[0].model_copy(update={"valid": False}), *state.selections[1:])})
    # When: computing progress from current validity.
    progress = require("handoff", "progress")(state)
    # Then: existence alone does not count.
    assert progress.accepted == 2
    assert progress.required == 3


def test_conditional_when_face_defect_imported(seed, tmp_path):
    # Given: conditional source has a defect in a requested attribute.
    from production.contracts import usable
    item = selection(seed, tmp_path)
    review = item.review.model_copy(update={"verdict": Verdict.CONDITIONAL, "defects": ("identity",), "post_fix": "replace region", "post_receiver": "post", "conditional_policy": "AP-conditional"})
    item = item.model_copy(update={"review": review})
    # When / Then: conditional status alone does not authorize identity reuse.
    assert not usable(item, ("identity",))


def test_delivery_when_boundary_missing(seed, tmp_path):
    # Given: every individual take is accepted but boundary reports are absent.
    state = all_selected(seed, tmp_path)
    # When / Then: individual quality does not certify the sequence.
    with pytest.raises(ContractError, match="join"):
        require("handoff", "build_handoff")(state,flow_for(state),"post","rights", tmp_path)


def test_handles_when_extra_source_frames_not_reviewed(seed, tmp_path):
    # Given: extra raw frames exist but selected playback did not review them.
    state = all_selected(seed,tmp_path)
    first = state.selections[0]
    first = first.model_copy(update={"take":first.take.model_copy(update={"frame_count":72})})
    state = state.model_copy(update={"selections":(first,*state.selections[1:])})
    state = state.model_copy(update={"join_reviews":joins_for(state)})
    # When: handing off the checked range.
    result = require("handoff","build_handoff")(state,flow_for(state),"receiver","rights", tmp_path)
    # Then: unreviewed margins are not promised as usable editing handles.
    assert result.handles[0] == ("C1",0,0)


def test_time_elision_when_prop_change_is_approved(seed,tmp_path):
    # Given: approved edit jumps in time and a prop changes from empty hand to held.
    plan=seed.batch.joins[0].model_copy(update={"relation":"time_elision","allowed_changes":("prop:empty->held",)})
    state=all_selected(seed.model_copy(update={"batch":seed.batch.model_copy(update={"joins":(plan,*seed.batch.joins[1:])})}),tmp_path)
    report=joins_for(state)[0].model_copy(update={"observed_changes":("prop:empty->held",)})
    # When / Then: approved discontinuity is preserved instead of forcing identical frames.
    assert require("handoff","check_join")(state,report) is None


def test_time_elision_when_prop_change_is_unapproved(seed,tmp_path):
    # Given: time jump exists, but not permission to change the prop's owner.
    plan=seed.batch.joins[0].model_copy(update={"relation":"time_elision","allowed_changes":("light:afternoon->dusk",)})
    state=all_selected(seed.model_copy(update={"batch":seed.batch.model_copy(update={"joins":(plan,*seed.batch.joins[1:])})}),tmp_path)
    report=joins_for(state)[0].model_copy(update={"observed_changes":("prop:empty->held",)})
    # When / Then: a relationship label does not authorize arbitrary state changes.
    with pytest.raises(ContractError,match="change"):
        require("handoff","check_join")(state,report)
