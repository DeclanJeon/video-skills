"""Deterministic source/spec/input-schema scope. Output evidence, journals and review reports are not executable source."""
import hashlib
from pathlib import Path

from postproduction.acceptance_models import SourceFile, SourceSnapshot

SOURCE_DIRS = ("postproduction","scripts","tests","schemas","references","examples",
               "docs/design","docs/superpowers/plans")
SUFFIXES = {".py",".md",".json"}


def snapshot(root: Path) -> SourceSnapshot:
    paths = {p for p in root.glob("*.md") if p.is_file()}
    paths.update(p for p in root.glob("*/SKILL.md") if p.is_file())
    paths.update(p for p in (root/"manifest.json",root/"pyproject.toml",
                            root/"docs/acceptance-map.json",root/"docs/operations.md") if p.is_file())
    for directory in SOURCE_DIRS:
        paths.update(p for p in (root/directory).rglob("*") if p.is_file() and p.suffix in SUFFIXES)
    files = tuple(SourceFile(path=p.relative_to(root).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                  for p in sorted(paths))
    return SourceSnapshot(files=files)
