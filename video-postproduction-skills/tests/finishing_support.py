"""Complete actual synthetic three-native-app technical fixture; no reported human/perceptual approval."""
import json
from conftest import require
from support import fixture,json_pin,modify_authority
from audio_support import stem
from test_templates import recipe as style_file


def build(root,conditional=False,loudness=None,variants=False,reorder=False,attribution=(),attribution_presentation=None):
    Backend=require("backends.finishing","FinishingBackend")
    request,production,handoff=fixture(root,conditional_clip="C1" if conditional else None,loudness=loudness)
    stems=[stem(root,"toneA"),stem(root,"toneB",frequency=880)]
    _,rawstyle=style_file(root,width=160,height=90,font_size=14,safe_bounds={"left":5,"top":5,"right":155,"bottom":85},
        attribution=list(attribution),**({"attribution_presentation":attribution_presentation} if attribution_presentation else {}))
    style=json_pin(root,"style.json",rawstyle)
    record={"format":"post-caption-source/1","id":"HELLO","source":{"clip_id":"C1","take_id":production.selections[0].take.id},
        "source_range":{"start":24,"end":48},"text":"Hello","speaker":"Actor A","kind":"dialogue","words":[],"approval_kind":"reported"}
    approval=json_pin(root,"literal-text.json",record)
    extra=[style.model_dump(),approval.model_dump(),rawstyle["font"]["license_evidence"]]
    assets=[*extra,*(p for s in stems for p in (s["asset"],s["independence_evidence"]))]
    request.update(stems=stems,upstream=extra)
    modify_authority(root,request,allowed_changes=["composite","audio","captions",*(["branch"] if variants else []),*(["reorder"] if reorder else [])],assets=assets)
    (root/"request.json").write_text(json.dumps(request))
    path=root/"project.json";path.write_text(json.dumps({"production":production.model_dump(mode="json"),"foreign":{"owner":"preserve"}}))
    intake=require("intake","load_intake")(root,root/"request.json",path);timeline=require("timeline","build_timeline")(intake)
    store=require("ledger","PostStore")(path);store.initialize(require("state_models","PostState")(intake=intake,timelines=(timeline,)))
    refs=[s.source.model_dump() for s in intake.sources]
    def render(id,domain,backend,recipe=None,dependencies=None,source_refs=None):
        order=require("work_models","WorkOrder").model_validate_json(json.dumps({"id":id,"domain":domain,"branch":"main","backend":backend,
            "source_refs":source_refs or refs,"recipe":None if recipe is None else recipe.model_dump(),"dependencies":dependencies or [],"output":"artifacts/"+id}))
        cls={"filmcraft":require("backends.filmcraft","FilmCraftBackend"),"effectcraft":require("backends.effectcraft","EffectCraftBackend"),"soundcraft":require("backends.soundcraft","SoundCraftBackend")}[backend]
        adapter=cls(store,root/(id+"-native"));cap=adapter.inspect();packet=adapter.prepare(order,cap,store.read_recorded().intake.authority)
        job=store.record_reservation(packet,store.read_recorded().revision)
        assert adapter.execute(packet).phase=="succeeded"
        return store.record_materialization(job.id,store.read_recorded().revision)
    picture=render("PICTURE","picture","filmcraft")
    motion=json_pin(root,"motion.json",{"format":"post-motion/1","width":160,"height":90,"fps":{"num":24,"den":1},"frame_count":12,"start_frame":48,
        "box_width":40,"box_height":30,"color":"#ff0000","start_position":[40,45],"end_position":[120,45]})
    plate=render("MOTION","motion","effectcraft",motion,source_refs=[refs[1]])
    source=require("caption_models","SourceCaption").model_validate_json(json.dumps({**record,"approval":approval.model_dump()}))
    caption=require("captions","map_cues")((source,),timeline)[0]
    textrecipe=json_pin(root,"text.json",{"format":"post-text/1","width":160,"height":90,"fps":{"num":24,"den":1},"frame_count":24,"start_frame":24,
        "style":style.model_dump(),"caption":json.loads(caption.model_dump_json()),"start_position":[80,60],"end_position":[80,60]})
    text=render("TEXT","motion","effectcraft",textrecipe,dependencies=extra,source_refs=[refs[0]])
    if conditional:
        render("UNUSED","motion","effectcraft",textrecipe,dependencies=extra,source_refs=[refs[0]])
    audiorecipe=json_pin(root,"sound.json",{"format":"post-sound/1","sample_rate":48000,"channels":2,"sample_count":288000,"picture":picture.pin.model_dump(),
        "picture_fps":{"num":24,"den":1},"cues":[{"id":"A","stem_id":"toneA","at_sample":0,"gain_db":-6},{"id":"B","stem_id":"toneB","at_sample":24000,"gain_db":-12}]})
    sound=render("SOUND","sound","soundcraft",audiorecipe,dependencies=[picture.pin.model_dump(),*(p for s in stems for p in (s["asset"],s["independence_evidence"]))])
    recipe=json_pin(root,"finishing.json",{"format":"post-finishing/1","id":"FINISH","branch":"main","picture":picture.id,"plates":[plate.id,text.id],"mix":sound.id})
    order=require("finishing","prepare_finishing")(store.read_recorded(),require("admission","local_pin")(recipe),root)
    backend=Backend(store,root/"finishing-native");cap=backend.inspect()
    packet=backend.prepare(order,cap,store.read_recorded().intake.authority)
    job=store.record_reservation(packet,store.read_recorded().revision)
    assert backend.execute(packet).phase=="succeeded"
    value=backend.observe(store.read_recorded().jobs[-1])
    return store,backend,packet,value
