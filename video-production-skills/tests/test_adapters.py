"""Read real existing contracts; fixture receipts are not actual provider runs."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest
from production.models import ContractError
from conftest import pin, require
from test_bindings import prepare


def test_legacy_ledger_when_registered_by_existing_tool(tmp_path):
    # Given: the actual preproduction Ledger writes a temporary project, not its source.
    source = Path(__file__).resolve().parents[2]/"video-preproduction-skills"/"scripts"
    (tmp_path/"asset.txt").write_text("temporary asset")
    code = "from pathlib import Path; from cp2.ledger import Ledger; import sys; Ledger.load(Path(sys.argv[1])).register('CHR-01','asset.txt',1,[])"
    import os
    result = subprocess.run([sys.executable, "-c", code, str(tmp_path)], capture_output=True, text=True, env={**os.environ, "PYTHONPATH": str(source), "PYTHONDONTWRITEBYTECODE": "1"})
    assert result.returncode == 0, result.stderr
    # When: resolving its actual file/version/hash schema.
    resolved = require("adapters", "resolve_legacy")(tmp_path/"ledger.json", "CHR-01@v1")
    # Then: exact current bytes, not an invented fixture registry, are recognized.
    assert resolved.sha256 == hashlib.sha256(b"temporary asset").hexdigest()


def test_legacy_when_artifact_superseded(tmp_path):
    # Given: only stale history exists.
    source = {"schema_version":1,"artifacts":{"CHR-01":[{"version":1,"path":"x","sha256":"0"*64,"consumes":[],"status":"stale"}]}}
    (tmp_path/"ledger.json").write_text(json.dumps(source))
    # When / Then: stale registrations cannot bind current references.
    with pytest.raises(ContractError, match="current"):
        require("adapters", "resolve_legacy")(tmp_path/"ledger.json", "CHR-01@v1")


def native_fixture(seed, capability, authority, tmp_path):
    packet = prepare(seed, capability, authority, tmp_path)
    arguments = {"model": capability.model, "prompt": packet.prompt_text, "reference_ids": [b.native_reference_id for b in packet.bindings], "duration": 2}
    call = {"tool": "fixture__send", "arguments": arguments}
    digest = hashlib.sha256(json.dumps(call,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return packet, {"format":"sequence-generation-call/1",**call,"call_sha256":digest,"submitted":False,"provider_conditioning":"not_verified","quality":"unverified"}


def test_native_call_when_checked_existing_shape(seed, capability, authority, tmp_path):
    # Given: existing prepare_generation_request format; synthetic provider name.
    packet, native = native_fixture(seed, capability, authority, tmp_path)
    # When: auditing local call selection against current planned bindings.
    result = require("adapters", "audit_native")(packet, native, "fixture__send", "/model", "/prompt", "/reference_ids", "/duration")
    # Then: no external job or conditioning claim.
    assert not result.submitted
    assert result.reference_ids == ("local-fixture-ref",)


def test_native_call_when_selected_reference_wrong(seed, capability, authority, tmp_path):
    # Given: otherwise well-hashed native request selects another ref.
    packet, native = native_fixture(seed, capability, authority, tmp_path)
    native["arguments"]["reference_ids"] = ["wrong-ref"]
    native["call_sha256"] = hashlib.sha256(json.dumps({"tool":native["tool"],"arguments":native["arguments"]},ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    # When / Then: upload existence does not mask wrong selected IDs.
    with pytest.raises(ContractError, match="selection"):
        require("adapters", "audit_native")(packet, native, "fixture__send", "/model", "/prompt", "/reference_ids", "/duration")


def test_real_preproduction_when_panel_and_speech_coverage(tmp_path):
    # Given: shape owned by the installed storyboard/project schema.
    project = {"project_id":"fixture", "shots":[{"id":"SH1","speech":[{"id":"D1"}]}], "storyboard":{"panels":[{"id":"P1","shot_id":"SH1","beat_ids":["B1"]}]}}
    path = tmp_path/"project.json"
    path.write_text(json.dumps(project))
    # When: deriving the upstream coverage set before creating clips.
    result = require("adapters", "derive_coverage")(path)
    # Then: panel and speech cannot disappear when the batch is drafted.
    assert {r.id for r in result} == {"shot:SH1", "panel:P1", "speech:D1", "beat:SH1:B1"}


def test_coverage_source_when_batch_erases_approved_item(seed):
    # Given: both queue and its local coverage omit a required upstream item.
    bad = seed.model_copy(update={"batch": seed.batch.model_copy(update={"coverage": seed.batch.coverage[:-1], "clips": seed.batch.clips[:-1], "edit_order": seed.batch.edit_order[:-1], "joins": seed.batch.joins[:-1]})})
    # When / Then: separate approved coverage anchor prevents self-counted completion.
    with pytest.raises(ContractError, match="coverage"):
        require("contracts", "validate_state")(bad)


def test_asset_scope_when_batch_omits_required_identity(seed, capability, authority, tmp_path):
    # Given: approved source explicitly assigns identity assets to shot SH1.
    import json
    from conftest import pin
    source = {"format":"production-coverage/1","requirements":[r.model_dump() for r in seed.approved_coverage],"asset_uses":[{"shot":"SH1","pin":seed.batch.clips[0].assets[0].model_dump()}]}
    scope = pin(tmp_path,"asset-scope.json",json.dumps(source))
    bad_clip = seed.batch.clips[0].model_copy(update={"assets":()})
    state = seed.model_copy(update={"coverage_source":scope,"batch":seed.batch.model_copy(update={"clips":(bad_clip,*seed.batch.clips[1:])})})
    # When / Then: file existence/coverage tags do not allow silently removing a mandatory asset.
    with pytest.raises(ContractError,match="asset"):
        require("adapters","verify_scope")(state,tmp_path)


def test_audio_cue_when_upstream_shot_requires_sound(tmp_path):
    # Given: sound is declared by cue rather than dialogue.
    project = {"shots":[{"id":"SH1","audio_cue_ids":["AMB1"]}],"storyboard":{"panels":[{"id":"P1","shot_id":"SH1","beat_ids":["B1"]}]}}
    path = tmp_path/"audio-project.json";path.write_text(json.dumps(project))
    # When: deriving source coverage.
    items = require("adapters","derive_coverage")(path)
    # Then: native/registered audio is a mandatory source obligation.
    assert next(r for r in items if r.id == "cue:SH1:AMB1").modality == "audio"


def test_native_fixture_when_existing_auditor_compares_exact_call(seed,capability,authority,tmp_path):
    # Given: a fixture in the existing prepare_generation_request packet shape.
    import os
    packet,native=native_fixture(seed,capability,authority,tmp_path)
    path=tmp_path/"native.json";path.write_text(json.dumps(native))
    source=Path.home()/".pi/agent/skills/video-production-assets/scripts"
    code="import json,sys;from prepare_generation_request import audit_call;p=json.load(open(sys.argv[1]));print(json.dumps(audit_call(p,{'tool':p['tool'],'arguments':p['arguments'],'transport_status':'unknown'})))"
    # When: the existing read-only auditor sees an ambiguous transport return.
    result=subprocess.run([sys.executable,"-c",code,str(path)],capture_output=True,text=True,env={**os.environ,"PYTHONPATH":str(source),"PYTHONDONTWRITEBYTECODE":"1"})
    # Then: its own real contract agrees: unknown, no permission to resubmit.
    assert result.returncode == 0, result.stderr
    verdict=json.loads(result.stdout)
    assert verdict["submission_state"] == "unknown"
    assert verdict["resubmit_allowed"] is False
