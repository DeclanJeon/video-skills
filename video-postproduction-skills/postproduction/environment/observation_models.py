"""Install-run provenance and narrow event facts, explicitly not creative/media readiness or issuer authentication."""
from typing import Literal

from postproduction.common import Digest, Frozen, Nonempty, Positive
from postproduction.environment.install_models import InstallEvent
from postproduction.environment.models import Tool


class InstallContext(Frozen):
    id: Nonempty
    host_id: Digest
    tool: Tool
    plan_digest: Digest
    evidence_kind: Literal["contract_fixture","vendor_installation"]


class EnvironmentObservation(Frozen):
    context: InstallContext
    sequence: Positive
    event: InstallEvent
    real_media_ready: Literal[False] = False

    @property
    def evidence_kind(self) -> Literal["contract_fixture","vendor_installation"]:
        """Public provenance projection; context remains the single immutable serialized value."""
        return self.context.evidence_kind
