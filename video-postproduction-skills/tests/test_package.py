"""Local package structure and enforceable procedure contracts, not an LLM pressure/compliance certification."""
import json,subprocess,sys,shutil
from pathlib import Path
import pytest
from conftest import require
ROOT=Path(__file__).resolve().parents[1]
ROLES=('postproduction-supervisor','picture-editor','motion-compositor','color-finisher','sound-editor-mixer','caption-editor','finishing-operator','postproduction-qa')


@pytest.mark.parametrize('role',ROLES)
def test_package_when_role_entry_matches_explicit_disabled_invocation(role):
    path=ROOT/role/'SKILL.md'
    assert path.is_file()
    header=path.read_text().split("---",2)[1]
    fields=dict(line.partition(":")[::2] for line in header.strip().splitlines())
    assert fields["name"].strip()==role and fields["disable-model-invocation"].strip()=="true"


def test_package_when_manifest_schema_examples_and_links_are_current():
    result=subprocess.run([sys.executable,str(ROOT/'scripts/check_package.py'),'--json'],capture_output=True,text=True,timeout=20)
    assert result.returncode==0,result.stdout+result.stderr
    data=json.loads(result.stdout)
    assert data['ok'] is True and data['roles']==8


def test_package_when_schema_or_role_is_missing_checker_rejects(tmp_path):
    result=require('package_checks','check_package')(tmp_path)
    assert result.ok is False and result.issues


@pytest.mark.parametrize('filename,module,model',[('profile.json','edit_models','DeliveryProfile'),('awaiting-install-authority.json','environment.consent_models','InstallAuthority'),('picture-order.json','work_models','WorkOrder')])
def test_package_when_example_is_syntax_only_it_still_matches_actual_boundary(filename,module,model):
    value=require(module,model).model_validate_json((ROOT/'examples'/filename).read_bytes())
    assert value is not None


def clone_package(tmp_path):
    for item in ['manifest.json','SKILL.md','references','schemas','examples',*ROLES]:
        source=ROOT/item
        if source.is_dir():shutil.copytree(source,tmp_path/item)
        else:shutil.copy2(source,tmp_path/item)
    return tmp_path


@pytest.mark.parametrize('damage',['schema','invocation','link','unsafe-role-path'])
def test_package_when_shipped_contract_drifts_checker_fails_closed(tmp_path,damage):
    root=clone_package(tmp_path)
    if damage=='schema':(root/'schemas/post-state.schema.json').write_text('{}')
    elif damage=='invocation':
        p=root/ROLES[0]/'SKILL.md';p.write_text(p.read_text().replace('disable-model-invocation: true','disable-model-invocation: false'))
    elif damage=='link':
        p=root/ROLES[0]/'SKILL.md';p.write_text(p.read_text()+'\n[missing](references/absent.md)\n')
    else:
        p=root/'manifest.json';m=json.loads(p.read_text());m['roles'][0]['path']=f'../{root.name}/{ROLES[0]}/SKILL.md';p.write_text(json.dumps(m))
    result=require('package_checks','check_package')(root)
    assert result.ok is False and result.issues
