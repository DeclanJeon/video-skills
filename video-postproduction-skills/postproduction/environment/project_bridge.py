"""Installer callback adapter: host lease journal facts precede this canonical project mirror."""
from dataclasses import dataclass
from typing import Protocol

from postproduction.environment.install_models import InstallEvent
from postproduction.environment.observation_models import EnvironmentObservation, InstallContext
from postproduction.job_models import PostStatus
from postproduction.store_port import WriterPort


class EnvironmentWriter(WriterPort,Protocol):
    def record_environment(self, observation: EnvironmentObservation, expected_revision: int) -> PostStatus: ...


@dataclass(frozen=True, slots=True)
class InstallProjectBridge:
    store: EnvironmentWriter
    context: InstallContext

    def record(self, event: InstallEvent) -> None:
        """No permission to replace producer/foreign data, reset history or claim perceptual readiness."""
        state = self.store.read_recorded()
        count = sum(e.context.id == self.context.id for e in state.environment_events)
        observation = EnvironmentObservation(context=self.context,sequence=count+1,event=event)
        _ = self.store.record_environment(observation,state.revision)
