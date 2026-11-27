"""Public read-only ensure boundary: reuse first, exact prepared question/action, never implicit provisioning."""
from typing import Literal

from postproduction.common import Frozen, Nonempty
from postproduction.environment.consent import make_question, verify_install_consent
from postproduction.environment.consent_models import InstallAuthority, QuestionDraft
from postproduction.environment.models import EnvironmentDecision, EnvStatus, HostSnapshot, ToolRequirement
from postproduction.environment.probe import plan_environment
from postproduction.errors import ContractError


class EnvironmentPreparation(Frozen):
    status: EnvStatus
    decision: EnvironmentDecision
    ready: Literal[False] = False
    question: QuestionDraft | None = None
    actual_question_asked: bool = False
    action: Nonempty


def ensure_environment(requirements: tuple[ToolRequirement, ...], host: HostSnapshot,
                       authority: InstallAuthority) -> EnvironmentPreparation:
    """Installation consent is neither a fetched artifact nor successful native smoke/readiness."""
    decision = plan_environment(requirements,host)
    if decision.status in {EnvStatus.REUSABLE,EnvStatus.NOT_REQUIRED}:
        return EnvironmentPreparation(status=decision.status,decision=decision,
                                      action="reuse inspected same-program installation; native readiness remains separate")
    plan = authority.install_plan
    if plan is None:
        status = EnvStatus.PLANNED if decision.status in {EnvStatus.MISSING,EnvStatus.INCOMPATIBLE} else decision.status
        return EnvironmentPreparation(status=status,decision=decision,
            action="exact bounded release/dependency/location/privilege/network/cost/license plan required before actual question")
    req = next((r for r in requirements if r.required and r.tool == plan.tool),None)
    tool = next((d for d in decision.tools if d.tool == plan.tool),None)
    if req is None or tool is None or (req.versions and plan.version not in req.versions):
        raise ContractError("install-plan", "plan is not for a required matching tool/version")
    if tool.status not in {EnvStatus.MISSING,EnvStatus.INCOMPATIBLE}:
        return EnvironmentPreparation(status=tool.status,decision=decision,
            action="resolve incomplete/resource/required-CLI inspection first; do not add another guessed installation")
    if (tool.status == EnvStatus.MISSING and plan.existing_change != "new"
        or tool.status == EnvStatus.INCOMPATIBLE and plan.existing_change == "new"):
        raise ContractError("install-plan", "exact existing-program change differs from current inspected state")
    asked = authority.question
    draft = make_question(plan,host,asked.question.id if asked is not None else f"install-{plan.id}")
    if asked is not None and asked.question != draft:
        raise ContractError("install-consent", "actual question record differs from exact current scope")
    status = verify_install_consent(plan,host,authority)
    return EnvironmentPreparation(status=status,decision=decision,question=draft,
        actual_question_asked=asked is not None,
        action="declined: do not fetch/install" if status==EnvStatus.DECLINED else
        "approved exact action; bounded installer/lease/facts/smoke still required before ready" if status==EnvStatus.APPROVED else
        "present full question through actual operator channel; a prepared draft is not an asked receipt or consent")
