"""Exact source-frame→master-tick maps and conservative overlap visibility checks."""
from fractions import Fraction
from typing import Final

from postproduction.clock import map_frame
from postproduction.common import ClockRate, SourceRange
from postproduction.edit_models import Change
from postproduction.errors import ContractError
from postproduction.intake_models import PostIntake
from postproduction.timeline_models import CutSpec, EventMap, TimelineSegment

FILM_CLOCK: Final = ClockRate(num=254016000000,den=1)


def layout(intake: PostIntake, cuts: tuple[CutSpec, ...]) -> tuple[TimelineSegment, ...]:
    """Keep all admitted ranges interior; no synthesized handles, conform or hidden retime."""
    sources = {s.source:s for s in intake.sources}
    result: list[TimelineSegment] = []
    position = 0
    previous_duration = 0
    for cut in cuts:
        source = sources[cut.source]
        rate = source.rate
        if Fraction(rate.num,rate.den) != Fraction(intake.profile.fps.num,intake.profile.fps.den):
            raise ContractError("conform", "mixed or changed FPS requires a verified explicit conform route")
        if cut.mode != "forward" or Fraction(cut.speed.num,cut.speed.den) != 1:
            raise ContractError("retime", "nonidentity playback needs an implemented verified time map")
        sr, approved = cut.source_range, source.approved_range
        if sr.start < approved.start or sr.end > approved.end:
            raise ContractError("range", "no exterior reviewed handles are supplied")
        if sr != approved and Change.TRIM not in intake.authority.allowed_changes:
            raise ContractError("authority", "trim is not approved")
        duration = map_frame(sr.length,rate,FILM_CLOCK,rounding="exact")
        overlap = map_frame(cut.overlap_frames,intake.profile.fps,FILM_CLOCK,rounding="exact")
        if overlap:
            if Change.OVERLAP not in intake.authority.allowed_changes:
                raise ContractError("authority", "interior overlap is not approved")
            if not result or overlap >= min(previous_duration,duration):
                raise ContractError("overlap", "overlap cannot erase a whole source or precede the first source")
        start = position-overlap
        end = start+duration
        result.append(TimelineSegment(id=cut.id,source=cut.source,source_range=sr,
                                      timeline_range=SourceRange(start=start,end=end)))
        position = end
        previous_duration = duration
    return tuple(result)


def event_maps(intake: PostIntake, segments: tuple[TimelineSegment, ...]) -> tuple[EventMap, ...]:
    """A retained subrange does not prove an event survived; absent anchors protect all frames."""
    result: list[EventMap] = []
    for segment in segments:
        source = next(s for s in intake.sources if s.source == segment.source)
        selected = next(s for s in intake.handoff.selections if s.take.clip_id == segment.source.clip_id)
        for requirement in intake.snapshot.approved_coverage:
            if requirement.id not in selected.review.fulfilled:
                continue
            anchor = next((a for a in intake.request.anchors
                           if a.requirement_id == requirement.id and a.source == segment.source),None)
            protected = anchor.source_range if anchor is not None else source.approved_range
            sr = segment.source_range
            if protected.start < sr.start or protected.end > sr.end:
                raise ContractError("anchor", "trim cannot remove any part of a required event or unknown full source")
            start = segment.timeline_range.start+map_frame(
                protected.start-sr.start,source.rate,FILM_CLOCK,rounding="exact")
            end = segment.timeline_range.start+map_frame(
                protected.end-sr.start,source.rate,FILM_CLOCK,rounding="exact")
            mapped = SourceRange(start=start,end=end)
            for other in segments:
                if other.id != segment.id and max(start,other.timeline_range.start) < min(end,other.timeline_range.end):
                    raise ContractError("anchor", "picture overlap covers a protected event/unknown interval")
            sample_range = None
            if requirement.modality == "audio":
                samples = ClockRate(num=intake.profile.sample_rate,den=1)
                sample_range = SourceRange(
                    start=map_frame(start,FILM_CLOCK,samples,rounding="nearest"),
                    end=map_frame(end,FILM_CLOCK,samples,rounding="nearest"))
            result.append(EventMap(requirement_id=requirement.id,source=segment.source,source_anchor=protected,
                                   master_range=mapped,
                                   anchor_mode="observed_anchor" if anchor is not None else "reviewed_full_source",
                                   evidence=anchor.evidence if anchor is not None else None,
                                   audio_sample_range=sample_range,
                                   audio_rounding="nearest" if sample_range is not None else None))
    if {e.requirement_id for e in result} != {r.id for r in intake.snapshot.approved_coverage}:
        raise ContractError("coverage", "timeline does not map the whole approved denominator")
    return tuple(result)
