"""Quoted/translated/editorial text and real word spans are distinct, source-pinned reported approvals."""
from typing import Literal, Self

from pydantic import model_validator

from postproduction.common import Digest, Frozen, Nonempty, Pin, SourceRange
from postproduction.errors import ContractError
from postproduction.intake_models import SourceRef


class WordStamp(Frozen):
    text: Nonempty
    characters: SourceRange
    source_range: SourceRange


class ApprovedCaption(Frozen):
    format: Literal["post-caption-source/1"]
    id: Nonempty
    source: SourceRef
    source_range: SourceRange
    text: Nonempty
    speaker: Nonempty
    kind: Literal["dialogue","translation","editorial","title"]
    words: tuple[WordStamp, ...] = ()
    timing_evidence: Pin | None = None
    approval_kind: Literal["reported"]

    @model_validator(mode="after")
    def actual_spans(self) -> Self:
        if self.words and self.timing_evidence is None:
            raise ContractError("word", "actual supplied word timing evidence required")
        previous = self.source_range.start
        for word in self.words:
            if (not self.source_range.start <= word.source_range.start < word.source_range.end <= self.source_range.end
                or word.source_range.start < previous
                or word.characters.end > len(self.text)
                or self.text[word.characters.start:word.characters.end] != word.text):
                raise ContractError("word", "actual word source/character span differs from approved literal text/range")
            previous = word.source_range.end
        return self


class SourceCaption(ApprovedCaption):
    approval: Pin
    word_highlight: bool = False


class MappedWord(Frozen):
    text: Nonempty
    master_range: SourceRange


class CaptionCue(Frozen):
    id: Nonempty
    source: SourceRef
    source_range: SourceRange
    source_approval: Pin
    text: Nonempty
    speaker: Nonempty
    kind: Literal["dialogue","translation","editorial","title"]
    master_range: SourceRange
    timeline_digest: Digest
    words: tuple[MappedWord, ...] = ()
    word_highlight: bool = False
