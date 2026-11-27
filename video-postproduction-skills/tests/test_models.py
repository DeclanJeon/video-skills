"""Mutations permitting unsafe pins, fake boundaries or mutable records must fail."""
import pytest
from pydantic import ValidationError
from conftest import require


@pytest.mark.parametrize("path",["/etc/passwd","../outside.png","a/../../outside.png","C:\\private\\face.png","a\\file.png","", "."])
def test_pin_when_path_is_not_project_relative(path):
    Pin=require("models","Pin")
    Error=require("errors","ContractError")
    with pytest.raises((ValidationError,Error)):
        Pin(id="source",version="v1",path=path,sha256="a"*64)


@pytest.mark.parametrize("digest",["bad","f"*63,"G"*64])
def test_pin_when_digest_cannot_identify_bytes(digest):
    with pytest.raises(ValidationError):
        require("models","Pin")(id="s",version="v1",path="s.png",sha256=digest)


def test_boundary_when_unknown_fields_or_mutation_are_attempted():
    Pin=require("models","Pin")
    with pytest.raises(ValidationError):
        Pin(id="s",version="v1",path="s.png",sha256="a"*64,approved=True)
    value=Pin(id="s",version="v1",path="s.png",sha256="a"*64)
    with pytest.raises(ValidationError):
        value.path="replacement.png"
    assert value.path == "s.png"


@pytest.mark.parametrize("start,end",[(0,0),(2,1),(-1,2),(True,2),(0,1.5)])
def test_source_range_when_empty_reversed_negative_or_noninteger(start,end):
    Range=require("models","SourceRange")
    Error=require("errors","ContractError")
    with pytest.raises((ValidationError,Error)):
        Range(start=start,end=end)


@pytest.mark.parametrize("reported",[1,"yes","true"])
def test_observation_when_report_flag_is_not_a_boolean(reported):
    Pin=require("models","Pin")
    with pytest.raises(ValidationError):
        require("intake_models","EventAnchor")(
            requirement_id="R1",source=require("intake_models","SourceRef")(clip_id="C1",take_id="T1"),
            source_range=require("models","SourceRange")(start=0,end=1),asset_hash="a"*64,
            range_revision=1,acceptance_revision=1,observer="fixture",
            evidence=Pin(id="e",version="1",path="e.txt",sha256="b"*64),video_observed=reported)


def test_source_range_when_end_is_exclusive():
    value=require("models","SourceRange")(start=12,end=60)
    assert value.length == 48


@pytest.mark.parametrize("num,den",[(0,1),(24,0),(-24,1),(float("nan"),1),(float("inf"),1),(True,1)])
def test_rate_when_not_a_positive_finite_integer_fraction(num,den):
    with pytest.raises(ValidationError):
        require("models","ClockRate")(num=num,den=den)
