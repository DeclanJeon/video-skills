"""Approved coverage is independent of a self-counted queue."""
import pytest
from production.models import ContractError, Requirement
from conftest import require


def test_complete_coverage_when_all_requirements_mapped(seed):
    # Given: three approved requirements and their clips.
    validate = require("contracts", "validate_batch")
    # When: checking the complete mapping.
    result = validate(seed.batch)
    # Then: no requirement is missing.
    assert result is None


def test_first_missing_shot_when_queue_omits_clip(seed):
    # Given: a batch silently missing its final required clip.
    batch = seed.batch.model_copy(update={"clips": seed.batch.clips[:-1], "edit_order": seed.batch.edit_order[:-1]})
    # When / Then: coverage cannot self-certify a reduced queue.
    with pytest.raises(ContractError, match="coverage"):
        require("contracts", "validate_batch")(batch)


def test_multi_shot_when_one_event_unmapped(seed):
    # Given: another event within the same shot.
    extra = Requirement(id="DIALOGUE", shot="SH1", panels=("P1",), modality="audio", locator="script#line2")
    batch = seed.batch.model_copy(update={"coverage": (*seed.batch.coverage, extra)})
    # When / Then: matching shot counts does not hide a missing event.
    with pytest.raises(ContractError, match="coverage"):
        require("contracts", "validate_batch")(batch)


def test_duplicate_ids_when_batch_is_ambiguous(seed):
    # Given: two clips use the same ID.
    batch = seed.batch.model_copy(update={"clips": (seed.batch.clips[0], *seed.batch.clips)})
    # When / Then: duplicate identities are rejected.
    with pytest.raises(ContractError, match="duplicate"):
        require("contracts", "validate_batch")(batch)


def test_wrong_shot_when_requirement_mapped_to_other_clip(seed):
    # Given: event R1 is assigned outside SH1.
    first = seed.batch.clips[0].model_copy(update={"shots": ("OTHER",)})
    batch = seed.batch.model_copy(update={"clips": (first, *seed.batch.clips[1:])})
    # When / Then: arbitrary requirement tags do not prove coverage.
    with pytest.raises(ContractError, match="coverage"):
        require("contracts", "validate_batch")(batch)
