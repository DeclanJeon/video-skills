"""Native EffectCraft RGBA composition path; semantic visibility/master adoption are separate gates."""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from uuid import uuid4

from pydantic import JsonValue, TypeAdapter

from postproduction.backends.base import CapabilitySnapshot, JobObservation, NativeMapping
from postproduction.backends.effect_models import CompositionRecipe, EffectEvidence, EffectHeader, EffectPlan
from postproduction.backends.effect_plate import verify_frames
from postproduction.backends.text_contract import TextContract
from postproduction.backends.effect_native import REQUIRED, build_steps, check_properties, resources, runner
from postproduction.backends.film_native import NativeStage, digest_file
from postproduction.backends.process import IsolatedProcess, ProcessResult, SandboxScope
from postproduction.clock import map_frame
from postproduction.common import Pin, SourceId, SourceRange
from postproduction.edit_models import Change, EditAuthority
from postproduction.environment.models import Tool, ToolRequirement
from postproduction.environment.probe import inspect_host
from postproduction.errors import ContractError
from postproduction.files import read_model, verified_file
from postproduction.job_models import JobPhase, JobReceipt, PostJob
from postproduction.store_port import ProjectPort
from postproduction.revisions import verify_work_inputs, work_fingerprint
from postproduction.timeline_map import FILM_CLOCK
from postproduction.work_models import RequestPacket, WorkOrder


