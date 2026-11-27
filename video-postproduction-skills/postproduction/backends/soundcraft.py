"""Actual private SoundCraft session/cues/faders/bounce with independent complete waveform verification."""
from dataclasses import dataclass
import hashlib
from pathlib import Path
from uuid import uuid4

from postproduction.audio import probe_audio, verify_stem
from postproduction.backends.base import CapabilitySnapshot, JobObservation
from postproduction.backends.film_native import NativeStage, digest_file, metadata_id
from postproduction.backends.process import IsolatedProcess, ProcessResult, SandboxScope
from postproduction.backends.sound_models import SoundEvidence, SoundPlan, SoundRecipe
from postproduction.backends.sound_native import REQUIRED, import_argv, imports, mix_argv, runner, summary
from postproduction.backends.sound_readback import check_session, compare_waveform
from postproduction.clock import map_frame
from postproduction.common import ClockRate, Pin, SourceId
from postproduction.edit_models import Change, EditAuthority
from postproduction.environment.models import Tool
from postproduction.errors import ContractError
from postproduction.files import read_model, verified_file
from postproduction.job_models import JobPhase, JobReceipt, PostJob
from postproduction.store_port import ProjectPort
from postproduction.media import probe_video
from postproduction.revisions import verify_work_inputs, work_fingerprint
from postproduction.work_models import RequestPacket, WorkOrder


