"""A candidate's own approval cannot mask drift in a consumed source's separate approval."""
import pytest

from conftest import require
from production.files import verified_file
from production.models import ContractError, Phase, Receipt
from test_quality import linked_running


def completed(state,packet):
    return require("execution","observe")(state,"ATT-C3",Receipt(phase=Phase.SUCCEEDED,job_id="fixture-C3",evidence="synthetic succeeded receipt",request_hash=packet.request_hash))


@pytest.mark.parametrize("optional",[False,True])
@pytest.mark.parametrize("damage",["approval","media"])
def test_generated_admission_when_consumed_source_pin_drifts(seed,capability,authority,tmp_path,optional,damage):
    # Given: C3's own approval is distinct; a required or chosen optional source was consumed.
    state,source,take,review,packet=linked_running(seed,capability,authority,tmp_path,separate_approval=True,optional_reference=optional)
    state=completed(state,packet)
    path=source.approval.evidence.path if damage == "approval" else source.take.asset.path
    (tmp_path/path).write_text("CONSUMED SOURCE PROOF REVOKED / BYTES REPLACED")
    # When / Then: unchanged own-approval and fingerprint do not authorize stale consumed proof.
    verified_file(tmp_path,packet.authority.evidence)
    assert require("contracts","fingerprint")(state,"C3") == take.fingerprint
    with pytest.raises(ContractError,match="hash"):
        require("quality","accept_take")(state,take,review,take.fingerprint,tmp_path)
    assert next(a for a in state.attempts if a.id == "ATT-C3").phase == Phase.SUCCEEDED
    assert all(s.take.clip_id != "C3" for s in state.selections)


@pytest.mark.parametrize("damage",["approval","media"])
def test_generated_admission_when_optional_source_was_explicitly_not_consumed(seed,capability,authority,tmp_path,damage):
    # Given: omission is approved in the clip and the request actually selected no history ref.
    state,source,take,review,packet=linked_running(seed,capability,authority,tmp_path,separate_approval=True,optional_reference=True,omit_reference=True)
    state=completed(state,packet)
    path=source.approval.evidence.path if damage == "approval" else source.take.asset.path
    (tmp_path/path).write_text("unused optional source drift")
    assert all(b.source_clip is None for b in packet.bindings)
    # When: reviewing only actually consumed evidence and mandatory current requirements.
    result=require("quality","accept_take")(state,take,review,take.fingerprint,tmp_path)
    # Then: a justified unused optional history does not masquerade as a required input.
    assert next(s for s in result.selections if s.take.clip_id == "C3").valid
