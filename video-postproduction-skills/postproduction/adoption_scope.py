"""Immutable global editing decisions, without re-probing unrelated media merely to do one scoped job."""
import hashlib
from pathlib import Path

import production.models as production_models
from production.models import Handoff

from postproduction.authority import authorize
from postproduction.edit_models import DeliveryProfile, EditAuthority, EditBrief
from postproduction.errors import ContractError
from postproduction.files import read_model, verified_file
from postproduction.intake import load_snapshot
from postproduction.intake_models import PostIntake


def verify_adopted_decisions(intake: PostIntake, root: Path) -> None:
    """Still bind actual schema/snapshot/handoff/brief/profile/authority bytes; omit only unconsumed media decode."""
    req = intake.request
    _ = verified_file(root,req.schema_pin)
    if hashlib.sha256(Path(production_models.__file__).read_bytes()).hexdigest() != req.schema_pin.sha256:
        raise ContractError("schema", "actual production schema changed")
    if (load_snapshot(root,req) != intake.snapshot
        or read_model(root,req.handoff,Handoff) != intake.handoff
        or read_model(root,req.brief,EditBrief) != intake.brief
        or read_model(root,req.profile,DeliveryProfile) != intake.profile
        or read_model(root,req.authority,EditAuthority) != intake.authority):
        raise ContractError("revision", "immutable adopted global edit decision differs from its actual pinned record")
    authorize(intake,root)
