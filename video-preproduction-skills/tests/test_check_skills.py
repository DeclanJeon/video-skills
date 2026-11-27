import json
from pathlib import Path
import subprocess
import sys

CHECK = Path(__file__).resolve().parents[1] / 'scripts/check_skills.py'
HEADINGS = '역할 입력 절차 산출물 다른_부서와의_경계 자체_점검 납품'.replace('_', '\u00a0').split(' ')


def package(root, *, name='crew', recorded='crew', description='production-director assigns this crew.', omit=None, body='', listed=None):
    path = root / 'crew/SKILL.md'
    path.parent.mkdir(parents=True)
    path.write_text(f'---\nname: {name}\ndescription: {description}\n---\n# Crew\n' + '\n'.join(f'## {h.replace(chr(160), " ")}' for h in HEADINGS if h != omit) + '\n' + body, encoding='utf-8')
    (root / 'manifest.json').write_text(json.dumps({'skills': listed or [recorded]}))


def run(root):
    result = subprocess.run([sys.executable, str(CHECK), '--root', str(root), '--json'], capture_output=True, text=True)
    return result.returncode, {item['code'] for item in json.loads(result.stdout)['findings']}


def test_valid(tmp_path):
    package(tmp_path)
    assert run(tmp_path) == (0, set())


def test_name_mismatch(tmp_path):
    package(tmp_path, name='wrong')
    assert run(tmp_path) == (1, {'SK01'})


def test_missing_heading(tmp_path):
    package(tmp_path, omit='절차')
    assert run(tmp_path) == (1, {'SK02'})


def test_description_limit(tmp_path):
    package(tmp_path, description='production-director ' + 'word ' * 41)
    assert run(tmp_path) == (1, {'SK03'})


def test_manifest_mismatch(tmp_path):
    package(tmp_path, listed=['other'])
    assert run(tmp_path) == (1, {'SK04'})


def test_budget_warning_only(tmp_path):
    package(tmp_path, description='production-director ' + 'word ' * 34)
    contents = (tmp_path / 'crew/SKILL.md').read_text()
    names = [f'crew-{i}' for i in range(60)]
    for name in names:
        path = tmp_path / name / 'SKILL.md'
        path.parent.mkdir()
        path.write_text(contents.replace('name: crew\n', f'name: {name}\n'))
    (tmp_path / 'manifest.json').write_text(json.dumps({'skills': ['crew', *names]}))
    assert run(tmp_path) == (0, {'SK05'})


def test_broken_link(tmp_path):
    package(tmp_path, body='[Missing](references/missing.md)')
    assert run(tmp_path) == (1, {'SK06'})


def test_reference_leak(tmp_path):
    package(tmp_path, body='A zebra-term appears here.')
    ref = tmp_path / 'docs/examples/ref-example/leak-terms.txt'
    ref.parent.mkdir(parents=True)
    ref.write_text('zebra-term\n')
    assert run(tmp_path) == (1, {'SK07'})
