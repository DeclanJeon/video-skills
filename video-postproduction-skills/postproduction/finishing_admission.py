"""One finishing work/recipe/input contract for preparation, raw dispatch and current historical QA."""
from pathlib import Path

from postproduction.edit_models import Change
from postproduction.environment.models import Tool
from postproduction.errors import ContractError
from postproduction.files import read_model
from postproduction.finishing import compile_finishing
from postproduction.finishing_models import FinishingInputs, FinishingPlan, FinishingRecipe
from postproduction.profile_checks import require_native_export_profile
from postproduction.revisions import verify_work_inputs, work_fingerprint
from postproduction.state_models import PostState
from postproduction.work_models import Domain, RequestPacket, WorkOrder


def bound_finishing_inputs(state: PostState, order: WorkOrder, project: Path) -> tuple[FinishingRecipe,FinishingInputs]:
    """Work identity is independent of recipe labels; branch, actual pin and consumption are not."""
    verify_work_inputs(state,order,project)
    if (order.domain,order.backend)!=(Domain.FINISHING,Tool.FILMCRAFT):
        raise ContractError("binding","finishing requires the reserved native finishing domain/backend")
    if not {Change.COMPOSITE,Change.AUDIO}<=set(state.intake.authority.allowed_changes):
        raise ContractError("authority","explicit current composition and mix authority required")
    if order.recipe is None or {(s.clip_id,s.take_id) for s in order.source_refs}!={(s.source.clip_id,s.source.take_id) for s in state.intake.sources}:
        raise ContractError("coverage","finishing requires explicit recipe and full current source denominator")
    recipe = read_model(project.parent,order.recipe,FinishingRecipe)
    if recipe.branch!=order.branch:
        raise ContractError("binding","finishing recipe branch differs from reserved destination branch")
    inputs = compile_finishing(state,recipe,project.parent)
    required = (inputs.picture.pin,*(p.artifact.pin for p in inputs.plates),inputs.mix.pin)
    if any(p not in order.dependencies for p in required):
        raise ContractError("dependency","reserved dependencies must contain actual picture/plate/mix lineage")
    require_native_export_profile(inputs.profile)
    return recipe,inputs


def projection(inputs: FinishingInputs) -> FinishingInputs:
    """Adoption is registry workflow state, not a changed native input; all immutable fields still compare."""
    return inputs.model_copy(update={
        "picture":inputs.picture.model_copy(update={"adopted":False}),
        "mix":inputs.mix.model_copy(update={"adopted":False}),
        "plates":tuple(p.model_copy(update={"artifact":p.artifact.model_copy(update={"adopted":False})}) for p in inputs.plates)})


def verify_finishing_packet(state: PostState, packet: RequestPacket, project: Path) -> FinishingPlan:
    plan = FinishingPlan.model_validate_json(packet.payload)
    recipe,inputs = bound_finishing_inputs(state,packet.order,project)
    if (plan.capability.tool!=Tool.FILMCRAFT or plan.recipe_pin!=packet.order.recipe
        or plan.recipe!=recipe or projection(plan.inputs)!=projection(inputs)
        or packet.input_fingerprint!=work_fingerprint(state,packet.order)):
        raise ContractError("binding","finishing payload recipe pin/inputs/capability must bind exact reserved work")
    return plan
