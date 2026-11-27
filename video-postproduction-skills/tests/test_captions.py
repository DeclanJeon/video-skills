"""Exact approved text/speaker and real supplied timing map, never invented ASR/word/translation approvals."""
import json
import pytest
from conftest import require
from support import json_pin
from test_ledger import built,project,prepare


def source(path,state,**changes):
    raw={"format":"post-caption-source/1","id":"CAP-1","source":state.intake.sources[1].source.model_dump(),
         "source_range":{"start":0,"end":24},"text":"Hello","speaker":"Actor A","kind":"dialogue","words":[],"approval_kind":"reported"}
    pin=json_pin(path.parent,"approved-caption.json",raw)
    return require("caption_models","SourceCaption").model_validate_json(json.dumps({
        **raw,"approval":pin.model_dump(),"word_highlight":False,**changes}))


def test_captions_when_source_times_map_to_current_master_without_paraphrase(project):
    path,store,state,production=prepare(project)
    cue=source(path,state)
    require("captions","verify_caption_sources")(path.parent,(cue,))
    mapped=require("captions","map_cues")((cue,),state.timelines[0])
    clock=state.timelines[0].clock.num
    assert (mapped[0].master_range.start,mapped[0].master_range.end)==(2*clock,3*clock)
    assert mapped[0].text=="Hello" and mapped[0].speaker=="Actor A"


@pytest.mark.parametrize("changes",[{"text":"Changed quote"},{"speaker":"Actor B"},{"kind":"translation"}])
def test_captions_when_text_speaker_or_translation_is_not_in_exact_approved_source_rejects(project,changes):
    path,store,state,production=prepare(project)
    cue=source(path,state,**changes)
    with pytest.raises(require("errors","ContractError")):
        require("captions","verify_caption_sources")(path.parent,(cue,))


def test_captions_when_sentence_timing_cannot_be_invented_as_word_timestamps(project):
    path,store,state,production=prepare(project)
    with pytest.raises(require("errors","ContractError")):
        cue=source(path,state,word_highlight=True)
        require("captions","map_cues")((cue,),state.timelines[0])


def test_captions_when_old_cues_after_timeline_revision_are_stale(project):
    path,store,state,production=prepare(project)
    cue=source(path,state)
    mapped=require("captions","map_cues")((cue,),state.timelines[0])
    changed=state.timelines[0].model_copy(update={"revision":2})
    with pytest.raises(require("errors","ContractError"),match="stale"):
        require("captions","verify_mapped_cues")(mapped,changed)
