"""Retaining generated footage cannot silently omit history actually selected in its request."""
import json

import pytest

from conftest import require
from production.models import ContractError, Verdict
from test_cli import cli
from test_consumed_approval import completed
from test_quality import linked_running


def accepted_pair(seed,capability,authority,root,optional=True,omitted=False):
    state,source,take,review,packet=linked_running(seed,capability,authority,root,
        separate_approval=True,optional_reference=optional,omit_reference=omitted)
    state=completed(state,packet)
    state=require("quality","accept_take")(state,take,review,take.fingerprint,root)
    return state,source,review,packet


def persist(state,root):
    initial=state.model_copy(update={"attempts":(),"selections":(),"history":(),"join_reviews":(),"revision":0})
    store=require("store","ProjectStore")(root/"ledger.json")
    store.initialize(initial)
    with store.transaction(0) as tx:
        tx.state=state
    return store


@pytest.mark.parametrize("optional",[False,True])
def test_cli_retention_when_consumed_source_invalid_and_pins_missing(seed,capability,authority,tmp_path,optional):
    # Given: C3 really selected C1, and both outputs were admitted with distinct approvals.
    state,source,review,packet=accepted_pair(seed,capability,authority,tmp_path,optional=optional)
    assert any(b.source_clip == "C1" for b in packet.bindings)
    store=persist(state,tmp_path)
    assert cli("invalidate",tmp_path/"ledger.json","C1","reported imported identity/pose defect",1).returncode == 0
    (tmp_path/source.take.asset.path).unlink()
    (tmp_path/source.approval.evidence.path).unlink()
    original=(tmp_path/"ledger.json").read_bytes()
    attempts=store.read().attempts
    report=tmp_path/"review.json";report.write_text(review.model_dump_json())
    current=require("contracts","fingerprint")(store.read(),"C3")
    # When: actual public CLI revalidation supplies the new fingerprint, not the stale one.
    result=cli("revalidate",tmp_path/"ledger.json","C3",report,current,2)
    # Then: chosen optional and required sources obey the same consumed-input safety rule.
    assert result.returncode != 0,result.stdout+result.stderr
    assert "dependency" in result.stdout
    assert (tmp_path/"ledger.json").read_bytes() == original
    assert not next(s for s in store.read().selections if s.take.clip_id == "C3").valid
    assert store.read().attempts == attempts
    progress=cli("progress",tmp_path/"ledger.json")
    assert progress.returncode == 0,progress.stdout+progress.stderr
    assert json.loads(progress.stdout)["accepted"] == 0


@pytest.mark.parametrize("optional",[False,True])
@pytest.mark.parametrize("defect",["pose","background_edge"])
def test_retention_when_conditional_source_defect_intersects_imports(seed,capability,authority,tmp_path,optional,defect):
    # Given: source itself is valid conditional, but pose is an actually imported attribute.
    state,source,review,packet=accepted_pair(seed,capability,authority,tmp_path,optional=optional)
    assert any("pose" in b.imports for b in packet.bindings if b.source_clip == "C1")
    source_report=source.review.model_copy(update={"verdict":Verdict.CONDITIONAL,"defects":(defect,),
        "post_fix":"reported postproduction repair","post_receiver":"fixture-post","conditional_policy":"fixture-explicit-policy"})
    state=require("quality","revalidate_take")(state,"C1",source_report,require("contracts","fingerprint")(state,"C1"),tmp_path)
    attempts=state.attempts
    current=require("contracts","fingerprint")(state,"C3")
    # When / Then: affecting imports blocks; unrelated conditional defects remain retainable.
    if defect == "pose":
        with pytest.raises(ContractError,match="dependency"):
            require("quality","revalidate_take")(state,"C3",review,current,tmp_path)
        assert not next(s for s in state.selections if s.take.clip_id == "C3").valid
    else:
        result=require("quality","revalidate_take")(state,"C3",review,current,tmp_path)
        assert next(s for s in result.selections if s.take.clip_id == "C3").valid
        assert result.attempts == attempts


def test_cli_retention_when_optional_source_was_never_selected(seed,capability,authority,tmp_path):
    # Given: original request explicitly omitted optional C1; no historical video was selected.
    state,source,review,packet=accepted_pair(seed,capability,authority,tmp_path,omitted=True)
    assert all(b.source_clip is None for b in packet.bindings)
    store=persist(state,tmp_path)
    assert cli("invalidate",tmp_path/"ledger.json","C1","unused optional source defect",1).returncode == 0
    (tmp_path/source.take.asset.path).unlink()
    (tmp_path/source.approval.evidence.path).unlink()
    report=tmp_path/"review.json";report.write_text(review.model_dump_json())
    attempts=store.read().attempts
    # When: explicitly re-reviewing the unaffected output against current requirements.
    result=cli("revalidate",tmp_path/"ledger.json","C3",report,require("contracts","fingerprint")(store.read(),"C3"),2)
    # Then: omission stays allowed without a new request or rewriting old bindings.
    assert result.returncode == 0,result.stdout+result.stderr
    assert next(s for s in store.read().selections if s.take.clip_id == "C3").valid
    assert store.read().attempts == attempts


def test_retention_when_chosen_optional_source_flag_is_valid_but_review_fingerprint_stale(seed,capability,authority,tmp_path):
    # Given: a selection's valid flag alone does not establish reviewed currentness.
    state,source,review,packet=accepted_pair(seed,capability,authority,tmp_path)
    stale=source.model_copy(update={"acceptance_revision":source.acceptance_revision+1,"reviewed_fingerprint":"f"*64})
    state=require("revisions","replace_selection")(state,stale)
    assert require("contracts","usable")(stale,state.batch.clips[2].references[0].imports)
    # When / Then: chosen optional history must be current as well as otherwise usable.
    with pytest.raises(ContractError,match="dependency"):
        require("quality","revalidate_take")(state,"C3",review,require("contracts","fingerprint")(state,"C3"),tmp_path)
