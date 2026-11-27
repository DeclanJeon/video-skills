"""Actual sample count/layout/decode and missing/fake-stem boundary; no meter-only or listening claim."""
import json
import math
import pytest
from conftest import require
from audio_support import tone,stem
from support import fixture,update_request,modify_authority


def test_audio_when_real_pcm_is_independently_decoded_and_measured(tmp_path):
    source=tone(tmp_path)
    pin=require("models","Pin").model_validate_json(source.model_dump_json())
    facts=require("audio","probe_audio")(tmp_path,pin)
    assert (facts.sample_rate,facts.channels,facts.sample_count)==(48000,2,24000)
    assert abs(facts.rms-0.2/math.sqrt(2))<0.00002
    assert len(facts.samples)==48000


@pytest.mark.parametrize("changes",[{"sample_count":23999},{"channels":1},{"sample_rate":44100},
    {"origin":"derived_from_mixed","role":"DX"}])
def test_stem_when_header_or_independent_origin_is_not_actual(tmp_path,changes):
    raw=stem(tmp_path)
    raw.update(changes)  # Keep physical stereo bytes fixed; mutate only the untrusted declaration.
    parsed=require("audio_models","StemAsset").model_validate_json(json.dumps(raw))
    with pytest.raises(require("errors","ContractError")):
        require("audio","verify_stem")(tmp_path,parsed)


def test_stem_when_actual_supplied_mono_is_not_mislabeled_as_stereo(tmp_path):
    raw=stem(tmp_path,channels=1)
    parsed=require("audio_models","StemAsset").model_validate_json(json.dumps(raw))
    actual=require("audio","verify_stem")(tmp_path,parsed)
    assert actual.channels==1 and actual.sample_count==24000


def test_intake_when_required_actual_separate_stem_is_supplied_can_be_adopted(tmp_path):
    request,production,handoff=fixture(tmp_path)
    provided=stem(tmp_path)
    request["stems"]=[provided]
    brief=json.loads((tmp_path/"brief.json").read_text());brief["required_stems"]=[provided["id"]]
    update_request(tmp_path,request,"brief","brief.json",brief)
    modify_authority(tmp_path,request,brief_digest=request["brief"]["sha256"],allowed_changes=["audio"],
                     assets=[provided["asset"],provided["independence_evidence"]])
    (tmp_path/"request.json").write_text(json.dumps(request))
    result=require("intake","load_intake")(tmp_path,tmp_path/"request.json")
    assert result.request.stems[0].id=="toneA"
    assert result.request.stems[0].sample_count==24000
