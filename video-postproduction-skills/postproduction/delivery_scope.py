"""Receiver/current-final-review/rights/font/source preflight before any bundle directory is written."""
from pathlib import Path

from postproduction.artifact_graph import artifact_union
from postproduction.backends.effect_models import EffectPlan
from postproduction.backends.text_models import TextRecipe
from postproduction.delivery_models import DeliveryContract
from postproduction.delivery_attribution import collect_attribution
from postproduction.errors import ContractError
from postproduction.files import read_model, verified_file
from postproduction.job_models import ArtifactRef
from postproduction.quality import evaluate_submission
from postproduction.quality_models import QualityReport
from postproduction.state_models import PostState
from postproduction.style_models import ExistingFont, StyleRecipe


def required_fonts(state: PostState, contract: DeliveryContract, root: Path) -> tuple[ExistingFont, ...]:
    result: list[ExistingFont] = []
    for artifact in artifact_union(state,(contract.artifact_id,*contract.variants)):
        job = next(j for j in state.jobs if j.id==artifact.job_id)
        if job.packet.order.backend.value!="effectcraft":
            continue
        plan = EffectPlan.model_validate_json(job.packet.payload)
        if isinstance(plan.recipe,TextRecipe):
            font = read_model(root,plan.recipe.style,StyleRecipe).font
            if font not in result:
                result.append(font)
    return tuple(result)


def preflight(state: PostState, contract: DeliveryContract, project: Path) -> tuple[ArtifactRef,QualityReport]:
    artifact = next((a for a in state.artifacts if a.id==contract.artifact_id),None)
    report = next((r for r in reversed(state.reviews) if r.submission.artifact_id==contract.artifact_id),None)
    if artifact is None or report is None or report.submission.receiver!=contract.receiver:
        raise ContractError("delivery", "actual known reviewed master/exact authorized receiver required")
    current = evaluate_submission(state,report.submission,project)
    if not current.scope_passed:
        raise ContractError("delivery", "current full master/coverage/fix/playback/listening/rights gates are not closed")
    if contract.mode=="reported_release" and (not artifact.adopted or current.acceptance_kind!="reported_not_authenticated"):
        raise ContractError("delivery", "technical fixture cannot become formal reported final adoption")
    origin = "reported" if contract.mode=="reported_release" else "fixture"
    if contract.rights.status!="reported_allowed" or contract.rights.origin!=origin:
        raise ContractError("rights", "current receiver/source access permission is unknown/denied/wrong scope")
    _ = verified_file(project.parent,contract.rights.evidence)
    _ = collect_attribution(state,contract,project.parent)
    stem_ids = {s.id for s in state.intake.request.stems}
    if set(contract.required_stems)-stem_ids:
        raise ContractError("stem", "required real separate stem not supplied; never manufacture DX/MX/FX")
    if contract.kind=="editable":
        for font in required_fonts(state,contract,project.parent):
            permission = next((p for p in contract.font_permissions if p.font_sha256==font.sha256),None)
            if permission is None or not (permission.redistribute or permission.receiver_present):
                raise ContractError("font", "editable project requires exact font/receiver dependency or explicit redistribution permission")
            _ = verified_file(project.parent,permission.evidence)
    return artifact,current
