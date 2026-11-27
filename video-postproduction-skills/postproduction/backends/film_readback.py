"""Check actual native item/clip/range/timebase linkage rather than assuming predictable resource IDs."""
from pathlib import Path

from pydantic import ValidationError

from postproduction.backends.base import NativeMapping
from postproduction.backends.film_models import FilmPlan, FilmProject, NativeItem
from postproduction.clock import map_frame
from postproduction.common import SourceRange
from postproduction.errors import ContractError
from postproduction.intake_models import SourceRef
from postproduction.timeline_map import FILM_CLOCK


def read_project(path: Path) -> FilmProject:
    """Parse only the actual verified native schema, preserving the original file as evidence."""
    try:
        return FilmProject.model_validate_json(path.read_bytes())
    except (ValidationError,OSError) as exc:
        raise ContractError("readback", "native project is missing/unsupported/malformed") from exc


def imported_items(project: FilmProject, plan: FilmPlan, root: Path) -> dict[SourceRef,NativeItem]:
    """Match actual file paths and native properties, refusing offline/placeholder source substitutions."""
    result: dict[SourceRef,NativeItem] = {}
    for source in plan.sources:
        matches = tuple(item for item in project.project.items.values()
                        if item.kind.media is not None
                        and Path(item.kind.media.media.file.path) == (root/source.asset.path).absolute())
        if len(matches) != 1 or matches[0].kind.media is None:
            raise ContractError("readback", "source has no unique actual native file item")
        item = matches[0]
        media = item.kind.media
        if media is None or media.offline or media.info.video is None:
            raise ContractError("readback", "offline/placeholder/no-picture native input refused")
        video = media.info.video
        if ((video.width,video.height,video.frame_rate, bool(media.info.audio_streams))
            != (source.width,source.height,source.rate,source.has_audio)):
            raise ContractError("readback", "native source properties differ from pinned decoded inputs")
        result[source.source] = item
    return result


def check_timeline(project: FilmProject, plan: FilmPlan, root: Path) -> tuple[NativeMapping, ...]:
    """Compare every placed picture item and exact source/timeline tick interval."""
    media = imported_items(project,plan,root)
    sequences = tuple(i.kind.sequence for i in project.project.items.values() if i.kind.sequence is not None)
    if len(sequences) != 1:
        raise ContractError("readback", "one exact owned native sequence required")
    sequence = sequences[0]
    settings = sequence.settings
    if (settings.width,settings.height,settings.frame_rate,settings.sample_rate) != (
        plan.profile.width,plan.profile.height,plan.profile.fps,plan.profile.sample_rate):
        raise ContractError("readback", "native sequence does not match approved exact delivery profile")
    clips = tuple(c for t in sequence.video_tracks for c in t.items)
    if len(clips) != len(plan.timeline.segments):
        raise ContractError("readback", "unexpected native picture clips/gaps/duplicates")
    result: list[NativeMapping] = []
    for clip,segment in zip(clips,plan.timeline.segments):
        source = next(s for s in plan.sources if s.source == segment.source)
        expected_in = map_frame(segment.source_range.start,source.rate,FILM_CLOCK,rounding="exact")
        expected_duration = segment.timeline_range.length
        if (clip.item,clip.start,clip.duration,clip.source_in,clip.speed,clip.reverse,clip.enabled) != (
            media[segment.source].id,segment.timeline_range.start,expected_duration,expected_in,1,False,True):
            raise ContractError("readback", "native clip/source/range/playback map was changed")
        result.append(NativeMapping(source=segment.source,native_item=clip.item,native_clip=clip.id,
                                    source_range=SourceRange(start=segment.source_range.start,end=segment.source_range.end),
                                    timeline_range=segment.timeline_range))
    return tuple(result)
