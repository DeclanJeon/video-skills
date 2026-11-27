"""Qualified native domain dispatch; no accidental FFmpeg replacement or arbitrary off-project workspace."""
from dataclasses import dataclass
from pathlib import Path
from typing import assert_never

from postproduction.backends.base import Backend, CapabilitySnapshot
from postproduction.backends.effectcraft import EffectCraftBackend
from postproduction.backends.filmcraft import FilmCraftBackend
from postproduction.backends.finishing import FinishingBackend
from postproduction.backends.soundcraft import SoundCraftBackend
from postproduction.environment.models import EnvStatus, Tool, ToolRequirement
from postproduction.environment.policy import decide_tool
from postproduction.environment.probe import inspect_host
from postproduction.errors import ContractError
from postproduction.job_models import PostJob
from postproduction.probe_models import Projection
from postproduction.store_port import ProjectPort
from postproduction.work_models import Domain, WorkOrder


class PlanLocation(Projection):
    workspace: Path
    capability: CapabilitySnapshot


@dataclass(frozen=True,slots=True)
class BackendWorkspace:
    store: ProjectPort
    workspace: Path
    binary: Path

    def create(self, order: WorkOrder) -> Backend:
        match order.backend:
            case Tool.FILMCRAFT:
                match order.domain:
                    case Domain.PICTURE:
                        return FilmCraftBackend(self.store,self.workspace,self.binary)
                    case Domain.FINISHING:
                        return FinishingBackend(self.store,self.workspace,self.binary)
                    case Domain.MOTION | Domain.COLOR | Domain.SOUND | Domain.CAPTIONS | Domain.QA | Domain.DELIVERY | Domain.ENVIRONMENT:
                        raise ContractError("backend", "unqualified FilmCraft domain")
                assert_never(order.domain)
            case Tool.EFFECTCRAFT:
                if order.domain!=Domain.MOTION:
                    raise ContractError("backend", "native composition domain required")
                return EffectCraftBackend(self.store,self.workspace,self.binary)
            case Tool.SOUNDCRAFT:
                if order.domain!=Domain.SOUND:
                    raise ContractError("backend", "native sound domain required")
                return SoundCraftBackend(self.store,self.workspace,self.binary)
            case Tool.AUTOCLIP | Tool.RESOLVE | Tool.PREMIERE | Tool.AFTER_EFFECTS | Tool.FFMPEG | Tool.FFPROBE:
                raise ContractError("backend", "this work domain has no qualified selected native adapter")
        assert_never(order.backend)



def for_order(store: ProjectPort, order: WorkOrder, workspace: Path) -> Backend:
    requirement = ToolRequirement(tool=order.backend,feature="selected-native-work")
    host = inspect_host((requirement,))
    decision = decide_tool(requirement,host)
    observed = decision.installation
    if decision.status!=EnvStatus.REUSABLE or observed is None or observed.cli_path is None:
        raise ContractError("environment", "inspect/reuse/actual installation question required: "+decision.reason)
    return BackendWorkspace(store,workspace,Path(observed.cli_path)).create(order)


def for_job(store: ProjectPort, job: PostJob) -> Backend:
    location = PlanLocation.model_validate_json(job.packet.payload)
    if not location.workspace.is_relative_to(store.path.parent):
        raise ContractError("path", "canonical native workspace is outside selected project; no implicit foreign-session ownership")
    if location.capability.tool!=job.packet.order.backend:
        raise ContractError("backend", "canonical native capability belongs to another tool")
    return BackendWorkspace(store,location.workspace.parent,Path(location.capability.binary_path)).create(job.packet.order)
