"""Actual isolated FilmCraft editing/export and independent source/order/range/decode checks."""
import json
import subprocess
import pytest
from conftest import require
from support import fixture,update_request,modify_authority
from production.models import State as ProductionState


def setup(root,with_audio=False,audio_codec="aac"):
    request,production,handoff=fixture(root,with_audio=with_audio)
    if audio_codec!="aac":
        profile=json.loads((root/"profile.json").read_text());profile["audio_codec"]=audio_codec
        update_request(root,request,"profile","profile.json",profile)
        modify_authority(root,request,profile_digest=request["profile"]["sha256"])
    path=root/"project.json";path.write_text(json.dumps({"production":production.model_dump(mode="json"),"foreign":{"owner":"preserve"}}))
    intake=require("intake","load_intake")(root,root/"request.json",path)
    timeline=require("timeline","build_timeline")(intake)
    state=require("state_models","PostState")(intake=intake,timelines=(timeline,))
    store=require("ledger","PostStore")(path);store.initialize(state)
    order=require("work_models","WorkOrder").model_validate_json(json.dumps({"id":"NATIVE-PICTURE","domain":"picture","branch":"main","backend":"filmcraft","source_refs":[s.source.model_dump() for s in intake.sources],"output":"renders/native-picture.mp4"}))
    backend=require("backends.filmcraft","FilmCraftBackend")(store,root/"native-work")
    cap=backend.inspect()
    packet=backend.prepare(order,cap,intake.authority)
    return store,backend,packet,cap


def rendered(root):
    store,backend,packet,cap=setup(root)
    with store.transaction(0) as tx:tx.state=require("jobs","reserve_work")(tx.state,packet)
    receipt=backend.execute(packet)
    assert receipt.phase=="succeeded"
    job=store.read_recorded().jobs[0]
    return store,backend,packet,backend.observe(job)


def test_filmcraft_when_real_native_three_cut_project_and_export_are_verified(tmp_path):
    store,backend,packet,value=rendered(tmp_path)
    assert value.technical_verified is True
    assert value.artifact is not None and value.native_project is not None
    assert value.frame_count==144
    assert len(value.mapping)==3
    assert tuple(m.source.clip_id for m in value.mapping)==("C1","C2","C3")
    assert len({m.native_item for m in value.mapping})==3
    output=tmp_path/value.artifact.path
    colors=[]
    for frame in (12,60,108):
        raw=subprocess.run(["ffmpeg","-v","error","-i",str(output),"-vf",f"select=eq(n\\,{frame})","-frames:v","1","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True,check=True,timeout=10).stdout
        pixel=(45*160+80)*3;colors.append(tuple(raw[pixel:pixel+3]))
    assert colors[0][0]>200 and colors[0][1]<30 and colors[0][2]<30
    assert colors[1][1]>80 and colors[1][0]<30 and colors[1][2]<30
    assert colors[2][2]>200 and colors[2][0]<30 and colors[2][1]<30
    assert json.loads(store.path.read_text())["foreign"]=={"owner":"preserve"}
    assert not store.read_recorded().artifacts  # Still not final current master/QA adoption.


def test_filmcraft_when_no_actual_reservation_cannot_dispatch(tmp_path):
    store,backend,packet,cap=setup(tmp_path)
    with pytest.raises(require("errors","ContractError"),match="reserv"):
        backend.execute(packet)


def test_filmcraft_when_prepared_binary_has_drifted_is_rejected(tmp_path):
    store,backend,packet,cap=setup(tmp_path)
    order=packet.order
    wrong=cap.model_copy(update={"binary_sha256":"a"*64})
    with pytest.raises(require("errors","ContractError"),match="binary"):
        backend.prepare(order,wrong,store.read_recorded().intake.authority)


def test_filmcraft_when_completed_native_job_is_not_replayed(tmp_path):
    store,backend,packet,value=rendered(tmp_path)
    before=store.path.read_bytes()
    with pytest.raises(require("errors","ContractError"),match="reserv"):
        backend.execute(packet)
    assert store.path.read_bytes()==before


def test_filmcraft_when_source_is_replaced_after_export_cannot_adopt_old_picture(tmp_path):
    store,backend,packet,value=rendered(tmp_path)
    (tmp_path/"source1.mp4").write_bytes((tmp_path/"source3.mp4").read_bytes())
    with pytest.raises(require("errors","ContractError")):
        backend.observe(store.read_recorded().jobs[0])
    assert store.read_recorded().jobs[0].phase=="succeeded"


def test_filmcraft_when_native_project_range_was_manually_changed_requires_reimport(tmp_path):
    store,backend,packet,value=rendered(tmp_path)
    native=tmp_path/value.native_project.path
    raw=json.loads(native.read_text())
    sequence=next(v["kind"]["Sequence"] for v in raw["project"]["items"].values() if "Sequence" in v["kind"])
    sequence["video_tracks"][0]["items"][0]["source_in"]+=1
    native.write_text(json.dumps(raw))
    with pytest.raises(require("errors","ContractError"),match="readback"):
        backend.observe(store.read_recorded().jobs[0])


def test_filmcraft_when_transcript_storage_fails_known_native_process_fact_is_already_durable(tmp_path,monkeypatch):
    from pathlib import Path
    store,backend,packet,cap=setup(tmp_path)
    with store.transaction(0) as tx:tx.state=require("jobs","reserve_work")(tx.state,packet)
    plan=require("backends.film_models","FilmPlan").model_validate_json(packet.payload)
    original=Path.write_bytes
    def fail_one(path,data):
        if path==plan.workspace/"stage1.stdout":raise OSError("fixture transcript storage failure")
        return original(path,data)
    monkeypatch.setattr(Path,"write_bytes",fail_one)
    with pytest.raises(OSError,match="transcript"):
        backend.execute(packet)
    known=store.read_recorded().jobs[0]
    assert known.job_id is not None
    assert known.phase=="running"
    assert len(known.observations)>=1


def test_filmcraft_when_export_file_is_partial_cannot_materialize(tmp_path):
    store,backend,packet,value=rendered(tmp_path)
    (tmp_path/value.artifact.path).write_bytes(b"partial file")
    with pytest.raises(require("errors","ContractError")):
        backend.observe(store.read_recorded().jobs[0])
