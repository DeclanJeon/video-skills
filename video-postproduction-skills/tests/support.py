"""Real supplied-source and review fixture; synthetic reports are not perceptual certification."""
import hashlib
import json
import subprocess
from pathlib import Path

from production.approval import clip_configuration_hash
from production.contracts import fingerprint
from production.handoff import build_handoff, selection_hash
from production.models import (
    ApprovedConfig, Authority, Batch, Clip, ClipId, FlowReview, JoinPlan, JoinReview,
    Pin, Playback, Requirement, Review, ReviewRender, SourceRange, State, Take, Verdict,
)
from production.quality import accept_supplied
from production.render import RenderManifest,render_review,slices


def pin(root,name,data=None):
    p=root/name
    if data is not None:
        p.write_bytes(data if isinstance(data,bytes) else data.encode())
    return Pin(id=name,version="1",path=name,sha256=hashlib.sha256(p.read_bytes()).hexdigest())


def json_pin(root,name,value):
    return pin(root,name,json.dumps(value,sort_keys=True))


def audio_review_fixture(root,state):
    # Separate real review-only fixture route: the protected upstream stream-copy
    # concat has a reproduced AAC non-monotonic DTS failure on this host. Do not
    # alter it or claim it passed. Decode/trim/concatenate once and encode once.
    argv=["ffmpeg","-v","error","-xerror"]
    for cid in state.batch.edit_order:
        item=next(s for s in state.selections if s.take.clip_id==cid)
        argv += ["-i",str(root/item.take.asset.path)]
    filters=[]
    for i in range(3):
        filters += [f"[{i}:v]trim=end_frame=48,setpts=PTS-STARTPTS[v{i}]",f"[{i}:a]atrim=end_sample=96000,asetpts=PTS-STARTPTS[a{i}]"]
    filters += ["[v0][a0][v1][a1][v2][a2]concat=n=3:v=1:a=1[v][a]"]
    argv += ["-filter_complex",";".join(filters),"-map","[v]","-map","[a]","-c:v","libx264","-c:a","aac",str(root/"review-only.mp4")]
    subprocess.run(argv,check=True,capture_output=True,timeout=30)
    asset=pin(root,"review-only.mp4")
    manifest=RenderManifest(selection_hash=selection_hash(state),artifact=asset,sources=slices(state))
    return ReviewRender(artifact=asset,manifest=pin(root,"review-only.sources.json",manifest.model_dump_json()),selection_hash=selection_hash(state))


