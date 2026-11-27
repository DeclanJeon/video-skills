"""Action-direction shot table checks (DES-12)."""
from pathlib import Path
import csv
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/action_lint.py'
COLUMNS = ('cut,t_start,t_end,segment,zone,screen_dir,shot_size,angle,camera_move,'
           'threat_in_frame,beat_role,cause_chain,lineup').split(',')
CHAIN = 'wind-up>launch>contact>reaction>trace'


def write(path: Path, rows: list[dict[str, str]]) -> Path:
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def row(i: int, start: float, end: float, **over: str) -> dict[str, str]:
    sizes = ['macro', 'ws', 'cu', 'ms', 'ecu', 'fs']
    angles = ['low', 'eye', 'ots', 'low', 'pov', 'top']
    moves = ['track', 'whip', 'static', 'handheld', 'push', 'track']
    base = dict(cut=f'S01-C{i:02}', t_start=f'{start:.1f}', t_end=f'{end:.1f}', segment='action',
                zone='A', screen_dir='L>R', shot_size=sizes[i % 6], angle=angles[i % 6],
                camera_move=moves[i % 6], threat_in_frame='part' if i % 5 else 'none',
                beat_role='attack' if i % 2 else 'counter', cause_chain=CHAIN, lineup='no')
    base.update(over)
    return base


def lint(path: Path, *extra: str) -> tuple[int, str]:
    done = subprocess.run([sys.executable, str(SCRIPT), '--shots', str(path), *extra],
                          capture_output=True, text=True, check=False)
    return done.returncode, done.stdout + done.stderr


def test_dynamic_table_passes(tmp_path: Path) -> None:
    rows = [row(i, 2.0 * (i - 1), 2.0 * i) for i in range(1, 11)]
    code, out = lint(write(tmp_path / 's.csv', rows))
    assert code == 0, out


def test_flat_static_lineup_table_is_flagged(tmp_path: Path) -> None:
    # Given: the observed failure — long, static, eye-level lineups with off-screen threat.
    rows = [row(i, 4.5 * (i - 1), 4.5 * i, shot_size='ms', angle='eye', camera_move='static',
                threat_in_frame='none', lineup='yes') for i in range(1, 7)]
    code, out = lint(write(tmp_path / 's.csv', rows))
    assert code == 1
    for finding in ('AL01', 'AL02', 'AL03', 'AL04', 'AL05', 'AL06', 'AL09'):
        assert finding in out


def test_attack_without_cause_chain_is_flagged(tmp_path: Path) -> None:
    rows = [row(i, 2.0 * (i - 1), 2.0 * i) for i in range(1, 11)]
    rows[3]['cause_chain'] = 'light wave'
    code, out = lint(write(tmp_path / 's.csv', rows))
    assert code == 1 and 'AL08' in out and 'S01-C04' in out


def test_release_segment_is_exempt_from_pace(tmp_path: Path) -> None:
    rows = [row(i, 2.0 * (i - 1), 2.0 * i) for i in range(1, 11)]
    rows.append(row(11, 20.0, 30.0, segment='release', shot_size='ms', angle='eye',
                    camera_move='static', threat_in_frame='none', beat_role='emotion',
                    cause_chain='', lineup='yes'))
    code, out = lint(write(tmp_path / 's.csv', rows))
    assert code == 0, out


@pytest.mark.parametrize('field, value, finding', [
    ('t_start', '3.0', 'AL10'),
    ('zone', '', 'AL07'),
    ('shot_size', 'huge', 'AL00'),
])
def test_structural_errors(tmp_path: Path, field: str, value: str, finding: str) -> None:
    rows = [row(i, 2.0 * (i - 1), 2.0 * i) for i in range(1, 11)]
    rows[2][field] = value
    code, out = lint(write(tmp_path / 's.csv', rows))
    assert code == 1 and finding in out


def test_unreadable_input_exits_two(tmp_path: Path) -> None:
    code, _ = lint(tmp_path / 'missing.csv')
    assert code == 2


def test_setpiece_segment_has_its_own_pace_and_mix(tmp_path: Path) -> None:
    # Given: a transformation set-piece of long static shots with only mid framing.
    rows = [row(i, 2.0 * (i - 1), 2.0 * i) for i in range(1, 11)]
    for k in range(4):
        rows.append(row(11 + k, 20.0 + 3 * k, 23.0 + 3 * k, segment='setpiece', shot_size='ms',
                        camera_move='static', threat_in_frame='none', cause_chain=''))
    code, out = lint(write(tmp_path / 's.csv', rows))
    assert code == 1 and 'AL11' in out and 'AL12' in out and 'AL13' in out


def test_dynamic_setpiece_passes_without_threat_or_chain(tmp_path: Path) -> None:
    rows = [row(i, 2.0 * (i - 1), 2.0 * i) for i in range(1, 11)]
    sizes = ['ecu', 'ws', 'macro', 'cu', 'topdown', 'ecu']
    for k in range(6):
        rows.append(row(11 + k, 20.0 + k, 21.0 + k, segment='setpiece', shot_size=sizes[k],
                        camera_move='track' if k % 2 else 'push', angle=['low', 'top', 'eye'][k % 3],
                        threat_in_frame='none', beat_role='setup', cause_chain=''))
    code, out = lint(write(tmp_path / 's.csv', rows))
    assert code == 0, out
