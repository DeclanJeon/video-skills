"""Read-only re-admission through actual production public contracts and local facts."""
from pathlib import Path
from typing import assert_never

from production.approval import requested_audio, validate_approval, validate_reuse
from production.contracts import clip_for, fingerprint, selection_for, usable
from production.models import Binding, Phase, Pin as ProductionPin, Selection, State, Verdict

from postproduction.common import Pin, SourceRange
from postproduction.errors import ContractError
from postproduction.files import verified_file
from postproduction.intake_models import SourceCaps, SourceRef
from postproduction.media import probe_video


def local_pin(pin: ProductionPin) -> Pin:
    """Reparse the legacy boundary into the stricter portable local pin contract."""
    return Pin.model_validate_json(pin.model_dump_json())


def dependencies(state: State, selected: Selection, consumed: tuple[Binding, ...], root: Path) -> None:
    """Optional input is exempt only when explicitly omitted and truly unconsumed."""
    for ref in clip_for(state,selected.take.clip_id).references:
        bound = any((b.source_clip,b.role,b.modality) == (ref.source_clip,ref.role,ref.modality)
                    for b in consumed)
        if not ref.required and ref.omission_evidence and not bound:
            continue
        source = selection_for(state,ref.source_clip)
        if (source is None or source.reviewed_fingerprint != fingerprint(state,ref.source_clip)
            or not usable(source,ref.imports)):
            raise ContractError("dependency", "required/consumed source is not current AND usable")
        _ = verified_file(root,local_pin(source.take.asset))
        _ = verified_file(root,local_pin(source.approval.evidence))


def source_approval(state: State, selected: Selection, root: Path) -> None:
    """Validate real current grants without invoking or mutating production execution."""
    take = selected.take
    _ = verified_file(root,local_pin(selected.approval.evidence))
    match take.origin:
        case "approved_reuse":
            validate_reuse(state,take,selected.approval,root)
            dependencies(state,selected,(),root)
            return
        case "generated":
            attempt = next((a for a in state.attempts if a.id == take.attempt_id),None)
            if (attempt is None or attempt.prepared.clip_id != take.clip_id
                or attempt.phase not in {Phase.SUCCEEDED,Phase.DOWNLOADED}):
                raise ContractError("attempt", "generated selection lacks its known successful job facts")
            validate_approval(state,take.clip_id,attempt.prepared.capability,selected.approval,root)
            dependencies(state,selected,attempt.prepared.bindings,root)
            inputs = (attempt.prepared.prompt,*(b.pin for b in attempt.prepared.bindings))
            for pin in inputs:
                _ = verified_file(root,local_pin(pin))
            if take.asset.sha256 in {p.sha256 for p in inputs}:
                raise ContractError("input", "a consumed input reference is not a generated result")
            if (take.width,take.height) != (attempt.prepared.capability.width,attempt.prepared.capability.height):
                raise ContractError("metadata", "source dimensions differ from approved job")
            return
    assert_never(take.origin)


def reviewed(state: State, selected: Selection) -> None:
    """Reported source viewing remains distinct from current post-master viewing."""
    take, review = selected.take, selected.review
    playback = review.playback
    if (not selected.valid or selected.reviewed_fingerprint != fingerprint(state,take.clip_id)
        or not playback.video_watched or playback.asset_hash != take.asset.sha256
        or playback.source_range != take.source_range):
        raise ContractError("playback", "selected source review is not current and bound")
    if (requested_audio(state,take.clip_id) and not take.has_audio) or (take.has_audio and not playback.audio_listened):
        raise ContractError("audio", "required source audio or listening report missing")
    if set(review.fulfilled) != set(clip_for(state,take.clip_id).requirements):
        raise ContractError("coverage", "required source events are not fulfilled")
    match review.verdict:
        case Verdict.ACCEPTED:
            if review.defects:
                raise ContractError("defect", "accepted source has unresolved defects")
            return
        case Verdict.CONDITIONAL:
            if (not review.post_fix or not review.post_receiver or not review.conditional_policy
                or set(review.defects) & {"identity","contact","dialogue","required_action"}):
                raise ContractError("conditional", "conditional source has no admissible repair contract")
            return
        case Verdict.REJECTED:
            raise ContractError("source", "rejected source is not adoptable")
    assert_never(review.verdict)


def admit_source(state: State, selected: Selection, root: Path) -> SourceCaps:
    """Observe exact media properties; do not revise or reseal the production selection."""
    source_approval(state,selected,root)
    reviewed(state,selected)
    take = selected.take
    pin = local_pin(take.asset)
    facts = probe_video(root,pin)
    if (facts.width,facts.height,facts.frame_count,facts.rate.num/facts.rate.den,facts.has_audio,facts.cfr) != (
        take.width,take.height,take.frame_count,take.fps,take.has_audio,take.cfr):
        raise ContractError("metadata", "declared source metadata differs from decoded bytes")
    if not facts.cfr:
        raise ContractError("conform", "VFR needs an implemented verified PTS/conform route")
    sr = SourceRange(start=take.source_range.start,end=take.source_range.end)
    duration = sr.length*facts.rate.den/facts.rate.num
    if sr.end > facts.frame_count or abs(duration-clip_for(state,take.clip_id).duration_s) > 0.5/take.fps:
        raise ContractError("range", "reviewed range does not supply the declared source duration")
    return SourceCaps(source=SourceRef(clip_id=take.clip_id,take_id=take.id),asset=pin,approved_range=sr,
                      frame_count=facts.frame_count,rate=facts.rate,timebase=facts.timebase,
                      width=facts.width,height=facts.height,has_audio=facts.has_audio,
                      start_pts=facts.start_pts,timecode=facts.timecode,
                      acceptance_revision=selected.acceptance_revision,range_revision=take.range_revision,
                      approval=local_pin(selected.approval.evidence))
