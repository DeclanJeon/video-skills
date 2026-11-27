import pytest
from timeline_check import check_timeline


def row(cut, start, end, segments='', dialogue='none'):
    return dict(cut=cut, t_start=str(start), t_end=str(end), segments=segments, dialogue=dialogue)


@pytest.mark.parametrize('rows, runtime, codes', [
    ([row('S01-C01', 0, 2), row('S01-C02', 2, 4)], '4', []),
    ([row('S01-C01', 0, 2), row('S01-C02', 3, 4)], '4', ['TL01']),
    ([row('S01-C01', 0, 3), row('S01-C02', 2, 4)], '4', ['TL02']),
    ([row('S01-C01', 0, 4, 'b1:0-1;b2:2-4')], '4', ['TL03']),
    ([row('S01-C01', 0, 4, 'b1:0-4')], '4', []),
])
def test_coverage(rows, runtime, codes):
    assert [finding['code'] for finding in check_timeline(rows, runtime)] == codes


def test_estimated_speech_and_missing_timing():
    rows = [row('S01-C01', 0, 2, 'b1:0-2', 'D001;D002')]
    spec = [dict(ids=['D001'], start='0', end='2', text='one two three four five six seven eight nine', lang='en')]
    assert [x['code'] for x in check_timeline(rows, '2', spec)] == ['TL04', 'TL05']


def test_overlap_only_when_exactly_declared():
    spec = [dict(ids=[i], start=s, end=e, text='one', lang='en')
            for i, s, e in [('D001', '0', '3'), ('D002', '2', '4')]]
    assert [x['code'] for x in check_timeline([row('S01-C01', 0, 4, '', 'D001;D002')], '4', spec)] == ['TL02']
    assert check_timeline([row('S01-C01', 0, 4, 'overlap:D001+D002@2-3', 'D001;D002')], '4', spec) == []


def test_lcut_is_not_an_overlap():
    rows = [row('S01-C01', 0, 2, 'lcut:D001>S01-C02', 'D001'), row('S01-C02', 2, 4, '', 'D001')]
    spec = [dict(ids=['D001'], start='1', end='3', text='one two', lang='en')]
    assert check_timeline(rows, '4', spec) == []


@pytest.mark.parametrize('name, runtime, expected', [
    ('ex02-defect-30s', '30', [('TL04', 'D001'), ('TL04', 'D002'), ('TL05', 'D004+D005'), ('TL04', 'D009+D010')]),
    ('ex02-fixed-34s', '34', []),
])
def test_ex02_cli(name, runtime, expected):
    from pathlib import Path
    import json
    import subprocess
    import sys

    root = Path(__file__).resolve().parents[1]
    fixture = root / 'tests/fixtures' / name
    result = subprocess.run([sys.executable, str(root / 'scripts/timeline_check.py'), '--index', str(fixture/'index.csv'),
                             '--runtime', runtime, '--script', str(fixture/'SCR.md'), '--json'], capture_output=True, text=True)
    assert result.returncode == int(bool(expected)), result.stderr
    assert [(x['code'], x['target']) for x in json.loads(result.stdout)] == expected
