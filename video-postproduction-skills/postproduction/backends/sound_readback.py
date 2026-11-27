"""Actual session sample mapping and independent waveform oracle, not meters or a listening certificate."""
from pathlib import Path

from postproduction.audio import AudioFacts, probe_audio
from postproduction.backends.base import AudioMapping
from postproduction.backends.sound_models import NativeAudioImport, SoundPlan, SoundSummary
from postproduction.common import SourceRange
from postproduction.errors import ContractError


def check_session(plan: SoundPlan, session: SoundSummary, imported: tuple[NativeAudioImport, ...]) -> tuple[AudioMapping, ...]:
    """Check actual channels/source frames/tracks/sample positions, including non-recording private session."""
    recipe = plan.recipe
    if ((session.sample_rate,session.frame_rate,session.main_format) != (recipe.sample_rate,"24","Stereo")
        or session.transport.playing or session.transport.recording or len(imported) != len(recipe.cues)):
        raise ContractError("readback", "native session rate/timecode/layout/cue inventory differs")
    audio = tuple(t for t in session.tracks if t.kind == "audio")
    if len(audio) != len(recipe.cues) or any(t.record_arm or t.mute or t.inactive for t in session.tracks):
        raise ContractError("readback", "unexpected/armed/muted/inactive actual native track")
    result: list[AudioMapping] = []
    for cue,item in zip(recipe.cues,imported):
        stem = next(s for s in plan.stems if s.id == cue.stem_id)
        track = next((t for t in audio if t.id == item.track),None)
        source = next((s for s in session.sources if s.id == item.source),None)
        if (track is None or source is None or not source.loaded or len(track.clips) != 1
            or (source.channels,source.frames,item.channels,item.frames) !=
            (stem.channels,stem.sample_count,stem.channels,stem.sample_count)):
            raise ContractError("readback", "actual source/channel/track inventory differs from supplied stems")
        clip = track.clips[0]
        if ((clip.id,clip.source,clip.start,clip.length,clip.offset,clip.end,clip.muted,clip.gain_db,track.volume_db)
            != (item.clip,item.source,cue.at_sample,stem.sample_count,0,cue.at_sample+stem.sample_count,
                False,0,cue.gain_db) or track.pan != ((-1,1) if stem.channels == 2 else (0,))):
            raise ContractError("readback", "native clip/sample offset/channel/gain map differs")
        result.append(AudioMapping(stem_id=stem.id,native_source=item.source,native_track=item.track,
                                   native_clip=item.clip,source_samples=SourceRange(start=0,end=stem.sample_count),
                                   mix_samples=SourceRange(start=cue.at_sample,end=cue.at_sample+stem.sample_count)))
    return tuple(result)


def compare_waveform(plan: SoundPlan, actual: AudioFacts, root: Path) -> None:
    """Every decoded sample must match explicitly planned gain/offset/layout; no normalize/dither/stem invention."""
    recipe = plan.recipe
    if (actual.sample_rate,actual.channels,actual.sample_count) != (
        recipe.sample_rate,recipe.channels,recipe.sample_count):
        raise ContractError("audio", "actual bounce rate/channel/sample duration differs")
    expected = [0.0]*(recipe.sample_count*2)
    for cue in recipe.cues:
        stem = next(s for s in plan.stems if s.id == cue.stem_id)
        source = probe_audio(root,stem.asset)
        gain = 10**(cue.gain_db/20)
        for frame in range(source.sample_count):
            for channel in range(2):
                value = source.samples[frame*source.channels+(channel if source.channels == 2 else 0)]
                coefficient = 1.0 if source.channels == 2 else 10**(recipe.mono_center_db/20)
                expected[(cue.at_sample+frame)*2+channel] += value*gain*coefficient
    if max(abs(a-b) for a,b in zip(actual.samples,expected)) > 0.000002:
        raise ContractError("audio", "independent full waveform differs from actual supplied cue/gain/sample plan")
