"""Current complete delivery is not the historical existence of a bundle with a now-invalid required variant."""
from conftest import require
from test_variant_delivery import branched
from test_delivery import contract


def test_progress_when_required_variant_invalidates_current_delivery_drops_but_history_remains(tmp_path_factory):
    store,main,variant=branched.__wrapped__(tmp_path_factory)
    c=contract(store,main,id='PROGRESS-REVIEW',variants=[variant.id],output='deliveries/progress-review')
    record=store.record_delivery(c,store.read_recorded().revision)
    before=require('progress','project_progress')(store.read_recorded(),store.path)
    assert next(b for b in before.branches if b.branch=='main').technical_fixture_deliveries==1
    store.record_invalidation((variant.pin,),store.read_recorded().revision)
    after=require('progress','project_progress')(store.read_recorded(),store.path)
    assert next(b for b in after.branches if b.branch=='main').technical_fixture_deliveries==0
    assert len(store.read_recorded().deliveries)==1
    assert (store.path.parent/record.bundle.path/'manifest.json').is_file()
