"""Parser/scope fixtures here are not a real native/perceptual run report."""
from pathlib import Path
import json
import subprocess
import sys
import pytest
from conftest import require
ROOT=Path(__file__).resolve().parents[1]


def fixtures(root):
    (root/'tests').mkdir(parents=True)
    (root/'tests/test_fixture.py').write_text('def test_contract():\n    assert True\n')
    mapping={'format':'post-acceptance-map/1','scenarios':[{'id':f'P{i:02}','purpose':f'parser fixture {i}','cases':['tests/test_fixture.py::test_contract'],'scopes':['structural_fixture'],'unverified':['parser fixture, not actual native scenario evidence']} for i in range(1,53)]}
    path=root/'docs/acceptance-map.json';path.parent.mkdir();path.write_text(json.dumps(mapping))
    results=root/'qa/results.xml';results.parent.mkdir()
    results.write_text('<testsuites><testsuite tests="1" failures="0" errors="0"><testcase classname="tests.test_fixture" name="test_contract"/></testsuite></testsuites>')
    scope=root/'qa/source-scope.json';scope.write_text(require('source_scope','snapshot')(root).model_dump_json())
    return path,results,scope


def test_acceptance_when_real_node_results_are_present_it_reports_qualified_scope(tmp_path):
    paths=fixtures(tmp_path)
    result=require('acceptance','check_acceptance')(tmp_path,*paths)
    assert result.ok is True and result.mapped_scenarios==52
    assert result.passed_cases==1 and result.fully_perceptually_verified is False


@pytest.mark.parametrize('damage',['missing-id','missing-node','failed-node','skipped-node','setup-error','changed-source','changed-mapping','truncated-results'])
def test_acceptance_when_mapping_execution_or_scope_is_incomplete_it_fails(tmp_path,damage):
    mapping,results,scope=fixtures(tmp_path)
    if damage=='missing-id':
        data=json.loads(mapping.read_text());data['scenarios'].pop();mapping.write_text(json.dumps(data))
    elif damage=='missing-node':results.write_text('<testsuites><testsuite tests="0" failures="0" errors="0"/></testsuites>')
    elif damage in ['failed-node','skipped-node','setup-error']:
        tag={'failed-node':'failure','skipped-node':'skipped','setup-error':'error'}[damage]
        results.write_text(f'<testsuites><testsuite tests="1"><testcase classname="tests.test_fixture" name="test_contract"><{tag}/></testcase></testsuite></testsuites>')
    elif damage=='changed-source':(tmp_path/'tests/test_fixture.py').write_text('raise RuntimeError("changed")')
    elif damage=='changed-mapping':
        data=json.loads(mapping.read_text());data['scenarios'][0]['purpose']='changed after the run';mapping.write_text(json.dumps(data))
    else:results.write_text('<testsuites><testcase')
    result=require('acceptance','check_acceptance')(tmp_path,mapping,results,scope)
    assert result.ok is False and result.issues


def test_acceptance_when_public_checker_has_no_results_it_never_claims_pass():
    result=subprocess.run([sys.executable,str(ROOT/'scripts/check_acceptance.py'),'--json','--results','qa/absent-for-negative.xml'],capture_output=True,text=True,timeout=20)
    assert result.returncode==1,result.stderr
    data=json.loads(result.stdout)
    assert data['ok'] is False
