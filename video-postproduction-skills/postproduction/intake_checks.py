"""Coverage anchors and review-only montage checks, never final-master certification."""
from fractions import Fraction
from pathlib import Path

from production.handoff import selection_hash
from production.models import State
from production.render import RenderManifest, slices

from postproduction.admission import local_pin
from postproduction.errors import ContractError
from postproduction.files import read_model, verified_file
from postproduction.intake_models import PostIntake
from postproduction.media import probe_video


def verify_review(intake: PostIntake, root: Path) -> None:
    """Verify physical review media/lineage without importing it as source footage."""
    proof = intake.handoff.flow.review_render
    manifest = read_model(root,local_pin(proof.manifest),RenderManifest)
    if (proof.selection_hash != selection_hash(intake.snapshot)
        or manifest.selection_hash != proof.selection_hash
        or manifest.artifact != proof.artifact or manifest.sources != slices(intake.snapshot)):
        raise ContractError("flow", "review-only montage has stale or mismatched lineage")
    facts = probe_video(root,local_pin(proof.artifact))
    duration = Fraction(facts.frame_count*facts.rate.den,facts.rate.num)
    expected = sum((Fraction(s.approved_range.length*s.rate.den,s.rate.num) for s in intake.sources),Fraction())
    if abs(duration-expected) > Fraction(facts.rate.den,facts.rate.num):
        raise ContractError("flow", "review montage does not cover the selected sequence")


def verify_anchors(intake: PostIntake, root: Path) -> None:
    """Every optional precision anchor must bind current exact source bytes and reviews."""
    ids = tuple(a.requirement_id for a in intake.request.anchors)
    if len(set(ids)) != len(ids):
        raise ContractError("anchor", "ambiguous duplicate requirement anchors")
    for anchor in intake.request.anchors:
        source = next((s for s in intake.sources if s.source == anchor.source),None)
        selected = next((s for s in intake.handoff.selections if s.take.clip_id == anchor.source.clip_id),None)
        if (source is None or selected is None or anchor.requirement_id not in selected.review.fulfilled
            or anchor.asset_hash != source.asset.sha256 or anchor.range_revision != source.range_revision
            or anchor.acceptance_revision != source.acceptance_revision
            or anchor.source_range.start < source.approved_range.start
            or anchor.source_range.end > source.approved_range.end or not anchor.video_observed):
            raise ContractError("anchor", "anchor is not current and actually observed within its selected source")
        requirement = next(r for r in intake.snapshot.approved_coverage if r.id == anchor.requirement_id)
        if requirement.modality == "audio" and not anchor.audio_observed:
            raise ContractError("anchor", "speech/audio anchor needs an actual listening report")
        _ = verified_file(root,anchor.evidence)


def snapshot_namespace_is_separate(state: State, root: Path, snapshot_path: Path, ledger: Path | None) -> None:
    """A mutable writer ledger cannot serve as its own immutable source snapshot."""
    if ledger is not None and ledger.resolve() in {snapshot_path.resolve(),(root/state.coverage_source.path).resolve()}:
        raise ContractError("snapshot", "mutable ledger must not be an immutable source/coverage pin")
