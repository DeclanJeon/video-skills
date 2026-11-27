"""Match current exact edit inputs; no permission is inferred from tool capability."""
from pathlib import Path

from postproduction.errors import ContractError
from postproduction.files import verified_file
from postproduction.intake_models import PostIntake


def authorize(intake: PostIntake, root: Path) -> None:
    """Validate the declared grant and its physical evidence, not issuer authenticity."""
    authority, request = intake.authority, intake.request
    expected = (request.project_id, intake.handoff.receiver, request.handoff.sha256,
                intake.snapshot.batch.scope_revision, request.brief.sha256, request.profile.sha256)
    actual = (authority.project_id, authority.receiver, authority.handoff_digest,
              authority.scope_revision, authority.brief_digest, authority.profile_digest)
    if actual != expected or intake.brief.project_id != request.project_id:
        raise ContractError("authority", "grant is not bound to these exact project/edit inputs")
    _ = verified_file(root, authority.evidence)
    extras = (*request.upstream,*(p for stem in request.stems for p in (stem.asset,stem.independence_evidence)))
    if any(pin not in authority.assets for pin in extras):
        raise ContractError("authority", "additional supplied media/provenance is not in the exact edit asset grant")
