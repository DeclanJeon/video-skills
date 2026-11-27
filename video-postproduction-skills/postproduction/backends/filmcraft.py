"""Actual FilmCraft headless import→observed IDs→edit/readback→CPU export→independent decode."""
from dataclasses import dataclass
import hashlib
from pathlib import Path
from uuid import uuid4

from pydantic import ValidationError

from postproduction.backends.base import CapabilitySnapshot, JobObservation
from postproduction.backends.film_models import FilmExport, FilmPlan, StageEvidence
from postproduction.backends.film_native import REQUIRED, NativeStage, digest_file, initial_script, metadata_id, place_script, runner
from postproduction.backends.film_readback import check_timeline, read_project
from postproduction.backends.process import IsolatedProcess, ProcessResult, SandboxScope
from postproduction.clock import map_frame
from postproduction.common import Pin, SourceId
from postproduction.edit_models import EditAuthority
from postproduction.environment.models import Tool
from postproduction.errors import ContractError
from postproduction.files import confined_path
from postproduction.job_models import JobPhase, JobReceipt, PostJob
from postproduction.jobs import request_digest
from postproduction.store_port import ProjectPort
from postproduction.media import probe_video
from postproduction.profile_checks import verify_encoding, require_native_export_profile
from postproduction.revisions import verify_work_inputs, work_fingerprint
from postproduction.timeline_map import FILM_CLOCK
from postproduction.work_models import RequestPacket, WorkOrder


