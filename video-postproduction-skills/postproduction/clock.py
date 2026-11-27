"""Exact integer clock conversion; nearest ties are rounded toward +infinity."""
from enum import StrEnum
from fractions import Fraction
from math import ceil, floor
from typing import assert_never

from postproduction.common import ClockRate
from postproduction.errors import ContractError


class Rounding(StrEnum):
    EXACT = "exact"
    FLOOR = "floor"
    CEIL = "ceil"
    NEAREST = "nearest"


def map_frame(frame: int, source: ClockRate, target: ClockRate, *, rounding: str) -> int:
    """Convert a signed frame/sample offset without float drift or implicit rounding."""
    try:
        policy = Rounding(rounding)
    except ValueError as exc:
        raise ContractError("rounding", "unknown rounding policy") from exc
    value = Fraction(frame*source.den*target.num, source.num*target.den)
    match policy:
        case Rounding.EXACT:
            if value.denominator != 1:
                raise ContractError("rounding", "exact conversion would discard a fractional unit")
            return value.numerator
        case Rounding.FLOOR:
            return floor(value)
        case Rounding.CEIL:
            return ceil(value)
        case Rounding.NEAREST:
            return floor(value+Fraction(1,2))
    assert_never(policy)
