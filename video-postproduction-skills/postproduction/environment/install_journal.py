"""Host/tool technical lease journal; canonical project adoption remains the postproduction namespace."""
import os
from pathlib import Path
import tempfile

from pydantic import ValidationError

from postproduction.environment.install_models import InstallJournal
from postproduction.environment.models import EnvStatus
from postproduction.errors import ContractError


def reconcile_required(path: Path) -> None:
    """In-flight/unknown operations cannot be blindly repeated under the same or a new plan."""
    if not path.exists():
        return
    try:
        previous = InstallJournal.model_validate_json(path.read_bytes())
    except (OSError,ValidationError) as exc:
        raise ContractError("reconcile", "unreadable prior installer state requires reconciliation") from exc
    if previous.phase not in {EnvStatus.FAILED,EnvStatus.DECLINED}:
        raise ContractError("reconcile", "known prior work requires inspection/reconciliation, not replay")


def write_journal(path: Path, value: InstallJournal) -> None:
    """Publish/fsync technical facts before invoking mutable project diagnostics."""
    temp: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="w",dir=path.parent,prefix=".install-journal-",
                                         delete=False,encoding="utf-8") as stream:
            temp = Path(stream.name)
            _ = stream.write(value.model_dump_json())
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp,path)
        directory = os.open(path.parent,os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if temp is not None and temp.exists():
            temp.unlink()
