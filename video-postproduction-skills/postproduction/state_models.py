"""Canonical postproduction namespace; native files remain projections, not competing registries."""
from typing import Literal

from postproduction.common import Frame, Frozen, Nonempty
from postproduction.environment.observation_models import EnvironmentObservation
from postproduction.intake_models import PostIntake
from postproduction.invalidation_models import Invalidation
from postproduction.quality_models import QualityReport
from postproduction.delivery_models import DeliveryRecord
from postproduction.job_models import ArtifactRef, PostJob
from postproduction.work_models import WorkOrder
from postproduction.timeline_models import PostTimeline


class PostState(Frozen):
    format: Literal["post-state/1"] = "post-state/1"
    revision: Frame = 0
    intake: PostIntake
    intake_history: tuple[PostIntake, ...] = ()
    timelines: tuple[PostTimeline, ...]
    timeline_history: tuple[PostTimeline, ...] = ()
    orders: tuple[WorkOrder, ...] = ()
    jobs: tuple[PostJob, ...] = ()
    artifacts: tuple[ArtifactRef, ...] = ()
    environment_events: tuple[EnvironmentObservation, ...] = ()
    invalidations: tuple[Invalidation, ...] = ()
    reviews: tuple[QualityReport, ...] = ()
    deliveries: tuple[DeliveryRecord, ...] = ()
    notes: tuple[Nonempty, ...] = ()
    observed_input_issues: tuple[Nonempty, ...] = ()
