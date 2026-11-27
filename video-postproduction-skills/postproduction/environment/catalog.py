"""Known program identities, not guessed installer commands or universal Craft APIs."""
from dataclasses import dataclass
from pathlib import Path
from typing import assert_never

from postproduction.environment.models import Tool


@dataclass(frozen=True, slots=True)
class ToolSpec:
    cli_names: tuple[str, ...]
    packages: tuple[str, ...]
    desktop_keyword: str
    locations: tuple[Path, ...]


def tool_spec(tool: Tool) -> ToolSpec:
    """Describe discovery hints only; an absent hint is not proof of global absence."""
    match tool:
        case Tool.FILMCRAFT | Tool.EFFECTCRAFT | Tool.SOUNDCRAFT:
            name = tool.value
            cli = f"{name}-cli"
            return ToolSpec((cli,),(name,),name,(
                Path("/usr/bin")/cli,Path("/usr/local/bin")/cli,
                Path.home()/".local/bin"/cli,Path("/opt")/name/cli,
                Path("/opt/ArtCraft")/name/cli,
            ))
        case Tool.AUTOCLIP:
            return ToolSpec((),("autoclip",),"autoclip",(Path("/opt/AutoClip"),Path.home()/".local/opt/autoclip"))
        case Tool.RESOLVE:
            return ToolSpec((),("davinci-resolve","resolve"),"resolve",(Path("/opt/resolve"),))
        case Tool.PREMIERE:
            return ToolSpec((),(),"premiere",())
        case Tool.AFTER_EFFECTS:
            return ToolSpec((),(),"aftereffects",())
        case Tool.FFMPEG | Tool.FFPROBE:
            name = tool.value
            return ToolSpec((name,),(name,),"",(
                Path("/usr/bin")/name,Path("/usr/local/bin")/name,Path.home()/".local/bin"/name,
            ))
    assert_never(tool)
