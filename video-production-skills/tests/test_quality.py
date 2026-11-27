"""Evidence contracts do not claim automatic semantic viewing/listening."""
import pytest
from production.models import ContractError, Phase, Receipt, SourceRange, Verdict
from conftest import require
from test_execution import reserved
from test_revisions import selection


def candidate(seed, capability, authority, tmp_path):
    from conftest import configurations
    authority = authority.model_copy(update={"configurations":configurations(seed,capability)})
    state, packet = reserved(seed, capability, authority, tmp_path)
    observe = require("execution", "observe")
    state = observe(state, "ATT-1", Receipt(phase=Phase.SUBMITTED, job_id="fixture-job", evidence="receipt", request_hash=packet.request_hash))
    state = observe(state, "ATT-1", Receipt(phase=Phase.SUCCEEDED, job_id="fixture-job", evidence="remote-success", request_hash=packet.request_hash))
    item = selection(seed, tmp_path)
    from test_media import make_video
    take = item.take.model_copy(update={"attempt_id": "ATT-1", "asset": make_video(tmp_path, audio=seed.batch.clips[0].audio_required), "has_audio": seed.batch.clips[0].audio_required})
    item = item.model_copy(update={"review": item.review.model_copy(update={"playback": item.review.playback.model_copy(update={"asset_hash": take.asset.sha256})})})
    return state, take, item.review


def test_accept_when_current_review_matches_source(seed, capability, authority, tmp_path):
    # Given: operator-reported successful source and explicit review.
    state, take, review = candidate(seed, capability, authority, tmp_path)
    # When: committing against current inputs.
    updated = require("quality", "accept_take")(state, take, review, take.fingerprint, tmp_path)
    # Then: current selection is published independently of remote success.
    assert updated.selections[0].take.id == take.id


@pytest.mark.parametrize("change", [
    {"video_watched": False},
    {"asset_hash": "f"*64},
    {"source_range": SourceRange(start=1, end=48)},
])
def test_review_when_playback_missing_or_mismatched(seed, capability, authority, tmp_path, change):
    # Given: claim does not describe the actual selected source.
    state, take, review = candidate(seed, capability, authority, tmp_path)
    review = review.model_copy(update={"playback": review.playback.model_copy(update=change)})
    # When / Then: selected stills alone are not motion evidence.
    with pytest.raises(ContractError, match="playback"):
        require("quality", "accept_take")(state, take, review, take.fingerprint, tmp_path)


def test_listening_when_audio_required(seed, capability, authority, tmp_path):
    # Given: shot requires sound but review did not listen.
    clip = seed.batch.clips[0].model_copy(update={"audio_required": True})
    seed = seed.model_copy(update={"batch": seed.batch.model_copy(update={"clips": (clip, *seed.batch.clips[1:])})})
    state, take, review = candidate(seed, capability, authority, tmp_path)
    take = take.model_copy(update={"has_audio": True})
    # When / Then: audio stream existence is not a listening PASS.
    with pytest.raises(ContractError, match="audio"):
        require("quality", "accept_take")(state, take, review, take.fingerprint, tmp_path)


def test_missing_requirement_when_all_frames_decode(seed, capability, authority, tmp_path):
    # Given: playable media but required event not fulfilled.
    state, take, review = candidate(seed, capability, authority, tmp_path)
    review = review.model_copy(update={"fulfilled": ()})
    # When / Then: decode success cannot replace story coverage.
    with pytest.raises(ContractError, match="coverage"):
        require("quality", "accept_take")(state, take, review, take.fingerprint, tmp_path)


def test_late_commit_when_design_changed(seed, capability, authority, tmp_path):
    # Given: QA is finished for old approved design.
    state, take, review = candidate(seed, capability, authority, tmp_path)
    state = state.model_copy(update={"batch": state.batch.model_copy(update={"scope_revision": "scope-2"})})
    # When / Then: old remote success remains, current acceptance does not open.
    with pytest.raises(ContractError, match="revision"):
        require("quality", "accept_take")(state, take, review, take.fingerprint, tmp_path)
    assert state.attempts[0].phase == Phase.SUCCEEDED


