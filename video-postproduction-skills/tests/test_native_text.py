"""Actual native literal text/font/readback/RGBA safe-mask representative; no original template pixels or fallback."""
import json
import pytest
from conftest import require
from support import fixture,json_pin,modify_authority
from test_templates import recipe as style_file


def setup(root,tamper_text=False,caption_text="Hello",caption_speaker="Actor A",**style_changes):
    request,production,handoff=fixture(root)
    settings={"width":160,"height":90,"font_size":14,"safe_bounds":{"left":5,"top":5,"right":155,"bottom":85},**style_changes}
    path,raw=style_file(root,**settings)
    style=json_pin(root,"style.json",raw)
    source={"format":"post-caption-source/1","id":"TEXT-C1","source":{"clip_id":production.selections[0].take.clip_id,"take_id":production.selections[0].take.id},
        "source_range":{"start":0,"end":24},"text":caption_text,"speaker":caption_speaker,"kind":"dialogue","words":[],"approval_kind":"reported"}
    approval=json_pin(root,"caption-source.json",source)
    assets=[style.model_dump(),approval.model_dump(),raw["font"]["license_evidence"]]
    request["upstream"]=assets
    modify_authority(root,request,allowed_changes=["composite","captions"],assets=assets)
    (root/"request.json").write_text(json.dumps(request))
    ledger=root/"project.json";ledger.write_text(json.dumps({"production":production.model_dump(mode="json")}))
    intake=require("intake","load_intake")(root,root/"request.json",ledger)
    timeline=require("timeline","build_timeline")(intake)
    state=require("state_models","PostState")(intake=intake,timelines=(timeline,))
    store=require("ledger","PostStore")(ledger);store.initialize(state)
    cue=require("caption_models","SourceCaption").model_validate_json(json.dumps({**source,"approval":approval.model_dump()}))
    mapped=require("captions","map_cues")((cue,),timeline)[0]
    if tamper_text:mapped=mapped.model_copy(update={"text":"NOT THE APPROVED QUOTE"})
    recipe={"format":"post-text/1","width":160,"height":90,"fps":{"num":24,"den":1},"frame_count":24,
        "start_frame":0,"style":style.model_dump(),"caption":json.loads(mapped.model_dump_json()),
        "start_position":[80,60],"end_position":[80,60]}
    pin=json_pin(root,"native-text-recipe.json",recipe)
    order=require("work_models","WorkOrder").model_validate_json(json.dumps({"id":"NATIVE-TEXT","domain":"motion","branch":"main","backend":"effectcraft",
        "source_refs":[intake.sources[0].source.model_dump()],"recipe":pin.model_dump(),"dependencies":assets,"output":"plates/text.json"}))
    backend=require("backends.effectcraft","EffectCraftBackend")(store,root/"native-text")
    return store,backend,order,backend.inspect()


def test_native_text_when_actual_font_and_quote_are_read_back_and_every_rgba_frame_is_safe(tmp_path):
    store,backend,order,cap=setup(tmp_path)
    packet=backend.prepare(order,cap,store.read_recorded().intake.authority)
    job=store.record_reservation(packet,0)
    result=backend.execute(packet);assert result.phase=="succeeded"
    value=backend.observe(store.read_recorded().jobs[0])
    assert value.frame_count==24 and len(value.frames)==24
    manifest=require("backends.effect_models","PlateManifest").model_validate_json((tmp_path/value.artifact.path).read_bytes())
    assert manifest.font_family=="DejaVu Sans" and manifest.source_text=="Hello"
    assert all(5<=b.left<b.right<=155 and 5<=b.top<b.bottom<=85 for b in manifest.bounds)


@pytest.mark.parametrize("literal",["안녕","한국어 자막은\n그대로 보여요"])
def test_native_text_when_actual_existing_korean_font_and_multiline_speaker_source_are_preserved(tmp_path,literal):
    from pathlib import Path
    import hashlib
    font=Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
    rights=json_pin(tmp_path,"korean-font-rights.json",{"scope":"reported existing-font technical fixture, no redistribution"})
    spec={"path":str(font),"sha256":hashlib.sha256(font.read_bytes()).hexdigest(),"family":"Noto Sans CJK KR","style":"Regular",
        "version":131334,"face_index":1,"license_evidence":rights.model_dump()}
    store,backend,order,cap=setup(tmp_path,caption_text=literal,caption_speaker="배우 가",font=spec)
    packet=backend.prepare(order,cap,store.read_recorded().intake.authority);store.record_reservation(packet,0)
    assert backend.execute(packet).phase=="succeeded"
    observed=backend.observe(store.read_recorded().jobs[0])
    manifest=require("backends.effect_models","PlateManifest").model_validate_json((tmp_path/observed.artifact.path).read_bytes())
    assert manifest.font_family=="Noto Sans CJK KR" and manifest.source_text==literal


def test_native_text_when_master_caption_text_was_changed_without_new_approved_source_rejects(tmp_path):
    store,backend,order,cap=setup(tmp_path,tamper_text=True)
    with pytest.raises(require("errors","ContractError"),match="caption"):
        backend.prepare(order,cap,store.read_recorded().intake.authority)


def test_native_text_when_actual_advance_is_wider_than_safe_mask_rejects_before_render(tmp_path):
    store,backend,order,cap=setup(tmp_path,safe_bounds={"left":75,"top":5,"right":85,"bottom":85})
    with pytest.raises(require("errors","ContractError"),match="bounds"):
        backend.prepare(order,cap,store.read_recorded().intake.authority)
