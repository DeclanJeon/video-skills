"""Actual FilmCraft full-picture + per-frame RGBA plate/text + SoundCraft WAV reintegration, not final human QA."""
import subprocess
import json
import pytest
from conftest import require
from finishing_support import build


@pytest.fixture(scope="module")
def finished(tmp_path_factory):
    return build(tmp_path_factory.mktemp("actual-three-craft-finishing"))


def rgb(path,frame):
    data=subprocess.run(["ffmpeg","-v","error","-i",str(path),"-vf",f"select=eq(n\\,{frame})","-frames:v","1","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True,check=True,timeout=15).stdout
    return data


def test_finishing_when_actual_native_inputs_rejoin_and_independent_video_audio_are_present(finished):
    store,backend,packet,value=finished
    assert value.technical_verified and value.frame_count==144
    assert len(value.artifact_mapping)==38  # base movie +12 motion PNGs +24 literal text PNGs +one real mix
    facts=require("media","probe_video")(store.path.parent,value.artifact)
    assert facts.has_audio is True
    frame=rgb(store.path.parent/value.artifact.path,54)
    center=(45*160+80)*3;corner=(5*160+5)*3
    assert frame[center]>200 and frame[center+1]<40
    assert frame[corner+1]>80 and frame[corner]<40
    text=rgb(store.path.parent/value.artifact.path,30)
    assert sum(all(text[(y*160+x)*3+c]>200 for c in range(3)) for y in range(45,65) for x in range(55,105))>10
    assert not any(a.adopted for a in store.read_recorded().artifacts)


def test_finishing_when_actual_final_native_projection_can_be_registered_without_human_adoption(finished):
    store,backend,packet,value=finished
    state=store.read_recorded()
    artifact=store.record_materialization(state.jobs[-1].id,state.revision)
    assert artifact.pin==value.artifact and artifact.kind=="video"
    assert artifact.adopted is False


def test_finishing_when_consumed_plate_frame_is_lost_cannot_adopt_unchanged_final_file(finished):
    store,backend,packet,value=finished
    frame=next(p for p in value.related_assets if p.path.endswith(".png"))
    path=store.path.parent/frame.path;before=path.read_bytes();path.unlink()
    try:
        with pytest.raises(require("errors","ContractError")):
            backend.observe(store.read_recorded().jobs[-1])
    finally:path.write_bytes(before)


@pytest.mark.parametrize("diagnostic",["offlineMedia","warnings","result_path"])
def test_finishing_when_actual_export_diagnostic_is_not_clean_cannot_materialize(finished,diagnostic):
    store,backend,packet,value=finished
    plan=require("finishing_models","FinishingPlan").model_validate_json(packet.payload)
    path=plan.workspace/"stage3.stdout";before=path.read_bytes()
    raw=json.loads(before)
    if diagnostic=="result_path":raw["result"]["path"]="unrelated-output.mp4"
    else:raw[diagnostic]=["injected diagnostic, not actual vendor warning"]
    path.write_text(json.dumps(raw))
    try:
        with pytest.raises(require("errors","ContractError")):
            backend.observe(store.read_recorded().jobs[-1])
    finally:path.write_bytes(before)


def test_finishing_when_native_manual_projection_changes_requires_reimport(finished):
    store,backend,packet,value=finished
    path=store.path.parent/value.native_project.path;before=path.read_bytes();path.write_bytes(before+b"\n")
    try:
        with pytest.raises(require("errors","ContractError"),match="readback"):
            backend.observe(store.read_recorded().jobs[-1])
    finally:path.write_bytes(before)