def test_input_as_output_when_download_matches_reference(seed, capability, authority, tmp_path):
    # Given: downloaded item is the uploaded identity fixture, not a job result.
    state, take, review = candidate(seed, capability, authority, tmp_path)
    take = take.model_copy(update={"asset": seed.batch.clips[0].assets[0]})
    # When / Then: input thumbnail cannot be accepted as output.
    with pytest.raises(ContractError, match="input"):
        require("quality", "accept_take")(state, take, review, take.fingerprint, tmp_path)


def test_conditional_when_no_receiver_or_fix(seed, capability, authority, tmp_path):
    # Given: unresolved issue is labelled conditional without a viable owner.
    state, take, review = candidate(seed, capability, authority, tmp_path)
    review = review.model_copy(update={"verdict": Verdict.CONDITIONAL, "defects": ("identity",)})
    # When / Then: conditional cannot hide unfinished mandatory work.
    with pytest.raises(ContractError, match="conditional"):
        require("quality", "accept_take")(state, take, review, take.fingerprint, tmp_path)


def test_unsupported_source_range_when_vfr_has_no_pts(seed, tmp_path):
    # Given: a VFR candidate, not CFR.
    take = selection(seed, tmp_path).take.model_dump()
    take["cfr"] = False
    # When / Then: nominal fps is not enough for frame precision.
    with pytest.raises(ContractError, match="timebase"):
        from production.models import Take
        Take.model_validate(take)


def test_metadata_when_operator_claim_differs_from_actual_bytes(seed, capability, authority, tmp_path):
    # Given: correct file hash, falsified declared FPS.
    state, take, review = candidate(seed, capability, authority, tmp_path)
    take = take.model_copy(update={"fps": 12})
    # When / Then: actual local probe, not reported metadata, controls admission.
    with pytest.raises(ContractError, match="metadata"):
        require("quality", "accept_take")(state, take, review, take.fingerprint, tmp_path)


def test_revalidation_when_historical_result_remains_usable(seed, capability, authority, tmp_path):
    # Given: previously accepted take, then related design revision changes.
    state, take, review = candidate(seed,capability,authority,tmp_path)
    state = require("quality","accept_take")(state,take,review,take.fingerprint,tmp_path)
    state = state.model_copy(update={"batch":state.batch.model_copy(update={"scope_revision":"scope-2"})})
    current = require("contracts","fingerprint")(state,"C1")
    # When: explicitly re-reviewing the known historical take against current requirements.
    from conftest import configurations
    current_approval=authority.model_copy(update={"configurations":configurations(state,capability)})
    updated = require("quality","revalidate_take")(state,"C1",review,current,tmp_path,current_approval)
    # Then: history is not falsified, but a new QA binding makes it currently usable.
    assert updated.selections[0].take.fingerprint == take.fingerprint
    assert updated.selections[0].reviewed_fingerprint == current
    assert updated.selections[0].acceptance_revision == 2


def test_audio_requirement_when_clip_flag_omits_speech(seed, capability, authority, tmp_path):
    # Given: approved coverage requires speech, even if clip.audio_required was omitted.
    import json
    from conftest import pin
    coverage = (seed.batch.coverage[0].model_copy(update={"modality":"audio"}),*seed.batch.coverage[1:])
    source = pin(tmp_path,"approved-coverage.json",json.dumps({"format":"production-coverage/1","requirements":[r.model_dump() for r in coverage]}))
    seed = seed.model_copy(update={"approved_coverage":coverage,"coverage_source":source,"batch":seed.batch.model_copy(update={"coverage":coverage})})
    state,take,review = candidate(seed,capability,authority,tmp_path)
    # When / Then: a silent take cannot fulfill an approved audio requirement by a label alone.
    with pytest.raises(ContractError,match="audio"):
        require("quality","accept_take")(state,take,review,take.fingerprint,tmp_path)


