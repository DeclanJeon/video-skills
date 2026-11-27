"""Local operator CLI. There is intentionally no upload/generate/execute command."""
from dataclasses import asdict
import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel, TypeAdapter, ValidationError
import typer

from production.adapters import export_coverage, verify_scope
from production.bindings import prepare_request
from production.contracts import ready_clips
from production.execution import reserve
from production.handoff import build_handoff, check_join, progress, selection_hash
from production.models import (
    AttemptId, Authority, Binding, Capability, ContractError, FlowReview,
    JoinReview, Prepared, Receipt, Review, State, Take,
)
from production.quality import accept_take, accept_supplied, revalidate_take
from production.scope import ScopeGrant, revise_scope
from production.revisions import invalidate_selection
from production.store import ProjectStore

app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False, help=__doc__)
T = TypeVar("T", bound=BaseModel)


def load(path: Path, model: type[T]) -> T:
    return model.model_validate_json(path.read_bytes())


def output(model: BaseModel) -> None:
    typer.echo(model.model_dump_json(indent=2))


@app.command("init")
def initialize(ledger: Path, input_file: Path) -> None:
    """Initialize only the production namespace, preserving existing ledger fields."""
    state = load(input_file, State)
    verify_scope(state, ledger.parent)
    ProjectStore(ledger).initialize(state)
    typer.echo(json.dumps({"initialized": True, "revision": state.revision}))


@app.command()
def validate(ledger: Path) -> None:
    state = ProjectStore(ledger).read()
    verify_scope(state, ledger.parent)
    typer.echo(json.dumps({"valid": True, "revision": state.revision}))


@app.command()
def ready(ledger: Path) -> None:
    state = ProjectStore(ledger).read()
    typer.echo(json.dumps({"ready": ready_clips(state), "revision": state.revision}))


@app.command("status")
def recorded_status(ledger: Path) -> None:
    """Read durable job identities and scope diagnostics, even if preparation inputs are broken."""
    typer.echo(json.dumps(asdict(ProjectStore(ledger).status())))


@app.command("progress")
def show_progress(ledger: Path) -> None:
    typer.echo(json.dumps(asdict(progress(ProjectStore(ledger).read()))))


@app.command("coverage")
def coverage_source(project: Path) -> None:
    """Derive required shot/panel/beat/speech source coverage, without drafting a batch."""
    output(export_coverage(project))


@app.command()
def prepare(ledger: Path, clip: str, capability: Path, authority: Path, bindings: Path) -> None:
    state = ProjectStore(ledger).read()
    refs = TypeAdapter(tuple[Binding, ...]).validate_json(bindings.read_bytes())
    output(prepare_request(state, clip, load(capability, Capability), load(authority, Authority), refs, ledger.parent))


@app.command("reserve")
def reserve_attempt(ledger: Path, packet: Path, attempt: str, revision: int, external_active: int) -> None:
    """Persist a pre-submission reservation. This command does NOT submit."""
    store = ProjectStore(ledger)
    with store.transaction(revision) as tx:
        tx.state = reserve(tx.state, load(packet, Prepared), AttemptId(attempt), external_active, ledger.parent)
    typer.echo(json.dumps({"reserved": attempt, "submitted": False}))


@app.command("observe")
def observe_receipt(ledger: Path, attempt: str, receipt: Path, revision: int) -> None:
    """Import a supplied exact request/job receipt; never re-submit an unknown job."""
    result = ProjectStore(ledger).record_observation(attempt,load(receipt,Receipt),revision)
    typer.echo(json.dumps({"recorded": attempt, **asdict(result)}))


@app.command("review")
def publish_review(ledger: Path, take: Path, review: Path, expected_fingerprint: str, revision: int) -> None:
    store = ProjectStore(ledger)
    with store.transaction(revision) as tx:
        tx.state = accept_take(tx.state, load(take, Take), load(review, Review), expected_fingerprint, ledger.parent)
    typer.echo(json.dumps({"review_recorded": True}))


@app.command("reuse")
def reuse(ledger: Path, take: Path, review: Path, authority: Path, revision: int) -> None:
    """Admit an explicitly approved existing source without inventing a remote attempt."""
    store = ProjectStore(ledger)
    with store.transaction(revision) as tx:
        tx.state = accept_supplied(tx.state, load(take,Take), load(review,Review), load(authority,Authority), ledger.parent)
    typer.echo(json.dumps({"source_reused":True,"remote_submission":False}))


@app.command("revise-scope")
def amend_scope(ledger: Path, batch: Path, grant: Path, revision: int) -> None:
    from production.models import Batch
    store = ProjectStore(ledger)
    with store.transaction(revision) as tx:
        tx.state = revise_scope(tx.state,load(batch,Batch),load(grant,ScopeGrant),ledger.parent)
    typer.echo(json.dumps({"scope_revised":True}))


@app.command("invalidate")
def invalidate(ledger: Path, clip: str, evidence: str, revision: int) -> None:
    store = ProjectStore(ledger)
    with store.transaction(revision) as tx:
        tx.state = invalidate_selection(tx.state, clip, evidence)
    typer.echo(json.dumps({"invalidated": clip}))


@app.command("revalidate")
def revalidate(ledger: Path, clip: str, review: Path, expected_fingerprint: str, revision: int, authority: Path | None = None) -> None:
    store = ProjectStore(ledger)
    with store.transaction(revision) as tx:
        tx.state = revalidate_take(tx.state, clip, load(review, Review), expected_fingerprint, ledger.parent, load(authority, Authority) if authority else None)
    typer.echo(json.dumps({"revalidated": clip}))


@app.command("probe")
def probe(ledger: Path, asset: Path) -> None:
    from production.media import probe_media
    from production.models import Pin
    typer.echo(json.dumps(asdict(probe_media(ledger.parent, load(asset, Pin)))))


@app.command("join")
def record_join(ledger: Path, review: Path, revision: int) -> None:
    store = ProjectStore(ledger)
    report = load(review, JoinReview)
    with store.transaction(revision) as tx:
        check_join(tx.state, report)
        tx.state = tx.state.model_copy(update={"join_reviews": (*tuple(j for j in tx.state.join_reviews if j.join_id != report.join_id), report)})
    typer.echo(json.dumps({"join_recorded": report.join_id}))


@app.command("render-review")
def render_montage(ledger: Path, output_path: str) -> None:
    """Render a local review-only montage; never a final master or remote generation."""
    from production.render import render_review
    output(render_review(ProjectStore(ledger).read(), ledger.parent, output_path))


@app.command("flow-hash")
def flow_hash(ledger: Path) -> None:
    typer.echo(json.dumps({"selection_hash": selection_hash(ProjectStore(ledger).read())}))


@app.command("handoff")
def handoff(ledger: Path, flow: Path, receiver: str, rights_evidence: str) -> None:
    from production.render import verify_render
    state = ProjectStore(ledger).read()
    report = load(flow, FlowReview)
    verify_render(state, ledger.parent, report.review_render)
    output(build_handoff(state, report, receiver, rights_evidence, ledger.parent))


def main() -> None:
    try:
        app()
    except (ContractError, ValidationError, OSError, UnicodeError) as exc:
        typer.echo(json.dumps({"status": "blocked", "error": str(exc), "new_submission": False}, ensure_ascii=False))
        raise SystemExit(2) from exc
