"""Read-only inspect/plan first. Real vendor CLI install requires this terminal's actual exact question/response."""
from datetime import datetime, timezone
from pathlib import Path
import sys
from uuid import uuid4

from pydantic import RootModel
import typer

from postproduction.cli_support import emit, input_model
from postproduction.common import Frozen
from postproduction.environment.consent import make_question, plan_digest
from postproduction.environment.consent_models import AskedQuestion, InstallAuthority, InstallConsent, InstallationPlan
from postproduction.environment.craft_installer import CraftPortableDriver
from postproduction.environment.installers import select_route
from postproduction.environment.models import EnvironmentDecision, EnvStatus, HostSnapshot, Tool, ToolRequirement
from postproduction.environment.native_smoke import NativeSmoke
from postproduction.environment.probe import inspect_host, plan_environment
from postproduction.environment.provision import Provisioner
from postproduction.environment.release_evidence import verify_release_evidence
from postproduction.environment.workflow import ensure_environment
from postproduction.errors import ContractError


class Requirements(RootModel[tuple[ToolRequirement, ...]]):
    pass


class Inspection(Frozen):
    host: HostSnapshot
    decision: EnvironmentDecision


def inspect_env(requirements: Path | None = None) -> None:
    reqs = (input_model(requirements,requirements.absolute().parent,Requirements).root if requirements is not None else
        tuple(ToolRequirement(tool=t,feature="native-postproduction") for t in (Tool.FILMCRAFT,Tool.EFFECTCRAFT,Tool.SOUNDCRAFT)))
    host = inspect_host(reqs)
    emit(Inspection(host=host,decision=plan_environment(reqs,host)))


def installation_context(file: Path) -> tuple[InstallationPlan,HostSnapshot,InstallAuthority]:
    path = file.absolute()
    plan = input_model(path,path.parent,InstallationPlan)
    host = inspect_host((ToolRequirement(tool=plan.tool,feature="explicit-installation",versions=(plan.version,)),))
    return plan,host,InstallAuthority(install_plan=plan)


def install_plan(plan_file: Path) -> None:
    plan,host,authority = installation_context(plan_file)
    emit(ensure_environment(host.requirements,host,authority))
    _ = plan


def install(plan_file: Path) -> None:
    plan,host,authority = installation_context(plan_file)
    preparation = ensure_environment(host.requirements,host,authority)
    if preparation.status==EnvStatus.REUSABLE:
        emit(preparation)
        return
    route = select_route(plan)
    if route.status!=EnvStatus.PLANNED:
        raise ContractError("needs_user_action",route.reason)
    _ = verify_release_evidence(plan_file.absolute().parent,plan)
    if plan.source_evidence_kind=="contract_fixture":
        raise ContractError("fixture", "fixture source/authority cannot authorize real CLI vendor installation")
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise ContractError("install-consent", "actual interactive operator question required; no --yes/file-policy bypass")
    question = make_question(plan,host,"CLI-"+uuid4().hex)
    asked = AskedQuestion(question=question,message_ref="tty-question-"+uuid4().hex,channel="interactive_tty",
                          asked_at=datetime.now(timezone.utc))
    typer.echo(question.text)
    answer = input(f"Type APPROVE {plan_digest(plan)} to approve this exact plan; anything else declines: ")
    consent = InstallConsent(question_id=question.id,question_ref=asked.message_ref,host_id=host.host_id,
        plan_digest=plan_digest(plan),answer="approve" if answer==f"APPROVE {plan_digest(plan)}" else "decline",
        actor="interactive-terminal-operator",response_ref="tty-response-"+uuid4().hex,response_text=answer or "(empty response)",
        channel="interactive_tty",answered_at=datetime.now(timezone.utc))
    authority = InstallAuthority(install_plan=plan,question=asked,consent=consent)
    if len(plan.write_paths)!=3:
        raise ContractError("install-plan", "portable CLI needs exact ordered target/cache/host-lease locations")
    target,cache,leases = tuple(Path(p) for p in plan.write_paths)
    driver = CraftPortableDriver(plan_file.absolute().parent,leases,cache,target,NativeSmoke(cache/"native-smoke").run)
    result = Provisioner(driver,lambda event:None).execute(plan,host,authority)
    emit(result)
    if result.status not in {EnvStatus.READY,EnvStatus.REUSABLE}:
        raise ContractError("installation", "not ready; retain receipt/known paths and reconcile explicit effects")


def register(app: typer.Typer) -> None:
    _ = app.command("inspect-env")(inspect_env)
    _ = app.command("install-plan")(install_plan)
    _ = app.command("install")(install)
