"""Actual production input acceptance: physical currentness precedes post adoption."""
import hashlib
from pathlib import Path
from typing import ClassVar, assert_never

from pydantic import BaseModel, ConfigDict, TypeAdapter, ValidationError
import production.models as production_models
from production.handoff import build_handoff
from production.models import ContractError as ProductionError, Handoff, State

from postproduction.admission import admit_source
from postproduction.audio import verify_stem
from postproduction.authority import authorize
from postproduction.edit_models import DeliveryProfile, EditAuthority, EditBrief
from postproduction.errors import ContractError
from postproduction.files import confined_path, read_model, verified_file
from postproduction.intake_checks import snapshot_namespace_is_separate, verify_anchors, verify_review
from postproduction.intake_models import IntakeRequest, PostIntake


class ProjectSnapshot(BaseModel):
    """Read only the production namespace; foreign project fields are not rewritten."""

    model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True, extra="ignore")
    production: State


def load_snapshot(root: Path, request: IntakeRequest) -> State:
    """Accept a standalone immutable export or a pinned existing project namespace."""
    path = verified_file(root,request.snapshot)
    value = TypeAdapter(State | ProjectSnapshot).validate_json(path.read_bytes())
    match value:
        case State() as state:
            return state
        case ProjectSnapshot(production=state):
            return state
    assert_never(value)


def adopt_request(root: Path, request: IntakeRequest, ledger: Path | None = None) -> PostIntake:
    """Re-observe an already parsed immutable request without writing a temporary input file."""
    try:
        root = root.absolute()
        _ = verified_file(root,request.schema_pin)
        runtime_schema = production_models.__file__
        if hashlib.sha256(Path(runtime_schema).read_bytes()).hexdigest() != request.schema_pin.sha256:
            raise ContractError("schema", "input schema is not the actual production model version")
        state = load_snapshot(root,request)
        snapshot_namespace_is_separate(state,root,root/request.snapshot.path,ledger)
        handoff = read_model(root,request.handoff,Handoff)
        actual = build_handoff(state,handoff.flow,handoff.receiver,handoff.rights_evidence,root)
        if actual != handoff or any(before or after for _,before,after in handoff.handles):
            raise ContractError("handoff", "current handoff differs; exterior handles are not certified")
        sources = tuple(admit_source(state,selected,root) for selected in handoff.selections)
        intake = PostIntake(request=request,snapshot=state,handoff=handoff,sources=sources,
                            brief=read_model(root,request.brief,EditBrief),
                            authority=read_model(root,request.authority,EditAuthority),
                            profile=read_model(root,request.profile,DeliveryProfile))
        upstream = {p.id for p in request.upstream}
        if len(upstream) != len(request.upstream) or set(intake.brief.required_assets)-upstream:
            raise ContractError("asset", "required assets are missing or ambiguously identified")
        for pin in request.upstream:
            _ = verified_file(root,pin)
        ids = tuple(s.id for s in request.stems)
        if len(set(ids)) != len(ids) or set(intake.brief.required_stems)-set(ids):
            raise ContractError("stem", "actual required separate stem inventory is missing/ambiguous")
        for stem in request.stems:
            _ = verify_stem(root,stem)
        for stem in request.stems:
            if any(other.role != stem.role and other.asset.sha256 == stem.asset.sha256 for other in request.stems):
                raise ContractError("stem", "one identical mixed source cannot be relabeled as different component stems")
        for selected in handoff.selections:
            if selected.review.post_receiver and selected.review.post_receiver != handoff.receiver:
                raise ContractError("conditional", "repair receiver does not match current handoff")
        authorize(intake,root)
        verify_review(intake,root)
        verify_anchors(intake,root)
        return intake
    except (ProductionError,ValidationError,OSError) as exc:
        raise ContractError("intake", f"production/record admission failed: {exc}") from exc


def load_intake(root: Path, request_path: Path, ledger: Path | None = None) -> PostIntake:
    """Parse and re-observe the complete input set; no registry write or remote calls."""
    root = root.absolute()
    absolute_request = request_path if request_path.is_absolute() else root/request_path
    try:
        relative_request = absolute_request.relative_to(root)
    except ValueError as exc:
        raise ContractError("path", "request must be project-local") from exc
    request_file = confined_path(root,relative_request.as_posix())
    if not request_file.is_file():
        raise ContractError("file", "request must be a regular project-local record")
    try:
        request = IntakeRequest.model_validate_json(request_file.read_bytes())
    except (OSError,ValidationError) as exc:
        raise ContractError("intake", "invalid intake request record") from exc
    return adopt_request(root,request,ledger)
