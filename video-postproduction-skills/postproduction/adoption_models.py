"""Explicit actual source/edit re-adoption request, not a mutable source snapshot overwrite."""
from postproduction.common import Digest, Frozen, Pin
from postproduction.intake_models import PostIntake
from postproduction.timeline_models import PostTimeline


class IntakeRevision(Frozen):
    previous_intake_digest: Digest
    intake: PostIntake
    timelines: tuple[PostTimeline, ...]
    evidence: Pin
