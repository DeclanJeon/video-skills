"""Compare explicit per-clip grants; capability is not consent."""
import hashlib
import json
from pathlib import Path

from production.contracts import clip_for
from production.files import verified_file
from production.models import ApprovedConfig, Authority, Capability, Clip, ContractError, State, Take


def clip_configuration_hash(clip: Clip) -> str:
    return hashlib.sha256(json.dumps(clip.model_dump(mode="json"),sort_keys=True,separators=(",",":")).encode()).hexdigest()


def requested_audio(state: State, clip_id: str) -> bool:
    clip=clip_for(state,clip_id)
    return clip.audio_required or any(r.modality == "audio" and r.id in clip.requirements for r in state.approved_coverage)


def validate_config(state: State, clip_id: str, authority: Authority, width: int, height: int, root: Path) -> ApprovedConfig:
    _=verified_file(root,authority.evidence)
    clip=clip_for(state,clip_id)
    grants=[g for g in authority.configurations if g.clip_id == clip.id]
    if len(grants) != 1 or clip.id not in authority.clips:
        raise ContractError("authority","exactly one explicit clip configuration grant required")
    grant=grants[0]
    if (grant.scope_revision != state.batch.scope_revision or grant.coverage_hash != state.coverage_source.sha256
        or grant.clip_hash != clip_configuration_hash(clip) or grant.duration_s != clip.duration_s
        or (grant.width,grant.height) != (width,height)
        or grant.audio_requested != requested_audio(state,clip_id)):
        raise ContractError("authority","duration/output/audio/design/scope differs from approved configuration")
    return grant


def validate_approval(state: State, clip_id: str, capability: Capability, authority: Authority, root: Path) -> None:
    """Check current execution approval pin, not authenticity of its issuer."""
    _=validate_config(state,clip_id,authority,capability.width,capability.height,root)
    if not authority.generation:
        raise ContractError("authority","current generation approval is not enabled")
    for name in ("account","model","transport","mode"):
        if getattr(capability,name) != getattr(authority,name):
            raise ContractError("authority",f"current {name} differs from approval")


def validate_reuse(state: State, take: Take, authority: Authority, root: Path) -> None:
    grant=validate_config(state,take.clip_id,authority,take.width,take.height,root)
    if (not authority.reuse or grant.reuse_source != take.asset or grant.reuse_range != take.source_range
        or take.asset.sha256 not in authority.allowed_hashes):
        raise ContractError("authority","existing source and exact range need an explicit reuse grant")
