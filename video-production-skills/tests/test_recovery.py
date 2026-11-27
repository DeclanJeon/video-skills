"""Real filesystem transactions and subprocess restart/lock behavior."""
import json
import os
import subprocess
import sys

import pytest
from production.models import ContractError
from conftest import require


def test_roundtrip_when_existing_ledger_has_other_fields(seed, tmp_path):
    # Given: a real pre-existing project ledger.
    path = tmp_path/"ledger.json"
    path.write_text(json.dumps({"schema_version": 1, "artifacts": {}, "unrelated": {"keep": 7}}))
    store = require("store", "ProjectStore")(path)
    # When: initializing the production namespace.
    store.initialize(seed)
    # Then: other project owners retain their fields.
    assert json.loads(path.read_text())["unrelated"] == {"keep": 7}
    assert store.read() == seed


def test_cas_when_another_writer_published(seed, tmp_path):
    # Given: durable revision advanced.
    store = require("store", "ProjectStore")(tmp_path/"ledger.json")
    store.initialize(seed)
    with store.transaction(0) as tx:
        tx.state = tx.state.model_copy(update={"batch": tx.state.batch.model_copy(update={"revision": 2})})
    # When / Then: stale writer cannot overwrite current revision.
    with pytest.raises(ContractError, match="revision"):
        with store.transaction(0):
            pass
    assert store.read().revision == 1


def test_abort_when_transaction_raises(seed, tmp_path):
    # Given: initial durable data.
    store = require("store", "ProjectStore")(tmp_path/"ledger.json")
    store.initialize(seed)
    before = (tmp_path/"ledger.json").read_bytes()
    # When: client fails before publication.
    with pytest.raises(RuntimeError):
        with store.transaction(0):
            raise RuntimeError("fixture failure before commit")
    # Then: original file remains intact.
    assert (tmp_path/"ledger.json").read_bytes() == before


def test_lock_when_second_process_attempts_write(seed, tmp_path):
    # Given: first writer holds the project lock.
    store = require("store", "ProjectStore")(tmp_path/"ledger.json")
    store.initialize(seed)
    code = "from pathlib import Path; from production.store import ProjectStore; s=ProjectStore(Path(__import__('sys').argv[1]));\nwith s.transaction(0): pass"
    # When: a different process attempts a transaction.
    with store.transaction(0):
        result = subprocess.run([sys.executable, "-c", code, str(tmp_path/"ledger.json")], capture_output=True, text=True)
    # Then: no waiting or lock stealing.
    assert result.returncode != 0
    assert "lock" in result.stderr


def test_no_overwrite_when_initialize_twice(seed, tmp_path):
    # Given: current state exists.
    store = require("store", "ProjectStore")(tmp_path/"ledger.json")
    store.initialize(seed)
    # When / Then: a restart cannot reset attempts.
    with pytest.raises(ContractError, match="exists"):
        store.initialize(seed)


def test_atomic_write_when_replace_fails(seed, tmp_path, monkeypatch):
    # Given: real existing state and an injected OS replacement error.
    store = require("store", "ProjectStore")(tmp_path/"ledger.json")
    store.initialize(seed)
    before = (tmp_path/"ledger.json").read_bytes()
    def fail_replace(src, dst):
        raise OSError("fixture disk error")
    monkeypatch.setattr(os, "replace", fail_replace)
    # When: publication is interrupted.
    with pytest.raises(OSError):
        with store.transaction(0):
            pass
    # Then: source remains parseable and unchanged.
    assert (tmp_path/"ledger.json").read_bytes() == before


def test_symlink_when_ledger_is_unmanaged(seed, tmp_path):
    # Given: ledger path points at a file owned outside the project.
    target = tmp_path/"target.json"
    target.write_text("{}")
    (tmp_path/"ledger.json").symlink_to(target)
    # When / Then: refuse following a managed-path symlink.
    with pytest.raises(ContractError, match="path"):
        require("store", "ProjectStore")(tmp_path/"ledger.json").initialize(seed)


def test_unknown_reservation_when_process_restarts(seed, capability, authority, tmp_path):
    # Given: unknown reservation persisted after a real atomic transaction.
    from production.models import Phase, Receipt
    from test_execution import reserved
    state, packet = reserved(seed,capability,authority,tmp_path)
    state = require("execution","observe")(state,"ATT-1",Receipt(phase=Phase.UNKNOWN,evidence="fixture-timeout",request_hash=packet.request_hash))
    store = require("store","ProjectStore")(tmp_path/"ledger.json")
    store.initialize(seed)
    with store.transaction(0) as tx:
        tx.state = state
    code = "from pathlib import Path; from production.store import ProjectStore; from production.contracts import ACTIVE; import sys; s=ProjectStore(Path(sys.argv[1])).read(); print(sum(a.phase in ACTIVE for a in s.attempts))"
    # When: reading from a fresh process after interruption.
    result = subprocess.run([sys.executable,"-c",code,str(tmp_path/"ledger.json")],capture_output=True,text=True)
    # Then: unknown does not disappear or free its slot on restart.
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "1"


def test_commit_when_noncooperating_writer_changes_ledger(seed,tmp_path):
    # Given: an outside writer ignores the advisory production lock.
    store=require("store","ProjectStore")(tmp_path/"ledger.json")
    store.initialize(seed)
    # When / Then: we preserve the observed other writer rather than clobbering its fields.
    with pytest.raises(ContractError,match="conflict"):
        with store.transaction(0):
            content=json.loads((tmp_path/"ledger.json").read_text())
            content["other_owner"]=17
            (tmp_path/"ledger.json").write_text(json.dumps(content))
    assert json.loads((tmp_path/"ledger.json").read_text())["other_owner"] == 17


def test_init_when_state_injects_unreviewed_acceptance(seed,tmp_path):
    # Given: input attempts to bypass operator/reviewer transitions at initialization.
    from test_revisions import selection
    forged=seed.model_copy(update={"selections":(selection(seed,tmp_path),)})
    # When / Then: init is for an initial plan, not trusted historical result import.
    with pytest.raises(ContractError,match="initial"):
        require("store","ProjectStore")(tmp_path/"ledger.json").initialize(forged)


@pytest.mark.parametrize("envelope",[False,True])
def test_initialization_when_mutable_ledger_would_invalidate_its_own_source(seed,tmp_path,envelope):
    # Given: approved source or exported origin points at the very file init would mutate.
    from conftest import pin
    payload={"format":"production-coverage/1","requirements":[r.model_dump() for r in seed.approved_coverage]}
    origin=pin(tmp_path,"ledger.json",json.dumps(payload))
    source=origin
    if envelope:
        source=pin(tmp_path,"scope.json",json.dumps({**payload,"origin":origin.model_dump()}))
    state=seed.model_copy(update={"coverage_source":source})
    before=(tmp_path/"ledger.json").read_bytes()
    # When / Then: require an immutable snapshot, never create an immediately stale self-pin.
    with pytest.raises(ContractError,match="scope"):
        require("store","ProjectStore")(tmp_path/"ledger.json").initialize(state)
    assert (tmp_path/"ledger.json").read_bytes() == before
