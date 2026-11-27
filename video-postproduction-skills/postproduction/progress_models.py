"""Distinct denominators; historical process success is not a current master or final human review."""
from postproduction.common import Frame, Frozen, Nonempty


class Completion(Frozen):
    complete: Frame
    total: Frame


class BranchProgress(Frozen):
    branch: Nonempty
    work: Completion
    coverage: Completion
    fixes: Completion
    final_qa: Completion
    technical_fixture_qa: Completion
    historical_succeeded: Frame
    formal_deliveries: Frame
    technical_fixture_deliveries: Frame


class ProjectProgress(Frozen):
    revision: Frame
    branches: tuple[BranchProgress, ...]
