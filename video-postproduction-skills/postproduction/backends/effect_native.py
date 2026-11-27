"""EffectCraft-specific native arrays/property CLI and observed comp/layer IDs."""
from typing import Final, assert_never

from pydantic import JsonValue, TypeAdapter

from postproduction.backends.effect_models import CompInfo, EffectPlan, EffectRun, MotionRecipe, PositionInfo
from postproduction.backends.text_models import TextRecipe
from postproduction.backends.process import IsolatedProcess, SandboxScope
from postproduction.errors import ContractError

REQUIRED: Final = ("comp.new","layer.newSolid","layer.newText","text.fonts","layer.setTransform","comp.info")


def runner(plan: EffectPlan) -> IsolatedProcess:
    return IsolatedProcess(SandboxScope(plan.workspace,plan.owner,memory_bytes=8589934592))


def build_steps(plan: EffectPlan) -> list[dict[str,JsonValue]]:
    """Only reviewed native commands; never JSX from a downloaded/user template."""
    recipe = plan.recipe
    steps: list[dict[str,JsonValue]] = [{"command":"comp.new","params":{"name":"PostMotion","width":recipe.width,"height":recipe.height,
        "frameRate":recipe.fps.num/recipe.fps.den,"duration":recipe.frame_count*recipe.fps.den/recipe.fps.num}}]
    match recipe:
        case MotionRecipe():
            steps.append({"command":"layer.newSolid","params":{"name":"PostBox","color":recipe.color,
                "width":recipe.box_width,"height":recipe.box_height}})
        case TextRecipe():
            settings = plan.text_settings
            if settings is None:
                raise ContractError("text", "exact native text settings were not admitted")
            steps.extend([{"command":"text.fonts","params":{"query":settings.family}},
                {"command":"layer.newText","params":{"text":recipe.caption.text,"font":settings.family,"style":settings.style,
                "size":settings.size,"fill":settings.color,"position":list(recipe.start_position),"edit":False,
                "justify":"center","applyFill":True,"applyStroke":False}}])
        case _:
            assert_never(recipe)
    steps.append({"command":"comp.info","params":{}})
    return steps


def resources(data: bytes) -> CompInfo:
    """Parse actual native return data rather than guessing comp1/layer4 or using #1."""
    result = EffectRun.model_validate_json(data)
    info = next((s.result for s in result.result if s.command == "comp.info"),None)
    if info is None:
        raise ContractError("readback", "native composition resource report missing")
    comp = CompInfo.model_validate_json(TypeAdapter(JsonValue).dump_json(info))
    if len(comp.layers) != 1:
        raise ContractError("readback", "unexpected native composition layer inventory")
    return comp


def check_properties(plan: EffectPlan, comp_id: int, layer_id: int) -> None:
    """Re-observe actual keyframe times/endpoints and evaluated midpoint before using a plate."""
    recipe = plan.recipe
    seconds = recipe.frame_count*recipe.fps.den/recipe.fps.num
    result = runner(plan).run((plan.capability.binary_path,"--project",str(plan.workspace/"native.ecproj"),
        "get",str(comp_id),str(layer_id),"transform/position","--time",str(seconds/2),"--json"))
    if result.returncode or result.timed_out:
        raise ContractError("readback", "native composition/layer/property inspection failed")
    position = PositionInfo.model_validate_json(result.stdout)
    expected = tuple((a+b)/2 for a,b in zip(recipe.start_position,recipe.end_position))
    if (position.layer != layer_id or not position.animated or len(position.keys) != 2
        or abs(position.keys[0].time) > 1e-9 or abs(position.keys[1].time-seconds) > 1e-9
        or position.keys[0].value != (*recipe.start_position,0)
        or position.keys[1].value != (*recipe.end_position,0)
        or any(abs(a-b)>1e-7 for a,b in zip(position.value,(*expected,0)))):
        raise ContractError("readback", "native position/property keyframe map differs")
