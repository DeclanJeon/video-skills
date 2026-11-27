"""Pure exact source→master timing; actual approved source comparisons stay separate from reported perception."""
from fractions import Fraction
from pathlib import Path

from postproduction.caption_models import ApprovedCaption, CaptionCue, MappedWord, SourceCaption
from postproduction.common import SourceRange
from postproduction.errors import ContractError
from postproduction.files import read_model, verified_file
from postproduction.timeline import timeline_digest
from postproduction.timeline_models import PostTimeline, TimelineSegment


def verify_caption_sources(root: Path, cues: tuple[SourceCaption, ...]) -> None:
    """No caption/speaker/translation/word edits acquire approval from a renderer, ASR or matching duration."""
    for cue in cues:
        actual = read_model(root,cue.approval,ApprovedCaption)
        declared = ApprovedCaption.model_validate_json(cue.model_dump_json(exclude={"approval","word_highlight"}))
        if actual != declared:
            raise ContractError("caption", "exact approved source text/speaker/kind/timing differs")
        if cue.timing_evidence is not None:
            _ = verified_file(root,cue.timing_evidence)


def mapped_range(segment: TimelineSegment, source: SourceRange) -> SourceRange:
    """Use the actual edit span, including retime; reject fractional ticks rather than invent a rounding policy."""
    start = Fraction((source.start-segment.source_range.start)*segment.timeline_range.length,segment.source_range.length)
    end = Fraction((source.end-segment.source_range.start)*segment.timeline_range.length,segment.source_range.length)
    if start.denominator != 1 or end.denominator != 1:
        raise ContractError("caption", "cue requires explicit supported rounding policy, not guessed timestamps")
    return SourceRange(start=segment.timeline_range.start+start.numerator,
                       end=segment.timeline_range.start+end.numerator)


def map_cues(cues: tuple[SourceCaption, ...], timeline: PostTimeline) -> tuple[CaptionCue, ...]:
    """Map exact supplied words/sentences once; cut-crossing/repeated-source ambiguity requires explicit recuration."""
    if len({c.id for c in cues}) != len(cues):
        raise ContractError("caption", "duplicate caption source identity")
    mapped: list[CaptionCue] = []
    for cue in cues:
        candidates = tuple(s for s in timeline.segments if s.source == cue.source
            and s.source_range.start <= cue.source_range.start < cue.source_range.end <= s.source_range.end)
        if len(candidates) != 1:
            raise ContractError("caption", "source cue is trimmed/cut-crossing or ambiguous repeated source; recurate explicitly")
        if cue.word_highlight and not cue.words:
            raise ContractError("word", "sentence timing cannot be fabricated into word timestamps")
        segment = candidates[0]
        mapped.append(CaptionCue(id=cue.id,source=cue.source,source_range=cue.source_range,source_approval=cue.approval,
            text=cue.text,speaker=cue.speaker,kind=cue.kind,master_range=mapped_range(segment,cue.source_range),
            timeline_digest=timeline_digest(timeline),word_highlight=cue.word_highlight,
            words=tuple(MappedWord(text=w.text,master_range=mapped_range(segment,w.source_range)) for w in cue.words)))
    return tuple(mapped)


def verify_mapped_cues(cues: tuple[CaptionCue, ...], timeline: PostTimeline) -> None:
    """Any changed timeline decision invalidates previously mapped positions, even if total duration happens to match."""
    digest = timeline_digest(timeline)
    if any(c.timeline_digest != digest for c in cues):
        raise ContractError("stale", "caption cues refer to an old timeline edit/retime revision")
