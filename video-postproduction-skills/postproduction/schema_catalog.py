"""One public input schema catalog generated from actual strict runtime boundary models."""
from pydantic import BaseModel

from postproduction.adoption_models import IntakeRevision
from postproduction.caption_models import SourceCaption
from postproduction.delivery_models import DeliveryContract
from postproduction.edit_models import DeliveryProfile
from postproduction.environment.consent_models import InstallAuthority, InstallationPlan
from postproduction.environment.models import HostSnapshot
from postproduction.finishing_models import FinishingRecipe
from postproduction.intake_models import IntakeRequest
from postproduction.quality_models import QualitySubmission
from postproduction.state_models import PostState
from postproduction.style_models import StyleRecipe
from postproduction.timeline_models import EditProposal
from postproduction.work_models import WorkOrder

SCHEMAS: dict[str,type[BaseModel]] = {
    "post-state.schema.json":PostState,"intake-request.schema.json":IntakeRequest,
    "edit-proposal.schema.json":EditProposal,"work-order.schema.json":WorkOrder,
    "installation-plan.schema.json":InstallationPlan,"install-authority.schema.json":InstallAuthority,
    "host-snapshot.schema.json":HostSnapshot,"style-recipe.schema.json":StyleRecipe,
    "caption-source.schema.json":SourceCaption,"quality-submission.schema.json":QualitySubmission,
    "delivery-contract.schema.json":DeliveryContract,"intake-revision.schema.json":IntakeRevision,
    "finishing-recipe.schema.json":FinishingRecipe,"delivery-profile.schema.json":DeliveryProfile,
}
