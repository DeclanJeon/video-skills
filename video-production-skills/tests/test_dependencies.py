"""Editing order does not force serial generation."""
import pytest
from production.models import ClipId, ContractError, Reference
from conftest import require


def linked(seed):
    ref = Reference(source_clip=ClipId("C1"), role="state", modality="video", imports=("identity", "pose"))
    third = seed.batch.clips[2].model_copy(update={"references": (ref,)})
    return seed.model_copy(update={"batch": seed.batch.model_copy(update={"clips": (*seed.batch.clips[:2], third)})})


def test_independent_ready_when_predecessor_not_accepted(seed):
    # Given: C3 needs C1 but C2 is independent.
    state = linked(seed)
    # When: computing the ready set.
    ready = require("contracts", "ready_clips")(state)
    # Then: C3 is blocked, while both independent clips are available.
    assert ready == ("C1", "C2")


def test_cycle_when_clips_require_each_other(seed):
    # Given: C1 and C3 depend on each other.
    state = linked(seed)
    first = state.batch.clips[0].model_copy(update={"references": (Reference(source_clip=ClipId("C3"), role="state", modality="video", imports=("pose",)),)})
    batch = state.batch.model_copy(update={"clips": (first, *state.batch.clips[1:])})
    # When / Then: no submission may start on a cyclic graph.
    with pytest.raises(ContractError, match="cycle"):
        require("contracts", "validate_batch")(batch)


def test_dangling_reference_when_source_not_in_batch(seed):
    # Given: a nonexistent history source is named.
    state = linked(seed)
    third = state.batch.clips[2].model_copy(update={"references": (Reference(source_clip=ClipId("MISSING"), role="state", modality="video", imports=("pose",)),)})
    batch = state.batch.model_copy(update={"clips": (*state.batch.clips[:2], third)})
    # When / Then: dangling references are not treated as independent.
    with pytest.raises(ContractError, match="reference"):
        require("contracts", "validate_batch")(batch)


def test_optional_missing_when_omission_not_justified(seed):
    # Given: an optional reference has no omitted-use rationale.
    ref = Reference(source_clip=ClipId("C1"), role="state", modality="video", imports=("pose",), required=False)
    third = seed.batch.clips[2].model_copy(update={"references": (ref,)})
    state = seed.model_copy(update={"batch": seed.batch.model_copy(update={"clips": (*seed.batch.clips[:2], third)})})
    # When: checking readiness.
    ready = require("contracts", "ready_clips")(state)
    # Then: optional does not mean silent omission.
    assert "C3" not in ready
