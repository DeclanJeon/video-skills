#!/usr/bin/env python3
"""Check an action shot table (DES-12) for pace, coverage variety, threat exposure and causality.

Read-only. Thresholds are package defaults, not research claims; a project may override them
with flags and must record why. Passing this lint is not a creative or visual QA verdict.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import json
from pathlib import Path
import sys
from typing import Final

SIZES: Final = frozenset('macro ecu cu mcu ms fs ws ews topdown'.split())
ANGLES: Final = frozenset('low eye high top pov ots dutch'.split())
MOVES: Final = frozenset('static track handheld whip push pull orbit crane tilt pan'.split())
THREAT: Final = frozenset('none shadow part full'.split())
ROLES: Final = frozenset('setup attack crisis counter reaction aftermath emotion'.split())
SEGMENTS: Final = frozenset(('action', 'setpiece', 'release'))
REQUIRED: Final = ('cut', 't_start', 't_end', 'segment', 'zone', 'screen_dir', 'shot_size', 'angle',
                   'camera_move', 'threat_in_frame', 'beat_role', 'cause_chain', 'lineup')
CHAINED: Final = frozenset(('attack', 'counter'))


@dataclass(frozen=True, slots=True)
class Finding:
    code: str
    target: str
    message: str


@dataclass(frozen=True, slots=True)
class Limits:
    max_asl: float
    min_insert: float
    min_dynamic_angle: float
    min_threat: float
    min_moving: float
    max_asl_setpiece: float = 2.2
    min_moving_setpiece: float = 0.6


def share(rows: list[dict[str, str]], test: frozenset[str], field: str) -> float:
    return sum(r[field] in test for r in rows) / len(rows) if rows else 1.0


def lint(rows: list[dict[str, str]], limits: Limits) -> list[Finding]:
    out: list[Finding] = []
    allowed = {'shot_size': SIZES, 'angle': ANGLES, 'camera_move': MOVES,
               'threat_in_frame': THREAT, 'beat_role': ROLES, 'segment': SEGMENTS}
    previous_end: float | None = None
    previous_look: tuple[str, str, str] | None = None
    for r in rows:
        cut = r['cut'] or '?'
        for field, values in allowed.items():
            if r[field] not in values:
                out.append(Finding('AL00', cut, f'{field}={r[field]!r} not in {sorted(values)}'))
        try:
            start, end = float(r['t_start']), float(r['t_end'])
        except ValueError:
            out.append(Finding('AL00', cut, 'non-numeric time'))
            continue
        if end <= start or (previous_end is not None and abs(start - previous_end) > 1e-6):
            out.append(Finding('AL10', cut, f'cut {start}-{end} does not continue from {previous_end}'))
        previous_end = end
        if not r['zone'].strip() or not r['screen_dir'].strip():
            out.append(Finding('AL07', cut, 'zone and screen_dir are required for spatial continuity'))
        if r['segment'] == 'release':
            previous_look = None
            continue
        if r['segment'] == 'setpiece':
            if r['lineup'] == 'yes':
                out.append(Finding('AL06', cut, 'frontal lineup tableau inside the set-piece'))
        elif r['lineup'] == 'yes':
            out.append(Finding('AL06', cut, 'frontal lineup tableau inside the action segment'))
        if r['beat_role'] in CHAINED and r['cause_chain'].count('>') < 3:
            out.append(Finding('AL08', cut, 'attack/counter needs wind-up>launch>contact>reaction(>trace)'))
        look = (r['shot_size'], r['angle'], r['camera_move'])
        if look == previous_look:
            out.append(Finding('AL09', cut, f'same size/angle/move as previous action cut: {look}'))
        previous_look = look
    piece = [r for r in rows if r['segment'] == 'setpiece']
    if piece:
        try:
            pasl = sum(float(r['t_end']) - float(r['t_start']) for r in piece) / len(piece)
        except ValueError:
            pasl = 0.0
        if pasl > limits.max_asl_setpiece:
            out.append(Finding('AL11', 'setpiece', f'set-piece ASL {pasl:.2f}s > {limits.max_asl_setpiece}s'))
        if share(piece, MOVES - {'static'}, 'camera_move') < limits.min_moving_setpiece:
            out.append(Finding('AL12', 'setpiece', f'moving camera in < {limits.min_moving_setpiece:.0%} of set-piece cuts'))
        if share(piece, frozenset(('macro', 'ecu', 'cu')), 'shot_size') < 0.3 or share(piece, frozenset(('ws', 'ews', 'fs', 'topdown')), 'shot_size') < 0.15:
            out.append(Finding('AL13', 'setpiece', 'set-piece needs both close inserts (>=30%) and wide space shots (>=15%)'))
    action = [r for r in rows if r['segment'] == 'action']
    if action:
        try:
            asl = sum(float(r['t_end']) - float(r['t_start']) for r in action) / len(action)
        except ValueError:
            asl = 0.0
        checks = (
            ('AL01', asl > limits.max_asl, f'action ASL {asl:.2f}s > {limits.max_asl}s'),
            ('AL02', share(action, frozenset(('macro', 'ecu')), 'shot_size') < limits.min_insert,
             f'macro/ECU inserts < {limits.min_insert:.0%}'),
            ('AL03', share(action, frozenset(('low', 'top', 'pov')), 'angle') < limits.min_dynamic_angle,
             f'low/top/POV angles < {limits.min_dynamic_angle:.0%}'),
            ('AL04', share(action, frozenset(('shadow', 'part', 'full')), 'threat_in_frame') < limits.min_threat,
             f'threat visible in < {limits.min_threat:.0%} of action cuts'),
            ('AL05', share(action, MOVES - {'static'}, 'camera_move') < limits.min_moving,
             f'moving camera in < {limits.min_moving:.0%} of action cuts'),
        )
        out += [Finding(code, 'action', message) for code, failed, message in checks if failed]
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--shots', type=Path, required=True)
    parser.add_argument('--max-asl', type=float, default=2.5)
    parser.add_argument('--min-insert', type=float, default=0.2)
    parser.add_argument('--min-dynamic-angle', type=float, default=0.2)
    parser.add_argument('--min-threat', type=float, default=0.6)
    parser.add_argument('--min-moving', type=float, default=0.4)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    try:
        with args.shots.open(newline='', encoding='utf-8-sig') as stream:
            reader = csv.DictReader(stream)
            missing = [c for c in REQUIRED if c not in (reader.fieldnames or [])]
            if missing:
                raise ValueError(f'missing columns: {missing}')
            rows = [{k: (v or '').strip() for k, v in r.items()} for r in reader]
    except (OSError, ValueError) as error:
        print(f'action_lint: {error}', file=sys.stderr)
        return 2
    limits = Limits(args.max_asl, args.min_insert, args.min_dynamic_angle, args.min_threat, args.min_moving)
    findings = lint(rows, limits)
    if args.json:
        print(json.dumps([
                          {'code': f.code, 'target': f.target, 'message': f.message} for f in findings],
                         ensure_ascii=False, indent=2))
    else:
        print('\n'.join(f'{f.code} {f.target}: {f.message}' for f in findings) or 'action OK')
    return int(bool(findings))


if __name__ == '__main__':
    raise SystemExit(main())
