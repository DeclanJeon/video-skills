"""SoundCraft's own command/inspection/sample semantics, not FilmCraft JSONL or AAF."""
import json
from pathlib import Path
from typing import Final

from pydantic import ValidationError

from postproduction.backends.process import IsolatedProcess, SandboxScope
from postproduction.backends.sound_models import AudioImports, NativeAudioImport, SoundPlan, SoundSummary
from postproduction.errors import ContractError

REQUIRED: Final = ("session.new","setup.session","file.import_video","file.import_audio","mix.volume","file.bounce_mix")


def runner(plan: SoundPlan, root: Path) -> IsolatedProcess:
    reads = (root/plan.recipe.picture.path,*(root/s.asset.path for s in plan.stems))
    return IsolatedProcess(SandboxScope(plan.workspace,plan.owner,reads,memory_bytes=8589934592))


def import_argv(plan: SoundPlan, root: Path) -> tuple[str, ...]:
    """Numeric at fields are observed sample positions; new tracks come from actual imports."""
    commands = [
        ("session.new",{"name":"Owned sound mix","sample_rate":plan.recipe.sample_rate,"bit_depth":24,"template":"blank"}),
        ("setup.session",{"frame_rate":"24"}),
        ("file.import_video",{"path":str(root/plan.recipe.picture.path),"at":0}),
    ]
    for cue in plan.recipe.cues:
        stem = next(s for s in plan.stems if s.id == cue.stem_id)
        commands.append(("file.import_audio",{"path":str(root/stem.asset.path),"at":cue.at_sample}))
    argv = [plan.capability.binary_path,"run"]
    for name,params in commands:
        argv.extend(("--cmd",name+"="+json.dumps(params)))
    argv.extend(("--save",str(plan.workspace/"imported.scraft"),"--inspect","--compact"))
    return tuple(argv)


def summary(data: bytes) -> SoundSummary:
    """--compact --inspect final line is actual session JSON; command results have ID prefixes."""
    try:
        lines = data.decode().splitlines()
        return SoundSummary.model_validate_json(lines[-1])
    except (ValidationError,IndexError,UnicodeError) as exc:
        raise ContractError("readback", "SoundCraft compact session inspection is missing/malformed") from exc


def imports(data: bytes) -> tuple[NativeAudioImport, ...]:
    """Use actual per-command resource returns rather than track5/8 or clip6/9 assumptions."""
    result: list[NativeAudioImport] = []
    for line in data.decode().splitlines():
        if line.startswith("file.import_audio: "):
            actual = AudioImports.model_validate_json(line.removeprefix("file.import_audio: "))
            if len(actual.imported) != 1:
                raise ContractError("readback", "expected exactly one actual source/track/clip per cue import")
            result.append(actual.imported[0])
    return tuple(result)


def mix_argv(plan: SoundPlan, actual: tuple[NativeAudioImport, ...]) -> tuple[str, ...]:
    if len(actual) != len(plan.recipe.cues):
        raise ContractError("readback", "actual imported audio inventory does not match cues")
    argv = [plan.capability.binary_path,"run","--in",str(plan.workspace/"imported.scraft")]
    for cue,item in zip(plan.recipe.cues,actual):
        argv.extend(("--cmd","mix.volume="+json.dumps({"tracks":[item.track],"db":cue.gain_db})))
    params = {"path":str(plan.workspace/"mix.wav"),"format":"wav","bit_depth":"32f",
              "start":0,"end":plan.recipe.sample_count,"normalize":False,"dither":False}
    argv.extend(("--cmd","file.bounce_mix="+json.dumps(params),"--save",str(plan.workspace/"mixed.scraft"),
                 "--inspect","--compact"))
    return tuple(argv)
