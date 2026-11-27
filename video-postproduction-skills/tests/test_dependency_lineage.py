"""A consumed current artifact consumes its actual producer lineage, not just unchanged rendered bytes."""
import json
import pytest
from conftest import require
from test_filmcraft import rendered


@pytest.mark.parametrize("consumed,blocked",[(True,True),(False,False)])
def test_lineage_when_actual_picture_producer_loses_source_affects_only_consumers(tmp_path,consumed,blocked):
    store,backend,packet,value=rendered(tmp_path)
    state=store.read_recorded();artifact=store.record_materialization(state.jobs[0].id,state.revision)
    state=store.read_recorded()
    raw={"id":"INDEPENDENT-CONTEXT","domain":"motion","branch":"main","backend":"effectcraft",
        "source_refs":[state.intake.sources[0].source.model_dump()],"dependencies":[artifact.pin.model_dump()] if consumed else [],"output":"plates/future.json"}
    order=require("work_models","WorkOrder").model_validate_json(json.dumps(raw))
    document=json.loads(store.path.read_text());document["production"]["selections"][2]["valid"]=False
    store.path.write_text(json.dumps(document))
    if blocked:
        with pytest.raises(require("errors","ContractError")):
            require("revisions","verify_work_inputs")(state,order,store.path)
    else:
        require("revisions","verify_work_inputs")(state,order,store.path)
