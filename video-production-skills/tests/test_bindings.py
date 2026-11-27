"""Final packets bind exact files, scope, role and source revisions."""
import pytest
from production.models import Binding, ContractError, Reference, ClipId
from conftest import require


def native(seed):
    asset = seed.batch.clips[0].assets[0]
    return Binding(pin=asset, role="asset", modality="image", imports=("identity",), native_asset_id="local-fixture-asset", native_reference_id="local-fixture-ref", ready=True)


def prepare(seed, capability, authority, tmp_path, binding=None):
    return require("bindings", "prepare_request")(seed, "C1", capability, authority, (binding or native(seed),), tmp_path)


def test_bound_request_when_inputs_ready(seed, capability, authority, tmp_path):
    # Given: explicit local capability, approval and ready native receipt.
    # When: preparing only (no remote call).
    request = prepare(seed, capability, authority, tmp_path)
    # Then: packet pins identity and prompt, not a fake generated result.
    assert request.bindings[0].pin == seed.batch.clips[0].assets[0]
    assert request.prompt_text == "Fictional person crosses the empty yard."


@pytest.mark.parametrize("change,code", [
    ({"ready": False}, "ready"),
    ({"role": "invented"}, "role"),
    ({"modality": "invented"}, "modality"),
    ({"source_clip": ClipId("C2")}, "binding"),
])
def test_reject_binding_when_native_contract_wrong(seed, capability, authority, tmp_path, change, code):
    # Given: a claimed receipt inconsistent with the request contract.
    binding = native(seed).model_copy(update=change)
    # When / Then: prepare fails closed.
    with pytest.raises(ContractError, match=code):
        prepare(seed, capability, authority, tmp_path, binding)


def test_reference_limit_when_required_count_exceeds_limit(seed, capability, authority, tmp_path):
    # Given: provider accepts zero refs but identity is mandatory.
    cap = capability.model_copy(update={"max_references": 0})
    # When / Then: reference is not silently dropped.
    with pytest.raises(ContractError, match="limit"):
        prepare(seed, cap, authority, tmp_path)


def test_transfer_when_asset_hash_not_authorized(seed, capability, authority, tmp_path):
    # Given: existence of local identity does not authorize transmission.
    approval = authority.model_copy(update={"allowed_hashes": ()})
    # When / Then: upload plan is blocked.
    with pytest.raises(ContractError, match="authority"):
        prepare(seed, capability, approval, tmp_path)


def test_missing_video_role_when_required_predecessor(seed, capability, authority, tmp_path):
    # Given: predecessor reference is required but not accepted.
    ref = Reference(source_clip=ClipId("C2"), role="state", modality="video", imports=("pose",))
    clip = seed.batch.clips[0].model_copy(update={"references": (ref,)})
    state = seed.model_copy(update={"batch": seed.batch.model_copy(update={"clips": (clip, *seed.batch.clips[1:])})})
    # When / Then: no image/text substitution.
    with pytest.raises(ContractError, match="dependency"):
        prepare(state, capability, authority, tmp_path)


def test_stale_file_when_bytes_changed(seed, capability, authority, tmp_path):
    # Given: manifest points to a now-changed source.
    (tmp_path / seed.batch.clips[0].assets[0].path).write_text("changed")
    # When / Then: hash verification catches stale bytes.
    with pytest.raises(ContractError, match="hash"):
        prepare(seed, capability, authority, tmp_path)


@pytest.mark.parametrize("path", ["../escape", "/etc/passwd"])
def test_unsafe_path_when_pin_escapes_project(seed, capability, authority, tmp_path, path):
    # Given: malicious relative or absolute source path.
    asset = seed.batch.clips[0].assets[0].model_copy(update={"path": path})
    binding = native(seed).model_copy(update={"pin": asset})
    clip = seed.batch.clips[0].model_copy(update={"assets": (asset,)})
    state = seed.model_copy(update={"batch": seed.batch.model_copy(update={"clips": (clip, *seed.batch.clips[1:])})})
    # When / Then: data outside the owned root is never read.
    from conftest import configurations
    approval = authority.model_copy(update={"configurations":configurations(state,capability)})
    with pytest.raises(ContractError, match="path"):
        prepare(state, capability, approval, tmp_path, binding)


def test_paid_alternative_when_unlimited_not_available(seed, capability, authority, tmp_path):
    # Given: composer showed credit cost or purchase screen.
    cap = capability.model_copy(update={"observed_mode": "purchase"})
    # When / Then: approved unlimited is not replaced with credits.
    with pytest.raises(ContractError, match="mode"):
        prepare(seed, cap, authority, tmp_path)


