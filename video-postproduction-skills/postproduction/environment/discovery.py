"""Combine PATH, package ownership, desktop entries, known paths and actual CLI files."""
import os
from pathlib import Path
import shutil

from postproduction.environment.catalog import tool_spec
from postproduction.environment.inventory_io import binary_hash, command
from postproduction.environment.models import Discovery, InstalledPackage, ToolObservation, ToolRequirement


def desktop_entries(keyword: str) -> tuple[tuple[str, ...],bool]:
    """Read entry names only; desktop Exec lines are not executable instructions."""
    found: list[str] = []
    complete = True
    if not keyword:
        return (),True
    for root in (Path("/usr/share/applications"),Path.home()/".local/share/applications"):
        try:
            with os.scandir(root) as entries:
                found.extend(str(root/entry.name) for entry in entries
                             if entry.name.endswith(".desktop") and keyword in entry.name.lower())
        except FileNotFoundError:
            continue
        except OSError:
            complete = False
    return tuple(sorted(found)),complete


def binary_version(binary: Path, packages: tuple[InstalledPackage, ...]) -> str | None:
    """Use the exact file package owner, not an unrelated installed application."""
    owned = command(("dpkg-query","-S",str(binary)))
    if owned is None:
        return None
    owners = {line.split(": ",1)[0].split(":")[0] for line in owned.splitlines() if ": " in line}
    return next((p.version for p in packages if p.name in owners),None)


def inspect_program(requirement: ToolRequirement, packages: tuple[InstalledPackage, ...],
                    package_scan_ok: bool) -> ToolObservation:
    """Discovery hints do not assert exhaustive global absence or functional readiness."""
    spec = tool_spec(requirement.tool)
    checked: list[Discovery] = [Discovery.PATH]
    errors: list[str] = []
    package = next((p for p in packages if p.name in spec.packages),None)
    if package_scan_ok:
        checked.append(Discovery.PACKAGE)
    else:
        errors.append("package database probe unavailable")
    entries,desktop_ok = desktop_entries(spec.desktop_keyword)
    if desktop_ok:
        checked.append(Discovery.DESKTOP)
    else:
        errors.append("desktop entry probe incomplete")
    candidates: list[Path] = []
    for directory in os.get_exec_path():
        path_directory = Path(directory or ".")
        try:
            _ = path_directory.stat()
            if path_directory.is_dir() and not os.access(path_directory,os.X_OK):
                errors.append("PATH includes an unsearchable directory")
        except FileNotFoundError:
            continue
        except OSError:
            errors.append("PATH directory metadata is unreadable")
    for name in spec.cli_names:
        value = shutil.which(name)
        if value:
            candidates.append(Path(value))
    locations: list[str] = []
    for path in spec.locations:
        try:
            _ = path.stat()
            locations.append(str(path))
            if path.is_file() and path.name in spec.cli_names:
                candidates.append(path)
        except FileNotFoundError:
            if path.is_symlink():
                errors.append("broken known location symlink")
        except OSError:
            errors.append("known location unreadable")
    checked.append(Discovery.LOCATIONS)
    if spec.cli_names or not requirement.needs_cli:
        checked.append(Discovery.CLI)
    else:
        errors.append("required CLI protocol is not established for this program")
    binary = next((p for p in candidates if p.is_file() and os.access(p,os.X_OK)),None)
    digest = binary_hash(binary) if binary is not None else None
    version = binary_version(binary,packages) if binary is not None else package.version if package else None
    if binary is not None and digest is None:
        errors.append("existing CLI could not be fingerprinted")
    return ToolObservation(tool=requirement.tool,cli_path=str(binary.resolve()) if binary else None,
                           cli_sha256=digest,version=version,package_name=package.name if package else None,
                           desktop_entries=entries,known_app_locations=tuple(locations),
                           checked=tuple(checked),errors=tuple(errors))