@dataclass(frozen=True, slots=True)
class EffectCraftBackend:
    store: ProjectPort
    workspace: Path
    binary: Path = Path("/usr/bin/effectcraft-cli")

    def inspect(self) -> CapabilitySnapshot:
        self.workspace.mkdir(exist_ok=True,mode=0o700)
        owner = uuid4().hex
        isolated = IsolatedProcess(SandboxScope(self.workspace/f"inspect-{owner}",owner))
        ids: list[str] = []
        for command in REQUIRED:
            result = isolated.run((str(self.binary),"commands","--filter",command,"--json"))
            parsed = TypeAdapter(list[dict[str,JsonValue]]).validate_json(result.stdout)
            if result.returncode or not any(p.get("id") == command for p in parsed):
                raise ContractError("capability", "actual EffectCraft command/property metadata unavailable")
            ids.append(command)
        host = inspect_host((ToolRequirement(tool=Tool.EFFECTCRAFT,feature="composition"),))
        observed = host.programs[0]
        digest = digest_file(self.binary)
        if digest is None or observed.version is None:
            raise ContractError("binary", "actual EffectCraft binary/version not established")
        return CapabilitySnapshot(tool=Tool.EFFECTCRAFT,binary_path=str(self.binary),binary_sha256=digest,
                                  version=observed.version,command_ids=tuple(ids))

    def prepare(self, order: WorkOrder, capability: CapabilitySnapshot, authority: EditAuthority) -> RequestPacket:
        state = self.store.read_recorded()
        verify_work_inputs(state,order,self.store.path)
        if (capability.tool != Tool.EFFECTCRAFT or capability.binary_path != str(self.binary)
            or capability.binary_sha256 != digest_file(self.binary)):
            raise ContractError("binary", "actual composition binary changed")
        if authority != state.intake.authority or Change.COMPOSITE not in authority.allowed_changes:
            raise ContractError("authority", "current explicit composition authority required")
        if order.recipe is None:
            raise ContractError("recipe", "actual independent native recipe required; MOGRT compatibility not inferred")
        recipe = read_model(self.store.path.parent,order.recipe,CompositionRecipe).root
        profile = state.intake.profile
        if (recipe.width,recipe.height,recipe.fps) != (profile.width,profile.height,profile.fps):
            raise ContractError("format", "recipe geometry/timebase is not the approved branch format")
        timeline = next(t for t in state.timelines if t.branch == order.branch)
        total = map_frame(timeline.segments[-1].timeline_range.end,FILM_CLOCK,recipe.fps,rounding="exact")
        if recipe.start_frame+recipe.frame_count > total:
            raise ContractError("range", "plate extends beyond approved timeline")
        for pin in recipe.references:
            _ = verified_file(self.store.path.parent,pin)
        text_settings = TextContract(state,self.store.path.parent).settings(order,recipe)
        owner = uuid4().hex
        plan = EffectPlan(workspace=(self.workspace/f"run-{owner}").absolute(),owner=owner,capability=capability,
                          recipe=recipe,recipe_pin=order.recipe,text_settings=text_settings,
                          sources=tuple(s for s in state.intake.sources if s.source in order.source_refs))
        return RequestPacket(order=order,input_fingerprint=work_fingerprint(state,order),payload=plan.model_dump_json())

    def plan_for(self, packet: RequestPacket) -> EffectPlan:
        state = self.store.read_recorded()
        verify_work_inputs(state,packet.order,self.store.path)
        plan = EffectPlan.model_validate_json(packet.payload)
        if (packet.input_fingerprint != work_fingerprint(state,packet.order)
            or plan.capability.binary_sha256 != digest_file(self.binary)
            or plan.capability.binary_path != str(self.binary)
            or plan.recipe != read_model(self.store.path.parent,plan.recipe_pin,CompositionRecipe).root
            or plan.sources != tuple(s for s in state.intake.sources if s.source in packet.order.source_refs)
            or plan.capability.tool != Tool.EFFECTCRAFT
            or not plan.workspace.is_relative_to(self.workspace.absolute())):
            raise ContractError("revision", "current native composition packet/input/binary/recipe differs")
        for reference in plan.recipe.references:
            _ = verified_file(self.store.path.parent,reference)
        if plan.text_settings != TextContract(state,self.store.path.parent).settings(packet.order,plan.recipe):
            raise ContractError("caption", "actual current text/style settings differ from the reserved plan")
        return plan

    def pin(self, path: Path, name: str) -> Pin:
        digest = digest_file(path)
        if digest is None:
            raise ContractError("frame", "actual plate/native file missing")
        return Pin(id=SourceId(name),version="1",path=path.relative_to(self.store.path.parent).as_posix(),sha256=digest)

    def stage(self, job: PostJob, plan: EffectPlan, step: NativeStage) -> tuple[ProcessResult,JobReceipt]:
        result = runner(plan).run(step.argv,stdin=step.stdin,timeout=90)
        phase = JobPhase.UNKNOWN if result.timed_out else JobPhase.FAILED if result.returncode else (
            JobPhase.SUCCEEDED if step.number == 4 else JobPhase.RUNNING)
        evidence = EffectEvidence(stage=step.number,pid=result.pid,returncode=result.returncode,
                                  timed_out=result.timed_out,stdout_sha256=hashlib.sha256(result.stdout).hexdigest())
        receipt = JobReceipt(phase=phase,request_hash=job.request_hash,job_id=f"effectcraft-{plan.owner}",
                             evidence=evidence.model_dump_json())
        _ = self.store.record_observation(job.id,receipt,self.store.read_recorded().revision)
        _ = (plan.workspace/f"stage{step.number}.stdout").write_bytes(result.stdout)
        _ = (plan.workspace/f"stage{step.number}.stderr").write_bytes(result.stderr)
        frames = tuple(self.pin(p,p.name) for p in sorted(plan.workspace.glob("plate_*.png"))) if step.number == 4 else ()
        info = resources((plan.workspace/"stage1.stdout").read_bytes())
        evidence = evidence.model_copy(update={"project_sha256":digest_file(plan.workspace/"native.ecproj"),
                                               "frames":frames,"comp_id":info.id,"layer_id":info.layers[0].id})
        receipt = receipt.model_copy(update={"evidence":evidence.model_dump_json()})
        _ = self.store.record_observation(job.id,receipt,self.store.read_recorded().revision)
        return result,receipt

    def execute(self, packet: RequestPacket) -> JobReceipt:
        job = next((j for j in self.store.read_recorded().jobs if j.packet == packet),None)
        if job is None or job.phase != JobPhase.DISPATCHING or job.job_id is not None:
            raise ContractError("reservation", "exact fresh composition reservation required")
        plan = self.plan_for(packet)
        if plan.workspace.exists():
            raise ContractError("reservation", "native comp already started; never replay edits")
        project = str(plan.workspace/"native.ecproj")
        binary = str(self.binary)
        first,receipt = self.stage(job,plan,NativeStage(1,(binary,"--empty","--save-as",project,
                                     "run","--commands","-","--json"),json.dumps(build_steps(plan)).encode()))
        if first.returncode or first.timed_out:
            return receipt
        info = resources(first.stdout)
        seconds = plan.recipe.frame_count*plan.recipe.fps.den/plan.recipe.fps.num
        for number,(time,position) in enumerate(((0,plan.recipe.start_position),(seconds,plan.recipe.end_position)),2):
            argv = (binary,"--project",project,"--save","set",str(info.id),str(info.layers[0].id),
                    "transform/position",json.dumps((*position,0)),"--time",str(time),"--json")
            result,receipt = self.stage(job,plan,NativeStage(number,argv))
            if result.returncode or result.timed_out:
                return receipt
        args = (binary,"--project",project,"render","--comp",str(info.id),"--out",str(plan.workspace/"plate.png"),
                "--format","png","--start","0","--end",str(seconds),"--fps",
                str(plan.recipe.fps.num/plan.recipe.fps.den),"--channels","rgba","--audio","off","--json")
        _,receipt = self.stage(job,plan,NativeStage(4,args))
        return receipt

    def observe(self, job: PostJob) -> JobObservation:
        if (next((j for j in self.store.read_recorded().jobs if j.id == job.id),None) != job
            or job.phase != JobPhase.SUCCEEDED or not job.observations):
            raise ContractError("job", "known completed composition job required")
        plan = self.plan_for(job.packet)
        evidence = EffectEvidence.model_validate_json(job.observations[-1].evidence)
        project = plan.workspace/"native.ecproj"
        if evidence.project_sha256 is None or digest_file(project) != evidence.project_sha256:
            raise ContractError("readback", "composition/native keyframe file changed after render")
        _ = EffectHeader.model_validate_json(project.read_bytes())
        if evidence.comp_id is None or evidence.layer_id is None:
            raise ContractError("readback", "actual composition/layer IDs missing")
        check_properties(plan,evidence.comp_id,evidence.layer_id)
        recipe = plan.recipe
        manifest = verify_frames(plan,evidence,self.store.path.parent)
        path = plan.workspace/"plate-manifest.json"
        data = manifest.model_dump_json().encode()
        if path.exists() and path.read_bytes() != data:
            raise ContractError("artifact", "existing materialization manifest changed; inspect rather than overwrite")
        if not path.exists():
            _ = path.write_bytes(data)
        start = map_frame(recipe.start_frame,recipe.fps,FILM_CLOCK,rounding="exact")
        end = map_frame(recipe.start_frame+recipe.frame_count,recipe.fps,FILM_CLOCK,rounding="exact")
        mapping = tuple(NativeMapping(source=s.source,native_item=evidence.comp_id,native_clip=evidence.layer_id,
            source_range=s.approved_range,timeline_range=SourceRange(start=start,end=end),relation="work_context")
            for s in plan.sources)
        return JobObservation(receipt=job.observations[-1],artifact=self.pin(path,job.id),
            native_project=self.pin(project,f"{job.id}-project"),mapping=mapping,frame_count=recipe.frame_count,
            technical_verified=True,frames=evidence.frames,media_kind="rgba_sequence")
