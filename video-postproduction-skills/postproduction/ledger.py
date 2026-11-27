"""One post namespace in the actual shared project file; no private production method bypass."""
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from pydantic import JsonValue, TypeAdapter, ValidationError
from pydantic_core import PydanticSerializationError

from postproduction.currentness import validate_current, validate_structure
from postproduction.errors import ContractError
from postproduction.environment.environment_recorder import EnvironmentRecorder
from postproduction.environment.observation_models import EnvironmentObservation
from postproduction.job_models import ArtifactRef, JobReceipt, PostJob, PostStatus
from postproduction.work_models import RequestPacket
from postproduction.revisions import invalidate_dependents, verify_work_inputs
from postproduction.common import Pin
from postproduction.adoption_models import IntakeRevision
from postproduction.adoption_recorder import AdoptionRecorder
from postproduction.delivery_models import DeliveryContract, DeliveryRecord
from postproduction.delivery_recorder import DeliveryRecorder
from postproduction.quality_models import QualityReport, QualitySubmission
from postproduction.quality_recorder import QualityRecorder
from postproduction.jobs import observe_job, reserve_work, validate_jobs
from postproduction.transitions import validate_edit_transition
from postproduction.ledger_io import check_paths, document, publish, shared_lock
from postproduction.state_models import PostState


@dataclass
class PostTransaction:
    """Mutable locked transaction buffer; publication always reparses untrusted model_copy."""
    state: PostState


