"""Pure decisions: positive reuse does not require pretending incomplete scans proved absence."""
from postproduction.environment.models import (
    Discovery, EnvStatus, HostSnapshot, ToolDecision, ToolRequirement,
)


def decide_tool(requirement: ToolRequirement, host: HostSnapshot) -> ToolDecision:
    """Choose reuse or a specific action; never execute installers or declare smoke readiness."""
    matches = tuple(p for p in host.programs if p.tool == requirement.tool)
    observed = matches[0] if len(matches) == 1 else None

    def result(status: EnvStatus, reason: str) -> ToolDecision:
        return ToolDecision(tool=requirement.tool,status=status,installation=observed,reason=reason)

    if not requirement.required:
        return result(EnvStatus.NOT_REQUIRED,requirement.omission_reason or "explicitly unselected")
    if host.system not in requirement.systems or host.architecture not in requirement.architectures:
        return result(EnvStatus.UNSUPPORTED,"required host OS/architecture is unsupported")
    if requirement.min_disk_bytes and (host.disk_available_bytes is None
                                      or host.disk_available_bytes < requirement.min_disk_bytes):
        return result(EnvStatus.NEEDS_USER_ACTION,"insufficient or unknown disk headroom; no automatic cleanup")
    if requirement.min_memory_bytes and (host.memory_available_bytes is None
                                        or host.memory_available_bytes < requirement.min_memory_bytes):
        return result(EnvStatus.NEEDS_USER_ACTION,"insufficient or unknown available memory")
    if requirement.requires_verified_gpu and host.gpu_status != "verified":
        return result(EnvStatus.NEEDS_USER_ACTION,"GPU identification is not verified feature readiness")
    if observed is None:
        return result(EnvStatus.UNKNOWN,"no unique current tool inspection exists")
    existing = bool(observed.cli_path or observed.package_name or observed.desktop_entries
                    or observed.known_app_locations)
    if observed.cli_path and (not observed.cli_sha256 or not observed.version):
        return result(EnvStatus.NEEDS_USER_ACTION,"existing CLI needs binary/version evidence, not another install")
    if observed.cli_path or (existing and not requirement.needs_cli):
        if observed.version is None:
            return result(EnvStatus.NEEDS_USER_ACTION,"existing application version needs verification")
        if requirement.versions and observed.version not in requirement.versions:
            return result(EnvStatus.INCOMPATIBLE,"existing version is incompatible; any change requires an exact plan")
        return result(EnvStatus.REUSABLE,"reuse existing installation; native smoke/readiness remains unverified")
    if existing:
        return result(EnvStatus.NEEDS_USER_ACTION,"existing application found; locate/repair its required CLI first")
    if observed.errors or set(observed.checked) != set(Discovery):
        return result(EnvStatus.UNKNOWN,"incomplete/failed inspection cannot establish contextual absence")
    return result(EnvStatus.MISSING,"not found in inspected PATH/package/desktop/known locations; ask before installing")
