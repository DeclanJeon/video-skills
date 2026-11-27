"""No install/fetch authority arises from goal activation, draft questions or generic policy."""
import json
import pytest
from pydantic import ValidationError
from conftest import require
from test_environment import host


def missing_host(**changes):
    return host(observation={"cli_path":None,"cli_sha256":None,"version":None,"package_name":None},**changes)


def plan(snapshot=None,**changes):
    snapshot=snapshot or missing_host()
    data={"id":"install-fixture-1","host_id":snapshot.host_id,
        "host_fingerprint":require("environment.consent","host_fingerprint")(snapshot),
        "tool":"filmcraft","version":"0.20.1-1","system":"Linux","architecture":"x86_64",
        "source_url":"https://fixture.invalid/tool.deb","source_sha256":"c"*64,
        "source_evidence":{"id":"fixture-not-official","version":"1","path":"fixture-source.txt","sha256":"d"*64},
        "source_evidence_kind":"contract_fixture","dependencies":[],"write_paths":["/fixture/tool"],
        "permissions":["user"],"network_hosts":["fixture.invalid"],"estimated_download_bytes":1024,
        "estimated_disk_bytes":4096,"cost":"0","currency":"USD","license_steps":[],
        "existing_change":"new","rollback":["remove only owned newly-created fixture files"],**changes}
    return require("environment.consent_models","InstallationPlan").model_validate_json(json.dumps(data))


def authority(p,h,answer="approve",**changes):
    question=require("environment.consent","make_question")(p,h,"Q1")
    record={"question":json.loads(question.model_dump_json()),"message_ref":"fixture-question-message-1",
        "channel":"contract_fixture","asked_at":"2026-11-26T00:01:00+00:00"}
    consent={"question_id":"Q1","question_ref":"fixture-question-message-1",
        "host_id":h.host_id,"plan_digest":require("environment.consent","plan_digest")(p),
        "answer":answer,"actor":"synthetic-test-operator","response_ref":"fixture-actual-response-2",
        "response_text":"Synthetic test approval, NOT a real vendor installation consent",
        "channel":"contract_fixture","answered_at":"2026-11-26T00:02:00+00:00",**changes}
    return require("environment.consent_models","InstallAuthority").model_validate_json(json.dumps({"question":record,"consent":consent}))


def verify(p,h,a):
    return require("environment.consent","verify_install_consent")(p,h,a)


def test_install_when_no_question_or_consent_exists():
    h=missing_host();p=plan(h)
    a=require("environment.consent_models","InstallAuthority")()
    assert verify(p,h,a)=="awaiting_consent"


def test_install_when_answer_exists_without_actual_question_record():
    h=missing_host();p=plan(h);a=authority(p,h)
    a=a.model_copy(update={"question":None})
    assert verify(p,h,a)=="awaiting_consent"


def test_install_when_question_was_only_prepared_not_asked():
    h=missing_host();p=plan(h)
    draft=require("environment.consent","make_question")(p,h,"draft-question")
    assert "설치해도" in draft.text
    assert require("environment.consent","plan_digest")(p) in draft.text
    a=require("environment.consent_models","InstallAuthority")()
    assert verify(p,h,a)=="awaiting_consent"


@pytest.mark.parametrize("answer,status",[("approve","approved"),("decline","declined")])
def test_install_when_exact_question_response_and_scope_match(answer,status):
    h=missing_host();p=plan(h)
    assert verify(p,h,authority(p,h,answer))==status


@pytest.mark.parametrize("change",[
    {"version":"new-version"},{"dependencies":[{"name":"runtime","version":"2","write_paths":["/fixture/runtime"]}]},
    {"write_paths":["/usr/local/changed"]},{"permissions":["admin"]},
    {"network_hosts":["fixture.invalid","extra.invalid"]},{"cost":"10"},
    {"source_url":"https://fixture.invalid/different.deb"},{"source_sha256":"e"*64},
    {"license_steps":["operator must accept new license"]},{"existing_change":"upgrade"},
    {"estimated_download_bytes":9999},{"system":"Darwin"},{"architecture":"arm64"},
])
def test_install_when_plan_changes_after_question_requires_new_consent(change):
    h=missing_host();p=plan(h);a=authority(p,h)
    changed=plan(h,**change)
    with pytest.raises(require("errors","ContractError")):
        verify(changed,h,a)


@pytest.mark.parametrize("field,value",[("host_id","f"*64),("question_id","other-question"),
    ("question_ref","other-message"),("plan_digest","a"*64),("channel","operator_message")])
def test_install_when_response_belongs_to_other_question_host_or_plan(field,value):
    h=missing_host();p=plan(h)
    with pytest.raises(require("errors","ContractError")):
        verify(p,h,authority(p,h,**{field:value}))


def test_install_when_question_text_was_not_the_full_exact_plan():
    h=missing_host();p=plan(h);a=authority(p,h)
    draft=a.question.question.model_copy(update={"text":"Install free software?"})
    a=a.model_copy(update={"question":a.question.model_copy(update={"question":draft})})
    with pytest.raises(require("errors","ContractError")):
        verify(p,h,a)


def test_install_when_host_inventory_changed_since_approval():
    h=missing_host();p=plan(h);a=authority(p,h)
    changed=h.model_copy(update={"architecture":"aarch64"})
    with pytest.raises(require("errors","ContractError")):
        verify(p,changed,a)


@pytest.mark.parametrize("field",["goal_activated","free_policy","yes","project_local"])
def test_install_when_generic_authority_is_not_a_real_question_response(field):
    with pytest.raises(ValidationError):
        require("environment.consent_models","InstallAuthority").model_validate_json(json.dumps({field:True}))


def test_install_when_question_contains_every_scope_and_cost_disclosure():
    h=missing_host();p=plan(h)
    text=require("environment.consent","make_question")(p,h,"Q").text
    for fragment in (h.host_id,p.version,p.source_url,"write_paths","permissions","network_hosts","cost","rollback"):
        assert fragment in text
    assert "미디어 업로드" in text
