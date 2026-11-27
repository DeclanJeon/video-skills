"""Canonical known local delivery facts follow durable bundle publication; no competing package decision registry."""
from dataclasses import dataclass

from postproduction.delivery import build_delivery
from postproduction.delivery_models import DeliveryContract, DeliveryRecord
from postproduction.errors import ContractError
from postproduction.ledger_io import document, publish, shared_lock
from postproduction.store_port import WriterPort


@dataclass(frozen=True,slots=True)
class DeliveryRecorder:
    store: WriterPort

    def record(self, contract: DeliveryContract, expected_revision: int) -> DeliveryRecord:
        with shared_lock(self.store.path):
            before = self.store.path.read_bytes()
            raw = document(self.store.path)
            state = self.store.read_recorded()
            if state.revision!=expected_revision:
                raise ContractError("revision", "delivery compare-and-swap failed")
            if any(d.contract.id==contract.id for d in state.deliveries):
                raise ContractError("delivery", "known delivery identity already exists; observe/version instead of replay")
            bundle = build_delivery(state,contract,self.store.path)
            record = DeliveryRecord(contract=contract,bundle=bundle)
            updated = self.store.reparse(state.model_copy(update={"deliveries":(*state.deliveries,record),"revision":state.revision+1}))
            self.store.cas_bytes(before)
            _ = publish(self.store.path,raw,updated)
            return record
