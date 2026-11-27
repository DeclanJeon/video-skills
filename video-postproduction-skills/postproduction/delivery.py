"""Actual local scoped bundle with current QA/provenance/checksums. No automatic cloud upload or publication."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from postproduction.artifact_graph import artifact_closure
from postproduction.delivery_io import BundleWriter
from postproduction.delivery_attribution import collect_attribution
from postproduction.delivery_models import DeliveryBundle, DeliveryContract
from postproduction.job_models import ArtifactRef
from postproduction.editable import copy_editable
from postproduction.delivery_scope import preflight
from postproduction.errors import ContractError
from postproduction.files import confined_path
from postproduction.materialization import verify_artifact_current
from postproduction.state_models import PostState


def lineage_record(state: PostState, id: str) -> bytes:
    closure = artifact_closure(state,id)
    values = [{"artifact_id":a.id,"sha256":a.pin.sha256,"source_id":a.pin.id,"version":a.pin.version,
               "job":a.job_id,"technical_proof_sha256":None if a.proof is None else a.proof.sha256} for a in closure]
    return json.dumps(values,indent=2).encode()


def build_delivery(state: PostState, contract: DeliveryContract, project: Path) -> DeliveryBundle:
    """Technical fixture remains labeled; formal mode requires current scoped reported final acceptance."""
    project_bytes = project.read_bytes()
    artifact,review = preflight(state,contract,project)
    root = project.parent
    target = confined_path(root,contract.output)
    if target.exists():
        raise ContractError("existing", "known bundle target exists; never overwrite/replay package publication")
    variants: list[ArtifactRef] = []
    for id in contract.variants:
        variant = next((a for a in state.artifacts if a.id==id),None)
        if variant is None or variant.id==artifact.id:
            raise ContractError("variant", "requested distinct actual variant missing")
        verify_artifact_current(state,variant,project)
        _ = preflight(state,contract.model_copy(update={"artifact_id":variant.id}),project)
        variants.append(variant)
    target.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=target.parent,prefix=".owned-delivery-") as temp:
        stage = Path(temp)/"payload"
        stage.mkdir()
        writer = BundleWriter(stage,root,contract)
        files = [writer.copy(artifact.pin,"master/master.mp4")]
        if contract.kind=="editable":
            files.extend(copy_editable(state,writer))
        for variant in variants:
            _,variant_review = preflight(state,contract.model_copy(update={"artifact_id":variant.id}),project)
            stem = f"records/variants/{variant.pin.sha256[:16]}"
            files.append(writer.copy(variant.pin,f"variants/{variant.pin.sha256[:16]}.mp4"))
            files.append(writer.metadata(stem+".qa.json",variant_review.model_dump_json(indent=2).encode()))
            files.append(writer.metadata(stem+".provenance.json",lineage_record(state,variant.id)))
        closure = artifact_closure(state,artifact.id)
        if contract.include_mix:
            mixes = tuple(a for a in closure if a.kind=="audio")
            if len(mixes)!=1:
                raise ContractError("mix", "one exact real native mix is required by this delivery contract")
            files.append(writer.copy(mixes[0].pin,"audio/mix.wav"))
        for id in contract.required_stems:
            stem = next(s for s in state.intake.request.stems if s.id==id)
            files.append(writer.copy(stem.asset,f"audio/stem-{stem.asset.sha256[:16]}.wav"))
        files.append(writer.metadata("records/qa.json",review.model_dump_json(indent=2).encode()))
        files.append(writer.metadata("records/rights.json",contract.rights.model_dump_json(indent=2).encode()))
        files.append(writer.metadata("records/attribution.json",collect_attribution(state,contract,root).model_dump_json(indent=2).encode()))
        files.append(writer.metadata("records/provenance.json",lineage_record(state,artifact.id)))
        manifest = {"id":contract.id,"mode":contract.mode,"formal_release":contract.mode=="reported_release",
                    "receiver":contract.receiver,"artifact_id":artifact.id,"input_fingerprint":artifact.input_fingerprint,
                    "note":"reported semantics/rights are not authenticated human/legal issuer certification; manifest excludes its own hash",
                    "files":[f.model_dump(mode="json") for f in files]}
        data = json.dumps(manifest,indent=2).encode()
        _ = writer.metadata("manifest.json",data)
        _ = preflight(state,contract,project)
        for variant in variants:
            _ = preflight(state,contract.model_copy(update={"artifact_id":variant.id}),project)
        if project.read_bytes()!=project_bytes:
            raise ContractError("conflict", "canonical project changed while packaging; retain owner data and do not publish stale bundle")
        _ = subprocess.run(["mv","--no-clobber","--no-target-directory","--",str(stage),str(target)],
                           capture_output=True,check=True,timeout=30)
        if stage.exists():
            raise ContractError("existing", "another writer published target; owned no-clobber move skipped")
        return DeliveryBundle(id=contract.id,mode=contract.mode,receiver=contract.receiver,path=contract.output,
            artifact_id=artifact.id,input_fingerprint=artifact.input_fingerprint,manifest_sha256=hashlib.sha256(data).hexdigest(),
            files=tuple(files),formal_release=contract.mode=="reported_release",native_relink_verified=contract.kind=="editable")
