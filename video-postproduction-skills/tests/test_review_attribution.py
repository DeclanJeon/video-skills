"""Supplied credit data must survive actual main/variant output delivery, not be replaced by an issuer-authenticity claim."""
import json
import pytest
import finishing_support
from conftest import require
from test_delivery import contract
from test_variant_delivery import branched
from quality_support import submission

CREDIT="REVIEW_REQUIRED_CREDIT_8291"


@pytest.fixture(scope="module")
def credited(tmp_path_factory):
    original=finishing_support.style_file
    def with_credit(root,**changes):
        changes["attribution"]=[CREDIT]
        return original(root,**changes)
    finishing_support.style_file=with_credit
    try:return branched.__wrapped__(tmp_path_factory)
    finally:finishing_support.style_file=original


@pytest.mark.parametrize("location",["main","variant"])
def test_delivery_when_supplied_consumed_credit_is_preserved_for_main_or_variant(credited,location):
    store,main,clean=credited
    artifact=main if location=="main" else clean
    variants=[] if location=="main" else [main.id]
    c=contract(store,artifact,id="CREDIT-"+location,variants=variants,output="deliveries/credits-"+location)
    bundle=require("delivery","build_delivery")(store.read_recorded(),c,store.path)
    root=store.path.parent/bundle.path
    assert any(CREDIT in p.read_text() for p in root.rglob("*.json"))


def test_delivery_when_on_screen_credit_is_explicit_cannot_be_satisfied_by_a_metadata_record(tmp_path):
    store,_,_,_=finishing_support.build(tmp_path,attribution=(CREDIT,),attribution_presentation="on_screen")
    state=store.read_recorded();artifact=store.record_materialization(state.jobs[-1].id,state.revision)
    report=store.record_review(submission(store,artifact,id="ONSCREEN-QA"),store.read_recorded().revision)
    assert report.scope_passed is False and next(g for g in report.gates if g.id=="PG6").status!="pass"
    c=contract(store,artifact,output="deliveries/not-burned-credit")
    with pytest.raises(require("errors","ContractError")) as raised:
        require("delivery","build_delivery")(store.read_recorded(),c,store.path)
    assert raised.value.stage=="delivery" and not (store.path.parent/c.output).exists()
