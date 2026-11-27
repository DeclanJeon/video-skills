"""Prepare offline request packets; never upload, submit, or invent native IDs."""
from pathlib import Path

from production.contracts import clip_for, fingerprint, ready_clips, selection_for, usable
from production.models import Authority, Binding, Capability, ContractError, Prepared, State
from production.files import verified_file, packet_hash


def prepare_request(state: State, clip_id: str, capability: Capability, authority: Authority,
                    bindings: tuple[Binding, ...], root: Path) -> Prepared:
    from production.adapters import verify_scope
    verify_scope(state, root)
    clip = clip_for(state, clip_id)
    if clip.id not in ready_clips(state):
        raise ContractError("dependency", f"{clip_id} is not ready")
    from production.approval import validate_approval
    validate_approval(state, clip_id, capability, authority, root)
    if not authority.generation or not authority.upload or clip.id not in authority.clips:
        raise ContractError("authority", "missing execution/transfer scope")
    for name in ("account", "model", "transport", "mode"):
        if getattr(capability, name) != getattr(authority, name):
            raise ContractError("authority", f"{name} mismatch")
    if capability.observed_mode != capability.mode:
        raise ContractError("mode", "observed submit mode does not match approval")
    needs_audio = clip.audio_required or any(r.modality == "audio" and r.id in clip.requirements for r in state.approved_coverage)
    if clip.duration_s not in capability.durations or (needs_audio and not capability.audio):
        raise ContractError("capability", "duration/audio unsupported")
    if len(bindings) > capability.max_references:
        raise ContractError("limit", "required refs exceed live contract")
    _ = verified_file(root, capability.evidence)
    _ = verified_file(root, authority.evidence)
    prompt = verified_file(root, clip.prompt).read_text()
    if clip.prompt.sha256 not in authority.allowed_hashes:
        raise ContractError("authority", "prompt transfer not approved")
    if len({b.native_reference_id for b in bindings}) != len(bindings):
        raise ContractError("binding", "duplicate native selected reference")
    expected_assets = {pin.id: pin for pin in clip.assets}
    consumed_assets: set[str] = set()
    consumed_sources: set[tuple[str,str,str]] = set()
    for binding in bindings:
        if not binding.ready:
            raise ContractError("ready", binding.native_reference_id)
        if binding.role not in capability.roles:
            raise ContractError("role", binding.role)
        if binding.modality not in capability.modalities:
            raise ContractError("modality", binding.modality)
        _ = verified_file(root, binding.pin)
        if binding.pin.sha256 not in authority.allowed_hashes:
            raise ContractError("authority", f"unapproved ref {binding.pin.id}")
        if binding.source_clip is None:
            if expected_assets.get(binding.pin.id) != binding.pin:
                raise ContractError("binding", "unexpected identity/design asset")
            consumed_assets.add(binding.pin.id)
        else:
            refs = [ref for ref in clip.references if ref.source_clip == binding.source_clip and ref.role == binding.role and ref.modality == binding.modality]
            source = selection_for(state, binding.source_clip)
            if len(refs) != 1 or source is None or not usable(source, refs[0].imports):
                raise ContractError("binding", "source is not accepted for this role")
            ref = refs[0]
            _ = verified_file(root, source.approval.evidence)
            if (binding.pin != source.take.asset or binding.source_range != source.take.source_range
                or binding.range_revision != source.take.range_revision
                or binding.acceptance_revision != source.acceptance_revision
                or binding.imports != ref.imports or binding.excludes != ref.excludes):
                raise ContractError("binding", "source/range/revision/attributes mismatch")
            consumed_sources.add((ref.source_clip,ref.role,ref.modality))
    if consumed_assets != set(expected_assets):
        raise ContractError("binding", "missing design asset")
    for ref in clip.references:
        key = (ref.source_clip,ref.role,ref.modality)
        if key not in consumed_sources and (ref.required or not ref.omission_evidence):
            raise ContractError("binding", "missing required predecessor role")
    packet = Prepared(clip_id=clip.id, fingerprint=fingerprint(state, clip.id),
        capability=capability, authority=authority, bindings=bindings, prompt=clip.prompt,
        prompt_text=prompt, audio_requested=needs_audio, duration_s=clip.duration_s, request_hash="0" * 64)
    return packet.model_copy(update={"request_hash": packet_hash(packet)})
