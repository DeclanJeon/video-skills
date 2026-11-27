import csv
from copy import deepcopy
from pathlib import Path

import pytest

from cp2.prompt_batch import check_batch


@pytest.fixture
def timeline():
    path = Path(__file__).parent / 'fixtures/ex02-fixed-34s/index.csv'
    with path.open() as stream:
        board = list(csv.DictReader(stream))
    packets = []
    for index, (offset, end, rows) in enumerate([(0, 22, board[:2]), (22, 34, board[2:])], 1):
        packets.append({'gen': f'GEN-{index:02}', 'global_offset_s': offset, 'duration_s': end-offset,
                        'screenplay': 'SCR@v1', 'fixed_block_baseline': 'GEN-01@v1',
                        'shots': [{'cut': row['cut'], 't': [float(row['t_start'])-offset, float(row['t_end'])-offset],
                                   'segments': [{'dialogue': row['dialogue'].split(';')}]} for row in rows]})
    return board, packets


def test_ex02_split(timeline):
    assert check_batch(*timeline, '34') == []


@pytest.mark.parametrize('mutate,code', [
    (lambda p: p[1].update(global_offset_s=23), 'PBG01'),
    (lambda p: p[1]['shots'].pop(0), 'PBG02'),
    (lambda p: p[1]['shots'][0]['segments'][0]['dialogue'].pop(), 'PBG03'),
    (lambda p: p[1]['shots'][0]['segments'][0]['dialogue'].append('D009'), 'PBG03'),
    (lambda p: p[1].update(fixed_block_baseline='GEN-01@v2'), 'PBG04'),
    (lambda p: p[1].update(gen='GEN-01'), 'PBG01'),
])
def test_whole_timeline_rejects_mismatch(timeline, mutate, code):
    board, packets = deepcopy(timeline)
    mutate(packets)
    assert code in {f['code'] for f in check_batch(board, packets, '34')}


def test_ex02_full_prompt_batch_cli(tmp_path):
    import json
    import shutil
    import subprocess
    import sys

    from cp2.ledger import Ledger

    cwd = Path(__file__).resolve().parents[1]
    fixture = cwd / 'tests/fixtures/ex02-gen-split'
    project = tmp_path / 'project'
    shutil.copytree(fixture, project)
    ledger = Ledger.load(project)
    for artifact, name in [('SCR','SCR.md'), ('GEN-01','baseline.json'), ('CTY','axis.json'), ('LGT-01','light.json')]:
        ledger.register(artifact, name, 1, [])
    result = subprocess.run([sys.executable, str(cwd/'scripts/prompt_batch_check.py'), '--project', str(project),
                             '--manifest', str(project/'batch.json'), '--json'], capture_output=True, text=True)
    assert result.returncode == 3, result.stderr
    report = json.loads(result.stdout)
    assert report['batch'] == []
    assert len(report['packets']) == 2
    assert not [item for rows in report['packets'].values() for item in rows if item['severity'] == 'error']

    # The real exit 3 still blocks even if every other gate input is a
    # simulated PASS/approval. This is not an approved provider submission.
    from decimal import Decimal
    from cp2.submission_gate import Approval, Review, authorize, fingerprint

    files = sorted(path.name for path in project.iterdir() if path.is_file())
    settings = {'model': 'fixture', 'endpoint': 'fixture'}
    digest = fingerprint(project, files, settings)
    assert authorize(project, files, settings, Review(0, result.returncode, 'PASS', digest),
                     Approval(digest, 'USD', Decimal('10')), 'USD', Decimal('0')) == ['batch']
