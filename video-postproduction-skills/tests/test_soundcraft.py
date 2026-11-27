"""Real native sample-offset/gain/stereo mix and independent waveform comparison; not listening QA."""
import json
import pytest
from conftest import require
from support import fixture,json_pin,update_request,modify_authority
from audio_support import stem


def setup(root,mono=False,**recipe_changes):
    request,production,handoff=fixture(root)
    stems=[stem(root,"toneA",channels=1 if mono else 2),stem(root,"toneB",frequency=880)]
    request["stems"]=stems
    brief=json.loads((root/"brief.json").read_text());brief["required_stems"]=[s["id"] for s in stems]
    update_request(root,request,"brief","brief.json",brief)
    assets=[p for s in stems for p in (s["asset"],s["independence_evidence"])]
    modify_authority(root,request,brief_digest=request["brief"]["sha256"],allowed_changes=["audio"],assets=assets)
    (root/"request.json").write_text(json.dumps(request))
    path=root/"project.json";path.write_text(json.dumps({"production":production.model_dump(mode="json")}))
    intake=require("intake","load_intake")(root,root/"request.json",path)
    timeline=require("timeline","build_timeline")(intake)
    state=require("state_models","PostState")(intake=intake,timelines=(timeline,))
    store=require("ledger","PostStore")(path);store.initialize(state)
    picture=production.selections[0].take.asset
    recipe={"format":"post-sound/1","sample_rate":48000,"channels":2,"sample_count":96000,
        "picture":picture.model_dump(),"picture_fps":{"num":24,"den":1},
        "cues":[{"id":"CUE-A","stem_id":"toneA","at_sample":0,"gain_db":-6},
                {"id":"CUE-B","stem_id":"toneB","at_sample":24000,"gain_db":-12}],**recipe_changes}
    rp=json_pin(root,"sound-recipe.json",recipe)
    order=require("work_models","WorkOrder").model_validate_json(json.dumps({"id":"NATIVE-SOUND","domain":"sound","branch":"main","backend":"soundcraft","source_refs":[intake.sources[0].source.model_dump()],"recipe":rp.model_dump(),"dependencies":[*assets,picture.model_dump()],"output":"mixes/current.wav"}))
    backend=require("backends.soundcraft","SoundCraftBackend")(store,root/"sound-native")
    cap=backend.inspect()
    return store,backend,order,cap


def rendered(root,mono=False):
    store,backend,order,cap=setup(root,mono=mono)
    packet=backend.prepare(order,cap,store.read_recorded().intake.authority)
    with store.transaction(0) as tx:tx.state=require("jobs","reserve_work")(tx.state,packet)
    result=backend.execute(packet);assert result.phase=="succeeded"
    return store,backend,packet,backend.observe(store.read_recorded().jobs[0])


@pytest.mark.parametrize("mono",[False,True])
def test_soundcraft_when_actual_layout_sample_offsets_and_gain_match_independent_audio(tmp_path,mono):
    store,backend,packet,value=rendered(tmp_path,mono)
    assert value.media_kind=="audio"
    assert (value.sample_count,value.sample_rate,value.channels)==(96000,48000,2)
    assert value.technical_verified is True
    assert len(value.audio_mapping)==2
    assert value.audio_mapping[1].mix_samples.start==24000
    assert value.audio_mapping[0].native_track!=value.audio_mapping[1].native_track
    assert not store.read_recorded().artifacts  # A native mix is not a human-listened approved master.


@pytest.mark.parametrize("changes",[{"channels":6},{"sample_rate":44100},{"sample_count":95000},{"format":"AAF"}])
def test_soundcraft_when_unsupported_or_mismatched_format_clock_length_is_not_guessed(tmp_path,changes):
    store,backend,order,cap=setup(tmp_path,**changes)
    with pytest.raises(require("errors","ContractError")):
        backend.prepare(order,cap,store.read_recorded().intake.authority)


def test_soundcraft_when_actual_bounce_replaced_with_silence_is_not_adopted(tmp_path):
    store,backend,packet,value=rendered(tmp_path)
    from audio_support import tone
    tone(tmp_path,"not-the-mix.wav",frames=96000,frequency=0)
    (tmp_path/value.artifact.path).write_bytes((tmp_path/"not-the-mix.wav").read_bytes())
    with pytest.raises(require("errors","ContractError")):
        backend.observe(store.read_recorded().jobs[0])


def test_soundcraft_when_native_track_or_sample_offset_changes_requires_reimport(tmp_path):
    store,backend,packet,value=rendered(tmp_path)
    project=tmp_path/value.native_project.path
    raw=project.read_text();project.write_text(raw+"\n ")  # Exact native bytes are pinned even if semantic JSON is similar.
    with pytest.raises(require("errors","ContractError"),match="readback"):
        backend.observe(store.read_recorded().jobs[0])
