"""Local QA4 replay guard. Never calls a provider or grants authority itself."""
from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Review:
    index_exit: int
    batch_exit: int
    verdict: str
    digest: str


@dataclass(frozen=True)
class Approval:
    digest: str
    currency: str
    limit: Decimal | None = None


def fingerprint(project: Path, files: Iterable[str], settings: dict) -> str:
    """Bind reviewed project-local files and approved submission settings."""
    root = project.resolve(strict=True)
    hashes: dict[str, str] = {}
    for name in files:
        if Path(name).is_absolute():
            raise ValueError('use project-relative snapshot paths')
        path = (root / name).resolve(strict=True)
        relative = path.relative_to(root).as_posix()
        if not path.is_file() or relative in hashes:
            raise ValueError(f'not a distinct project file: {name}')
        hashes[relative] = sha256(path.read_bytes()).hexdigest()
    if not hashes or not all(isinstance(settings.get(key), str) and settings[key].strip()
                             for key in ('model', 'endpoint')):
        raise ValueError('review snapshot needs files, model and endpoint')
    payload = json.dumps({'files': hashes, 'settings': settings}, sort_keys=True,
                         separators=(',', ':'), allow_nan=False).encode('utf-8')
    return sha256(payload).hexdigest()


def authorize(project: Path, files: Iterable[str], settings: dict, review: Review,
              approval: Approval | None, currency: str, total_cost: Decimal) -> list[str]:
    """Return blockers; callers supply trusted evidence and total quoted cost.

    An empty list does not prove authorship, user identity or provider authorization.
    """
    blockers = []
    if type(review.index_exit) is not int or review.index_exit != 0:
        blockers.append('index')
    if type(review.batch_exit) is not int or review.batch_exit != 0:
        blockers.append('batch')
    if review.verdict != 'PASS':
        blockers.append('review')
    try:
        digest = fingerprint(project, files, settings)
    except (OSError, TypeError, ValueError):
        digest = None
    if digest is None or digest != review.digest:
        blockers.append('snapshot')
    if approval is None or approval.digest != review.digest:
        blockers.append('approval')
    elif (not currency or currency != approval.currency or not total_cost.is_finite()
          or total_cost < 0 or (approval.limit is not None and
                                (not approval.limit.is_finite() or total_cost > approval.limit))):
        blockers.append('budget')
    return blockers
