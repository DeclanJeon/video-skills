#!/usr/bin/env python3
"""Validate cut coverage and estimate speech density from an explicit timing block."""
import argparse
import csv
from decimal import Decimal, InvalidOperation
from itertools import combinations
import json
from pathlib import Path
import re

from cp2.ids import parse_cut
from cp2.speech import count_units, rate_verdict

NUM = r'[0-9]+(?:\.[0-9]+)?'
SEGMENT = re.compile(rf'b[1-9][0-9]*:({NUM})-({NUM})')
OVERLAP = re.compile(rf'overlap:(D\d{{3}})\+(D\d{{3}})@({NUM})-({NUM})')
LCUT = re.compile(r'lcut:(D\d{3})>(S\d{2}-C\d{2})')
DIALOGUE = re.compile(r'D[0-9]{3}')


def seconds(value: str) -> Decimal:
    result = Decimal(str(value))
    if not result.is_finite() or result < 0:
        raise ValueError(f'invalid seconds: {value}')
    return result


def check_timeline(rows: list[dict], runtime: str, speech: list[dict] | None = None) -> list[dict]:
    findings = []

    def add(code: str, target: str, message: str) -> None:
        findings.append(dict(code=code, target=target, message=message,
                             severity='warning' if code == 'TL05' else 'error'))

    limit = seconds(runtime)
    if not limit:
        raise ValueError('runtime must be positive')
    cursor = Decimal(0)
    overlaps, links, ranges, assigned = set(), set(), {}, {}
    for row in rows:
        cut = row['cut']
        if parse_cut(cut)[2] is not None or cut in ranges:
            raise ValueError(f'expected a unique cut ID: {cut}')
        start, end = seconds(row['t_start']), seconds(row['t_end'])
        if end <= start or end > limit:
            add('TL02', cut, 'cut is empty, reversed, or beyond runtime')
        if start != cursor:
            add('TL01' if start > cursor else 'TL02', cut, f'expected next start {cursor}, got {start}')
        cursor = max(cursor, end)
        ranges[cut] = (start, end)
        assigned[cut] = set(re.findall(r'\bD[0-9]{3}\b', row.get('dialogue') or ''))
        point, has_segments, seen = start, False, set()
        for token in (row.get('segments') or '').split(';'):
            token = token.strip()
            if not token:
                continue
            if m := SEGMENT.fullmatch(token):
                has_segments = True
                left, right = map(seconds, m.groups())
                label = token.split(':', 1)[0]
                if left != point or right <= left or right > end or label in seen:
                    add('TL03', cut, f'invalid segment {token}; expected start {point}')
                seen.add(label)
                point = right
            elif m := OVERLAP.fullmatch(token):
                a, b, left, right = m.groups()
                overlaps.add((frozenset((a, b)), seconds(left), seconds(right)))
            elif m := LCUT.fullmatch(token):
                line, target = m.groups()
                links.add((line, cut, target))
            else:
                add('TL03', cut, f'unknown segment notation: {token}')
        if has_segments and point != end:
            add('TL03', cut, 'segments do not reach cut end')
    if cursor < limit:
        add('TL01', 'runtime', f'timeline ends at {cursor}, expected {limit}')

    measured = []
    covered = set()
    for cue in speech or []:
        ids = cue['ids']
        if not isinstance(ids, list) or not ids or any(not DIALOGUE.fullmatch(i) for i in ids):
            raise ValueError('speech timing block requires a list of dialogue IDs per cue')
        target = '+'.join(ids)
        left, right = seconds(cue['start']), seconds(cue['end'])
        if right <= left or right > limit or len(set(ids)) != len(ids) or set(ids) & covered:
            add('TL02', target, 'invalid or duplicate dialogue timing')
            continue
        covered.update(ids)
        cuts = [cut for cut, (start, end) in ranges.items() if start < right and left < end]
        for line in ids:
            if (not cuts or any(line not in assigned[cut] for cut in cuts)
                    or any((line, a, b) not in links for a, b in zip(cuts, cuts[1:]))):
                add('TL02', line, 'dialogue timing disagrees with cut assignments or lacks L-cut annotation')
        measured.append((set(ids), left, right))
        units, trusted = count_units(cue['text'], cue['lang'])
        pauses = cue.get('pauses', 0)
        if type(pauses) is not int or pauses < 0:
            raise ValueError('pauses must be a nonnegative count')
        verdict = rate_verdict(units, float(right - left), cue['lang'], cue.get('mode', 'normal'), pauses, trusted and units > 0)
        if verdict != 'ok':
            add('TL04' if verdict == 'block' else 'TL05', target, f'speech-rate {verdict}: {units} units / {right - left}s, {pauses} pauses')
    for (a, left_a, right_a), (b, left_b, right_b) in combinations(measured, 2):
        left, right = max(left_a, left_b), min(right_a, right_b)
        if left < right and any((frozenset((i, j)), left, right) not in overlaps for i in a for j in b):
            add('TL02', '+'.join(sorted(a | b)), 'unannotated dialogue overlap')
    for line in sorted(set().union(*assigned.values()) - covered):
        add('TL05', line, 'speech timing unverified')
    return findings


def read_speech(script: Path) -> list[dict]:
    blocks = re.findall(r'^```speech-timing\s*\n(.*?)^```[ \t]*$', script.read_text(encoding='utf-8'), re.M | re.S)
    if len(blocks) > 1:
        raise ValueError('expected at most one speech-timing block')
    value = json.loads(blocks[0]) if blocks else []
    if not isinstance(value, list):
        raise ValueError('speech-timing block must contain a JSON array')
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index', required=True, type=Path)
    parser.add_argument('--runtime', required=True)
    parser.add_argument('--script', type=Path)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    try:
        with args.index.open(encoding='utf-8-sig', newline='') as stream:
            findings = check_timeline(list(csv.DictReader(stream)), args.runtime, read_speech(args.script) if args.script else None)
    except (OSError, KeyError, ValueError, TypeError, InvalidOperation) as error:
        parser.error(str(error))
    print(json.dumps(findings, ensure_ascii=False, indent=2) if args.json else ('\n'.join(
        f'{f["code"]} {f["target"]}: {f["message"]}' for f in findings) or 'timeline OK'))
    return int(any(f['severity'] == 'error' for f in findings))


if __name__ == '__main__':
    raise SystemExit(main())
