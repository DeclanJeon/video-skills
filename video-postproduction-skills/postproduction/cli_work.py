"""Actual canonical native prepare/reserve/run/observe commands; historical succeeded is not final adoption."""
from pathlib import Path
from typing import Literal

from pydantic import RootModel
import typer

from postproduction.backend_registry import for_job, for_order
from postproduction.backends.base import JobObservation
from postproduction.cli_support import emit, input_model, store_for
from postproduction.common import Frozen
from postproduction.environment.models import Tool
from postproduction.errors import ContractError
from postproduction.job_models import ArtifactRef
from postproduction.work_models import RequestPacket, WorkOrder


class SourceIds(Frozen):
    source_ids: tuple[int, ...]


class Observed(Frozen):
    status: Literal["materialized"] = "materialized"
    backend: Tool
    artifact: ArtifactRef
    native_readback: SourceIds


class Prepared(RootModel[RequestPacket]):
    pass


def ready(project: Path, order: Path) -> None:
    store = store_for(project)
    value = input_model(order,store.path.parent,WorkOrder)
    workspace = store.path.parent/".post-native"/value.backend.value
    workspace.mkdir(parents=True,exist_ok=True)
    backend = for_order(store,value,workspace)
    packet = backend.prepare(value,backend.inspect(),store.read_recorded().intake.authority)
    emit(Prepared(packet))


def prepare(project: Path, order: Path) -> None:
    store = store_for(project)
    value = input_model(order,store.path.parent,WorkOrder)
    workspace = store.path.parent/".post-native"/value.backend.value
    workspace.mkdir(parents=True,exist_ok=True)
    backend = for_order(store,value,workspace)
    packet = backend.prepare(value,backend.inspect(),store.read_recorded().intake.authority)
    emit(store.record_reservation(packet,store.read_recorded().revision))


def run(project: Path, job_id: str) -> None:
    store = store_for(project)
    job = next((j for j in store.read_recorded().jobs if j.id==job_id),None)
    if job is None:
        raise ContractError("job", "canonical reserved job missing")
    emit(for_job(store,job).execute(job.packet))


def observe(project: Path, job_id: str, facts_only: bool = False) -> None:
    store = store_for(project)
    job = next((j for j in store.read_recorded().jobs if j.id==job_id),None)
    if job is None:
        raise ContractError("job", "canonical reserved job missing")
    if facts_only:
        emit(job)
        return
    value: JobObservation = for_job(store,job).observe(job)
    artifact = store.record_materialization(job.id,store.read_recorded().revision)
    ids = tuple(sorted({*(m.native_item for m in value.mapping),*(m.native_source for m in value.audio_mapping),
                        *(m.native_item for m in value.artifact_mapping)}))
    emit(Observed(backend=job.packet.order.backend,artifact=artifact,native_readback=SourceIds(source_ids=ids)))


def register(app: typer.Typer) -> None:
    _ = app.command("ready")(ready)
    _ = app.command("prepare")(prepare)
    _ = app.command("run")(run)
    _ = app.command("render")(run)
    _ = app.command("observe")(observe)