def test_multiple_history_sources_when_same_clip_consumes_both(seed, capability, authority, tmp_path):
    # Given: C3 consumes distinct roles from C1 and C2, excluding repeated action/dialogue.
    from test_revisions import selection
    refs = tuple(Reference(source_clip=ClipId(f"C{i}"), role="state", modality="video", imports=("identity",) if i == 1 else ("pose",), excludes=("prior_dialogue", "prior_action")) for i in (1,2))
    third = seed.batch.clips[2].model_copy(update={"references": refs})
    state = seed.model_copy(update={"batch": seed.batch.model_copy(update={"clips": (*seed.batch.clips[:2], third)})})
    sources = tuple(selection(state, tmp_path, f"C{i}") for i in (1,2))
    state = state.model_copy(update={"selections": sources})
    direct = native(seed)
    bindings = (direct, *tuple(Binding(pin=s.take.asset, source_clip=s.take.clip_id, source_range=s.take.source_range, range_revision=s.take.range_revision, acceptance_revision=s.acceptance_revision, role=r.role, modality=r.modality, imports=r.imports, excludes=r.excludes, native_asset_id=f"fixture-{i}", native_reference_id=f"fixture-ref-{i}", ready=True) for i,(s,r) in enumerate(zip(sources,refs))))
    from conftest import configurations
    approval = authority.model_copy(update={"allowed_hashes": (*authority.allowed_hashes, *(s.take.asset.sha256 for s in sources)), "configurations":configurations(state,capability)})
    # When: preparing the third clip from both accepted histories.
    packet = require("bindings", "prepare_request")(state,"C3",capability,approval,bindings,tmp_path)
    # Then: neither non-adjacent identity nor current exit state is dropped.
    assert tuple(b.source_clip for b in packet.bindings) == (None,"C1","C2")
    assert packet.bindings[1].excludes == ("prior_dialogue", "prior_action")


@pytest.mark.parametrize("unsupported", ["video", "state"])
def test_supported_predecessor_when_video_input_unavailable(seed,capability,authority,tmp_path,unsupported):
    # Given: the predecessor IS accepted and every other binding is ready.
    from conftest import configurations
    from test_revisions import selection
    ref=Reference(source_clip=ClipId("C2"),role="state",modality="video",imports=("pose",))
    clip=seed.batch.clips[0].model_copy(update={"references":(ref,)})
    state=seed.model_copy(update={"batch":seed.batch.model_copy(update={"clips":(clip,*seed.batch.clips[1:])})})
    source=selection(state,tmp_path,"C2")
    state=state.model_copy(update={"selections":(source,)})
    binding=Binding(pin=source.take.asset,source_clip=ref.source_clip,source_range=source.take.source_range,range_revision=source.take.range_revision,acceptance_revision=source.acceptance_revision,role="state",modality="video",imports=ref.imports,native_asset_id="fixture-source",native_reference_id="fixture-source-ref",ready=True)
    cap=capability.model_copy(update={"modalities":("image","audio")} if unsupported == "video" else {"roles":("asset",)})
    auth=authority.model_copy(update={"configurations":configurations(state,cap),"allowed_hashes":(*authority.allowed_hashes,source.take.asset.sha256)})
    # When / Then: failure reaches native support checks, not the missing-dependency gate.
    with pytest.raises(ContractError,match="modality|role"):
        require("bindings","prepare_request")(state,"C1",cap,auth,(native(state),binding),tmp_path)


def test_required_binding_when_namespaced_keys_would_collide(seed,capability,authority,tmp_path):
    # Given: two distinct source/role identities that collide when joined with ':'.
    from conftest import configurations
    from test_revisions import selection
    source_id=ClipId("C1:state")
    second=seed.batch.clips[1].model_copy(update={"id":source_id})
    refs=(Reference(source_clip=ClipId("C1"),role="state:image",modality="video",imports=("pose",)),Reference(source_clip=source_id,role="image",modality="video",imports=("pose",)))
    third=seed.batch.clips[2].model_copy(update={"references":refs})
    joins=(seed.batch.joins[0].model_copy(update={"after":source_id}),seed.batch.joins[1].model_copy(update={"before":source_id}))
    batch=seed.batch.model_copy(update={"clips":(seed.batch.clips[0],second,third),"edit_order":(ClipId("C1"),source_id,ClipId("C3")),"joins":joins})
    state=seed.model_copy(update={"batch":batch})
    a,b=selection(seed,tmp_path),selection(seed,tmp_path,"C2")
    fp=require("contracts","fingerprint")(state,source_id)
    b=b.model_copy(update={"take":b.take.model_copy(update={"clip_id":source_id,"fingerprint":fp}),"reviewed_fingerprint":fp})
    state=state.model_copy(update={"selections":(a,b)})
    cap=capability.model_copy(update={"roles":("asset","state:image","image")})
    auth=authority.model_copy(update={"clips":tuple(c.id for c in state.batch.clips),"configurations":configurations(state,cap),"allowed_hashes":(*authority.allowed_hashes,a.take.asset.sha256,b.take.asset.sha256)})
    only_first=Binding(pin=a.take.asset,source_clip=refs[0].source_clip,source_range=a.take.source_range,range_revision=a.take.range_revision,acceptance_revision=a.acceptance_revision,role=refs[0].role,modality=refs[0].modality,imports=refs[0].imports,native_asset_id="fixture-first",native_reference_id="fixture-first-ref",ready=True)
    # When / Then: first reference cannot count as the second missing required binding.
    with pytest.raises(ContractError,match="binding"):
        require("bindings","prepare_request")(state,"C3",cap,auth,(native(state),only_first),tmp_path)
