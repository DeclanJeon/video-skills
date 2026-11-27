"""Ensure produces readiness/action, never guesses install scope or calls an installer before a real question."""
import pytest
from conftest import require
from test_environment import host,requirement
from test_install_consent import missing_host,plan,authority


def test_ensure_when_same_program_is_adequate_reuses_without_install_plan():
    a=require("environment.consent_models","InstallAuthority")()
    value=require("environment.workflow","ensure_environment")((requirement(),),host(),a)
    assert value.status=="reusable"
    assert value.question is None
    assert value.actual_question_asked is False


def test_ensure_when_missing_but_no_concrete_plan_has_no_fabricated_question():
    a=require("environment.consent_models","InstallAuthority")()
    value=require("environment.workflow","ensure_environment")((requirement(),),missing_host(),a)
    assert value.status=="planned"
    assert value.question is None
    assert value.ready is False


def test_ensure_when_plan_exists_but_question_not_asked_returns_only_full_draft():
    h=missing_host();p=plan(h)
    a=require("environment.consent_models","InstallAuthority")(install_plan=p)
    value=require("environment.workflow","ensure_environment")((requirement(),),h,a)
    assert value.status=="awaiting_consent"
    assert value.question is not None
    assert value.actual_question_asked is False


@pytest.mark.parametrize("answer,status",[("decline","declined"),("approve","approved")])
def test_ensure_when_exact_recorded_question_response_selects_only_matching_action(answer,status):
    h=missing_host();p=plan(h)
    a=authority(p,h,answer).model_copy(update={"install_plan":p})
    value=require("environment.workflow","ensure_environment")((requirement(),),h,a)
    assert value.status==status
    assert value.actual_question_asked is True
    assert value.ready is False  # Approval/action is not installer exit or native readiness.