class PostStore:
    """Preserve producer/foreign fields and increment only this namespace revision."""

    def __init__(self, path: Path) -> None:
        self.path: Path = path.absolute()

    def initialize(self, state: PostState) -> None:
        """Attach a validated initial post namespace without replacing another project owner."""
        with shared_lock(self.path):
            before = self.path.read_bytes() if self.path.exists() else None
            raw = document(self.path)
            if "postproduction" in raw:
                raise ContractError("exists", "post namespace already exists; resume it")
            validated = self.reparse(state)
            if (validated.revision != 0 or validated.orders or validated.jobs or validated.artifacts
                or validated.timeline_history or validated.environment_events or validated.invalidations or validated.reviews or validated.deliveries or validated.intake_history):
                raise ContractError("initial", "init requires a clean post plan; resume actual known facts instead")
            validate_current(validated,self.path)
            self.cas_bytes(before)
            _ = publish(self.path,raw,validated)

    def reparse(self, state: PostState) -> PostState:
        """Validate the actual serialized record, not a model_copy trust bypass."""
        try:
            value = PostState.model_validate_json(state.model_dump_json(warnings="error"))
            validate_structure(value)
            return value
        except (ValidationError,PydanticSerializationError) as exc:
            raise ContractError("state", "post state failed strict persistence parse") from exc

    def cas_bytes(self, before: bytes | None) -> None:
        """A noncooperating external writer is not overwritten even if it ignores the shared lock."""
        actual = self.path.read_bytes() if self.path.exists() else None
        if actual != before:
            raise ContractError("conflict", "project bytes changed outside cooperating writer lock")

    def read_recorded(self) -> PostState:
        """Historical model-valid facts remain available after mutable media or rights are lost."""
        _ = check_paths(self.path)
        raw = document(self.path)
        if "postproduction" not in raw:
            raise ContractError("state", "postproduction namespace missing")
        try:
            value = PostState.model_validate_json(TypeAdapter(JsonValue).dump_json(raw["postproduction"]))
            validate_jobs(value)
            return value
        except ValidationError as exc:
            raise ContractError("state", "stored post state failed strict parse") from exc

    def read(self) -> PostState:
        """Current readiness is a fresh separate gate, not a property of historical existence."""
        state = self.read_recorded()
        validate_current(state,self.path)
        return state

    def input_issues(self, state: PostState) -> tuple[str, ...]:
        """Mutable readiness diagnostics never grant a new dispatch from historical observation."""
        try:
            validate_current(state,self.path)
        except (ContractError,OSError,ValidationError) as exc:
            return (str(exc),)
        return ()

    def status(self) -> PostStatus:
        state = self.read_recorded()
        issues = self.input_issues(state)
        return PostStatus(revision=state.revision,jobs=state.jobs,inputs_ready=not issues,issues=issues)

    def record_observation(self, job_id: str, receipt: JobReceipt, expected_revision: int) -> PostStatus:
        """Persist known job facts before diagnostics; deliberately not a generic mutation bypass."""
        with shared_lock(self.path):
            before = self.path.read_bytes()
            raw = document(self.path)
            state = self.read_recorded()
            if state.revision != expected_revision:
                raise ContractError("revision", "observation compare-and-swap failed")
            updated = self.reparse(observe_job(state,job_id,receipt))
            facts = updated.model_copy(update={"revision":state.revision+1,
                "observed_input_issues":("readiness diagnosis pending; historical fact is not new-work permission",)})
            self.cas_bytes(before)
            fact_bytes = publish(self.path,raw,facts)
            issues = self.input_issues(facts)
            diagnosed = facts.model_copy(update={"revision":facts.revision+1,"observed_input_issues":issues})
            self.cas_bytes(fact_bytes)
            _ = publish(self.path,raw,diagnosed)
            return PostStatus(revision=diagnosed.revision,jobs=diagnosed.jobs,inputs_ready=not issues,issues=issues)

    def record_revision(self, adoption: IntakeRevision, expected_revision: int) -> PostState:
        """Re-admit actual new pinned source scope without rewriting old decisions/job facts."""
        return AdoptionRecorder(self).record(adoption,expected_revision)

    def record_delivery(self, contract: DeliveryContract, expected_revision: int) -> DeliveryRecord:
        """No precomputed delivered/PASS flag; builder rechecks current gates and actual scoped bytes."""
        return DeliveryRecorder(self).record(contract,expected_revision)

    def record_review(self, submission: QualitySubmission, expected_revision: int) -> QualityReport:
        """Exact scoped reported checks are evaluated locally; precomputed gates cannot be imported as PASS."""
        return QualityRecorder(self).record(submission,expected_revision)

    def record_invalidation(self, pins: tuple[Pin, ...], expected_revision: int) -> PostStatus:
        """Narrow scoped revocation retains old facts even when changed input bytes no longer exist."""
        with shared_lock(self.path):
            before = self.path.read_bytes()
            raw = document(self.path)
            state = self.read_recorded()
            if state.revision != expected_revision:
                raise ContractError("revision", "invalidation compare-and-swap failed")
            updated = self.reparse(invalidate_dependents(state,pins).model_copy(update={"revision":state.revision+1}))
            self.cas_bytes(before)
            _ = publish(self.path,raw,updated)
            issues = self.input_issues(updated)
            return PostStatus(revision=updated.revision,jobs=updated.jobs,inputs_ready=not issues,issues=issues)

    def record_environment(self, observation: EnvironmentObservation, expected_revision: int) -> PostStatus:
        """Narrow append-only installation fact, not a media/readiness/adoption bypass."""
        return EnvironmentRecorder(self).record(observation,expected_revision)

    def record_reservation(self, packet: RequestPacket, expected_revision: int) -> PostJob:
        """Scope admission to actual consumed inputs; never let unrelated loss grant full final readiness."""
        with shared_lock(self.path):
            before = self.path.read_bytes()
            raw = document(self.path)
            state = self.read_recorded()
            if state.revision != expected_revision:
                raise ContractError("revision", "reservation compare-and-swap failed")
            verify_work_inputs(state,packet.order,self.path)
            updated = self.reparse(reserve_work(state,packet))
            self.cas_bytes(before)
            _ = publish(self.path,raw,updated.model_copy(update={"revision":state.revision+1}))
            return updated.jobs[-1]

    def record_materialization(self, job_id: str, expected_revision: int) -> ArtifactRef:
        """Narrow actual-backend verification, not a caller-controlled artifact/adoption replacement."""
        from postproduction.materialization import checked_materialization, verify_artifact_current
        with shared_lock(self.path):
            before = self.path.read_bytes()
            raw = document(self.path)
            state = self.read_recorded()
            if state.revision != expected_revision:
                raise ContractError("revision", "materialization compare-and-swap failed")
            artifact = checked_materialization(self,state,job_id)
            prior = next((a for a in state.artifacts if a.id == artifact.id),None)
            if prior is not None:
                if prior != artifact:
                    raise ContractError("artifact", "known materialization identity cannot be silently replaced")
                verify_artifact_current(state,prior,self.path)
                return prior
            updated = self.reparse(state.model_copy(update={"artifacts":(*state.artifacts,artifact)}))
            verify_artifact_current(updated,artifact,self.path)
            self.cas_bytes(before)
            _ = publish(self.path,raw,updated.model_copy(update={"revision":state.revision+1}))
            return artifact

    @contextmanager
    def transaction(self, expected_revision: int) -> Generator[PostTransaction]:
        with shared_lock(self.path):
            before = self.path.read_bytes()
            raw = document(self.path)
            state = self.read_recorded()
            if state.revision != expected_revision:
                raise ContractError("revision", "post namespace compare-and-swap failed")
            validate_current(state,self.path)
            tx = PostTransaction(state)
            yield tx
            validated = self.reparse(tx.state)
            if validated.revision != state.revision:
                raise ContractError("revision", "namespace revision is owned by the store")
            validate_edit_transition(state,validated)
            validate_current(validated,self.path)
            self.cas_bytes(before)
            _ = publish(self.path,raw,validated.model_copy(update={"revision":state.revision+1}))
