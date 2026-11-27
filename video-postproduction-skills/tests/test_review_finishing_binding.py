"""Actual new reverse picture/mix vs stale main assets. Same-content clean reuse remains covered by variant delivery."""
import json,subprocess
import pytest
from conftest import require
from finishing_support import build
from support import json_pin


@pytest.fixture(scope="module")
def assets(tmp_path_factory):
    root=tmp_path_factory.mktemp("review-finishing-binding")
    store,_,_,_=build(root,variants=True,reorder=True)
    state=store.read_recorded();main=state.timelines[0]
    proposal=require("timeline_models","EditProposal").model_validate_json(json.dumps({"branch":"reverse","cuts":[
        {"id":s.id,"source":s.source.model_dump(),"source_range":s.source_range.model_dump()} for s in reversed(main.segments)]}))
    reverse=require("timeline","build_timeline")(state.intake,proposal,main)
    with store.transaction(state.revision) as tx:
        tx.state=tx.state.model_copy(update={"timelines":(*state.timelines,reverse)})
    def render(id,domain,tool,recipe=None,deps=()):
        state=store.read_recorded()
        order=require("work_models","WorkOrder").model_validate_json(json.dumps({"id":id,"domain":domain,"branch":"reverse","backend":tool,
            "source_refs":[s.source.model_dump() for s in state.intake.sources],
            "recipe":None if recipe is None else recipe.model_dump(),"dependencies":[p.model_dump() for p in deps],"output":"artifacts/"+id}))
        cls=require("backends.filmcraft","FilmCraftBackend") if tool=="filmcraft" else require("backends.soundcraft","SoundCraftBackend")
        adapter=cls(store,root/(id+"-native"))
        packet=adapter.prepare(order,adapter.inspect(),state.intake.authority)
        job=store.record_reservation(packet,store.read_recorded().revision)
        assert adapter.execute(packet).phase=="succeeded"
        return store.record_materialization(job.id,store.read_recorded().revision)
    picture=render("REVERSE-PICTURE","picture","filmcraft")
    state=store.read_recorded();oldmix=next(a for a in state.artifacts if a.id.startswith("SOUND-"))
    producer=next(j for j in state.jobs if j.id==oldmix.job_id)
    sound=require("backends.sound_models","SoundPlan").model_validate_json(producer.packet.payload)
    raw=json.loads(sound.recipe.model_dump_json());raw["picture"]=picture.pin.model_dump()
    recipe=require("admission","local_pin")(json_pin(root,"reverse-sound.json",raw))
    deps=(picture.pin,*(p for s in state.intake.request.stems for p in (s.asset,s.independence_evidence)))
    mix=render("REVERSE-SOUND","sound","soundcraft",recipe,deps)
    state=store.read_recorded()
    return store,picture,mix,next(a for a in state.artifacts if a.id.startswith("PICTURE-")),oldmix,next(a for a in state.artifacts if a.id.startswith("TEXT-"))


def recipe(picture,mix,plates=()):
    return require("finishing_models","FinishingRecipe")(format="post-finishing/1",id="REVERSE-FINISH",branch="reverse",
        picture=picture.id,mix=mix.id,plates=tuple(p.id for p in plates))


@pytest.mark.parametrize("mismatch",["picture","mix-lock","caption-map"])
def test_finishing_when_reused_current_assets_do_not_match_destination_edit_map_rejects(assets,mismatch):
    store,picture,mix,oldpicture,oldmix,text=assets
    request=recipe(oldpicture,oldmix) if mismatch=="picture" else recipe(picture,oldmix) if mismatch=="mix-lock" else recipe(picture,mix,(text,))
    with pytest.raises(require("errors","ContractError")):
        require("finishing","compile_finishing")(store.read_recorded(),request,store.path.parent)


def test_finishing_when_reverse_picture_and_its_own_mix_are_bound_renders_blue_first(assets):
    store,picture,mix,oldpicture,oldmix,text=assets
    root=store.path.parent
    rp=require("admission","local_pin")(json_pin(root,"bound-finishing.json",recipe(picture,mix).model_dump(mode="json")))
    order=require("finishing","prepare_finishing")(store.read_recorded(),rp,root)
    adapter=require("backends.finishing","FinishingBackend")(store,root/"bound-finishing-native")
    packet=adapter.prepare(order,adapter.inspect(),store.read_recorded().intake.authority)
    job=store.record_reservation(packet,store.read_recorded().revision)
    assert adapter.execute(packet).phase=="succeeded"
    value=adapter.observe(store.read_recorded().jobs[-1])
    data=subprocess.run(["ffmpeg","-v","error","-i",str(root/value.artifact.path),"-vf","select=eq(n\\,12)","-frames:v","1","-f","rawvideo","-pix_fmt","rgb24","-"],
        capture_output=True,check=True,timeout=30).stdout
    pixel=(45*160+80)*3
    assert data[pixel+2]>200 and data[pixel]<30


def test_quality_when_legacy_wrong_branch_output_is_materialized_cannot_reuse_old_proof(assets,monkeypatch):
    from quality_support import submission
    store,picture,mix,oldpicture,oldmix,text=assets;root=store.path.parent
    request=recipe(oldpicture,oldmix).model_copy(update={"id":"LEGACY-REVERSED"})
    rp=require("admission","local_pin")(json_pin(root,"legacy-finishing.json",request.model_dump(mode="json")))
    # Capture the real earlier bug's native result; bypass ONLY its missing historical compile guard.
    with monkeypatch.context() as patch:
        patch.setattr("postproduction.finishing.verify_picture_binding",lambda *args:None)
        order=require("finishing","prepare_finishing")(store.read_recorded(),rp,root)
        backend=require("backends.finishing","FinishingBackend")(store,root/"legacy-native")
        packet=backend.prepare(order,backend.inspect(),store.read_recorded().intake.authority)
        job=store.record_reservation(packet,store.read_recorded().revision)
        assert backend.execute(packet).phase=="succeeded"
        artifact=store.record_materialization(job.id,store.read_recorded().revision)
    # Current real validation must revoke the historical technical proof without deleting facts/bytes.
    result=require("quality","evaluate_submission")(store.read_recorded(),submission(store,artifact,id="LEGACY-QA"),store.path)
    assert next(g for g in result.gates if g.id=="PG5").status=="fail" and result.scope_passed is False
