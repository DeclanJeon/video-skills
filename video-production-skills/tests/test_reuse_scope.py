"""Explicit local-source reuse and approved scope amendments; no invented remote jobs."""
import json

import pytest

from conftest import pin, require
from production.models import ContractError
from test_media import make_video
from test_revisions import selection


def supplied(seed,capability,authority,tmp_path):
    item=selection(seed,tmp_path)
    asset=make_video(tmp_path,"supplied-source.mp4",color="purple")
    take=item.take.model_copy(update={"asset":asset,"origin":"approved_reuse","attempt_id":None})
    report=item.review.model_copy(update={"playback":item.review.playback.model_copy(update={"asset_hash":asset.sha256})})
    grant=authority.configurations[0].model_copy(update={"reuse_source":asset,"reuse_range":take.source_range})
    approval=authority.model_copy(update={"generation":False,"upload":False,"reuse":True,"configurations":(grant,*authority.configurations[1:]),"allowed_hashes":(*authority.allowed_hashes,asset.sha256)})
    return take,report,approval


def test_supplied_source_when_reuse_is_explicitly_approved(seed,capability,authority,tmp_path):
    # Given: rights/approval pins name an existing local source and exact selected range.
    take,report,approval=supplied(seed,capability,authority,tmp_path)
    # When: admitting supplied media without generation.
    state=require("quality","accept_supplied")(seed,take,report,approval,tmp_path)
    # Then: no remote success/attempt is invented for existing footage.
    assert not state.attempts
    assert state.selections[0].take.origin == "approved_reuse"
    assert state.selections[0].take.attempt_id is None


def test_supplied_source_when_generation_grant_is_not_reuse_permission(seed,capability,authority,tmp_path):
    # Given: a generation-only grant, not permission to reuse this file.
    take,report,approval=supplied(seed,capability,authority,tmp_path)
    approval=approval.model_copy(update={"reuse":False})
    # When / Then: possession of media or a generation grant does not authorize reuse.
    with pytest.raises(ContractError,match="authority"):
        require("quality","accept_supplied")(seed,take,report,approval,tmp_path)


def test_scope_revision_when_exclusion_explicitly_approved(seed,tmp_path):
    # Given: exact old/new scope hashes and explicit approved removal of R3.
    scope=pin(tmp_path,"coverage-v2.json",json.dumps({"format":"production-coverage/1","requirements":[r.model_dump() for r in seed.approved_coverage[:-1]]}))
    evidence=pin(tmp_path,"exclude-approval.txt","fixture approval of exactly R3 exclusion")
    grant=require("scope","ScopeGrant")(old_source_hash=seed.coverage_source.sha256,old_scope_revision=seed.batch.scope_revision,new_source=scope,new_scope_revision="scope-2",removed=("R3",),added=(),changed=(),asset_changes=(),evidence=evidence)
    batch=seed.batch.model_copy(update={"scope_revision":"scope-2","revision":2,"coverage":seed.batch.coverage[:-1],"clips":seed.batch.clips[:-1],"edit_order":seed.batch.edit_order[:-1],"joins":seed.batch.joins[:-1]})
    # When: applying a reviewed scope revision, never silently editing the denominator.
    state=require("scope","revise_scope")(seed,batch,grant,tmp_path)
    # Then: changed denominator is anchored in a new scope with explicit evidence.
    assert len(state.approved_coverage) == 2
    assert state.batch.scope_revision == "scope-2"
    assert evidence.path in state.change_evidence


def test_scope_revision_when_missing_exclusion_grant(seed,tmp_path):
    # Given: same reduced plan but no authorization for removed required items.
    scope=pin(tmp_path,"coverage-v2.json",json.dumps({"format":"production-coverage/1","requirements":[r.model_dump() for r in seed.approved_coverage[:-1]]}))
    evidence=pin(tmp_path,"no-exclusion.txt","does not approve an exclusion")
    grant=require("scope","ScopeGrant")(old_source_hash=seed.coverage_source.sha256,old_scope_revision=seed.batch.scope_revision,new_source=scope,new_scope_revision="scope-2",removed=(),added=(),changed=(),asset_changes=(),evidence=evidence)
    batch=seed.batch.model_copy(update={"scope_revision":"scope-2","revision":2,"coverage":seed.batch.coverage[:-1],"clips":seed.batch.clips[:-1],"edit_order":seed.batch.edit_order[:-1],"joins":seed.batch.joins[:-1]})
    # When / Then: completed clips do not authorize dropping missing coverage.
    with pytest.raises(ContractError,match="scope"):
        require("scope","revise_scope")(seed,batch,grant,tmp_path)


def test_scope_cli_when_approved_change_is_persisted(seed,tmp_path):
    # Given: an existing real project ledger and a separately pinned approved exclusion.
    from test_cli import cli
    from production.store import ProjectStore
    from production.scope import ScopeGrant
    input_file=tmp_path/"state.json";input_file.write_text(seed.model_dump_json())
    ledger=tmp_path/"ledger.json"
    assert cli("init",ledger,input_file).returncode == 0
    source=pin(tmp_path,"coverage-v2.json",json.dumps({"format":"production-coverage/1","requirements":[r.model_dump() for r in seed.approved_coverage[:-1]]}))
    proof=pin(tmp_path,"scope-approval.txt","fixture explicit R3 exclusion")
    grant=ScopeGrant(old_source_hash=seed.coverage_source.sha256,old_scope_revision=seed.batch.scope_revision,new_source=source,new_scope_revision="scope-2",removed=("R3",),added=(),changed=(),asset_changes=(),evidence=proof)
    batch=seed.batch.model_copy(update={"scope_revision":"scope-2","revision":2,"coverage":seed.batch.coverage[:-1],"clips":seed.batch.clips[:-1],"edit_order":seed.batch.edit_order[:-1],"joins":seed.batch.joins[:-1]})
    batch_file=tmp_path/"batch.json";batch_file.write_text(batch.model_dump_json())
    grant_file=tmp_path/"grant.json";grant_file.write_text(grant.model_dump_json())
    # When: applying through the public revision-checked CLI, not manual state editing.
    result=cli("revise-scope",ledger,batch_file,grant_file,0)
    # Then: exact pinned approval and scope transition survive a fresh store read.
    assert result.returncode == 0,result.stdout+result.stderr
    restored=ProjectStore(ledger).read()
    assert restored.revision == 1
    assert restored.scope_history[-1].evidence == proof
    assert restored.scope_history[-1].removed == ("R3",)


def test_reuse_cli_when_existing_source_has_no_remote_attempt(seed,capability,authority,tmp_path):
    # Given: a real local file and a synthetic explicit local reuse permission/report.
    from test_cli import cli
    from production.store import ProjectStore
    take,report,approval=supplied(seed,capability,authority,tmp_path)
    values={"state.json":seed,"take.json":take,"review.json":report,"approval.json":approval}
    for name,value in values.items():
        (tmp_path/name).write_text(value.model_dump_json())
    ledger=tmp_path/"ledger.json"
    assert cli("init",ledger,tmp_path/"state.json").returncode == 0
    # When: admitting the source without generation using the public command.
    result=cli("reuse",ledger,tmp_path/"take.json",tmp_path/"review.json",tmp_path/"approval.json",0)
    # Then: no fake job IDs are created; original source identity/range is preserved.
    assert result.returncode == 0,result.stdout+result.stderr
    restored=ProjectStore(ledger).read()
    assert not restored.attempts
    assert restored.selections[0].take.asset == take.asset
    assert restored.selections[0].take.attempt_id is None
