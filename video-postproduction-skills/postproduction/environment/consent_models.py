"""Exact installation scope and external question/response records; no generic approval flag."""
from decimal import Decimal
from pathlib import PurePosixPath, PureWindowsPath
from typing import Annotated, Literal, Self
from urllib.parse import urlsplit

from pydantic import AwareDatetime, Field, model_validator

from postproduction.common import Digest, Frame, Frozen, Nonempty, Pin, Positive
from postproduction.environment.models import System, Tool
from postproduction.errors import ContractError


class DependencyPlan(Frozen):
    name: Nonempty
    version: Nonempty
    write_paths: tuple[Nonempty, ...]


class InstallationPlan(Frozen):
    id: Nonempty
    host_id: Digest
    host_fingerprint: Digest
    tool: Tool
    version: Nonempty
    system: System
    architecture: Nonempty
    source_url: Nonempty
    source_sha256: Digest
    source_evidence: Pin
    source_evidence_kind: Literal["official_checksum","official_signature","self_hash_unverified","contract_fixture"]
    dependencies: tuple[DependencyPlan, ...]
    write_paths: tuple[Nonempty, ...]
    permissions: tuple[Literal["user","admin","reboot"], ...]
    network_hosts: tuple[Nonempty, ...]
    estimated_download_bytes: Frame | None
    estimated_disk_bytes: Frame | None
    cost: Annotated[Decimal,Field(ge=0)] | None
    currency: Literal["USD","KRW","EUR"]
    license_steps: tuple[Nonempty, ...]
    existing_change: Literal["new","repair","upgrade"]
    rollback: tuple[Nonempty, ...]
    allow_unverified_publisher: bool = False
    max_download_bytes: Positive = 1073741824
    max_unpacked_bytes: Positive = 4294967296

    @model_validator(mode="after")
    def bounded(self) -> Self:
        source = urlsplit(self.source_url)
        if (source.scheme != "https" or source.hostname is None
            or source.hostname not in self.network_hosts or source.username or source.password
            or source.query or source.fragment):
            raise ContractError("install-plan", "explicit HTTPS origin required; no credentials/query/hidden redirects")
        if not self.write_paths or not self.permissions or not self.rollback:
            raise ContractError("install-plan", "write/permission/rollback scope cannot be empty")
        paths = (*self.write_paths,*(p for d in self.dependencies for p in d.write_paths))
        if any(not (PurePosixPath(p).is_absolute() or PureWindowsPath(p).is_absolute()) for p in paths):
            raise ContractError("install-plan", "write locations must be exact absolute paths")
        if len({d.name for d in self.dependencies}) != len(self.dependencies):
            raise ContractError("install-plan", "dependency versions must be unambiguous")
        return self


class QuestionDraft(Frozen):
    id: Nonempty
    host_id: Digest
    plan_digest: Digest
    text: Nonempty


type ConsentChannel = Literal["operator_message","interactive_tty","contract_fixture"]


class AskedQuestion(Frozen):
    question: QuestionDraft
    message_ref: Nonempty
    channel: ConsentChannel
    asked_at: AwareDatetime


class InstallConsent(Frozen):
    question_id: Nonempty
    question_ref: Nonempty
    host_id: Digest
    plan_digest: Digest
    answer: Literal["approve","decline"]
    actor: Nonempty
    response_ref: Nonempty
    response_text: Nonempty
    channel: ConsentChannel
    answered_at: AwareDatetime


class InstallAuthority(Frozen):
    install_plan: InstallationPlan | None = None
    question: AskedQuestion | None = None
    consent: InstallConsent | None = None
