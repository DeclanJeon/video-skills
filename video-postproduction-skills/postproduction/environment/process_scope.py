"""Readonly same-user /proc command scope inspection. Never kill, attach, lock-steal or touch another app."""
import os
from pathlib import Path
import sys
from typing import Literal


def owned_process_state(paths: tuple[Path, ...]) -> Literal["not_running","running","unknown"]:
    """Portable install children include exact target/cache argv; hidden same-user metadata stays unknown."""
    if sys.platform != "linux":
        return "unknown"
    roots = tuple(str(p.absolute()).encode() for p in paths)
    try:
        entries = tuple(Path("/proc").iterdir())
    except OSError:
        return "unknown"
    unknown = False
    for entry in entries:
        if not entry.name.isdigit() or int(entry.name) == os.getpid():
            continue
        try:
            if entry.stat().st_uid != os.getuid():
                continue
            args = (entry/"cmdline").read_bytes().split(b"\0")
            if any(arg == root or arg.startswith(root+b"/") for arg in args for root in roots):
                return "running"
        except FileNotFoundError:  # Process can terminate between enumeration and readonly inspection.
            continue
        except OSError:
            unknown = True
    return "unknown" if unknown else "not_running"
