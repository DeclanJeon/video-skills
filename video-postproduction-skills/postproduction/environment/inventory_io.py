"""Bounded local metadata reads; no application commands, downloads or secret environment dumps."""
import hashlib
from pathlib import Path
import subprocess


def command(argv: tuple[str, ...]) -> str | None:
    """Run an explicit local metadata command, treating unavailable probes as unknown."""
    try:
        result = subprocess.run(argv,capture_output=True,text=True,check=True,timeout=10)
    except (OSError,subprocess.CalledProcessError,subprocess.TimeoutExpired):
        return None
    return result.stdout


def text_file(path: Path) -> str | None:
    """Read known system metadata; absence/permission failure is not a negative fact."""
    try:
        return path.read_text()
    except OSError:
        return None


def binary_hash(path: Path) -> str | None:
    """Fingerprint the existing binary rather than modifying/launching it."""
    try:
        with path.open("rb") as stream:
            return hashlib.file_digest(stream,"sha256").hexdigest()
    except OSError:
        return None


def memory_available() -> int | None:
    """Read only available RAM, never process arguments or environment contents."""
    data = text_file(Path("/proc/meminfo"))
    if data is None:
        return None
    for line in data.splitlines():
        if line.startswith("MemAvailable:"):
            try:
                return int(line.split()[1])*1024
            except (ValueError,IndexError):
                return None
    return None
