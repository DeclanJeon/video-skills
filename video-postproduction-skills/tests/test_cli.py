"""Actual subprocess CLI: no install on help/intake/validate; all3 existing native engines and restart refusal."""
import json,os,subprocess,sys
from pathlib import Path
import pytest
from test_ledger import built,project

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'scripts/postproduction.py'


def call(*args):
    return subprocess.run([sys.executable,str(SCRIPT),*map(str,args)],cwd=ROOT,capture_output=True,text=True,timeout=100)


def test_cli_when_help_has_no_install_side_effects(tmp_path):
    result=call('--help')
    assert result.returncode==0
    assert 'inspect-env' in result.stdout and 'install-plan' in result.stdout
    assert not list(tmp_path.iterdir())


def test_cli_when_actual_host_inspection_reuses_three_existing_editors():
    result=call('inspect-env')
    assert result.returncode==0,result.stderr
    data=json.loads(result.stdout)
    assert data['decision']['status']=='reusable'
    assert data['decision']['ready'] is False
    assert len(data['host']['programs'])==3


def test_cli_when_actual_intake_validate_plan_progress_roundtrip(project):
    path,production=project
    result=call('intake',path,'--request',path.parent/'request.json')
    assert result.returncode==0,result.stderr
    for command in ('validate','plan','progress'):
        result=call(command,path)
        assert result.returncode==0,result.stderr
        assert isinstance(json.loads(result.stdout),dict)
    assert json.loads(path.read_text())['production']==production


def test_cli_when_unknown_or_bad_json_is_rejected_before_native_dispatch(project):
    path,production=project
    (path.parent/'request.json').write_text('{"unknown":true}')
    result=call('intake',path,'--request',path.parent/'request.json')
    assert result.returncode!=0
    assert 'Traceback' not in result.stderr
    assert json.loads(result.stderr)['error']
    assert not (path.parent/'.post-native').exists()


def test_cli_when_missing_actual_install_question_cannot_fetch_or_install(tmp_path):
    from test_install_consent import plan,missing_host
    p=plan(missing_host(),tool='autoclip',write_paths=[str(tmp_path/'target'),str(tmp_path/'cache'),str(tmp_path/'leases')])
    file=tmp_path/'install-plan.json';file.write_text(p.model_dump_json())
    result=call('install',file)
    assert result.returncode!=0
    assert json.loads(result.stderr)['error']
    assert not (tmp_path/'cache').exists() and not (tmp_path/'target').exists()


@pytest.mark.parametrize('engine',['filmcraft','effectcraft','soundcraft'])
def test_cli_when_actual_native_prepare_run_observe_and_restart_refusal(tmp_path,engine):
    if engine=='filmcraft':
        from test_filmcraft import setup
        store,backend,packet,cap=setup(tmp_path);order=packet.order
    elif engine=='effectcraft':
        from test_effectcraft import setup
        store,backend,order,cap=setup(tmp_path)
    else:
        from test_soundcraft import setup
        store,backend,order,cap=setup(tmp_path)
    file=tmp_path/'order.json';file.write_text(order.model_dump_json())
    result=call('prepare',store.path,file)
    assert result.returncode==0,result.stderr
    job=json.loads(result.stdout)
    result=call('run',store.path,job['id'])
    assert result.returncode==0,result.stderr
    result=call('observe',store.path,job['id'])
    assert result.returncode==0,result.stderr
    observed=json.loads(result.stdout)
    assert observed['status']=='materialized'
    assert observed['backend']==engine
    before=store.path.read_bytes()
    result=call('run',store.path,job['id'])
    assert result.returncode!=0 and store.path.read_bytes()==before
