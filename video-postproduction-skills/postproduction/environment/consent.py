"""Question-first exact scope matching; matching records do not authenticate a human issuer."""
import hashlib
from typing import assert_never

from postproduction.environment.consent_models import (
    InstallAuthority, InstallationPlan, QuestionDraft,
)
from postproduction.environment.models import EnvStatus, HostSnapshot
from postproduction.errors import ContractError


def host_fingerprint(host: HostSnapshot) -> str:
    """Bind stable inspected state, not volatile free RAM/disk/time or transient package locks."""
    data = host.model_dump_json(exclude={
        "inspected_at","disk_available_bytes","memory_available_bytes","package_lock_status",
    })
    return hashlib.sha256(data.encode()).hexdigest()


def plan_digest(plan: InstallationPlan) -> str:
    """Every declared scope/dependency/permission/cost change requires a new question."""
    return hashlib.sha256(plan.model_dump_json().encode()).hexdigest()


def bound_host(plan: InstallationPlan, host: HostSnapshot) -> None:
    """A grant for one host/inspection is never an unscoped machine installation permission."""
    if ((plan.host_id,plan.system,plan.architecture,plan.host_fingerprint)
        != (host.host_id,host.system,host.architecture,host_fingerprint(host))):
        raise ContractError("install-consent", "host or inspected installation state changed; inspect/ask again")


def make_question(plan: InstallationPlan, host: HostSnapshot, question_id: str) -> QuestionDraft:
    """Prepare a fully disclosed question; this alone is NOT an actually asked question receipt."""
    bound_host(plan,host)
    digest = plan_digest(plan)
    text = (
        "시스템/동일 프로그램 점검 후 필요한 아래 정확한 계획으로 설치해도 될까요?\n"
        "null 수치/공급망·라이선스 미확인은 미확인으로 남습니다. 기존 설치/범위 변경은 다시 묻습니다.\n"
        "이 동의는 미디어 업로드·구매·로그인·계획 밖 변경을 허용하지 않습니다.\n"
        f"host={host.host_id}\nplan_sha256={digest}\n{plan.model_dump_json(indent=2)}"
    )
    return QuestionDraft(id=question_id,host_id=host.host_id,plan_digest=digest,text=text)


def verify_install_consent(plan: InstallationPlan, host: HostSnapshot, authority: InstallAuthority) -> EnvStatus:
    """Check captured question/answer against exact current scope without any install/fetch side effects."""
    bound_host(plan,host)
    asked,consent = authority.question,authority.consent
    if asked is None or consent is None:
        return EnvStatus.AWAITING_CONSENT
    expected = make_question(plan,host,asked.question.id)
    if asked.question != expected:
        raise ContractError("install-consent", "the actual question did not disclose this exact plan")
    if (consent.question_id != asked.question.id or consent.question_ref != asked.message_ref
        or consent.host_id != host.host_id or consent.plan_digest != plan_digest(plan)
        or consent.channel != asked.channel or consent.response_ref == asked.message_ref
        or consent.answered_at < asked.asked_at):
        raise ContractError("install-consent", "response is not for this actual question/host/plan")
    match consent.answer:
        case "approve":
            return EnvStatus.APPROVED
        case "decline":
            return EnvStatus.DECLINED
    assert_never(consent.answer)
