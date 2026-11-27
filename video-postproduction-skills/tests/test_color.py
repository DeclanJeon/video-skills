"""Stream metadata is not pixel/gamut detection or automatic user approval of a color assignment."""
import json
import pytest
from conftest import require
from test_ledger import built,project,prepare
from support import json_pin


def test_color_when_actual_source_has_unknown_tags_does_not_invent_rec709(project):
    path,store,state,production=prepare(project)
    actual=require("color","probe_color")(path.parent,state.intake.sources[0].asset)
    assert actual.primaries is None and actual.transfer is None
    assert actual.pixel_format=="yuv420p" and actual.bit_depth==8


def test_color_when_explicit_assignment_retains_unknown_detection_and_actual_evidence(project):
    path,store,state,production=prepare(project)
    source=state.intake.sources[0].asset
    evidence=json_pin(path.parent,"color-assignment.json",{"scope":"reported fixture source assignment, not measured gamut"})
    assignment=require("color_models","ColorAssignment")(source=source,space="Rec709",evidence=require("admission","local_pin")(evidence),origin="assigned")
    value=require("color","resolve_color")(path.parent,source,assignment)
    assert value.detected.primaries is None
    assert value.assignment.space=="Rec709"
    assert value.assignment.origin=="assigned"


def test_color_when_assignment_is_bound_to_another_source_rejects(project):
    path,store,state,production=prepare(project)
    evidence=json_pin(path.parent,"color-assignment.json",{"scope":"fixture"})
    assignment=require("color_models","ColorAssignment")(source=state.intake.sources[1].asset,space="Rec709",evidence=require("admission","local_pin")(evidence),origin="assigned")
    with pytest.raises(require("errors","ContractError")):
        require("color","resolve_color")(path.parent,state.intake.sources[0].asset,assignment)


def test_color_when_unknown_output_tags_cannot_claim_detected_target(project):
    path,store,state,production=prepare(project)
    target=require("color_models","ColorTarget")(primaries="bt709",transfer="bt709",matrix="bt709",range="tv",bit_depth=8)
    with pytest.raises(require("errors","ContractError"),match="color"):
        require("color","verify_color_output")(path.parent,state.intake.sources[0].asset,target)
