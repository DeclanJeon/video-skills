"""Vendor-specific provision routes: no guessed silent flags or interchangeable Craft commands."""
from typing import Literal
from urllib.parse import urlsplit

from postproduction.common import Frozen, Nonempty
from postproduction.environment.consent_models import InstallationPlan
from postproduction.environment.models import EnvStatus, System, Tool


class InstallerRoute(Frozen):
    status: EnvStatus
    kind: Nonempty
    reason: Nonempty
    evidence: Nonempty
    required_actions: tuple[Nonempty, ...] = ()
    ready: Literal[False] = False


def select_route(plan: InstallationPlan) -> InstallerRoute:
    """Select only supported concrete paths; optional vendor restrictions are not readiness."""
    if plan.tool in {Tool.FILMCRAFT,Tool.EFFECTCRAFT,Tool.SOUNDCRAFT}:
        if plan.system == System.LINUX and urlsplit(plan.source_url).path.endswith((".tar.gz",".tgz",".tar.xz")):
            return InstallerRoute(status=EnvStatus.PLANNED,kind="linux_portable_tar",
                                  reason="pinned official portable archive, owned extraction and native smoke required",
                                  evidence="installed local README release inventory; actual vendor installation unperformed")
        return InstallerRoute(status=EnvStatus.NEEDS_USER_ACTION,kind="craft_official_artifact",
                              reason="verify the exact signed/official OS artifact and installer protocol before execution",
                              evidence="local README platform/download inventory, not executable installer verification",
                              required_actions=("supply exact release artifact/version/checksum evidence",
                                                "verify package-manager privileges/dependencies and supported install protocol"))
    if plan.tool == Tool.AUTOCLIP:
        return InstallerRoute(status=EnvStatus.NEEDS_USER_ACTION,kind="autoclip_isolated",
                              reason="pin release/runtime dependency lock and diagnostics/media defaults before first run",
                              evidence="pinned source research; actual install/egress certification unperformed",
                              required_actions=("verify official artifact and exact selected ASR/LLM/runtime dependencies",
                                                "network deny + dummy media from first launch; test diagnostics/media/cloud/publish separately"))
    if plan.tool == Tool.RESOLVE:
        return InstallerRoute(status=EnvStatus.NEEDS_USER_ACTION,kind="resolve_official",
                              reason="exact Free/Studio, OS/GPU/driver and official registration/license artifact are required",
                              evidence="official vendor route in research; no unverified silent installer/API flags",
                              required_actions=("operator completes only vendor identity/terms/license steps when required",
                                                "pin official artifact and verified install/API protocol; re-inspect then resume"))
    if plan.tool in {Tool.PREMIERE,Tool.AFTER_EFFECTS}:
        linux = plan.system == System.LINUX
        return InstallerRoute(status=EnvStatus.UNSUPPORTED if linux else EnvStatus.NEEDS_USER_ACTION,
                              kind="adobe_creative_cloud",
                              reason="Linux is not a supported Adobe host" if linux else
                              "verify official Creative Cloud/organization deployment and legitimate subscription/login",
                              evidence="official supported-host/licensing boundary; no crack/compatibility bypass",
                              required_actions=() if linux else ("operator performs actual licensed login/2FA only",
                                                                 "verify official managed-install protocol and required app feature"))
    return InstallerRoute(status=EnvStatus.NEEDS_USER_ACTION,kind="runtime_official",
                          reason="pin exact trusted runtime/font/plugin/model artifact and scoped install recipe",
                          evidence="no guessed distribution package ID or shell-pipe installer",
                          required_actions=("inspect same runtime installation and license first",))
