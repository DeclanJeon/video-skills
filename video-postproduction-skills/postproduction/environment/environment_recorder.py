"""Facts-first canonical install mirror under the actual shared project lock/CAS."""
from dataclasses import dataclass

from postproduction.environment.observation_models import EnvironmentObservation
from postproduction.errors import ContractError
from postproduction.job_models import PostStatus
from postproduction.ledger_io import document, publish, shared_lock
from postproduction.store_port import WriterPort


@dataclass(frozen=True, slots=True)
class EnvironmentRecorder:
    store: WriterPort

    def record(self, observation: EnvironmentObservation, expected_revision: int) -> PostStatus:
        """Publish known technical event before mutable source/readiness diagnosis; preserve foreign fields."""
        store = self.store
        with shared_lock(store.path):
            before = store.path.read_bytes()
            raw = document(store.path)
            state = store.read_recorded()
            if state.revision != expected_revision:
                raise ContractError("revision", "environment fact compare-and-swap failed")
            prior = tuple(e for e in state.environment_events if e.context.id == observation.context.id)
            if any(e.context != observation.context for e in prior) or observation.sequence != len(prior)+1:
                raise ContractError("environment", "install run provenance/sequence is not the exact append-only continuation")
            updated = store.reparse(state.model_copy(update={
                "revision":state.revision+1,"environment_events":(*state.environment_events,observation),
                "observed_input_issues":("diagnosis pending; installation event is not new-media permission",)}))
            store.cas_bytes(before)
            fact_bytes = publish(store.path,raw,updated)
            issues = store.input_issues(updated)
            diagnosed = updated.model_copy(update={"revision":updated.revision+1,"observed_input_issues":issues})
            store.cas_bytes(fact_bytes)
            _ = publish(store.path,raw,diagnosed)
            return PostStatus(revision=diagnosed.revision,jobs=diagnosed.jobs,inputs_ready=not issues,issues=issues)
