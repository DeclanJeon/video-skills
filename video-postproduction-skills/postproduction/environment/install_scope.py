"""Validate physical driver results rather than trusting successful method/exit status."""
import os
from pathlib import Path


def contained_regular_file(path: Path, root: Path) -> bool:
    """A receipt must point to actual nonsymlink bytes inside the exact approved scope."""
    if not path.absolute().is_relative_to(root.absolute()):
        return False
    if any(parent.is_symlink() for parent in (path,*path.parents)):
        return False
    return path.is_file() and path.resolve().is_relative_to(root.resolve())


def installed_files_valid(files: tuple[Path, ...], root: Path) -> bool:
    """The first installed file is the executable, not an empty claim or a missing placeholder."""
    return bool(files and all(contained_regular_file(p,root) for p in files) and os.access(files[0],os.X_OK))