@dataclass(frozen=True, slots=True)
class SoundCraftBackend:
    store: ProjectPort
    workspace: Path
    binary: Path = Path("/usr/bin/soundcraft-cli")

    def inspect(self) -> CapabilitySnapshot:
        self.workspace.mkdir(exist_ok=True,mode=0o700)
        owner = uuid4().hex
        isolated = IsolatedProcess(SandboxScope(self.workspace/f"inspect-{owner}",owner))
        version = isolated.run((str(self.binary),"--version"))
        ids: list[str] = []
        for command in REQUIRED:
            result = isolated.run((str(self.binary),"describe",command))
            if result.returncode or metadata_id(result.stdout) != command:
                raise ContractError("capability", "actual SoundCraft CLI command protocol unavailable")
            ids.append(command)
        digest = digest_file(self.binary)
        if version.returncode or digest is None:
            raise ContractError("binary", "actual sound binary/version not established")
        return CapabilitySnapshot(tool=Tool.SOUNDCRAFT,binary_path=str(self.binary),binary_sha256=digest,
                                  version=version.stdout.decode().strip(),command_ids=tuple(ids))

    def prepare(self, order: WorkOrder, capability: CapabilitySnapshot, authority: EditAuthority) -> RequestPacket:
        state = self.store.read_recorded()
        verify_work_inputs(state,order,self.store.path)
        if (capability.tool != Tool.SOUNDCRAFT or capability.binary_path != str(self.binary)
            or capability.binary_sha256 != digest_file(self.binary)):
            raise ContractError("binary", "sound capability differs from current actual binary")
        if authority != state.intake.authority or Change.AUDIO not in authority.allowed_changes:
            raise ContractError("authority", "exact current sound editing authority required")
        if order.recipe is None:
            raise ContractError("recipe", "actual WAV/cue recipe required; AAF or invented stems not inferred")
        recipe = read_model(self.store.path.parent,order.recipe,SoundRecipe)
        profile = state.intake.profile
        if ((recipe.sample_rate,recipe.channels,recipe.picture_fps) != (profile.sample_rate,2,profile.fps)
            or profile.fps != ClockRate(num=24,den=1)):
            raise ContractError("format", "verified initial sound route is exact24fps picture/approved sample rate/stereo")
        if recipe.mono_center_db != -3.0:
            raise ContractError("pan-law", "actual verified Mono-center route is explicit -3dB, not inferred equal-power sqrt(.5)")
        picture = probe_video(self.store.path.parent,recipe.picture)
        expected = map_frame(picture.frame_count,picture.rate,ClockRate(num=recipe.sample_rate,den=1),rounding="exact")
        if picture.has_audio or picture.rate != recipe.picture_fps or recipe.sample_count != expected:
            raise ContractError("picture", "initial picture reference must be silent and match exact approved sample duration")
        ids = {c.stem_id for c in recipe.cues}
        stems = tuple(s for s in state.intake.request.stems if s.id in ids)
        if len(stems) != len(ids):
            raise ContractError("stem", "recipe cannot create missing component stems")
        required = (recipe.picture,*(p for s in stems for p in (s.asset,s.independence_evidence)))
        if any(p not in order.dependencies for p in required):
            raise ContractError("dependency", "all actual selected audio/picture/provenance pins must bind work inputs")
        for stem in stems:
            _ = verify_stem(self.store.path.parent,stem)
            if stem.sample_rate != recipe.sample_rate or stem.channels not in {1,2}:
                raise ContractError("conform", "unsupported channel/resample needs a verified explicit route")
        if any(c.at_sample+next(s.sample_count for s in stems if s.id==c.stem_id) > recipe.sample_count for c in recipe.cues):
            raise ContractError("range", "audio cue extends beyond the exact picture/mix range")
        owner = uuid4().hex
        plan = SoundPlan(workspace=(self.workspace/f"run-{owner}").absolute(),owner=owner,capability=capability,
                         recipe=recipe,recipe_pin=order.recipe,stems=stems,
                         sources=tuple(s for s in state.intake.sources if s.source in order.source_refs))
        return RequestPacket(order=order,input_fingerprint=work_fingerprint(state,order),payload=plan.model_dump_json())

    def plan_for(self, packet: RequestPacket) -> SoundPlan:
        state = self.store.read_recorded()
        verify_work_inputs(state,packet.order,self.store.path)
        plan = SoundPlan.model_validate_json(packet.payload)
        used = {c.stem_id for c in plan.recipe.cues}
        if (packet.input_fingerprint != work_fingerprint(state,packet.order)
            or plan.capability.binary_sha256 != digest_file(self.binary)
            or plan.capability.binary_path != str(self.binary) or plan.capability.tool != Tool.SOUNDCRAFT
            or plan.recipe != read_model(self.store.path.parent,plan.recipe_pin,SoundRecipe)
            or plan.stems != tuple(s for s in state.intake.request.stems if s.id in used)
            or not plan.workspace.is_relative_to(self.workspace.absolute())):
            raise ContractError("revision", "current sound packet/consumed inputs/actual binary changed")
        return plan

    def pin(self, path: Path, name: str) -> Pin:
        digest = digest_file(path)
        if digest is None:
            raise ContractError("artifact", "actual native session/media/bounce missing")
        return Pin(id=SourceId(name),version="1",path=path.relative_to(self.store.path.parent).as_posix(),sha256=digest)

    def stage(self, job: PostJob, plan: SoundPlan, step: NativeStage) -> tuple[ProcessResult,JobReceipt]:
        result = runner(plan,self.store.path.parent).run(step.argv,stdin=step.stdin,timeout=90)
        phase = JobPhase.UNKNOWN if result.timed_out else JobPhase.FAILED if result.returncode else (
            JobPhase.SUCCEEDED if step.number==2 else JobPhase.RUNNING)
        evidence = SoundEvidence(stage=step.number,pid=result.pid,returncode=result.returncode,
                                 timed_out=result.timed_out,stdout_sha256=hashlib.sha256(result.stdout).hexdigest())
        receipt = JobReceipt(phase=phase,request_hash=job.request_hash,job_id=f"soundcraft-{plan.owner}",
                             evidence=evidence.model_dump_json())
        _ = self.store.record_observation(job.id,receipt,self.store.read_recorded().revision)
        _ = (plan.workspace/f"stage{step.number}.stdout").write_bytes(result.stdout)
        _ = (plan.workspace/f"stage{step.number}.stderr").write_bytes(result.stderr)
        project = plan.workspace/("mixed.scraft" if step.number==2 else "imported.scraft")
        related = tuple(self.pin(p,p.name) for p in sorted((plan.workspace/"Audio Files").glob("*.wav")))
        evidence = evidence.model_copy(update={"project_sha256":digest_file(project),
                                               "output_sha256":digest_file(plan.workspace/"mix.wav"),
                                               "related_assets":related})
        receipt = receipt.model_copy(update={"evidence":evidence.model_dump_json()})
        _ = self.store.record_observation(job.id,receipt,self.store.read_recorded().revision)
        return result,receipt

    def execute(self, packet: RequestPacket) -> JobReceipt:
        job = next((j for j in self.store.read_recorded().jobs if j.packet==packet),None)
        if job is None or job.phase!=JobPhase.DISPATCHING or job.job_id is not None:
            raise ContractError("reservation", "exact fresh sound reservation required; never replay uncertain bounce")
        plan = self.plan_for(packet)
        if plan.workspace.exists():
            raise ContractError("reservation", "sound session already started; reconcile actual state")
        first,receipt = self.stage(job,plan,NativeStage(1,import_argv(plan,self.store.path.parent)))
        if first.returncode or first.timed_out:
            return receipt
        imported = imports(first.stdout)
        _,receipt = self.stage(job,plan,NativeStage(2,mix_argv(plan,imported)))
        return receipt

    def observe(self, job: PostJob) -> JobObservation:
        if (next((j for j in self.store.read_recorded().jobs if j.id==job.id),None)!=job
            or job.phase!=JobPhase.SUCCEEDED or not job.observations):
            raise ContractError("job", "known exact native mix completion required")
        plan = self.plan_for(job.packet)
        evidence = SoundEvidence.model_validate_json(job.observations[-1].evidence)
        project,output = plan.workspace/"mixed.scraft",plan.workspace/"mix.wav"
        if evidence.project_sha256 is None or digest_file(project)!=evidence.project_sha256:
            raise ContractError("readback", "native session/track/sample map changed after bounce")
        if evidence.output_sha256 is None or digest_file(output)!=evidence.output_sha256:
            raise ContractError("audio", "actual bounce missing/changed/partial after completion")
        for related in evidence.related_assets:
            _ = verified_file(self.store.path.parent,related)
        initial,final = plan.workspace/"stage1.stdout",plan.workspace/"stage2.stdout"
        if digest_file(final)!=evidence.stdout_sha256:
            raise ContractError("readback", "native compact inspection transcript changed")
        audio_mapping = check_session(plan,summary(final.read_bytes()),imports(initial.read_bytes()))
        pin = self.pin(output,job.id)
        actual = probe_audio(self.store.path.parent,pin)
        compare_waveform(plan,actual,self.store.path.parent)
        frames = map_frame(actual.sample_count,ClockRate(num=actual.sample_rate,den=1),
                           plan.recipe.picture_fps,rounding="exact")
        return JobObservation(receipt=job.observations[-1],artifact=pin,native_project=self.pin(project,f"{job.id}-project"),
            mapping=(),frame_count=frames,technical_verified=True,media_kind="audio",sample_count=actual.sample_count,
            sample_rate=actual.sample_rate,channels=actual.channels,audio_mapping=audio_mapping,
            related_assets=evidence.related_assets)
