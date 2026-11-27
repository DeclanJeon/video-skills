"""Exercise the actual local CLI in subprocesses, including error paths."""
import json
from pathlib import Path
import subprocess
import sys

from conftest import require


def cli(*args):
    script = Path(__file__).resolve().parents[1]/"scripts/production.py"
    assert script.is_file(), "production CLI not implemented"
    return subprocess.run([sys.executable,str(script),*map(str,args)],capture_output=True,text=True)


def test_cli_init_and_restart_when_project_is_valid(seed, tmp_path):
    # Given: serialized input and existing project directory.
    path = tmp_path/"input.json"; path.write_text(seed.model_dump_json())
    # When: initialize and query in a new process.
    init = cli("init", tmp_path/"ledger.json", path)
    result = cli("ready", tmp_path/"ledger.json")
    # Then: durable state is read on restart.
    assert init.returncode == 0, init.stdout + init.stderr
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["ready"] == ["C1","C2","C3"]


def test_cli_invalid_json_when_input_malformed(tmp_path):
    # Given: malformed input document.
    path = tmp_path/"bad.json";path.write_text("{")
    # When: invoking the real boundary.
    result = cli("init",tmp_path/"ledger.json",path)
    # Then: clear failure and no state publication.
    assert result.returncode != 0
    assert not (tmp_path/"ledger.json").exists()


def test_cli_help_when_no_remote_execution_allowed():
    # Given: installed local command surface.
    # When: querying help.
    result = cli("--help")
    # Then: inspectable commands, no implicit generation.
    assert result.returncode == 0
    assert "Traceback" not in result.stderr


def test_cli_complete_batch_when_offline_receipts_and_reported_qa(seed, capability, authority, tmp_path):
    # Given: three-clip technical batch; C3 consumes two accepted history sources.
    # Provider/semantic review receipts below are FIXTURES, not actual provider/visual QA.
    from production.models import Binding, ClipId, Reference, Take, Review, Playback, SourceRange, Verdict
    from production.store import ProjectStore
    from production.contracts import fingerprint
    from production.handoff import selection_hash
    from test_media import make_video
    from test_handoff import joins_for, flow_for
    refs = tuple(Reference(source_clip=ClipId(f"C{i}"),role="state",modality="video",imports=("pose",)) for i in (1,2))
    last = seed.batch.clips[2].model_copy(update={"references": refs})
    seed = seed.model_copy(update={"batch": seed.batch.model_copy(update={"clips": (*seed.batch.clips[:2],last)})})
    def write(name, value):
        p = tmp_path/name
        p.write_text(value.model_dump_json() if hasattr(value,"model_dump_json") else json.dumps(value))
        return p
    ledger = tmp_path/"ledger.json"
    state_file = write("state.json",seed)
    assert cli("init",ledger,state_file).returncode == 0
    store = ProjectStore(ledger)
    for i,clip in enumerate(seed.batch.clips,1):
        current = store.read()
        binding = Binding(pin=clip.assets[0],role="asset",modality="image",imports=("identity",),native_asset_id="fixture-asset",native_reference_id="fixture-identity",ready=True)
        sources = []
        for ref in clip.references:
            source = next(s for s in current.selections if s.take.clip_id == ref.source_clip)
            sources.append(Binding(pin=source.take.asset,source_clip=ref.source_clip,source_range=source.take.source_range,range_revision=source.take.range_revision,acceptance_revision=source.acceptance_revision,role=ref.role,modality=ref.modality,imports=ref.imports,native_asset_id=f"fixture-asset-{ref.source_clip}",native_reference_id=f"fixture-ref-{ref.source_clip}",ready=True))
        from conftest import configurations
        scope = authority.model_copy(update={"allowed_hashes": (*authority.allowed_hashes,*(b.pin.sha256 for b in sources)), "configurations":configurations(current,capability)})
        cap_file, auth_file = write("cap.json",capability), write("auth.json",scope)
        bind_file = write("bindings.json",[b.model_dump(mode="json") for b in (binding,*sources)])
        prepared = cli("prepare",ledger,clip.id,cap_file,auth_file,bind_file)
        assert prepared.returncode == 0, prepared.stdout+prepared.stderr
        packet = json.loads(prepared.stdout)
        packet_file = write("prepared.json",packet)
        reserved = cli("reserve",ledger,packet_file,f"A{i}",store.read().revision,0)
        assert reserved.returncode == 0, reserved.stdout+reserved.stderr
        for phase in ("submitted","succeeded"):
            receipt = write("receipt.json",{"phase":phase,"job_id":f"fixture-job-{i}","evidence":"synthetic remote receipt, not actual service","request_hash":packet["request_hash"]})
            result = cli("observe",ledger,f"A{i}",receipt,store.read().revision)
            assert result.returncode == 0, result.stdout+result.stderr
        asset = make_video(tmp_path,f"take-{i}.mp4",color=("blue","green","red")[i-1])
        take = Take(id=f"TAKE{i}",clip_id=clip.id,attempt_id=f"A{i}",asset=asset,frame_count=48,fps=24,width=1280,height=720,has_audio=False,decode_evidence="actual local technical probe",source_range=SourceRange(start=0,end=48),fingerprint=packet["fingerprint"])
        report = Review(verdict=Verdict.ACCEPTED,fulfilled=clip.requirements,playback=Playback(asset_hash=asset.sha256,source_range=take.source_range,reviewer="synthetic-review-fixture",evidence="FIXTURE semantic report, not actual viewing",video_watched=True))
        result = cli("review",ledger,write("take.json",take),write("review.json",report),packet["fingerprint"],store.read().revision)
        assert result.returncode == 0, result.stdout+result.stderr
    # When: exact joins and whole-flow reported fixtures are added through public CLI.
    for join in joins_for(store.read()):
        result = cli("join",ledger,write("join.json",join),store.read().revision)
        assert result.returncode == 0, result.stdout+result.stderr
    rendered = cli("render-review",ledger,"qa/rough-v1.mp4")
    assert rendered.returncode == 0, rendered.stdout+rendered.stderr
    from production.models import ReviewRender
    proof = ReviewRender.model_validate_json(rendered.stdout)
    flow = flow_for(store.read()).model_copy(update={"review_render":proof})
    delivered = cli("handoff",ledger,write("flow.json",flow),"fixture-post-receiver","fixture-rights")
    # Then: full batch and both predecessor bindings survive process-by-process persistence.
    assert delivered.returncode == 0, delivered.stdout+delivered.stderr
    assert len(json.loads(delivered.stdout)["selections"]) == 3
    assert len(store.read().attempts[-1].prepared.bindings) == 3