@dataclass(frozen=True, slots=True)
class FilmCraftBackend:
    store: ProjectPort
    workspace: Path
    binary: Path = Path("/usr/bin/filmcraft-cli")

    def inspect(self) -> CapabilitySnapshot:
        """Query actual installed metadata in a private network-denied session, not a user app bridge."""
        if any(p.is_symlink() for p in (self.workspace,*self.workspace.parents)):
            raise ContractError("path", "backend workspace prefix cannot be a symlink")
        self.workspace.mkdir(exist_ok=True,mode=0o700)
        owner = uuid4().hex
        isolated = IsolatedProcess(SandboxScope(self.workspace/f"inspect-{owner}",owner))
        result = isolated.run((str(self.binary),"--version"))
        if result.returncode or result.timed_out:
            raise ContractError("capability", "existing FilmCraft CLI version probe failed")
        ids: list[str] = []
        for command in REQUIRED:
            described = isolated.run((str(self.binary),"describe",command))
            if described.returncode or metadata_id(described.stdout) != command:
                raise ContractError("capability", "required actual FilmCraft command protocol unavailable")
            ids.append(command)
        digest = digest_file(self.binary)
        if digest is None:
            raise ContractError("binary", "actual FilmCraft binary unavailable")
        return CapabilitySnapshot(tool=Tool.FILMCRAFT,binary_path=str(self.binary),binary_sha256=digest,
                                  version=result.stdout.decode().strip(),command_ids=tuple(ids))

    def prepare(self, order: WorkOrder, capability: CapabilitySnapshot, authority: EditAuthority) -> RequestPacket:
        """Build an immutable native packet without creating/editing a native project."""
        state = self.store.read_recorded()
        verify_work_inputs(state,order,self.store.path)
        if (capability.tool != Tool.FILMCRAFT or capability.binary_path != str(self.binary)
            or capability.binary_sha256 != digest_file(self.binary)):
            raise ContractError("binary", "capability does not match the exact current native binary")
        if authority != state.intake.authority or order.backend != Tool.FILMCRAFT:
            raise ContractError("authority", "actual current edit authority/backend differs")
        timeline = next((t for t in state.timelines if t.branch == order.branch),None)
        if timeline is None or {(s.clip_id,s.take_id) for s in order.source_refs} != {
            (s.source.clip_id,s.source.take_id) for s in state.intake.sources}:
            raise ContractError("coverage", "initial native picture route needs the full approved source set")
        if any(a.timeline_range.end != b.timeline_range.start for a,b in zip(timeline.segments,timeline.segments[1:])):
            raise ContractError("overlap", "native transition/overlap needs a separately verified command recipe")
        profile = state.intake.profile
        require_native_export_profile(profile)
        if any((s.width,s.height,s.rate) != (profile.width,profile.height,profile.fps) for s in state.intake.sources):
            raise ContractError("conform", "geometry/FPS change needs explicit verified finishing/conform")
        if confined_path(self.store.path.parent,order.output).exists():
            raise ContractError("existing", "requested output already exists; do not overwrite")
        owner = uuid4().hex
        plan = FilmPlan(workspace=(self.workspace/f"run-{owner}").absolute(),owner=owner,capability=capability,
                        timeline=timeline,sources=state.intake.sources,profile=profile)
        return RequestPacket(order=order,input_fingerprint=work_fingerprint(state,order),payload=plan.model_dump_json())

    def plan_for(self, packet: RequestPacket) -> FilmPlan:
        """Reparse the stored opaque native protocol and bind it back to actual current decisions."""
        try:
            plan = FilmPlan.model_validate_json(packet.payload)
        except ValidationError as exc:
            raise ContractError("packet", "invalid backend-owned FilmCraft plan") from exc
        require_native_export_profile(plan.profile)
        state = self.store.read_recorded()
        verify_work_inputs(state,packet.order,self.store.path)
        if packet.input_fingerprint != work_fingerprint(state,packet.order):
            raise ContractError("revision", "consumed work inputs changed")
        if (plan.capability.binary_sha256 != digest_file(self.binary)
            or plan.capability.binary_path != str(self.binary)):
            raise ContractError("binary", "native binary changed since preparation")
        if (plan.sources != state.intake.sources or plan.profile != state.intake.profile
            or plan.timeline != next((t for t in state.timelines if t.branch == packet.order.branch),None)
            or not plan.workspace.is_relative_to(self.workspace.absolute())):
            raise ContractError("packet", "native packet differs from canonical adopted inputs/owned paths")
        return plan

    def stage(self, job: PostJob, plan: FilmPlan, step: NativeStage) -> tuple[ProcessResult,JobReceipt]:
        """Publish actual process facts before mutable transcript/hash/readback/readiness diagnostics."""
        packet,number = job.packet,step.number
        result = runner(plan,self.store.path.parent).run(step.argv,stdin=step.stdin,timeout=90)
        phase = JobPhase.UNKNOWN if result.timed_out else JobPhase.FAILED if result.returncode else (
            JobPhase.SUCCEEDED if number == 3 else JobPhase.RUNNING)
        evidence = StageEvidence(stage=number,pid=result.pid,returncode=result.returncode,timed_out=result.timed_out,
            stdout_sha256=hashlib.sha256(result.stdout).hexdigest(),stderr_sha256=hashlib.sha256(result.stderr).hexdigest(),
            project_sha256=None,output_sha256=None)
        receipt = JobReceipt(phase=phase,request_hash=request_digest(packet),job_id=f"filmcraft-{plan.owner}",
                             evidence=evidence.model_dump_json())
        current = self.store.read_recorded()
        _ = self.store.record_observation(job.id,receipt,current.revision)
        _ = (plan.workspace/f"stage{number}.stdout").write_bytes(result.stdout)
        _ = (plan.workspace/f"stage{number}.stderr").write_bytes(result.stderr)
        hashes = evidence.model_copy(update={"project_sha256":digest_file(plan.workspace/"native.fcproj"),
                                             "output_sha256":digest_file(plan.workspace/"result.mp4")})
        receipt = receipt.model_copy(update={"evidence":hashes.model_dump_json()})
        _ = self.store.record_observation(job.id,receipt,self.store.read_recorded().revision)
        return result,receipt

    def execute(self, packet: RequestPacket) -> JobReceipt:
        """Never dispatch without exact prior reservation or replay an already known native job."""
        state = self.store.read_recorded()
        job = next((j for j in state.jobs if j.packet == packet),None)
        if job is None or job.phase != JobPhase.DISPATCHING or job.job_id is not None:
            raise ContractError("reservation", "an exact fresh reservation is required; never replay known work")
        plan = self.plan_for(packet)
        if plan.workspace.exists():
            raise ContractError("reservation", "owned native workspace already started; inspect rather than replay")
        binary = str(self.binary)
        project = str(plan.workspace/"native.fcproj")
        first,receipt = self.stage(job,plan,NativeStage(1,(binary,"--compact","--save-as",project,"run","-"),
                                  initial_script(plan,self.store.path.parent)))
        if first.returncode or first.timed_out:
            return receipt
        _ = self.store.read()
        second,receipt = self.stage(job,plan,NativeStage(2,(binary,"--project",project,"--save","--compact","run","-"),
                                    place_script(plan,self.store.path.parent)))
        if second.returncode or second.timed_out:
            return receipt
        _ = check_timeline(read_project(Path(project)),plan,self.store.path.parent)
        output = str(plan.workspace/"result.mp4")
        args = (binary,"--project",project,"export",output,"--format","h264","--gpu-rendering","off")
        if not any(s.has_audio for s in plan.sources):
            args += ("--no-audio",)
        _,receipt = self.stage(job,plan,NativeStage(3,args))
        return receipt

    def observe(self, job: PostJob) -> JobObservation:
        """Verify exact stored output/native bytes and current source lineage, independently decoding output."""
        actual = next((j for j in self.store.read_recorded().jobs if j.id == job.id),None)
        if actual != job or job.phase != JobPhase.SUCCEEDED or not job.observations:
            raise ContractError("job", "only an exact known succeeded attempt can be materialized")
        plan = self.plan_for(job.packet)
        evidence = StageEvidence.model_validate_json(job.observations[-1].evidence)
        project,output = plan.workspace/"native.fcproj",plan.workspace/"result.mp4"
        if evidence.project_sha256 is None or evidence.project_sha256 != digest_file(project):
            raise ContractError("readback", "native project changed after observed export")
        if evidence.output_sha256 is None or evidence.output_sha256 != digest_file(output):
            raise ContractError("artifact", "native output missing/changed/partial after known completion")
        report = FilmExport.model_validate_json((plan.workspace/"stage3.stdout").read_bytes())
        if report.offlineMedia or report.warnings or report.path != str(output) or report.result.path != str(output):
            raise ContractError("offline", "native export has unresolved warnings/offline media or returned another output")
        mapping = check_timeline(read_project(project),plan,self.store.path.parent)
        pin = Pin(id=SourceId(job.id),version="1",path=output.relative_to(self.store.path.parent).as_posix(),
                  sha256=evidence.output_sha256)
        native = Pin(id=SourceId(f"{job.id}-project"),version="1",path=project.relative_to(self.store.path.parent).as_posix(),
                     sha256=evidence.project_sha256)
        verify_encoding(self.store.path.parent,pin,plan.profile,audio_required=any(s.has_audio for s in plan.sources))
        facts = probe_video(self.store.path.parent,pin)
        expected = map_frame(plan.timeline.segments[-1].timeline_range.end,FILM_CLOCK,plan.profile.fps,rounding="exact")
        if ((facts.width,facts.height,facts.frame_count,facts.rate,facts.cfr,facts.has_audio)
            != (plan.profile.width,plan.profile.height,expected,plan.profile.fps,True,any(s.has_audio for s in plan.sources))
            or report.result.frames != expected or report.result.bytes != output.stat().st_size):
            raise ContractError("metadata", "independent decoded native result differs from approved sequence")
        return JobObservation(receipt=job.observations[-1],artifact=pin,native_project=native,mapping=mapping,
                              frame_count=facts.frame_count,technical_verified=True)
