"""Public read-only inspection and pure reuse decisions; no app launch or installer path."""
from postproduction.environment.models import (
    EnvironmentDecision, EnvStatus, HostSnapshot, ToolRequirement,
)
from postproduction.environment.policy import decide_tool
from postproduction.errors import ContractError


def inspect_host(requirements: tuple[ToolRequirement, ...]) -> HostSnapshot:
    """Inspect local metadata only; separate backend smoke must establish functional readiness."""
    from postproduction.environment.inventory import inspect_local_host
    return inspect_local_host(requirements)


def plan_environment(requirements: tuple[ToolRequirement, ...], host: HostSnapshot) -> EnvironmentDecision:
    """Keep unknown/missing/incompatible distinct and never synthesize installation consent."""
    if len({r.tool for r in requirements}) != len(requirements):
        raise ContractError("environment", "ambiguous duplicate tool requirements")
    tools = tuple(decide_tool(r,host) for r in requirements)
    priority = (EnvStatus.UNSUPPORTED,EnvStatus.NEEDS_USER_ACTION,EnvStatus.UNKNOWN,
                EnvStatus.INCOMPATIBLE,EnvStatus.MISSING)
    status = next((state for state in priority if any(t.status == state for t in tools)),None)
    if status is None:
        status = EnvStatus.REUSABLE if any(t.status == EnvStatus.REUSABLE for t in tools) else EnvStatus.NOT_REQUIRED
    return EnvironmentDecision(host_id=host.host_id,status=status,tools=tools)
