"""Receiver-facing supplied credits from actual main/variant consumption; no legal-issuer or on-screen compliance fiction."""
from pathlib import Path
from typing import Literal

from postproduction.artifact_graph import artifact_union
from postproduction.backends.effect_models import EffectPlan
from postproduction.backends.text_models import TextRecipe
from postproduction.common import Frozen, Nonempty, Pin
from postproduction.delivery_models import DeliveryContract
from postproduction.environment.models import Tool
from postproduction.errors import ContractError
from postproduction.files import read_model, verified_file
from postproduction.state_models import PostState
from postproduction.style_models import StyleRecipe


class AttributionRecord(Frozen):
    artifact_id: Nonempty
    style: Pin
    credits: tuple[Nonempty, ...]
    presentation: Literal["receiver_record"] = "receiver_record"
    reference_use: Literal["concept_only","licensed_pixels"]
    references: tuple[Pin, ...]
    license_evidence: tuple[Pin, ...]


class AttributionManifest(Frozen):
    format: Literal["post-attributions/1"] = "post-attributions/1"
    receiver: Nonempty
    issuer_authenticated: Literal[False] = False
    records: tuple[AttributionRecord, ...]


def attribution_records(state: PostState, artifact_ids: tuple[str, ...], root: Path) -> tuple[AttributionRecord, ...]:
    records: list[AttributionRecord] = []
    for artifact in artifact_union(state,artifact_ids):
        producer = next(j for j in state.jobs if j.id==artifact.job_id)
        if producer.packet.order.backend!=Tool.EFFECTCRAFT:
            continue
        plan = EffectPlan.model_validate_json(producer.packet.payload)
        if not isinstance(plan.recipe,TextRecipe):
            continue
        style = read_model(root,plan.recipe.style,StyleRecipe)
        if style.attribution_presentation=="on_screen":
            raise ContractError("attribution","on-screen credit requires an explicitly verified presentation route; receiver metadata is not fulfillment")
        if not style.attribution:
            continue
        evidence = (style.font.license_evidence,*((style.asset_license_evidence,) if style.asset_license_evidence is not None else ()))
        for pin in (*evidence,*style.references):
            _ = verified_file(root,pin)
        records.append(AttributionRecord(artifact_id=artifact.id,style=plan.recipe.style,credits=style.attribution,
            reference_use=style.reference_use,references=style.references,license_evidence=evidence))
    return tuple(records)


def collect_attribution(state: PostState, contract: DeliveryContract, root: Path) -> AttributionManifest:
    return AttributionManifest(receiver=contract.receiver,
        records=attribution_records(state,(contract.artifact_id,*contract.variants),root))
