"""Actual selected source pins/approval with controlled typed binding contracts; optional does not mean ignored when consumed."""
import pytest
from production.models import Binding,Reference,Verdict
from conftest import require
from test_ledger import built,project,prepare


@pytest.mark.parametrize("bound,current,conditional_conflict,blocked",[
    (True,True,False,False),(True,False,False,True),(False,False,False,False),
    (True,True,True,True),(False,True,True,False),
])
def test_optional_when_consumed_requires_current_and_usable_but_justified_unconsumed_is_exempt(project,bound,current,conditional_conflict,blocked):
    path,store,post,production=prepare(project);state=post.intake.snapshot
    target=state.selections[1]
    review=target.review
    if conditional_conflict:
        review=review.model_copy(update={"verdict":Verdict.CONDITIONAL,"defects":("lighting",),"post_fix":"repair lighting",
            "post_receiver":"fixture-post","conditional_policy":"lighting imports blocked until repaired"})
    target=target.model_copy(update={"valid":current,"review":review})
    selected=state.selections[0]
    reference=Reference(source_clip=target.take.clip_id,role="continuity",modality="video",imports=("lighting",),required=False,omission_evidence="explicitly unconsumed optional reference")
    clip=state.batch.clips[0].model_copy(update={"references":(reference,)})
    state=state.model_copy(update={"batch":state.batch.model_copy(update={"clips":(clip,*state.batch.clips[1:])}),"selections":(selected,target,*state.selections[2:])})
    binding=Binding(pin=target.take.asset,source_clip=target.take.clip_id,source_range=target.take.source_range,
        range_revision=target.take.range_revision,acceptance_revision=target.acceptance_revision,role="continuity",modality="video",
        imports=("lighting",),native_asset_id="contract-resource",native_reference_id="contract-binding",ready=True)
    if blocked:
        with pytest.raises(require("errors","ContractError")):
            require("admission","dependencies")(state,selected,(binding,) if bound else (),path.parent)
    else:
        require("admission","dependencies")(state,selected,(binding,) if bound else (),path.parent)
