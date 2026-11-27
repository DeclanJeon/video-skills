"""One writer/CAS publishes exact computed current review; caller cannot provide precomputed local gate results."""
from dataclasses import dataclass

from postproduction.errors import ContractError
from postproduction.ledger_io import document, publish, shared_lock
from postproduction.quality import review_artifact
from postproduction.quality_models import QualityReport, QualitySubmission
from postproduction.store_port import WriterPort


@dataclass(frozen=True,slots=True)
class QualityRecorder:
    store: WriterPort

    def record(self, submission: QualitySubmission, expected_revision: int) -> QualityReport:
        with shared_lock(self.store.path):
            before = self.store.path.read_bytes()
            raw = document(self.store.path)
            state = self.store.read_recorded()
            if state.revision!=expected_revision:
                raise ContractError("revision", "review compare-and-swap failed")
            updated = self.store.reparse(review_artifact(state,submission,self.store.path))
            self.store.cas_bytes(before)
            _ = publish(self.store.path,raw,updated.model_copy(update={"revision":state.revision+1}))
            return updated.reviews[-1]
