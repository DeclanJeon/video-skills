"""Real FilmCraft full picture/actual RGBA still-frame sequence/native mix reintegration, no final human QA claim."""
from dataclasses import dataclass
import hashlib
from pathlib import Path
from uuid import uuid4

from postproduction.backends.base import CapabilitySnapshot, JobObservation
from postproduction.backends.film_models import FilmExport, StageEvidence
from postproduction.backends.film_native import NativeStage, digest_file
from postproduction.backends.filmcraft import FilmCraftBackend
from postproduction.backends.finishing_audio import verify_mix
from postproduction.backends.finishing_native import imports, placements, readback, runner
from postproduction.backends.process import ProcessResult
from postproduction.common import Pin, SourceId
from postproduction.edit_models import EditAuthority
from postproduction.environment.models import Tool
from postproduction.errors import ContractError
from postproduction import finishing_admission
from postproduction.finishing_models import FinishingPlan
from postproduction.job_models import JobPhase, JobReceipt, PostJob
from postproduction.media import probe_video
from postproduction.profile_checks import verify_encoding
from postproduction.revisions import work_fingerprint
from postproduction.store_port import ProjectPort
from postproduction.work_models import Domain, RequestPacket, WorkOrder


@dataclass(frozen=True,slots=True)
class FinishingBackend:
    store: ProjectPort
    workspace: Path
    binary: Path = Path("/usr/bin/filmcraft-cli")

    def inspect(self) -> CapabilitySnapshot:
        return FilmCraftBackend(self.store,self.workspace,self.binary).inspect()

    def prepare(self, order: WorkOrder, capability: CapabilitySnapshot, authority: EditAuthority) -> RequestPacket:
        state = self.store.read_recorded()
        if (order.domain!=Domain.FINISHING or order.backend!=Tool.FILMCRAFT
            or capability.tool!=Tool.FILMCRAFT or capability.binary_path!=str(self.binary)
            or capability.binary_sha256!=digest_file(self.binary)):
            raise ContractError("capability", "actual current native FilmCraft finishing route required")
        if authority!=state.intake.authority:
            raise ContractError("authority", "exact current composition/mix authority required")
        recipe,inputs = finishing_admission.bound_finishing_inputs(state,order,self.store.path)
        if order.recipe is None:
            raise ContractError("recipe", "explicit finishing recipe pin required")
        owner = uuid4().hex
        plan = FinishingPlan(workspace=(self.workspace/f"run-{owner}").absolute(),owner=owner,capability=capability,
                             recipe=recipe,recipe_pin=order.recipe,inputs=inputs)
        return RequestPacket(order=order,input_fingerprint=work_fingerprint(state,order),payload=plan.model_dump_json())

    def plan_for(self, packet: RequestPacket) -> FinishingPlan:
        state = self.store.read_recorded()
        plan = finishing_admission.verify_finishing_packet(state,packet,self.store.path)
        if (plan.capability.binary_sha256!=digest_file(self.binary)
            or plan.capability.binary_path!=str(self.binary)
            or not plan.workspace.is_relative_to(self.workspace.absolute())):
            raise ContractError("revision", "actual finishing packet/inputs/producer lineage changed")
        return plan

    def pin(self, path: Path, id: str) -> Pin:
        digest = digest_file(path)
        if digest is None:
            raise ContractError("artifact", "actual native finishing file missing")
        return Pin(id=SourceId(id),version="1",path=path.relative_to(self.store.path.parent).as_posix(),sha256=digest)

    def stage(self, job: PostJob, plan: FinishingPlan, step: NativeStage) -> tuple[ProcessResult,JobReceipt]:
        result = runner(plan,self.store.path.parent).run(step.argv,stdin=step.stdin,timeout=120)
        phase = JobPhase.UNKNOWN if result.timed_out else JobPhase.FAILED if result.returncode else (
            JobPhase.SUCCEEDED if step.number==3 else JobPhase.RUNNING)
        evidence = StageEvidence(stage=step.number,pid=result.pid,returncode=result.returncode,timed_out=result.timed_out,
            stdout_sha256=hashlib.sha256(result.stdout).hexdigest(),stderr_sha256=hashlib.sha256(result.stderr).hexdigest(),
            project_sha256=None,output_sha256=None)
        receipt = JobReceipt(phase=phase,request_hash=job.request_hash,job_id=f"finishing-{plan.owner}",evidence=evidence.model_dump_json())
        _ = self.store.record_observation(job.id,receipt,self.store.read_recorded().revision)
        _ = (plan.workspace/f"stage{step.number}.stdout").write_bytes(result.stdout)
        _ = (plan.workspace/f"stage{step.number}.stderr").write_bytes(result.stderr)
        if step.stdin is not None:
            _ = (plan.workspace/f"stage{step.number}.request").write_bytes(step.stdin)
        evidence = evidence.model_copy(update={"project_sha256":digest_file(plan.workspace/"native.fcproj"),
                                               "output_sha256":digest_file(plan.workspace/"master.mp4")})
        receipt = receipt.model_copy(update={"evidence":evidence.model_dump_json()})
        _ = self.store.record_observation(job.id,receipt,self.store.read_recorded().revision)
        return result,receipt

    def execute(self, packet: RequestPacket) -> JobReceipt:
        job = next((j for j in self.store.read_recorded().jobs if j.packet==packet),None)
        if job is None or job.phase!=JobPhase.DISPATCHING or job.job_id is not None:
            raise ContractError("reservation", "exact fresh finishing reservation required; never replay uncertain work")
        plan = self.plan_for(packet)
        if plan.workspace.exists():
            raise ContractError("reservation", "owned finishing already started; inspect/reconcile, not replay")
        project,binary = str(plan.workspace/"native.fcproj"),str(self.binary)
        first,receipt = self.stage(job,plan,NativeStage(1,(binary,"--compact","--save-as",project,"run","-"),
                                                     imports(plan,self.store.path.parent)))
        if first.returncode or first.timed_out:
            return receipt
        _ = self.plan_for(packet)
        second,receipt = self.stage(job,plan,NativeStage(2,(binary,"--project",project,"--save","--compact","run","-"),
                                                       placements(plan,self.store.path.parent)))
        if second.returncode or second.timed_out:
            return receipt
        _ = readback(plan,self.store.path.parent)
        _,receipt = self.stage(job,plan,NativeStage(3,(binary,"--project",project,"export",str(plan.workspace/"master.mp4"),
                                                       "--format","h264","--gpu-rendering","off")))
        return receipt

    def observe(self, job: PostJob) -> JobObservation:
        if next((j for j in self.store.read_recorded().jobs if j.id==job.id),None)!=job or job.phase!=JobPhase.SUCCEEDED:
            raise ContractError("job", "exact known completed native finishing attempt required")
        plan = self.plan_for(job.packet)
        evidence = StageEvidence.model_validate_json(job.observations[-1].evidence)
        project,output = plan.workspace/"native.fcproj",plan.workspace/"master.mp4"
        if evidence.project_sha256 is None or digest_file(project)!=evidence.project_sha256:
            raise ContractError("readback", "native manual finishing projection changed after export")
        if evidence.output_sha256 is None or digest_file(output)!=evidence.output_sha256:
            raise ContractError("artifact", "native working master missing/changed/partial")
        report = FilmExport.model_validate_json((plan.workspace/"stage3.stdout").read_bytes())
        if (report.offlineMedia or report.warnings or report.path!=str(output) or report.result.path!=str(output)
            or report.result.frames!=plan.inputs.total_frames or report.result.bytes!=output.stat().st_size):
            raise ContractError("offline", "native finishing export does not match current actual full sequence")
        mappings = readback(plan,self.store.path.parent)
        pin = self.pin(output,job.id)
        verify_encoding(self.store.path.parent,pin,plan.inputs.profile)
        facts = probe_video(self.store.path.parent,pin)
        p = plan.inputs.profile
        if (facts.width,facts.height,facts.rate,facts.frame_count,facts.cfr,facts.has_audio)!=(
            p.width,p.height,p.fps,plan.inputs.total_frames,True,True):
            raise ContractError("metadata", "independent working master decode differs from actual finishing plan")
        verify_mix(plan,pin,self.store.path.parent)
        return JobObservation(receipt=job.observations[-1],artifact=pin,native_project=self.pin(project,f"{job.id}-project"),
            mapping=(),artifact_mapping=mappings,frame_count=facts.frame_count,technical_verified=True,
            related_assets=plan.inputs.pins)
