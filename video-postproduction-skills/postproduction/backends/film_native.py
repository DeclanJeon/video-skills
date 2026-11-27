"""FilmCraft-only {id,params} JSONL, never used as a generic Craft protocol."""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Final

from pydantic import JsonValue, TypeAdapter

from postproduction.backends.film_models import FilmPlan
from postproduction.backends.film_readback import imported_items, read_project
from postproduction.backends.process import IsolatedProcess, SandboxScope
from postproduction.clock import map_frame
from postproduction.timeline_map import FILM_CLOCK

REQUIRED: Final = ("file.newProject","file.newSequence","file.import","timeline.place","file.exportMedia")


@dataclass(frozen=True, slots=True)
class NativeStage:
    number: int
    argv: tuple[str, ...]
    stdin: bytes | None = None


def digest_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    with path.open("rb") as stream:
        return hashlib.file_digest(stream,"sha256").hexdigest()


def runner(plan: FilmPlan, root: Path) -> IsolatedProcess:
    """8GiB address-space bound is evidenced; the earlier4GiB probe aborted with low actual RSS."""
    return IsolatedProcess(SandboxScope(plan.workspace,plan.owner,
        tuple((root/s.asset.path).absolute() for s in plan.sources),memory_bytes=8589934592))


def initial_script(plan: FilmPlan, root: Path) -> bytes:
    """Create/import only; actual native IDs are observed from the saved project afterwards."""
    profile = plan.profile
    steps: tuple[dict[str,JsonValue], ...] = (
        {"id":"file.newProject","params":{"name":"Owned postproduction picture"}},
        {"id":"file.newSequence","params":{"name":"Picture","width":profile.width,"height":profile.height,
          "fps":profile.fps.num/profile.fps.den,"sampleRate":profile.sample_rate,"video":1,"audio":1}},
        {"id":"file.import","params":{"paths":[str((root/s.asset.path).absolute()) for s in plan.sources]}},
    )
    return ("\n".join(json.dumps(s) for s in steps)+"\n").encode()


def place_script(plan: FilmPlan, root: Path) -> bytes:
    """Use observed native resource IDs and exact ticks, not guessed counters or float seconds."""
    items = imported_items(read_project(plan.workspace/"native.fcproj"),plan,root)
    steps: list[dict[str,JsonValue]] = []
    for segment in plan.timeline.segments:
        source = next(s for s in plan.sources if s.source == segment.source)
        steps.append({"id":"timeline.place","params":{"item":items[segment.source].id,"track":"V1",
            "time":segment.timeline_range.start,"insert":False,
            "sourceIn":map_frame(segment.source_range.start,source.rate,FILM_CLOCK,rounding="exact"),
            "duration":segment.timeline_range.length,"video":True,"audio":source.has_audio}})
    return ("\n".join(json.dumps(s) for s in steps)+"\n").encode()


def metadata_id(data: bytes) -> str:
    """Validate command descriptor JSON without retaining untyped dictionaries."""
    parsed = TypeAdapter(dict[str,JsonValue]).validate_json(data)
    value = parsed.get("id")
    return value if isinstance(value,str) else ""
