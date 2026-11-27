"""Explicit pinned finishing requests, not guessing a template/mix from a delivery profile alone."""
from pathlib import Path

from postproduction.backends.effect_models import EffectPlan, PlateManifest
from postproduction.clock import map_frame
from postproduction.common import Pin
from postproduction.environment.models import Tool
from postproduction.errors import ContractError
from postproduction.files import read_model
from postproduction.finishing_models import FinishingInputs, FinishingRecipe, PlatePlacement
from postproduction.finishing_binding import verify_picture_binding, verify_mix_binding, verify_plate_binding
from postproduction.job_models import ArtifactRef
from postproduction.state_models import PostState
from postproduction.timeline_map import FILM_CLOCK
from postproduction.work_models import Domain, WorkOrder


def artifact_for(state: PostState, id: str) -> ArtifactRef:
    actual = next((a for a in state.artifacts if a.id==id),None)
    if actual is None or actual.proof is None:
        raise ContractError("artifact", "required actual materialized finishing input/proof missing")
    return actual


def prepare_finishing(state: PostState, recipe_pin: Pin, root: Path) -> WorkOrder:
    """Declare exact consumed actual artifact pins; native backend still re-admits their entire producer lineage."""
    recipe = read_model(root,recipe_pin,FinishingRecipe)
    inputs = (artifact_for(state,recipe.picture),*(artifact_for(state,id) for id in recipe.plates),artifact_for(state,recipe.mix))
    if len({a.id for a in inputs}) != len(inputs):
        raise ContractError("finishing", "duplicate finishing artifact role is ambiguous")
    return WorkOrder(id=recipe.id,domain=Domain.FINISHING,branch=recipe.branch,backend=Tool.FILMCRAFT,
        source_refs=tuple(s.source for s in state.intake.sources),dependencies=tuple(a.pin for a in inputs),
        recipe=recipe_pin,output=f"renders/{recipe.id}.mp4")


def compile_finishing(state: PostState, recipe: FinishingRecipe, root: Path) -> FinishingInputs:
    picture,mix = artifact_for(state,recipe.picture),artifact_for(state,recipe.mix)
    if picture.kind!="video" or mix.kind!="audio":
        raise ContractError("finishing", "actual native picture plus real decoded native mix required")
    timeline = next((t for t in state.timelines if t.branch==recipe.branch),None)
    if timeline is None:
        raise ContractError("branch", "actual finishing timeline missing")
    verify_picture_binding(state,picture,timeline)
    total = map_frame(timeline.segments[-1].timeline_range.end,FILM_CLOCK,state.intake.profile.fps,rounding="exact")
    verify_mix_binding(state,mix,picture,total)
    plates: list[PlatePlacement] = []
    for id in recipe.plates:
        artifact = artifact_for(state,id)
        producer = next((j for j in state.jobs if j.id==artifact.job_id),None)
        if artifact.kind!="rgba_sequence" or producer is None or producer.packet.order.backend!=Tool.EFFECTCRAFT:
            raise ContractError("plate", "only actual verified native RGBA sequence supported")
        verify_plate_binding(state,producer,timeline)
        plan = EffectPlan.model_validate_json(producer.packet.payload)
        manifest = read_model(root,artifact.pin,PlateManifest)
        if ((manifest.width,manifest.height,manifest.fps) != (
            state.intake.profile.width,state.intake.profile.height,state.intake.profile.fps)
            or plan.recipe.start_frame+manifest.frame_count>total):
            raise ContractError("plate", "actual plate dimensions/rate/range differ from finishing picture")
        plates.append(PlatePlacement(artifact=artifact,manifest=manifest,start_frame=plan.recipe.start_frame))
    return FinishingInputs(picture=picture,mix=mix,plates=tuple(plates),profile=state.intake.profile,total_frames=total)