def fixture(root,order=(1,2,3),with_audio=False,conditional_clip=None,rates=(24,24,24),loudness=None):
    prompt=pin(root,"prompt.txt","Synthetic red/green/blue rooms; no person or private media.")
    requirements=tuple(Requirement(id=f"R{i}",shot=f"SH{i}",panels=(f"P{i}",),locator=f"script#{i}",modality="audio" if with_audio and i==2 else "video") for i in (1,2,3))
    clips=tuple(Clip(id=ClipId(f"C{i}"),shots=(f"SH{i}",),requirements=(f"R{i}",),duration_s=2,prompt=prompt,audio_required=with_audio) for i in (1,2,3))
    joins=tuple(JoinPlan(id=f"J{i}",before=ClipId(f"C{before}"),after=ClipId(f"C{after}"),relation="angle_change" if order==(1,2,3) else "reaction_first",reveal_order=(f"R{before}",f"R{after}"),locator="board#cuts") for i,(before,after) in enumerate(zip(order,order[1:]),1))
    batch=Batch(id="B1",scope_revision="scope-1",coverage=requirements,clips=clips,edit_order=tuple(ClipId(f"C{i}") for i in order),joins=joins)
    cov=json_pin(root,"coverage.json",{"format":"production-coverage/1","requirements":[r.model_dump() for r in requirements]})
    state=State(batch=batch,approved_coverage=requirements,coverage_source=cov)
    evidence=pin(root,"reuse-approval.txt","Synthetic fixture explicit local reuse of exact files/ranges, not generation authority.")
    for i,color in enumerate(("red","green","blue"),1):
        name=f"source{i}.mp4"
        args=["ffmpeg","-v","error","-f","lavfi","-i",f"color={color}:s=160x90:r={rates[i-1]}:d=2"]
        if with_audio:
            args+=["-f","lavfi","-i","sine=frequency=440:sample_rate=48000:duration=2","-c:a","aac"]
        subprocess.run([*args,"-c:v","libx264","-pix_fmt","yuv420p",str(root/name)],check=True,capture_output=True,timeout=30)
        asset=pin(root,name)
        sr=SourceRange(start=0,end=2*rates[i-1])
        clip=clips[i-1]
        grant=ApprovedConfig(clip_id=clip.id,scope_revision="scope-1",coverage_hash=cov.sha256,clip_hash=clip_configuration_hash(clip),duration_s=2,width=160,height=90,audio_requested=with_audio,reuse_source=asset,reuse_range=sr)
        auth=Authority(id=f"AP{i}",clips=(clip.id,),allowed_hashes=(asset.sha256,),configurations=(grant,),account="offline",model="supplied",transport="local",mode="reuse",reuse=True,evidence=evidence)
        take=Take(id=f"T{i}",clip_id=clip.id,attempt_id=None,origin="approved_reuse",asset=asset,frame_count=2*rates[i-1],fps=rates[i-1],cfr=True,width=160,height=90,has_audio=with_audio,decode_evidence="synthetic real ffmpeg source; accept_supplied independently probes",source_range=sr,fingerprint=fingerprint(state,clip.id))
        review=Review(verdict=Verdict.ACCEPTED,fulfilled=clip.requirements,playback=Playback(asset_hash=asset.sha256,source_range=sr,reviewer="synthetic-fixture",evidence="reported fixture semantics, not actual human certification",video_watched=True,audio_listened=with_audio))
        if conditional_clip==f"C{i}":
            review=review.model_copy(update={"verdict":Verdict.CONDITIONAL,"defects":("caption_missing",),"post_fix":"show approved literal caption","post_receiver":"fixture-post","conditional_policy":"verify current native text on final master and review side effects"})
        state=accept_supplied(state,take,review,auth,root)
    selected={s.take.clip_id:s for s in state.selections}
    reports=tuple(JoinReview(join_id=j.id,before_take=selected[j.before].take.id,after_take=selected[j.after].take.id,before_revision=selected[j.before].acceptance_revision,after_revision=selected[j.after].acceptance_revision,before_range_revision=1,after_range_revision=1,reveal_order=j.reveal_order,passed=True,evidence="synthetic reported boundary QA",continuous_playback=True) for j in joins)
    state=state.model_copy(update={"join_reviews":reports})
    rendered=audio_review_fixture(root,state) if with_audio else render_review(state,root,"review-only.mp4")
    flow=FlowReview(review_render=rendered,selection_hash=selection_hash(state),clip_order=batch.edit_order,passed=True,evidence="synthetic reported flow, not perceptual certification",continuous_playback=True,audio_listened=with_audio)
    handoff=build_handoff(state,flow,"fixture-post","fixture rights",root)
    snapshot=pin(root,"snapshot.json",state.model_dump_json())
    hp=pin(root,"handoff.json",handoff.model_dump_json())
    schema_path=Path(__file__).parents[2]/"video-production-skills/production/models.py"
    schema=pin(root,"upstream-schema.py.txt",schema_path.read_bytes())
    profile=json_pin(root,"profile.json",{"id":"master-160","width":160,"height":90,"fps":{"num":24,"den":1},"sample_rate":48000,"channels":2,"container":"mp4","video_codec":"h264","audio_codec":"aac",**({"loudness":loudness} if loudness is not None else {})})
    brief=json_pin(root,"brief.json",{"project_id":"synthetic-post","intent":"Preserve three approved events","required_assets":[],"required_stems":[]})
    post_evidence=pin(root,"edit-grant.txt","Synthetic fixture only. Exact handoff/scope/brief/profile bound local editing.")
    auth=json_pin(root,"edit-authority.json",{"id":"AP-POST","project_id":"synthetic-post","receiver":"fixture-post","handoff_digest":hp.sha256,"scope_revision":"scope-1","brief_digest":brief.sha256,"profile_digest":profile.sha256,"allowed_changes":[],"evidence":post_evidence.model_dump()})
    request={"project_id":"synthetic-post","snapshot":snapshot.model_dump(),"handoff":hp.model_dump(),"schema":schema.model_dump(),"brief":brief.model_dump(),"authority":auth.model_dump(),"profile":profile.model_dump(),"upstream":[],"anchors":[]}
    (root/"request.json").write_text(json.dumps(request))
    return request,state,handoff


def update_request(root,request,key,name,data):
    request[key]=json_pin(root,name,data).model_dump()
    (root/"request.json").write_text(json.dumps(request))


def modify_authority(root,request,**updates):
    current=json.loads((root/request["authority"]["path"]).read_text())
    update_request(root,request,"authority","edit-authority.json",{**current,**updates})
