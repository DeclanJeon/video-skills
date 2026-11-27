"""Bind reported QA to real decoded sources and current explicit approvals."""
from pathlib import Path
from typing import assert_never

from production.approval import validate_approval, validate_reuse
from production.contracts import clip_for, fingerprint, selection_for, usable
from production.files import verified_file
from production.models import Authority, Binding, ContractError, Phase, Review, Selection, State, Take, Verdict
from production.revisions import replace_selection


def _sources_current(state: State, clip_id: str, root: Path, consumed: tuple[Binding, ...] = ()) -> None:
    for ref in clip_for(state,clip_id).references:
        bound=any((b.source_clip,b.role,b.modality) == (ref.source_clip,ref.role,ref.modality) for b in consumed)
        if not ref.required and ref.omission_evidence and not bound:
            continue
        source=selection_for(state,ref.source_clip)
        if (source is None or source.reviewed_fingerprint != fingerprint(state,ref.source_clip)
            or not usable(source,ref.imports)):
            raise ContractError("dependency","required or consumed upstream state remains unresolved")
        _=verified_file(root,source.take.asset)
        _=verified_file(root,source.approval.evidence)


def _apply_review(state: State, take: Take, review: Review, expected_fingerprint: str,
                  root: Path, revalidation: bool, current_authority: Authority | None = None) -> State:
    clip=clip_for(state,take.clip_id)
    current=fingerprint(state,take.clip_id)
    if expected_fingerprint != current or (not revalidation and take.fingerprint != current):
        raise ContractError("revision","QA inputs are no longer current")
    from production.upstream import verify_scope
    verify_scope(state,root)
    approval: Authority
    match take.origin:
        case "generated":
            attempt=next((a for a in state.attempts if a.id == take.attempt_id),None)
            if attempt is None or attempt.prepared.clip_id != take.clip_id or attempt.phase not in {Phase.SUCCEEDED,Phase.DOWNLOADED}:
                raise ContractError("attempt","candidate not bound to successful remote job")
            approval=current_authority or attempt.prepared.authority
            validate_approval(state,take.clip_id,attempt.prepared.capability,approval,root)
            _sources_current(state,take.clip_id,root,attempt.prepared.bindings)
            if not revalidation and attempt.prepared.fingerprint != current:
                raise ContractError("revision","remote result consumed replaced inputs")
            if (take.width,take.height) != (attempt.prepared.capability.width,attempt.prepared.capability.height):
                raise ContractError("format","result resolution differs from request")
            inputs={attempt.prepared.prompt.sha256,*(b.pin.sha256 for b in attempt.prepared.bindings)}
            if take.asset.sha256 in inputs:
                raise ContractError("input","download is an input reference, not a result")
        case "approved_reuse":
            if current_authority is None or take.attempt_id is not None:
                raise ContractError("authority","reuse requires an explicit current local-source grant, not a remote attempt")
            approval=current_authority
            validate_reuse(state,take,approval,root)
            _sources_current(state,take.clip_id,root)
        case unreachable:
            assert_never(unreachable)
    _=verified_file(root,take.asset)
    from production.media import probe_media
    actual=probe_media(root,take.asset)
    if (actual.width,actual.height,actual.frame_count,actual.fps,actual.has_audio,actual.cfr) != (take.width,take.height,take.frame_count,take.fps,take.has_audio,take.cfr):
        raise ContractError("metadata","declared media metadata differs from actual decoded bytes")
    if abs((take.source_range.end-take.source_range.start)/take.fps-clip.duration_s) > 0.5/take.fps:
        raise ContractError("duration","selected range does not supply planned clip length")
    playback=review.playback
    if not playback.video_watched or playback.asset_hash != take.asset.sha256 or playback.source_range != take.source_range:
        raise ContractError("playback","full selected source was not reviewed")
    from production.approval import requested_audio
    if (requested_audio(state,clip.id) and not take.has_audio) or (take.has_audio and not playback.audio_listened):
        raise ContractError("audio","required audio/listening evidence missing")
    match review.verdict:
        case Verdict.ACCEPTED:
            if review.defects:
                raise ContractError("defect","accepted result still has unresolved defects")
            if set(review.fulfilled) != set(clip.requirements):
                raise ContractError("coverage","mandatory events/speech not fulfilled")
        case Verdict.CONDITIONAL:
            if (not review.post_fix or not review.post_receiver or not review.conditional_policy
                or set(review.defects) & {"identity","contact","dialogue","required_action"}
                or set(review.fulfilled) != set(clip.requirements)):
                raise ContractError("conditional","mandatory defect or missing post acceptance")
        case Verdict.REJECTED:
            if not review.defects:
                raise ContractError("defect","rejection needs a concrete finding")
        case unreachable:
            assert_never(unreachable)
    previous=selection_for(state,take.clip_id)
    selection=Selection(take=take,review=review,reviewed_fingerprint=current,approval=approval,
        acceptance_revision=previous.acceptance_revision+1 if previous else 1)
    updated=replace_selection(state,selection)
    return updated.model_copy(update={"attempts":tuple(a.model_copy(update={"phase":Phase.DOWNLOADED}) if a.id == take.attempt_id else a for a in updated.attempts)})


def accept_take(state: State, take: Take, review: Review, expected_fingerprint: str, root: Path) -> State:
    return _apply_review(state,take,review,expected_fingerprint,root,False)


def accept_supplied(state: State, take: Take, review: Review, authority: Authority, root: Path) -> State:
    match take.origin:
        case "approved_reuse":
            return _apply_review(state,take,review,take.fingerprint,root,False,authority)
        case "generated":
            raise ContractError("authority","supplied media must declare reuse origin without a remote attempt")
        case unreachable:
            assert_never(unreachable)


def revalidate_take(state: State, clip_id: str, review: Review, expected_fingerprint: str,
                    root: Path, current_authority: Authority | None = None) -> State:
    previous=selection_for(state,clip_id)
    if previous is None:
        raise ContractError("revision","no known historical selection to revalidate")
    return _apply_review(state,previous.take,review,expected_fingerprint,root,True,current_authority or previous.approval)
