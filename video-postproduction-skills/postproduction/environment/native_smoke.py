"""Actual per-tool synthetic native E3 + private network-negative smoke, distinct from a real vendor installation."""
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import struct
import shutil
import sys
from uuid import uuid4
import wave
from typing import assert_never

from pydantic import JsonValue, ValidationError

from postproduction.audio import probe_audio
from postproduction.backends.effect_native import resources
from postproduction.backends.film_readback import read_project
from postproduction.backends.image_probe import inspect_rgba
from postproduction.backends.process import IsolatedProcess, ProcessResult, SandboxScope
from postproduction.common import Pin, SourceId
from postproduction.environment.consent_models import InstallationPlan
from postproduction.environment.install_models import SmokeResult
from postproduction.environment.models import Tool
from postproduction.errors import ContractError
from postproduction.media import probe_video
from postproduction.timeline_map import FILM_CLOCK


NETWORK_NEGATIVE = """import socket,sys
s=socket.socket();s.settimeout(.2)
try:
 s.connect(('1.1.1.1',443))
except OSError:
 sys.exit(0)
else:
 sys.exit(9)
finally:
 s.close()
"""


def checked(value: ProcessResult) -> bytes:
    if value.returncode or value.timed_out:
        raise ContractError("smoke", f"actual native synthetic command failed rc={value.returncode}, timeout={value.timed_out}: {value.stderr.decode(errors='replace')[:1200]}")
    return value.stdout