def test_selected_duration_when_source_is_long_but_chosen_range_short(seed, capability, authority, tmp_path):
    # Given: full source is 2s but the selected material supplies only 1s.
    state,take,review = candidate(seed,capability,authority,tmp_path)
    interval = SourceRange(start=0,end=24)
    take = take.model_copy(update={"source_range":interval})
    review = review.model_copy(update={"playback":review.playback.model_copy(update={"source_range":interval})})
    # When / Then: metadata of the full source cannot certify the delivered timeline.
    with pytest.raises(ContractError,match="duration"):
        require("quality","accept_take")(state,take,review,take.fingerprint,tmp_path)


def test_reported_repeated_dialogue_when_take_otherwise_decodes(seed,capability,authority,tmp_path):
    # Given: a fixture reviewer observed unwanted repetition from the reference.
    state,take,review=candidate(seed,capability,authority,tmp_path)
    review=review.model_copy(update={"defects":("unwanted_prior_dialogue_repeat",)})
    # When / Then: structural/source correctness cannot override a reported semantic defect.
    with pytest.raises(ContractError,match="defect"):
        require("quality","accept_take")(state,take,review,take.fingerprint,tmp_path)


def linked_running(seed,capability,authority,tmp_path,separate_approval=False,optional_reference=False,omit_reference=False):
    """Actual local files, successful source receipt, and a running dependent fixture job."""
    from conftest import configurations, pin
    from production.models import Binding, AttemptId, Take, Playback, Review, ClipId
    from test_dependencies import linked
    from test_media import make_video
    from test_bindings import native
    from test_revisions import selection
    state=linked(seed)
    if optional_reference:
        clip=state.batch.clips[2]
        reference=clip.references[0].model_copy(update={"required":False,"omission_evidence":"explicit optional history may be omitted"})
        state=state.model_copy(update={"batch":state.batch.model_copy(update={"clips":(*state.batch.clips[:2],clip.model_copy(update={"references":(reference,)}))})})
    state,source_take,source_review=candidate(state,capability,authority,tmp_path)
    state=require("quality","accept_take")(state,source_take,source_review,source_take.fingerprint,tmp_path)
    source=next(s for s in state.selections if s.take.clip_id == "C1")
    ref=state.batch.clips[2].references[0]
    binding=Binding(pin=source.take.asset,source_clip=ClipId("C1"),source_range=source.take.source_range,range_revision=source.take.range_revision,acceptance_revision=source.acceptance_revision,role=ref.role,modality=ref.modality,imports=ref.imports,excludes=ref.excludes,native_asset_id="fixture-A",native_reference_id="fixture-ref-A",ready=True)
    auth=authority.model_copy(update={"configurations":configurations(state,capability),"allowed_hashes":(*authority.allowed_hashes,source.take.asset.sha256)})
    if separate_approval:
        auth=auth.model_copy(update={"evidence":pin(tmp_path,"approval-C3.txt","separate current C3 fixture approval")})
    refs=(native(state),) if omit_reference else (native(state),binding)
    packet=require("bindings","prepare_request")(state,"C3",capability,auth,refs,tmp_path)
    state=require("execution","reserve")(state,packet,AttemptId("ATT-C3"),0,tmp_path)
    for phase in (Phase.SUBMITTED,Phase.RUNNING):
        state=require("execution","observe")(state,"ATT-C3",Receipt(phase=phase,job_id="fixture-C3",evidence="synthetic running receipt",request_hash=packet.request_hash))
    asset=make_video(tmp_path,"dependent-C3.mp4",color="green")
    take=Take(id="TAKE-C3",clip_id=ClipId("C3"),attempt_id=AttemptId("ATT-C3"),asset=asset,frame_count=48,fps=24,width=1280,height=720,has_audio=False,decode_evidence="technical fixture actual decode",source_range=SourceRange(start=0,end=48),fingerprint=packet.fingerprint)
    review=Review(verdict=Verdict.ACCEPTED,fulfilled=("R3",),playback=Playback(asset_hash=asset.sha256,source_range=take.source_range,reviewer="fixture-reviewer",evidence="reported semantic fixture",video_watched=True))
    return state,source,take,review,packet


