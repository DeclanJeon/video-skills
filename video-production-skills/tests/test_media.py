"""Real deterministic local media probes, not generative provider QA."""
from pathlib import Path
import subprocess

import pytest
from production.models import ContractError
from conftest import pin, require


def make_video(root: Path, name="technical.mp4", duration=2, audio=False, color="blue"):
    path = root/name
    args = ["ffmpeg","-v","error","-f","lavfi","-i",f"color=c={color}:s=1280x720:r=24:d={duration}"]
    if audio:
        args += ["-f","lavfi","-i",f"sine=frequency=440:duration={duration}","-c:a","aac","-shortest"]
    result = subprocess.run([*args,"-c:v","libx264","-preset","ultrafast","-pix_fmt","yuv420p",str(path)], capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    import hashlib
    from production.models import Pin
    return Pin(id=name,version="1",sha256=hashlib.sha256(path.read_bytes()).hexdigest(),path=name)


def test_probe_when_real_local_video_decodes(tmp_path):
    # Given: generated technical fixture (not a story clip/provider output).
    source = make_video(tmp_path)
    # When: probing and fully decoding actual bytes.
    result = require("media", "probe_media")(tmp_path, source)
    # Then: observed properties, not declared ones.
    assert (result.width,result.height,result.frame_count,result.fps,result.has_audio) == (1280,720,48,24,False)


def test_probe_when_text_pretends_to_be_video(tmp_path):
    # Given: a valid file hash but no decodable media.
    source = pin(tmp_path,"invalid.mp4","not video")
    # When / Then: a file extension and claimed metadata are not sufficient.
    with pytest.raises(ContractError, match="decode"):
        require("media", "probe_media")(tmp_path, source)


def test_render_when_actual_selected_sources_are_available(seed,tmp_path):
    # Given: three technically decodable local fixtures with reported QA selections.
    from test_handoff import all_selected, joins_for
    from production.models import SourceRange
    state = all_selected(seed,tmp_path)
    items=[]
    for i,s in enumerate(state.selections):
        asset=make_video(tmp_path,f"render-source-{i}.mp4",color=("blue","green","red")[i])
        items.append(s.model_copy(update={"take":s.take.model_copy(update={"asset":asset}),"review":s.review.model_copy(update={"playback":s.review.playback.model_copy(update={"asset_hash":asset.sha256})})}))
    state=state.model_copy(update={"selections":tuple(items)})
    state=state.model_copy(update={"join_reviews":joins_for(state)})
    # When: producing a local full-flow review artifact, not a final master.
    proof=require("render","render_review")(state,tmp_path,"review/rough.mp4")
    # Then: actual video duration and lineage match all selected sources.
    result=require("media","probe_media")(tmp_path,proof.artifact)
    assert result.frame_count == 144
    require("render","verify_render")(state,tmp_path,proof)
