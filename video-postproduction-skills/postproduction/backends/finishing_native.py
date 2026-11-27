"""Actual FilmCraft still-image per-frame hold and movie/WAV placement, using observed schema17 resource IDs."""
import json
from pathlib import Path

from pydantic import JsonValue

from postproduction.backends.base import ArtifactMapping
from postproduction.backends.film_readback import read_project
from postproduction.backends.process import IsolatedProcess, SandboxScope
from postproduction.clock import map_frame
from postproduction.common import ClockRate, SourceRange
from postproduction.errors import ContractError
from postproduction.finishing_models import FinishingPlan, NativePlacement
from postproduction.timeline_map import FILM_CLOCK


def runner(plan: FinishingPlan, root: Path) -> IsolatedProcess:
    return IsolatedProcess(SandboxScope(plan.workspace,plan.owner,
        tuple(root/p.path for p in plan.inputs.pins),memory_bytes=8589934592))


def encode(steps: list[dict[str,JsonValue]]) -> bytes:
    return ("\n".join(json.dumps(s) for s in steps)+"\n").encode()


def imports(plan: FinishingPlan, root: Path) -> bytes:
    profile = plan.inputs.profile
    return encode([{"id":"file.newProject","params":{"name":"Owned native finishing"}},
        {"id":"file.newSequence","params":{"name":"Finished","width":profile.width,"height":profile.height,
        "fps":profile.fps.num/profile.fps.den,"sampleRate":profile.sample_rate,"video":1+len(plan.inputs.plates),"audio":1}},
        {"id":"file.import","params":{"paths":[str(root/p.path) for p in plan.inputs.pins]}}])


def ids_for(plan: FinishingPlan, root: Path) -> dict[str,int]:
    project = read_project(plan.workspace/"native.fcproj")
    result: dict[str,int] = {}
    for pin in plan.inputs.pins:
        matches = tuple(i for i in project.project.items.values() if i.kind.media is not None
            and Path(i.kind.media.media.file.path)==root/pin.path)
        if len(matches)!=1 or matches[0].kind.media is None or matches[0].kind.media.offline:
            raise ContractError("readback", "exact actual imported movie/still/WAV resource missing/offline")
        result[pin.path] = matches[0].id
    return result


def expected_placements(plan: FinishingPlan) -> tuple[NativePlacement, ...]:
    inputs,profile = plan.inputs,plan.inputs.profile
    total_ticks = map_frame(inputs.total_frames,profile.fps,FILM_CLOCK,rounding="exact")
    rows = [NativePlacement(source=inputs.picture.pin,track="V1",start_tick=0,duration_ticks=total_ticks,
        source_range=SourceRange(start=0,end=inputs.total_frames),source_unit="frames")]
    frame_tick = map_frame(1,profile.fps,FILM_CLOCK,rounding="exact")
    for track,plate in enumerate(inputs.plates,2):
        for index,pin in enumerate(plate.manifest.frames):
            rows.append(NativePlacement(source=pin,track=f"V{track}",start_tick=(plate.start_frame+index)*frame_tick,
                duration_ticks=frame_tick,source_range=SourceRange(start=0,end=1),source_unit="still"))
    samples = map_frame(inputs.total_frames,profile.fps,ClockRate(num=profile.sample_rate,den=1),rounding="exact")
    rows.append(NativePlacement(source=inputs.mix.pin,track="A1",start_tick=0,duration_ticks=total_ticks,
        source_range=SourceRange(start=0,end=samples),source_unit="samples"))
    return tuple(rows)


def placements(plan: FinishingPlan, root: Path) -> bytes:
    ids = ids_for(plan,root)
    return encode([{"id":"timeline.place","params":{"item":ids[row.source.path],"track":row.track,"time":row.start_tick,"sourceIn":0,
        "duration":row.duration_ticks,"insert":False,"video":row.track.startswith("V"),"audio":row.track.startswith("A")}}
        for row in expected_placements(plan)])


def readback(plan: FinishingPlan, root: Path) -> tuple[ArtifactMapping, ...]:
    project = read_project(plan.workspace/"native.fcproj")
    ids = ids_for(plan,root)
    sequences = tuple(i.kind.sequence for i in project.project.items.values() if i.kind.sequence is not None)
    if len(sequences)!=1:
        raise ContractError("readback", "exact owned finishing sequence required")
    sequence = sequences[0]
    profile = plan.inputs.profile
    s = sequence.settings
    if (s.width,s.height,s.frame_rate,s.sample_rate)!=(profile.width,profile.height,profile.fps,profile.sample_rate):
        raise ContractError("readback", "finishing sequence clock/size/sample rate differs")
    expected = expected_placements(plan)
    if sum(len(t.items) for t in (*sequence.video_tracks,*sequence.audio_tracks))!=len(expected):
        raise ContractError("readback", "unexpected/duplicate/missing finishing clip")
    result: list[ArtifactMapping] = []
    for row in expected:
        tracks = sequence.video_tracks if row.track.startswith("V") else sequence.audio_tracks
        clips = tracks[int(row.track[1:])-1].items
        matches = tuple(c for c in clips if (c.item,c.start,c.duration,c.source_in,c.speed,c.reverse,c.enabled)==(
            ids[row.source.path],row.start_tick,row.duration_ticks,0,1,False,True))
        if len(matches)!=1:
            raise ContractError("readback", "actual native finishing source/time/frame/sample placement differs")
        result.append(ArtifactMapping(source=row.source,native_item=ids[row.source.path],native_clip=matches[0].id,
            source_unit=row.source_unit,source_range=row.source_range,
            timeline_range=SourceRange(start=row.start_tick,end=row.start_tick+row.duration_ticks)))
    return tuple(result)
