"""Intake/plan/current review/progress/delivery CLI commands, not native or installer dispatch."""
from pathlib import Path
from typing import Annotated

from pydantic import RootModel
import typer

from postproduction.adoption_models import IntakeRevision
from postproduction.cli_support import emit, input_model, store_for
from postproduction.common import Pin
from postproduction.delivery_models import DeliveryContract
from postproduction.intake import load_intake
from postproduction.progress import project_progress
from postproduction.quality_models import QualitySubmission
from postproduction.state_models import PostState
from postproduction.timeline import build_timeline
from postproduction.timeline_models import EditProposal


class Pins(RootModel[tuple[Pin, ...]]):
    pass


def intake(project: Path, request: Annotated[Path,typer.Option()], revision: Path | None = None) -> None:
    store = store_for(project)
    if revision is not None:
        change = input_model(revision,store.path.parent,IntakeRevision)
        emit(store.record_revision(change,store.read_recorded().revision))
        return
    actual = load_intake(store.path.parent,request,store.path)
    state = PostState(intake=actual,timelines=(build_timeline(actual),))
    store.initialize(state)
    emit(store.status())


def validate(project: Path) -> None:
    store = store_for(project)
    _ = store.read()
    emit(store.status())


def plan(project: Path, proposal: Path | None = None, commit: bool = False) -> None:
    store = store_for(project)
    state = store.read()
    decision = input_model(proposal,store.path.parent,EditProposal) if proposal is not None else None
    parent = state.timelines[0] if decision is not None else None
    timeline = build_timeline(state.intake,decision,parent)
    if commit:
        timeline = timeline.model_copy(update={"revision":state.timelines[0].revision+1})
        with store.transaction(state.revision) as tx:
            others = tuple(t for t in state.timelines if t.branch!=timeline.branch)
            old = tuple(t for t in state.timelines if t.branch==timeline.branch)
            tx.state = tx.state.model_copy(update={"timelines":(*others,timeline),
                "timeline_history":(*state.timeline_history,*old)})
    emit(timeline)


def progress(project: Path) -> None:
    store = store_for(project)
    emit(project_progress(store.read_recorded(),store.path))


def review(project: Path, report: Path) -> None:
    store = store_for(project)
    value = input_model(report,store.path.parent,QualitySubmission)
    emit(store.record_review(value,store.read_recorded().revision))


def invalidate(project: Path, pins: Path) -> None:
    store = store_for(project)
    value = input_model(pins,store.path.parent,Pins).root
    emit(store.record_invalidation(value,store.read_recorded().revision))


def deliver(project: Path, contract: Path) -> None:
    store = store_for(project)
    value = input_model(contract,store.path.parent,DeliveryContract)
    emit(store.record_delivery(value,store.read_recorded().revision))


def register(app: typer.Typer) -> None:
    _ = app.command("intake")(intake)
    _ = app.command("validate")(validate)
    _ = app.command("plan")(plan)
    _ = app.command("progress")(progress)
    _ = app.command("review")(review)
    _ = app.command("invalidate")(invalidate)
    _ = app.command("deliver")(deliver)
