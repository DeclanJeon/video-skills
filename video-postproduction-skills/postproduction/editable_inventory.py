"""Gather only actual known native source paths; unknown/shared/private dependencies cannot be silently bundled."""
from pathlib import Path

from pydantic import JsonValue, TypeAdapter

from postproduction.artifact_graph import artifact_union
from postproduction.backends.base import JobObservation
from postproduction.common import Pin
from postproduction.delivery_models import DeliveryContract
from postproduction.editable_models import EditableInventory, NativeProjection
from postproduction.errors import ContractError
from postproduction.files import read_model, verified_file
from postproduction.quality import PlanCapability
from postproduction.relink import referenced_paths
from postproduction.state_models import PostState


def editable_inventory(state: PostState, contract: DeliveryContract, root: Path) -> EditableInventory:
    closure = artifact_union(state,(contract.artifact_id,*contract.variants))
    known: list[Pin] = [s.asset for s in state.intake.sources]
    known.extend(s.asset for s in state.intake.request.stems)
    projects: list[NativeProjection] = []
    for artifact in closure:
        known.extend((artifact.pin,*artifact.related))
        job = next(j for j in state.jobs if j.id==artifact.job_id)
        known.extend(job.packet.order.dependencies)
        if artifact.proof is None:
            raise ContractError("editable", "actual native technical proof missing")
        proof = read_model(root,artifact.proof,JobObservation)
        if proof.native_project is None:
            raise ContractError("editable", "required native project missing")
        source = proof.native_project
        cap = PlanCapability.model_validate_json(job.packet.payload).capability
        projects.append(NativeProjection(source=source,destination=f"native/{source.sha256[:16]}{Path(source.path).suffix}",
                                         capability=cap,frame_count=proof.frame_count))
    media: list[Pin] = []
    for native in projects:
        file = verified_file(root,native.source)
        value = TypeAdapter(JsonValue).validate_json(file.read_bytes())
        for text in referenced_paths(value):
            path = Path(text)
            absolute = path.absolute() if path.is_absolute() else (file.parent/path).absolute()
            if absolute==file:
                continue
            pin = next((p for p in known if (root/p.path).absolute()==absolute),None)
            if pin is None:
                raise ContractError("editable", "native dependency not in exact known verified source inventory")
            if pin not in media:
                _ = verified_file(root,pin)
                media.append(pin)
    return EditableInventory(projects=tuple(projects),media=tuple(media))
