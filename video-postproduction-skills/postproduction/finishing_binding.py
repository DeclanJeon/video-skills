"""Native edit-content equivalence is stronger than producer-currentness and weaker than branch-name equality."""
from postproduction.backends.film_models import FilmPlan
from postproduction.backends.sound_models import SoundPlan
from postproduction.common import ClockRate, SourceRange
from postproduction.clock import map_frame
from postproduction.environment.models import Tool
from postproduction.errors import ContractError
from postproduction.intake_models import SourceRef
from postproduction.job_models import ArtifactRef, PostJob
from postproduction.state_models import PostState
from postproduction.timeline_models import PostTimeline
from postproduction.work_models import Domain


def edit_content(timeline: PostTimeline, refs: tuple[SourceRef, ...]) -> tuple[tuple[SourceRef,SourceRange,SourceRange], ...]:
    """Source identities/order, reviewed ranges and exact destination ticks, not incidental cut labels."""
    return tuple((s.source,s.source_range,s.timeline_range) for s in timeline.segments if s.source in refs)


def verify_picture_binding(state: PostState, picture: ArtifactRef, timeline: PostTimeline) -> None:
    producer = next((j for j in state.jobs if j.id==picture.job_id),None)
    if producer is None or (producer.packet.order.backend,producer.packet.order.domain)!=(Tool.FILMCRAFT,Domain.PICTURE):
        raise ContractError("binding","qualified actual native picture producer required")
    plan = FilmPlan.model_validate_json(producer.packet.payload)
    refs = tuple(s.source for s in state.intake.sources)
    if (plan.profile!=state.intake.profile or plan.timeline.clock!=timeline.clock
        or edit_content(plan.timeline,refs)!=edit_content(timeline,refs)):
        raise ContractError("binding","picture edit content/order/ranges/timing differs from destination branch")


def verify_mix_binding(state: PostState, mix: ArtifactRef, picture: ArtifactRef, total_frames: int) -> None:
    producer = next((j for j in state.jobs if j.id==mix.job_id),None)
    if producer is None or (producer.packet.order.backend,producer.packet.order.domain)!=(Tool.SOUNDCRAFT,Domain.SOUND):
        raise ContractError("binding","qualified actual native mix producer required")
    recipe = SoundPlan.model_validate_json(producer.packet.payload).recipe
    profile = state.intake.profile
    expected = map_frame(total_frames,profile.fps,ClockRate(num=profile.sample_rate,den=1),rounding="exact")
    if (recipe.picture!=picture.pin or recipe.picture_fps!=profile.fps
        or (recipe.sample_rate,recipe.channels,recipe.sample_count)!=(profile.sample_rate,profile.channels,expected)):
        raise ContractError("binding","mix picture lock/sample clock/layout does not match selected finishing picture")


def verify_plate_binding(state: PostState, producer: PostJob, timeline: PostTimeline) -> None:
    original = next((t for t in state.timelines if t.branch==producer.packet.order.branch),None)
    refs = producer.packet.order.source_refs
    if original is None or original.clock!=timeline.clock or edit_content(original,refs)!=edit_content(timeline,refs):
        raise ContractError("binding","plate/caption source-to-master map differs from destination branch")
