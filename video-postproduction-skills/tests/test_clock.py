"""Independent rational expectations catch drift and unannounced rounding."""
import pytest
from conftest import require


@pytest.mark.parametrize("frame,source,target,want",[
    (24000,(24000,1001),(48000,1),48048000),
    (30000,(30000,1001),(48000,1),48048000),
    (48,(24,1),(254016000000,1),508032000000),
    (-24,(24,1),(48000,1),-48000),
])
def test_clock_when_exact_common_film_and_audio_rates(frame,source,target,want):
    Rate=require("models","ClockRate")
    assert require("clock","map_frame")(frame,Rate(num=source[0],den=source[1]),Rate(num=target[0],den=target[1]),rounding="exact") == want


@pytest.mark.parametrize("policy,want",[("floor",0),("ceil",1),("nearest",1)])
def test_clock_when_fractional_result_requires_declared_rounding(policy,want):
    Rate=require("models","ClockRate")
    assert require("clock","map_frame")(1,Rate(num=24,den=1),Rate(num=12,den=1),rounding=policy) == want


def test_clock_when_exact_policy_would_lose_half_a_frame():
    Rate=require("models","ClockRate")
    with pytest.raises(require("errors","ContractError"),match="rounding"):
        require("clock","map_frame")(1,Rate(num=24,den=1),Rate(num=12,den=1),rounding="exact")


def test_clock_when_unknown_rounding_policy_is_supplied():
    Rate=require("models","ClockRate")
    with pytest.raises(require("errors","ContractError"),match="rounding"):
        require("clock","map_frame")(1,Rate(num=24,den=1),Rate(num=12,den=1),rounding="guess")
