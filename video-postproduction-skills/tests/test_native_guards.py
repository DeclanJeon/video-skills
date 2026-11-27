"""Actual source/native filesystem and interrupted-job safety. Diagnostic failures are deliberately injected."""
import hashlib
import json
import subprocess
import pytest
from conftest import require
from support import fixture,pin
from production.models import ContractError as ProductionError
from test_filmcraft import setup,rendered
from test_effectcraft import setup as effect_setup
from test_soundcraft import setup as sound_setup


def tree(root):
    return {p.relative_to(root).as_posix():(p.stat().st_mode,hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None)
            for p in root.rglob("*")}


@pytest.mark.parametrize("tool",["filmcraft","effectcraft","soundcraft"])
def test_prepare_when_existing_capability_is_known_does_not_write_native_source_or_ledger(tmp_path,tool):
    # Given: capabilities already inspected in a private workspace; no native execution.
    if tool=="filmcraft":
        store,backend,packet,cap=setup(tmp_path);order=packet.order
    else:
        store,backend,order,cap=(effect_setup if tool=="effectcraft" else sound_setup)(tmp_path)
    before=tree(tmp_path)
    # When: only the immutable preparation runs.
    packet=backend.prepare(order,cap,store.read_recorded().intake.authority)
    # Then: no project/source/settings/output/reservation is modified or created.
    assert packet.order==order and tree(tmp_path)==before


def test_source_when_actual_mixed_fps_cannot_enter_handoff_without_verified_conform(tmp_path):
    # Given/When: real 24/30/24fps sources are submitted to the actual upstream review/handoff path.
    with pytest.raises(ProductionError,match="conform"):
        fixture(tmp_path,rates=(24,30,24))
    # Then: independently observe the differing clocks and no fabricated usable post handoff.
    observed=[require("media","probe_video")(tmp_path,require("admission","local_pin")(pin(tmp_path,f"source{i}.mp4"))).rate.num for i in (1,2,3)]
    assert observed==[24,30,24] and not (tmp_path/"handoff.json").exists()


def test_source_when_actual_pts_are_variable_cannot_be_admitted_without_conform(tmp_path):
    # Given: actual VFR encoded source with deliberately nonuniform PTS.
    request,state,handoff=fixture(tmp_path)
    subprocess.run(["ffmpeg","-v","error","-f","lavfi","-i","color=blue:s=160x90:r=24:d=2",
        "-vf","setpts=(N+floor(N/2))/(24*TB)","-fps_mode","vfr","-c:v","libx264",str(tmp_path/"vfr.mp4")],
        check=True,capture_output=True,timeout=30)
    asset=pin(tmp_path,"vfr.mp4")
    facts=require("media","probe_video")(tmp_path,require("admission","local_pin")(asset))
    assert facts.cfr is False
    selected=state.selections[0]
    take=selected.take.model_copy(update={"asset":asset,"frame_count":facts.frame_count,"fps":facts.rate.num/facts.rate.den,"cfr":False})
    config=selected.approval.configurations[0].model_copy(update={"reuse_source":asset})
    grant=selected.approval.model_copy(update={"allowed_hashes":(asset.sha256,),"configurations":(config,)})
    playback=selected.review.playback.model_copy(update={"asset_hash":asset.sha256})
    selected=selected.model_copy(update={"take":take,"approval":grant,"review":selected.review.model_copy(update={"playback":playback})})
    state=state.model_copy(update={"selections":(selected,*state.selections[1:])})
    # When/Then: independently decoded nonuniform timestamps require an implemented conform path.
    with pytest.raises(require("errors","ContractError"),match="conform"):
        require("admission","admit_source")(state,selected,tmp_path)


@pytest.mark.parametrize("diagnostic",["offlineMedia","warnings"])
def test_picture_when_export_reports_offline_or_warning_cannot_materialize(tmp_path,diagnostic):
    store,backend,packet,value=rendered(tmp_path)
    plan=require("backends.film_models","FilmPlan").model_validate_json(packet.payload)
    stdout=plan.workspace/"stage3.stdout"
    raw=json.loads(stdout.read_text())
    raw[diagnostic]=["injected export diagnostic; not a genuine vendor warning"]
    stdout.write_text(json.dumps(raw))
    with pytest.raises(require("errors","ContractError")):
        backend.observe(store.read_recorded().jobs[0])


def test_picture_when_real_second_native_batch_partially_fails_cannot_blindly_replay(tmp_path,monkeypatch):
    # Given: narrow script seam produces one actual valid edit then one invalid native command.
    import postproduction.backends.filmcraft as film
    store,backend,packet,cap=setup(tmp_path)
    original=film.place_script
    def interrupted(plan,root):
        first=original(plan,root).splitlines()[0]
        return first+b'\n{"id":"fixture.deliberate_invalid_command","params":{}}\n'
    monkeypatch.setattr(film,"place_script",interrupted)
    store.record_reservation(packet,store.read_recorded().revision)
    # When: the actual existing CLI executes the incomplete native batch.
    try:
        backend.execute(packet)
    except require("errors","ContractError"):
        pass
    job=store.read_recorded().jobs[0]
    assert job.job_id is not None and job.phase!="succeeded"
    before=tree(tmp_path)
    # Then: exact known incomplete attempt is retained and duplicate native apply is denied.
    with pytest.raises(require("errors","ContractError"),match="reserv"):
        backend.execute(packet)
    assert tree(tmp_path)==before
