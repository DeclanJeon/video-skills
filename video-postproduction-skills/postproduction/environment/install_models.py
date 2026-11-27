"""Install facts remain distinct from smoke readiness and real-media authorization."""
from typing import Literal

from postproduction.common import Digest, Frozen, Nonempty
from postproduction.environment.models import EnvStatus, Tool


class SmokeResult(Frozen):
    passed: bool
    evidence: Nonempty
    network_denied: bool


class InstallEvent(Frozen):
    phase: EnvStatus
    detail: Nonempty
    installed: bool | None


class InstallJournal(Frozen):
    host_id: Digest
    tool: Tool
    plan_digest: Digest
    phase: EnvStatus
    installed: bool | None
    detail: Nonempty


class InstallReceipt(Frozen):
    host_id: Digest
    tool: Tool
    plan_digest: Digest
    status: EnvStatus
    installed: bool | None
    evidence_kind: Literal["contract_fixture","vendor_installation"]
    events: tuple[InstallEvent, ...] = ()
    smoke: SmokeResult | None = None
    real_media_ready: Literal[False] = False
