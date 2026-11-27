"""Current exact source/edit revision preserves historical work, process facts and original typed source snapshots."""
from dataclasses import dataclass
import hashlib

from postproduction.adoption_models import IntakeRevision
from postproduction.currentness import validate_current
from postproduction.edit_models import Change
from postproduction.errors import ContractError
from postproduction.files import verified_file
from postproduction.intake import adopt_request
from postproduction.job_models import ArtifactRef
from postproduction.ledger_io import document, publish, shared_lock
from postproduction.revisions import work_fingerprint
from postproduction.state_models import PostState
from postproduction.store_port import WriterPort


@dataclass(frozen=True,slots=True)
class AdoptionRecorder:
    store: WriterPort

    def record(self, adoption: IntakeRevision, expected_revision: int) -> PostState:
        with shared_lock(self.store.path):
            before = self.store.path.read_bytes()
            raw = document(self.store.path)
            state = self.store.read_recorded()
            if (state.revision!=expected_revision or adoption.previous_intake_digest!=
                hashlib.sha256(state.intake.model_dump_json().encode()).hexdigest()):
                raise ContractError("revision", "exact previous current intake/namespace revision differs")
            if (adoption.intake.request.project_id,adoption.intake.handoff.receiver)!=(
                state.intake.request.project_id,state.intake.handoff.receiver):
                raise ContractError("scope", "cannot replace namespace with another project/receiver")
            _ = verified_file(self.store.path.parent,adoption.evidence)
            actual = adopt_request(self.store.path.parent,adoption.intake.request,self.store.path)
            if actual!=adoption.intake:
                raise ContractError("intake", "new adopted inputs do not match actual current files/producer")
            if ({t.branch for t in adoption.timelines}!={t.branch for t in state.timelines}
                and Change.BRANCH not in actual.authority.allowed_changes):
                raise ContractError("branch", "branch denominator change requires exact new branch scope")
            updated = state.model_copy(update={"intake":actual,"intake_history":(*state.intake_history,state.intake),
                "timelines":adoption.timelines,"timeline_history":(*state.timeline_history,*state.timelines)})
            artifacts: list[ArtifactRef] = []
            for artifact in updated.artifacts:
                job = next(j for j in updated.jobs if j.id==artifact.job_id)
                try:
                    current = work_fingerprint(updated,job.packet.order)==artifact.input_fingerprint
                except ContractError:
                    current = False
                artifacts.append(artifact if current else artifact.model_copy(update={"adopted":False}))
            updated = self.store.reparse(updated.model_copy(update={"artifacts":tuple(artifacts),"revision":state.revision+1}))
            validate_current(updated,self.store.path)
            self.store.cas_bytes(before)
            _ = publish(self.store.path,raw,updated)
            return updated
