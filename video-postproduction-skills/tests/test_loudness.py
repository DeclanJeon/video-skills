"""Actual 1kHz stereo reference tones; independent expected -20 LUFS/-20 dBTP, not native meters/listening."""
import subprocess
import pytest
from conftest import require
from support import pin


@pytest.fixture
def tone(tmp_path):
    subprocess.run(['ffmpeg','-v','error','-f','lavfi','-i','aevalsrc=0.1*sin(2*PI*1000*t)|0.1*sin(2*PI*1000*t):s=48000:d=4','-c:a','pcm_f32le',str(tmp_path/'reference.wav')],capture_output=True,check=True,timeout=20)
    return tmp_path,require('admission','local_pin')(pin(tmp_path,'reference.wav'))


def test_loudness_when_actual_stereo_reference_is_measured_not_native_meter(tone):
    root,asset=tone
    value=require('loudness','measure_loudness')(root,asset)
    assert value.artifact==asset
    assert abs(value.integrated_lufs-(-20.0))<0.3
    assert abs(value.true_peak_dbtp-(-20.0))<0.3


@pytest.mark.parametrize('target,peak,want',[(-20.0,-19.0,True),(-14.0,-19.0,False),(-20.0,-21.0,False)])
def test_loudness_when_explicit_project_targets_fail_independently(tone,target,peak,want):
    root,asset=tone
    policy=require('loudness_models','LoudnessPolicy')(integrated_lufs=target,tolerance_lu=0.5,max_true_peak_dbtp=peak)
    actual=require('loudness','measure_loudness')(root,asset)
    if want:require('loudness','verify_loudness')(actual,policy)
    else:
        with pytest.raises(require('errors','ContractError'),match='loudness'):
            require('loudness','verify_loudness')(actual,policy)


def test_loudness_when_exact_decimal_tolerance_boundary_is_not_floating_point_rejected(tone):
    root,asset=tone
    actual=require('loudness_models','LoudnessMeasurement')(artifact=asset,integrated_lufs=-19.9,true_peak_dbtp=-20.0)
    policy=require('loudness_models','LoudnessPolicy')(integrated_lufs=-20.0,tolerance_lu=0.1,max_true_peak_dbtp=-19.0)
    require('loudness','verify_loudness')(actual,policy)


def test_loudness_when_source_changes_cannot_reuse_old_measurement(tone):
    root,asset=tone
    (root/asset.path).write_bytes(b'replaced')
    with pytest.raises(require('errors','ContractError')):
        require('loudness','measure_loudness')(root,asset)


@pytest.mark.parametrize('changes',[{'integrated_lufs':float('nan')},{'tolerance_lu':-1.0},{'max_true_peak_dbtp':1.0}])
def test_loudness_when_profile_targets_are_invalid_not_silently_accepted(changes):
    from pydantic import ValidationError
    raw={'integrated_lufs':-20.0,'tolerance_lu':0.5,'max_true_peak_dbtp':-1.0,**changes}
    with pytest.raises(ValidationError):require('loudness_models','LoudnessPolicy').model_validate(raw)
