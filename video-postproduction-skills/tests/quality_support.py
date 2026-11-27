"""Reported-semantic contract fixtures over actual local native output; never real human certification."""
import json
from conftest import require
from support import json_pin
from finishing_support import build


def ready(root):
    require("quality_models","QualitySubmission")
    store,backend,packet,value=build(root)
    state=store.read_recorded();artifact=store.record_materialization(state.jobs[-1].id,state.revision)
    return store,artifact


def submission(store,artifact,id="QA-1",**changes):
    state=store.read_recorded()
    producer=next(j for j in state.jobs if j.id==artifact.job_id)
    timeline=next(t for t in state.timelines if t.branch==producer.packet.order.branch)
    evidence=json_pin(store.path.parent,id+"-evidence.json",{"scope":"contract_fixture reported checks only; no actual human watching/listening or legal issuer authentication"})
    checks=[]
    for name in ("picture","composite","color","sound","captions","video_playback","audio_listening","rights","adoption"):
        span={"start":0,"end":288000 if name=="audio_listening" else 144} if name in {"video_playback","audio_listening"} else None
        checks.append({"name":name,"status":"pass","origin":"fixture","artifact":artifact.pin.model_dump(),"evidence":evidence.model_dump(),"range":span,"reason":"explicit reported-semantic contract fixture, not actual human approval"})
    coverage=[]
    for event in timeline.event_map:
        cap=next(s for s in state.intake.sources if s.source==event.source)
        coverage.append({"requirement_id":event.requirement_id,"status":"pass","source":event.source.model_dump(),"source_hash":cap.asset.sha256,
            "source_range":event.source_anchor.model_dump(),"master_range":event.master_range.model_dump(),"video_observed":True,"audio_observed":False,
            "evidence":evidence.model_dump()})
    raw={"id":id,"mode":"technical_fixture","artifact_id":artifact.id,"artifact":artifact.pin.model_dump(),"receiver":"fixture-local-receiver",
        "input_fingerprint":artifact.input_fingerprint,"timeline_digest":require("timeline","timeline_digest")(timeline),"checks":checks,"coverage":coverage,"resolutions":[],**changes}
    return require("quality_models","QualitySubmission").model_validate_json(json.dumps(raw))
