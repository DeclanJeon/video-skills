"""Current-host metadata inspection without executing Craft/apps or claiming GPU readiness."""
from datetime import UTC, datetime
import hashlib
from pathlib import Path
import platform
import shutil

from postproduction.environment.catalog import tool_spec
from postproduction.environment.discovery import inspect_program
from postproduction.environment.inventory_io import command, memory_available, text_file
from postproduction.environment.models import HostSnapshot, InstalledPackage, System, ToolRequirement
from postproduction.errors import ContractError


def installed_packages(requirements: tuple[ToolRequirement, ...]) -> tuple[tuple[InstalledPackage, ...],bool]:
    """Query installed package DB, retaining only requested apps and the actual launcher."""
    format_arg = "--showformat=$"+"{binary:Package}\t$"+"{Version}\n"
    data = command(("dpkg-query","-W",format_arg))
    if data is None:
        return (),False
    wanted = {"artcraft-launcher"}
    for requirement in requirements:
        wanted.update(tool_spec(requirement.tool).packages)
    result: list[InstalledPackage] = []
    for line in data.splitlines():
        fields = line.split("\t")
        if len(fields) != 2:
            continue
        name,version = fields
        name = name.split(":")[0]
        if name in wanted:
            result.append(InstalledPackage(name=name,version=version))
    return tuple(sorted(result,key=lambda p:p.name)),True


def inspect_local_host(requirements: tuple[ToolRequirement, ...]) -> HostSnapshot:
    """Identify resources/executables; help/native/media tests are separate evidence tiers."""
    try:
        system = System(platform.system())
    except ValueError as exc:
        raise ContractError("environment", "unsupported host inspection platform") from exc
    identity = text_file(Path("/etc/machine-id")) or platform.node()
    host_id = hashlib.sha256((identity+platform.system()+platform.machine()).encode()).hexdigest()
    packages,scan_ok = installed_packages(requirements)
    programs = tuple(inspect_program(r,packages,scan_ok) for r in requirements)
    pci = command(("lspci","-nn"))
    gpu = tuple(line for line in (pci or "").splitlines()
                if any(term in line for term in ("VGA compatible controller","3D controller","Display controller")))
    try:
        disk = shutil.disk_usage(Path.cwd()).free
    except OSError:
        disk = None
    return HostSnapshot(host_id=host_id,system=system,architecture=platform.machine(),
                        programs=programs,packages=packages,disk_available_bytes=disk,
                        memory_available_bytes=memory_available(),gpu_status="identified" if gpu else "unknown",
                        gpu_info=gpu,evidence_kind="read_only_host",inspected_at=datetime.now(UTC),
                        requirements=requirements)
