"""Source bytes alone do not pin range, acceptance or imported state."""
from production.models import Reference, ClipId, Playback, Review, Selection, SourceRange, Take, Verdict
from conftest import pin, require
from test_dependencies import linked


def selection(seed, tmp_path, clip_id="C1", revision=1):
    take = Take(id=f"TAKE-{clip_id}-{revision}", clip_id=ClipId(clip_id), attempt_id=f"ATT-{clip_id}", asset=pin(tmp_path, f"take-{clip_id}.dat", "synthetic source"), frame_count=48, fps=24, width=1280, height=720, has_audio=False, decode_evidence="fixture-probe", source_range=SourceRange(start=0, end=48), fingerprint=require("contracts", "fingerprint")(seed, clip_id))
    review = Review(verdict=Verdict.ACCEPTED, fulfilled=seed.batch.clips[int(clip_id[1:])-1].requirements, playback=Playback(asset_hash=take.asset.sha256, source_range=take.source_range, reviewer="fixture-reviewer", evidence="fixture-playback", video_watched=True))
    from conftest import capability, authority
    cap = capability.__wrapped__(tmp_path)
    approval = authority.__wrapped__(tmp_path,seed,cap)
    return Selection(take=take, review=review, reviewed_fingerprint=take.fingerprint, approval=approval, acceptance_revision=revision)


def test_fingerprint_when_same_bytes_range_changed(seed, tmp_path):
    # Given: accepted source and a dependent clip.
    state = linked(seed)
    source = selection(state, tmp_path)
    state = state.model_copy(update={"selections": (source,)})
    old = require("contracts", "fingerprint")(state, "C3")
    changed = source.model_copy(update={"take": source.take.model_copy(update={"source_range": SourceRange(start=1, end=48), "range_revision": 2})})
    # When: changing only selected range of identical bytes.
    new = require("contracts", "fingerprint")(state.model_copy(update={"selections": (changed,)}), "C3")
    # Then: changed input cannot inherit the old acceptance.
    assert new != old


def test_descendants_when_source_replaced(seed, tmp_path):
    # Given: C3 consumed C1; C2 is independent.
    state = linked(seed)
    c1, c2 = selection(state, tmp_path), selection(state, tmp_path, "C2")
    state = state.model_copy(update={"selections": (c1, c2)})
    c3 = selection(state, tmp_path, "C3")
    state = state.model_copy(update={"selections": (*state.selections, c3)})
    # When: replacing the upstream selection.
    new = require("revisions", "replace_selection")(state, c1.model_copy(update={"acceptance_revision": 2}))
    # Then: affected descendant is blocked while independent selection remains valid.
    assert not next(s for s in new.selections if s.take.clip_id == "C3").valid
    assert next(s for s in new.selections if s.take.clip_id == "C2").valid


def test_unrelated_batch_revision_when_consumed_inputs_same(seed):
    # Given: unrelated batch book-keeping changes.
    old = require("contracts", "fingerprint")(seed, "C1")
    # When: changing batch revision only.
    new = require("contracts", "fingerprint")(seed.model_copy(update={"batch": seed.batch.model_copy(update={"revision": 2})}), "C1")
    # Then: independent input retains its fingerprint.
    assert new == old


def test_fingerprint_when_imports_change(seed,tmp_path):
    # Given: same source bytes and range, different imported attribute contract.
    state=linked(seed)
    state=state.model_copy(update={"selections":(selection(state,tmp_path),)})
    old=require("contracts","fingerprint")(state,"C3")
    ref=state.batch.clips[2].references[0].model_copy(update={"imports":("pose",),"excludes":("prior_dialogue",)})
    clip=state.batch.clips[2].model_copy(update={"references":(ref,)})
    # When: the consumption contract changes, not source bytes.
    changed=state.model_copy(update={"batch":state.batch.model_copy(update={"clips":(*state.batch.clips[:2],clip)})})
    # Then: stale imported identity/pose assumptions cannot reuse an acceptance fingerprint.
    assert require("contracts","fingerprint")(changed,"C3") != old


def test_fingerprint_when_conditional_acceptance_changes(seed,tmp_path):
    # Given: source bytes/range stay identical while the defect/acceptance decision changes.
    state=linked(seed)
    source=selection(state,tmp_path)
    state=state.model_copy(update={"selections":(source,)})
    old=require("contracts","fingerprint")(state,"C3")
    report=source.review.model_copy(update={"verdict":Verdict.CONDITIONAL,"defects":("pose",),"post_fix":"reviewed future correction","post_receiver":"fixture-post","conditional_policy":"fixture-policy"})
    changed=source.model_copy(update={"review":report,"acceptance_revision":2})
    # When: source acceptance is no longer equivalent.
    new=require("contracts","fingerprint")(state.model_copy(update={"selections":(changed,)}),"C3")
    # Then: the old downstream acceptance binding is invalidated.
    assert new != old
