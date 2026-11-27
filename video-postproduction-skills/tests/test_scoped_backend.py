"""Actual narrow native path remains independent of unconsumed lost footage; global final QA still closes."""
import json
import pytest
from conftest import require
from test_effectcraft import setup


def scoped(root):
    return setup(root)  # Generated plate consumes C1 work context, not the full picture source set.


def test_backend_when_unconsumed_live_selection_is_invalid_can_prepare_and_reserve_scoped_work(tmp_path):
    store,backend,order,cap=scoped(tmp_path)
    raw=json.loads(store.path.read_text());raw["production"]["selections"][2]["valid"]=False
    store.path.write_text(json.dumps(raw))
    with pytest.raises(require("errors","ContractError")):store.read()  # Final whole-flow gate remains closed.
    packet=backend.prepare(order,cap,store.read_recorded().intake.authority)
    job=store.record_reservation(packet,store.read_recorded().revision)
    assert job.packet==packet


def test_backend_when_unconsumed_source_disappears_can_render_only_current_consumed_source(tmp_path):
    store,backend,order,cap=scoped(tmp_path)
    packet=backend.prepare(order,cap,store.read_recorded().intake.authority)
    with store.transaction(0) as tx:tx.state=require("jobs","reserve_work")(tx.state,packet)
    (tmp_path/"source3.mp4").unlink()
    receipt=backend.execute(packet)
    assert receipt.phase=="succeeded"
    observed=backend.observe(store.read_recorded().jobs[0])
    assert observed.frame_count==12
    assert observed.media_kind=="rgba_sequence"
    assert observed.technical_verified is True
    assert store.status().inputs_ready is False  # Scoped result cannot certify the full original denominator.


def test_backend_when_global_profile_pin_changes_cannot_prepare_scoped_work(tmp_path):
    store,backend,order,cap=scoped(tmp_path)
    (tmp_path/"profile.json").write_text("replacement")
    with pytest.raises(require("errors","ContractError")):
        backend.prepare(order,cap,store.read_recorded().intake.authority)
