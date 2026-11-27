"""Temporary real files and explicit fixtures; no external jobs."""
import hashlib
import json
import importlib
import importlib.util
from pathlib import Path

import pytest

from production.models import (
    ApprovedConfig, Authority, Batch, Capability, Clip, ClipId, JoinPlan, Pin, Requirement, State,
)


def require(module, name):
    """Fail as an assertion when a planned behavior is not implemented yet."""
    assert importlib.util.find_spec(f"production.{module}"), f"missing {module} runtime"
    value = getattr(importlib.import_module(f"production.{module}"), name, None)
    assert callable(value), f"missing {module}.{name} behavior"
    return value


def pin(root: Path, name: str, text: str = "fixture") -> Pin:
    path = root / name
    path.write_text(text)
    return Pin(id=name, version="1", sha256=hashlib.sha256(path.read_bytes()).hexdigest(), path=name)


@pytest.fixture
def seed(tmp_path):
    prompt = pin(tmp_path, "prompt.txt", "Fictional person crosses the empty yard.")
    face = pin(tmp_path, "face.txt", "synthetic identity fixture; not an image")
    clips = tuple(Clip(id=ClipId(f"C{i}"), shots=(f"SH{i}",), requirements=(f"R{i}",), duration_s=2, prompt=prompt, assets=(face,)) for i in range(1, 4))
    coverage = tuple(Requirement(id=f"R{i}", shot=f"SH{i}", panels=(f"P{i}",), locator=f"script#R{i}") for i in range(1, 4))
    joins = tuple(JoinPlan(id=f"J{i}", before=ClipId(f"C{i}"), after=ClipId(f"C{i+1}"), relation="angle_change", reveal_order=(f"R{i}", f"R{i+1}"), locator="board#cuts") for i in (1, 2))
    batch = Batch(id="B1", scope_revision="scope-1", coverage=coverage, clips=clips, edit_order=tuple(c.id for c in clips), joins=joins)
    source = pin(tmp_path, "approved-coverage.json", json.dumps({"format": "production-coverage/1", "requirements": [r.model_dump() for r in coverage]}))
    return State(batch=batch, approved_coverage=coverage, coverage_source=source)


@pytest.fixture
def capability(tmp_path):
    return Capability(account="fixture-account", model="fixture-model", transport="offline-receipt", mode="unlimited", observed_mode="unlimited", roles=("asset", "state"), modalities=("image", "video", "audio"), max_references=4, max_active=2, durations=(2,), width=1280, height=720, audio=True, evidence=pin(tmp_path, "capability.txt", "fixture contract; not live provider evidence"))


def configurations(state, capability):
    from production.approval import clip_configuration_hash, requested_audio
    return tuple(ApprovedConfig(clip_id=c.id,scope_revision=state.batch.scope_revision,coverage_hash=state.coverage_source.sha256,clip_hash=clip_configuration_hash(c),duration_s=c.duration_s,width=capability.width,height=capability.height,audio_requested=requested_audio(state,c.id)) for c in state.batch.clips)


@pytest.fixture
def authority(tmp_path, seed, capability):
    return Authority(id="AP-1", configurations=configurations(seed,capability), clips=tuple(c.id for c in seed.batch.clips), allowed_hashes=tuple(p.sha256 for c in seed.batch.clips for p in (c.prompt, *c.assets)), account="fixture-account", model="fixture-model", transport="offline-receipt", mode="unlimited", max_attempts=2, max_active=2, upload=True, generation=True, evidence=pin(tmp_path, "authority.txt", "offline test authorization only"))
