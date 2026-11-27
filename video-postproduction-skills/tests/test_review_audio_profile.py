"""Audio-bearing actual FilmCraft picture and independent actual encoding checks, not only finishing or meters."""
import pytest
from conftest import require
from test_filmcraft import setup


def test_picture_when_explicit_audio_codec_is_unsupported_rejects_before_dispatch(tmp_path):
    with pytest.raises(require("errors","ContractError")) as raised:
        setup(tmp_path,with_audio=True,audio_codec="flac")
    assert raised.value.stage=="format"
    assert not tuple((tmp_path/"native-work").glob("run-*"))


@pytest.fixture(scope="module")
def actual_audio_picture(tmp_path_factory):
    root=tmp_path_factory.mktemp("native-audio-profile")
    store,backend,packet,cap=setup(root,with_audio=True)
    job=store.record_reservation(packet,store.read_recorded().revision)
    assert backend.execute(packet).phase=="succeeded"
    value=backend.observe(store.read_recorded().jobs[0])
    return store,value


def test_encoding_when_actual_picture_matches_explicit_audio_profile_passes(actual_audio_picture):
    store,value=actual_audio_picture
    require("profile_checks","verify_encoding")(store.path.parent,value.artifact,store.read_recorded().intake.profile)


@pytest.mark.parametrize("changes",[{"audio_codec":"flac"},{"video_codec":"hevc"},{"sample_rate":44100},{"channels":1}])
def test_encoding_when_real_native_output_violates_declared_codec_or_layout_rejects(actual_audio_picture,changes):
    store,value=actual_audio_picture
    profile=store.read_recorded().intake.profile.model_copy(update=changes)
    with pytest.raises(require("errors","ContractError")) as raised:
        require("profile_checks","verify_encoding")(store.path.parent,value.artifact,profile)
    assert raised.value.stage=="encoding"


def test_encoding_when_container_brand_is_unknown_does_not_invent_mp4_compliance():
    actual=require('profile_checks','Container').model_validate({'format_name':'mov,mp4,m4a,3gp,3g2,mj2','tags':{}})
    assert require('profile_checks','container_matches')('mp4',actual) is False


def test_picture_when_raw_reserved_packet_requests_unsupported_codec_cannot_bypass_prepare(tmp_path):
    import json
    from uuid import uuid4
    from support import fixture,update_request,modify_authority
    request,production,handoff=fixture(tmp_path,with_audio=True)
    profile=json.loads((tmp_path/'profile.json').read_text());profile['audio_codec']='flac'
    update_request(tmp_path,request,'profile','profile.json',profile)
    modify_authority(tmp_path,request,profile_digest=request['profile']['sha256'])
    path=tmp_path/'project.json';path.write_text(json.dumps({'production':production.model_dump(mode='json')}))
    intake=require('intake','load_intake')(tmp_path,tmp_path/'request.json',path)
    timeline=require('timeline','build_timeline')(intake)
    state=require('state_models','PostState')(intake=intake,timelines=(timeline,))
    store=require('ledger','PostStore')(path);store.initialize(state)
    backend=require('backends.filmcraft','FilmCraftBackend')(store,tmp_path/'raw-native')
    cap=backend.inspect();owner=uuid4().hex
    order=require('work_models','WorkOrder').model_validate_json(json.dumps({'id':'RAW-UNSUPPORTED','domain':'picture','branch':'main','backend':'filmcraft',
        'source_refs':[s.source.model_dump() for s in intake.sources],'output':'raw.mp4'}))
    plan=require('backends.film_models','FilmPlan')(workspace=(backend.workspace/('run-'+owner)).absolute(),owner=owner,capability=cap,
        timeline=timeline,sources=intake.sources,profile=intake.profile)
    packet=require('work_models','RequestPacket')(order=order,input_fingerprint=require('revisions','work_fingerprint')(state,order),payload=plan.model_dump_json())
    store.record_reservation(packet,store.read_recorded().revision)
    with pytest.raises(require('errors','ContractError')) as raised:backend.execute(packet)
    assert raised.value.stage=='format' and not plan.workspace.exists()
