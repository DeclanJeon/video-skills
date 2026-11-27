"""Actual materialized artifact producer closure, not every unrelated branch/artifact in the project."""
from postproduction.errors import ContractError
from postproduction.job_models import ArtifactRef
from postproduction.state_models import PostState


def artifact_closure(state: PostState, artifact_id: str) -> tuple[ArtifactRef, ...]:
    pending = [artifact_id]
    found: list[ArtifactRef] = []
    while pending:
        id = pending.pop()
        if any(a.id==id for a in found):
            continue
        artifact = next((a for a in state.artifacts if a.id==id),None)
        job = next((j for j in state.jobs if artifact is not None and j.id==artifact.job_id),None)
        if artifact is None or job is None:
            raise ContractError("artifact", "known materialized artifact/producer missing")
        found.append(artifact)
        pending.extend(a.id for p in job.packet.order.dependencies for a in state.artifacts if a.pin==p)
    return tuple(found)


def artifact_union(state: PostState, artifact_ids: tuple[str, ...]) -> tuple[ArtifactRef, ...]:
    """Distinct actual producers for a main plus every requested variant, never main-only editable/font scope."""
    found: dict[str,ArtifactRef] = {}
    for id in artifact_ids:
        for artifact in artifact_closure(state,id):
            found[artifact.id] = artifact
    return tuple(found.values())
