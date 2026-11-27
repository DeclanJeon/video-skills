"""Narrow actual-backend reinspection and current artifact registration, never final creative approval."""
import hashlib
from pathlib import Path
from typing import assert_never

from postproduction.backends.base import JobObservation
from postproduction.common import Pin, SourceId
from postproduction.environment.models import Tool
from postproduction.errors import ContractError
from postproduction.files import confined_path, verified_file
from postproduction.job_models import ArtifactRef, JobPhase, PostJob
from postproduction.revisions import verify_work_inputs, work_fingerprint
from postproduction.state_models import PostState
from postproduction.work_models import Domain

from postproduction.store_port import ProjectPort


def observe_actual(store: ProjectPort, job: PostJob) -> JobObservation:
    """Each actual adapter parses its own schema; no generic success boolean or arbitrary result JSON."""
    match job.packet.order.backend:
        case Tool.FILMCRAFT:
            match job.packet.order.domain:
                case Domain.FINISHING:
                    from postproduction.backends.finishing import FinishingBackend
                    from postproduction.finishing_models import FinishingPlan
                    finish = FinishingPlan.model_validate_json(job.packet.payload)
                    return FinishingBackend(store,finish.workspace.parent).observe(job)
                case Domain.PICTURE:
                    from postproduction.backends.film_models import FilmPlan
                    from postproduction.backends.filmcraft import FilmCraftBackend
                    plan = FilmPlan.model_validate_json(job.packet.payload)
                    return FilmCraftBackend(store,plan.workspace.parent).observe(job)
                case Domain.MOTION | Domain.COLOR | Domain.SOUND | Domain.CAPTIONS | Domain.QA | Domain.DELIVERY | Domain.ENVIRONMENT:
                    raise ContractError("backend", "this FilmCraft domain has no qualified native adapter")
            assert_never(job.packet.order.domain)
        case Tool.EFFECTCRAFT:
            from postproduction.backends.effect_models import EffectPlan
            from postproduction.backends.effectcraft import EffectCraftBackend
            effect = EffectPlan.model_validate_json(job.packet.payload)
            return EffectCraftBackend(store,effect.workspace.parent).observe(job)
        case Tool.SOUNDCRAFT:
            from postproduction.backends.sound_models import SoundPlan
            from postproduction.backends.soundcraft import SoundCraftBackend
            sound = SoundPlan.model_validate_json(job.packet.payload)
            return SoundCraftBackend(store,sound.workspace.parent).observe(job)
        case Tool.AUTOCLIP | Tool.RESOLVE | Tool.PREMIERE | Tool.AFTER_EFFECTS | Tool.FFMPEG | Tool.FFPROBE:
            raise ContractError("backend", "this native materialization route has no verified adapter")
    assert_never(job.packet.order.backend)


def checked_materialization(store: ProjectPort, state: PostState, job_id: str) -> ArtifactRef:
    """Re-observe actual known outputs/current inputs, write immutable proof, keep adopted=False."""
    job = next((j for j in state.jobs if j.id == job_id),None)
    if job is None or job.phase != JobPhase.SUCCEEDED:
        raise ContractError("job", "known succeeded native job required, not an invented output claim")
    verify_work_inputs(state,job.packet.order,store.path)
    if work_fingerprint(state,job.packet.order) != job.packet.input_fingerprint:
        raise ContractError("revision", "native output is for replaced consumed inputs")
    observation = observe_actual(store,job)
    if not observation.technical_verified or observation.artifact is None or observation.native_project is None:
        raise ContractError("materialization", "actual verified output/project proof incomplete")
    related: list[Pin] = []
    for pin in (observation.native_project,*observation.frames,*observation.related_assets):
        _ = verified_file(store.path.parent,pin)
        if pin not in related:
            related.append(pin)
    data = observation.model_dump_json().encode()
    proof_relative = observation.artifact.path+".observation.json"
    proof_path = confined_path(store.path.parent,proof_relative)
    if proof_path.exists():
        if proof_path.read_bytes() != data:
            raise ContractError("proof", "existing materialization proof is immutable and differs")
    else:
        with proof_path.open("xb") as out:
            _ = out.write(data)
    proof = Pin(id=SourceId(f"{job.id}-proof"),version="1",path=proof_relative,
                sha256=hashlib.sha256(data).hexdigest())
    return ArtifactRef(id=f"{job.id}-artifact",job_id=job.id,pin=observation.artifact,
                       input_fingerprint=job.packet.input_fingerprint,proof=proof,related=tuple(related),
                       kind=observation.media_kind)


def verify_artifact_current(state: PostState, artifact: ArtifactRef, project: Path) -> None:
    """Current technical bytes/lineage is distinct from reported playback/listening/final QA."""
    job = next((j for j in state.jobs if j.id == artifact.job_id),None)
    if (job is None or job.phase != JobPhase.SUCCEEDED or artifact.proof is None
        or artifact.input_fingerprint != job.packet.input_fingerprint
        or work_fingerprint(state,job.packet.order) != artifact.input_fingerprint):
        raise ContractError("revision", "artifact is not bound to current consumed work and known job")
    if job.packet.order.domain==Domain.FINISHING:
        from postproduction.finishing_admission import verify_finishing_packet
        # Same contract as fresh raw dispatch; historical success cannot grandfather mismatched work.
        _ = verify_finishing_packet(state,job.packet,project)
    else:
        verify_work_inputs(state,job.packet.order,project)
    for pin in (artifact.pin,artifact.proof,*artifact.related):
        _ = verified_file(project.parent,pin)
    proof_path = verified_file(project.parent,artifact.proof)
    proof = JobObservation.model_validate_json(proof_path.read_bytes())
    if (proof.artifact != artifact.pin or proof.receipt.request_hash != job.request_hash
        or not proof.technical_verified or proof.media_kind != artifact.kind):
        raise ContractError("proof", "artifact materialization and exact native job proof differ")
