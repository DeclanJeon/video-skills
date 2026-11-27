"""Narrow OS rename fault injection, retaining real atomic publication and actual native command effects."""
import json
import os
from pathlib import Path
import pytest
from conftest import require
from test_ledger import built,project,prepare
from test_filmcraft import setup


def test_publication_when_atomic_replace_fails_preserves_previous_complete_document(project,monkeypatch):
    # Given: existing complete source/foreign/post namespaces.
    path,store,state,production=prepare(project);store.initialize(state)
    before=path.read_bytes()
    original=os.replace
    def fail(src,dst):
        if Path(dst)==path:raise OSError("injected atomic rename failure")
        return original(src,dst)
    monkeypatch.setattr(os,"replace",fail)
    # When: durable temp bytes cannot be atomically published.
    with pytest.raises(OSError,match="rename"):
        with store.transaction(0) as tx:
            tx.state=tx.state.model_copy(update={"notes":("must not publish",)})
    # Then: no truncated document, lost foreign namespace, or orphan owned temp.
    assert path.read_bytes()==before and not tuple(path.parent.glob(".postproduction-*"))


def test_native_when_second_canonical_write_fails_keeps_first_actual_process_fact(tmp_path,monkeypatch):
    # Given: a reserved actual native job and failure at its second namespace replace.
    store,backend,packet,cap=setup(tmp_path)
    store.record_reservation(packet,store.read_recorded().revision)
    original=os.replace;writes=0
    def fail_second(src,dst):
        nonlocal writes
        if Path(dst)==store.path:
            writes+=1
            if writes==2:raise OSError("injected second canonical write failure")
        return original(src,dst)
    monkeypatch.setattr(os,"replace",fail_second)
    # When: actual CLI has acted and the follow-up diagnostic publication fails.
    with pytest.raises(OSError,match="second canonical"):
        backend.execute(packet)
    # Then: first known process receipt/history survives; replay is not permission to repair diagnostics.
    state=store.read_recorded();job=state.jobs[0]
    assert job.job_id is not None and job.phase=="running" and job.observations
    before=store.path.read_bytes()
    with pytest.raises(require("errors","ContractError"),match="reserv"):
        backend.execute(packet)
    assert store.path.read_bytes()==before and json.loads(before)["foreign"]=={"owner":"preserve"}
