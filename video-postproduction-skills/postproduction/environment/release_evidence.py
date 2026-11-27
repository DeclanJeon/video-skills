"""Validate pinned declared release records; offline records are not crypto issuer authentication."""
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from postproduction.common import Digest, Frozen, Nonempty
from postproduction.environment.consent_models import InstallationPlan
from postproduction.environment.models import Tool
from postproduction.errors import ContractError
from postproduction.files import read_model


class ReleaseEvidence(Frozen):
    tool: Tool
    version: Nonempty
    asset_url: Nonempty
    asset_sha256: Digest
    verification: Literal["official_checksum","self_hash_unverified"]
    source_document_url: Nonempty


def official_repository(tool: Tool) -> str:
    """Repository identities are verified in the installed primary README files."""
    if tool not in {Tool.FILMCRAFT,Tool.EFFECTCRAFT,Tool.SOUNDCRAFT}:
        raise ContractError("publisher", "this release verifier covers only the selected Craft repositories")
    return f"/storytold/{tool.value}/"


def verify_release_evidence(root: Path, plan: InstallationPlan) -> ReleaseEvidence:
    """Match exact declared record and expected repository; never call a self hash publisher proof."""
    if plan.source_evidence_kind == "self_hash_unverified" and not plan.allow_unverified_publisher:
        raise ContractError("publisher", "self-computed hash does not verify publisher; exact risk approval required")
    if plan.source_evidence_kind not in {"official_checksum","self_hash_unverified"}:
        raise ContractError("publisher", "this adapter has no verified detached-signature/fixture publisher route")
    record = read_model(root,plan.source_evidence,ReleaseEvidence)
    source,doc = urlsplit(plan.source_url),urlsplit(record.source_document_url)
    prefix = official_repository(plan.tool)
    if (source.scheme != "https" or source.hostname != "github.com"
        or not source.path.startswith(prefix+"releases/download/")
        or doc.scheme != "https" or doc.hostname != "github.com"
        or not doc.path.startswith(prefix+"releases/")):
        raise ContractError("publisher", "release source/document is not the declared known primary repository")
    if ((record.tool,record.version,record.asset_url,record.asset_sha256,record.verification)
        != (plan.tool,plan.version,plan.source_url,plan.source_sha256,plan.source_evidence_kind)):
        raise ContractError("publisher", "release evidence and exact plan artifact/version/checksum differ")
    return record