def test_late_remote_success_when_running_consumer_source_replaced(seed,capability,authority,tmp_path):
    # Given: C3 is already running with selected source C1 A.
    from test_media import make_video
    state,source,take,review,packet=linked_running(seed,capability,authority,tmp_path)
    b=make_video(tmp_path,"replacement-B.mp4",color="red")
    replacement=source.model_copy(update={"take":source.take.model_copy(update={"id":"TAKE-B","asset":b}),"review":source.review.model_copy(update={"playback":source.review.playback.model_copy(update={"asset_hash":b.sha256})}),"acceptance_revision":2})
    state=require("revisions","replace_selection")(state,replacement)
    # When: C3's original remote job succeeds after A was replaced by B.
    state=require("execution","observe")(state,"ATT-C3",Receipt(phase=Phase.SUCCEEDED,job_id="fixture-C3",evidence="late success fixture",request_hash=packet.request_hash))
    # Then: old success is preserved, but it cannot publish current C3 acceptance.
    with pytest.raises(ContractError,match="revision"):
        require("quality","accept_take")(state,take,review,packet.fingerprint,tmp_path)
    assert next(a for a in state.attempts if a.id == "ATT-C3").phase == Phase.SUCCEEDED
    assert all(s.take.clip_id != "C3" for s in state.selections)


def test_consumer_revalidation_when_required_upstream_invalid(seed,capability,authority,tmp_path):
    # Given: both source and dependent were accepted, then source is invalidated.
    state,source,take,review,packet=linked_running(seed,capability,authority,tmp_path)
    state=require("execution","observe")(state,"ATT-C3",Receipt(phase=Phase.SUCCEEDED,job_id="fixture-C3",evidence="success fixture",request_hash=packet.request_hash))
    state=require("quality","accept_take")(state,take,review,take.fingerprint,tmp_path)
    state=require("revisions","invalidate_selection")(state,"C1","source defect affects required imported state")
    current=require("contracts","fingerprint")(state,"C3")
    # When / Then: full self-review cannot bypass an unresolved mandatory dependency.
    with pytest.raises(ContractError,match="dependency"):
        require("quality","revalidate_take")(state,"C3",review,current,tmp_path)


def test_consumer_revalidation_when_source_defect_excludes_imported_attributes(seed,capability,authority,tmp_path):
    # Given: C3 consumed pose; source is re-reviewed conditional for unrelated background only.
    state,source,take,review,packet=linked_running(seed,capability,authority,tmp_path)
    state=require("execution","observe")(state,"ATT-C3",Receipt(phase=Phase.SUCCEEDED,job_id="fixture-C3",evidence="success fixture",request_hash=packet.request_hash))
    state=require("quality","accept_take")(state,take,review,take.fingerprint,tmp_path)
    source_report=source.review.model_copy(update={"verdict":Verdict.CONDITIONAL,"defects":("background_edge",),"post_fix":"crop proven background edge only","post_receiver":"fixture-post","conditional_policy":"fixture-explicit-policy"})
    source=source.model_copy(update={"review":source_report,"acceptance_revision":2})
    state=require("revisions","replace_selection")(state,source)
    current=require("contracts","fingerprint")(state,"C3")
    # When: explicit revalidation observes that the imported pose is unaffected.
    updated=require("quality","revalidate_take")(state,"C3",review,current,tmp_path)
    # Then: reviewed retention is allowed without inventing a new generation request.
    assert next(s for s in updated.selections if s.take.clip_id == "C3").valid


def test_reported_identity_drift_when_remote_take_succeeded(seed,capability,authority,tmp_path):
    # Given: a successful, technically decodable output whose fixture report finds face drift.
    state,take,review=candidate(seed,capability,authority,tmp_path)
    review=review.model_copy(update={"defects":("identity",)})
    # When / Then: a previously successful model call does not authorize drift propagation.
    with pytest.raises(ContractError,match="defect"):
        require("quality","accept_take")(state,take,review,take.fingerprint,tmp_path)
