"""Actual existing three Craft CLIs reopen delivered projections in private network-denied workspace, never a user session."""
from pathlib import Path
from typing import assert_never

from pydantic import JsonValue, TypeAdapter

from postproduction.backends.effect_models import EffectStep
from postproduction.backends.film_models import FilmExport
from postproduction.backends.process import IsolatedProcess, SandboxScope
from postproduction.backends.sound_models import SoundSummary
from postproduction.editable_models import EditableInventory
from postproduction.environment.models import Tool
from postproduction.errors import ContractError


def verify_relinked(inventory: EditableInventory, stage: Path, workspace: Path) -> None:
    runner = IsolatedProcess(SandboxScope(workspace,"owned-editable-relink",(stage,),memory_bytes=8589934592))
    for index,native in enumerate(inventory.projects):
        binary,path = native.capability.binary_path,str(stage/native.destination)
        match native.capability.tool:
            case Tool.FILMCRAFT:
                output = workspace/f"reopen-{index}.mp4"
                result = runner.run((binary,"--project",path,"export",str(output),"--format","h264","--gpu-rendering","off"),timeout=120)
                if result.returncode or result.timed_out:
                    raise ContractError("editable", "actual relinked FilmCraft native reopen/export failed")
                report = FilmExport.model_validate_json(result.stdout)
                if report.offlineMedia or report.result.frames!=native.frame_count:
                    raise ContractError("editable", "actual reopened FilmCraft uses offline/missing media or wrong extent")
            case Tool.EFFECTCRAFT:
                command: list[dict[str,JsonValue]] = [{"command":"comp.info","params":{}}]
                result = runner.run((binary,"--project",path,"run","--commands","-","--json"),
                                    stdin=TypeAdapter(list[dict[str,JsonValue]]).dump_json(command))
                if result.returncode or result.timed_out:
                    raise ContractError("editable", "actual EffectCraft composition reopen failed")
                steps = TypeAdapter(tuple[EffectStep, ...]).validate_json(result.stdout)
                if not any(r.command=="comp.info" for r in steps):
                    raise ContractError("editable", "actual reopened composition missing")
            case Tool.SOUNDCRAFT:
                result = runner.run((binary,"run","--in",path,"--inspect","--compact"))
                if result.returncode or result.timed_out:
                    raise ContractError("editable", "actual SoundCraft native reopen failed")
                session = SoundSummary.model_validate_json(result.stdout.decode().splitlines()[-1])
                if not session.sources or any(not s.loaded for s in session.sources):
                    raise ContractError("editable", "actual reopened SoundCraft source media missing")
            case Tool.AUTOCLIP | Tool.RESOLVE | Tool.PREMIERE | Tool.AFTER_EFFECTS | Tool.FFMPEG | Tool.FFPROBE:
                raise ContractError("editable", "unqualified native project type cannot claim editable delivery")
            case _:
                assert_never(native.capability.tool)