def pin(path: Path) -> Pin:
    return Pin(id=SourceId(path.name),version="1",path=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def film_smoke(runner: IsolatedProcess, binary: str, ffmpeg: str) -> None:
    root = runner.scope.workspace
    _ = checked(runner.run((ffmpeg,"-v","error","-f","lavfi","-i","color=c=red:s=96x64:r=24:d=0.25",
        "-c:v","libx264","-pix_fmt","yuv420p",str(root/"source.mp4"))))
    commands: list[dict[str,JsonValue]] = [{"id":"file.newProject","params":{"name":"Synthetic isolated smoke"}},
        {"id":"file.newSequence","params":{"name":"Smoke","width":96,"height":64,"fps":24,"video":1,"audio":1}},
        {"id":"file.import","params":{"paths":[str(root/"source.mp4")]}}]
    script = ("\n".join(json.dumps(c) for c in commands)+"\n").encode()
    project = root/"smoke.fcproj"
    _ = checked(runner.run((binary,"--compact","--save-as",str(project),"run","-"),stdin=script))
    media = tuple(i for i in read_project(project).project.items.values() if i.kind.media is not None)
    if len(media)!=1:
        raise ContractError("smoke", "actual FilmCraft imported resource not established")
    place = {"id":"timeline.place","params":{"item":media[0].id,"track":"V1","time":0,
             "sourceIn":0,"duration":FILM_CLOCK.num//4,"insert":False,"video":True,"audio":False}}
    _ = checked(runner.run((binary,"--project",str(project),"--save","--compact","run","-"),
                           stdin=(json.dumps(place)+"\n").encode()))
    output = root/"smoke.mp4"
    _ = checked(runner.run((binary,"--project",str(project),"export",str(output),"--format","h264","--gpu-rendering","off","--no-audio")))
    facts = probe_video(root,pin(output))
    if (facts.width,facts.height,facts.frame_count)!=(96,64,6):
        raise ContractError("smoke", "actual FilmCraft native output full decode differs")


def effect_smoke(runner: IsolatedProcess, binary: str) -> None:
    root = runner.scope.workspace
    commands: list[dict[str,JsonValue]] = [{"command":"comp.new","params":{"name":"Smoke","width":96,"height":64,"frameRate":24,"duration":.25}},
        {"command":"layer.newSolid","params":{"name":"Box","width":16,"height":12,"color":"#ffffff"}},
        {"command":"comp.info","params":{}}]
    project = root/"smoke.ecproj"
    out = checked(runner.run((binary,"--empty","--save-as",str(project),"run","--commands","-","--json"),
                             stdin=json.dumps(commands).encode()))
    comp = resources(out)
    _ = checked(runner.run((binary,"--project",str(project),"render","--comp",str(comp.id),"--out",str(root/"smoke.png"),
                            "--format","png","--start","0","--end",".25","--fps","24","--channels","rgba","--audio","off","--json")))
    frames = tuple(sorted(root.glob("smoke_*.png")))
    if len(frames)!=6:
        raise ContractError("smoke", "actual EffectCraft complete native sequence missing")
    for path in frames:
        facts = inspect_rgba(path,"#ffffff")
        if (facts.width,facts.height)!=(96,64):
            raise ContractError("smoke", "actual EffectCraft output canvas differs")


def sound_smoke(runner: IsolatedProcess, binary: str) -> None:
    root = runner.scope.workspace
    with wave.open(str(root/"source.wav"),"wb") as stream:
        stream.setparams((1,2,48000,4800,"NONE","not compressed"))
        stream.writeframes(b"".join(struct.pack("<h",int(math.sin(i*2*math.pi*440/48000)*3276)) for i in range(4800)))
    output = root/"smoke.wav"
    commands = (("session.new",{"name":"Synthetic isolated smoke","sample_rate":48000,"template":"blank"}),
        ("file.import_audio",{"path":str(root/"source.wav"),"at":0}),
        ("file.bounce_mix",{"path":str(output),"format":"wav","bit_depth":"32f","start":0,"end":4800,"normalize":False,"dither":False}))
    args = [binary,"run"]
    for id,params in commands:
        args.extend(("--cmd",id+"="+json.dumps(params)))
    args.extend(("--save",str(root/"smoke.scraft"),"--inspect","--compact"))
    _ = checked(runner.run(tuple(args)))
    facts = probe_audio(root,pin(output))
    if (facts.sample_rate,facts.sample_count,facts.channels)!=(48000,4800,2) or facts.sample_peak<.01:
        raise ContractError("smoke", "actual SoundCraft native bounce sample/channel/signal differs")


@dataclass(frozen=True,slots=True)
class NativeSmoke:
    parent: Path

    def run(self, plan: InstallationPlan, files: tuple[Path, ...]) -> SmokeResult:
        self.parent.mkdir(parents=True,exist_ok=True)
        owner = uuid4().hex
        ffmpeg = shutil.which("ffmpeg")
        # Installer supplies the complete verified regular-file payload, CLI first.
        # Preserve sibling resources without mounting a broad target/home directory.
        reads = (*files,*((Path(ffmpeg),) if ffmpeg is not None else ()))
        runner = IsolatedProcess(SandboxScope(self.parent/owner,owner,reads,memory_bytes=8589934592))
        _ = runner.prepare()
        network = False
        try:
            network = runner.run((sys.executable,"-c",NETWORK_NEGATIVE)).returncode==0
            if not network or not files:
                raise ContractError("smoke", "actual egress-negative or installed executable missing")
            binary = str(files[0])
            match plan.tool:
                case Tool.FILMCRAFT:
                    if ffmpeg is None:
                        raise ContractError("dependency", "existing FFmpeg synthetic fixture dependency missing; ask before setup")
                    film_smoke(runner,binary,ffmpeg)
                case Tool.EFFECTCRAFT:
                    effect_smoke(runner,binary)
                case Tool.SOUNDCRAFT:
                    sound_smoke(runner,binary)
                case Tool.AUTOCLIP | Tool.RESOLVE | Tool.PREMIERE | Tool.AFTER_EFFECTS | Tool.FFMPEG | Tool.FFPROBE:
                    raise ContractError("smoke", "actual native fixture route is not qualified for this tool")
                case _:
                    assert_never(plan.tool)
            return SmokeResult(passed=True,network_denied=network,
                evidence=f"actual isolated {plan.tool.value} synthetic native output/full decode plus network-negative; no real-media/perceptual certification")
        except (ContractError,OSError,ValidationError) as exc:
            return SmokeResult(passed=False,network_denied=network,evidence=f"actual synthetic smoke failed: {exc}")
