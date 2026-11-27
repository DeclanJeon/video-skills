#!/usr/bin/env python3
"""Check claimed WO-13 timing/endpoint evidence locally; do not run or grade lanes."""
import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import re

from cp2.model_facts import effective_status


BRIEF_HASH = {
    'X-1': 'ba66c8179a7c8e482ec24c1c49dbe47c11efad86a7c00825f98ff2ba4c266576',
    'X-2': '7e5dd9e042bf27bebc36f373408ae94a449aa56c978091a4cab4620eda4f717d',
    'X-3': '3215f10ce82c85c23005207949bf85a170cf87d22ea1de534c706e11c4c6c6f8',
}
GATE = {'v1': 'S08', 'v2': 'QA4'}
EVENTS = ('wall_start', 'conti_start', 'conti_end', 'formal_endpoint')
TIMING_PROTOCOL = 'wo13-preflight-v1'
TARGET = ('transport', 'model', 'endpoint')


def object_value(value, name):
    if not isinstance(value, dict):
        raise ValueError(f'{name}: expected object')
    return value


def text(value, name):
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ValueError(f'{name}: expected nonblank string without surrounding whitespace')
    return value


def local_file(root, name, label):
    relative = Path(text(name, label))
    if not relative.is_absolute() and '..' not in relative.parts:
        path = (root / relative).resolve()
        if path.is_relative_to(root) and path.is_file() and path.stat().st_size > 0:
            return path
    raise ValueError(f'{label}: expected nonempty project-local file')


def checked_file(root, value, label):
    ref = object_value(value, label)
    path = local_file(root, ref.get('path'), label)
    digest = sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            digest.update(chunk)
    if digest.hexdigest() != ref.get('sha256'):
        raise ValueError(f'{label}: SHA-256 mismatch')
    return path


def decode_json(data):
    def unique_fields(pairs):
        result = dict(pairs)
        if len(result) != len(pairs):
            raise ValueError('duplicate JSON field')
        return result

    return json.loads(data, object_pairs_hook=unique_fields)


def string_list(value):
    return (isinstance(value, list) and bool(value)
            and all(isinstance(item, str) and item and item == item.strip() for item in value))


def check_provider(root, lane):
    provider = object_value(lane.get('provider'), 'provider')
    target = tuple(text(provider.get(key), f'provider.{key}') for key in TARGET)
    receipt_file = checked_file(root, lane.get('provider_receipt'), 'provider_receipt')
    try:
        receipt = object_value(decode_json(receipt_file.read_text(encoding='utf-8')), 'provider_receipt')
    except ValueError as error:
        raise ValueError(f'provider_receipt: {error}') from error
    if target != tuple(receipt.get(key) for key in TARGET):
        raise ValueError('provider target does not match receipt')
    checked_file(root, receipt.get('source_evidence'), 'provider_receipt.source_evidence')
    ttl = receipt.get('ttl_days', 30)
    if type(ttl) is not int or ttl <= 0:
        raise ValueError('provider_receipt.ttl_days: expected positive integer')
    facts = object_value(receipt.get('facts'), 'provider_receipt.facts')

    def fact(name):
        entry = object_value(facts.get(name), f'provider_receipt.{name}')
        source = entry.get('source')
        if (effective_status(entry, ttl) != 'verified' or
                not re.fullmatch(r'user|doc:\S+|experiment:EXP-\S+', source)):
            raise ValueError(f'provider_receipt.{name}: expected a current verified fact with source')
        return entry.get('value')

    duration = fact('max_duration_s')
    if (type(duration) not in (int, float) or duration <= 0
            or (type(duration) is float and not math.isfinite(duration))):
        raise ValueError('provider_receipt.max_duration_s: expected positive finite duration')
    aspects = fact('aspects')
    if not string_list(aspects) or any(not re.fullmatch(r'[1-9]\d*:[1-9]\d*', v) for v in aspects):
        raise ValueError('provider_receipt.aspects: expected nonempty list of aspect ratios')
    references = fact('reference_images_max')
    if type(references) is not int or references <= 0:
        raise ValueError('provider_receipt.reference_images_max: expected positive image-reference limit')
    audio = fact('native_audio')
    if type(audio) is not bool:
        raise ValueError('provider_receipt.native_audio: expected boolean')
    if audio and lane['scenario'] != 'X-3' and not string_list(fact('dialogue_languages')):
        raise ValueError('provider_receipt.dialogue_languages: expected nonempty language list')
    return target


def check_timing(root, lane):
    if lane.get('timing_protocol') != TIMING_PROTOCOL:
        raise ValueError(f'timing_protocol: expected {TIMING_PROTOCOL}')
    clock_id = text(lane.get('clock_id'), 'clock_id')
    events = lane.get('events')
    if (not isinstance(events, list) or any(not isinstance(e, dict) for e in events)
            or tuple(e.get('event') for e in events) != EVENTS):
        raise ValueError(f'event sequence: expected {", ".join(EVENTS)}')
    ticks = [e.get('tick_ns') for e in events]
    if (any(type(t) is not int or not 0 <= t < 2**64 for t in ticks)
            or any(a >= b for a, b in zip(ticks, ticks[1:]))):
        raise ValueError('ticks: expected strictly increasing nonnegative uint64 nanoseconds')
    log = checked_file(root, lane.get('event_log'), 'event_log').read_text(encoding='utf-8').split('\n')
    lines = [e.get('line') for e in events]
    if (any(type(n) is not int or not 1 <= n <= len(log) or not log[n-1].strip() for n in lines)
            or any(a >= b for a, b in zip(lines, lines[1:]))):
        raise ValueError('event log line: expected ordered distinct nonblank line locators')
    for event, tick, line in zip(EVENTS, ticks, lines):
        label = f'event log line {line}'
        try:
            observed = object_value(decode_json(log[line-1]), label)
        except ValueError as error:
            raise ValueError(f'{label}: expected observer JSON object ({error})') from error
        expected = dict(event=event, tick_ns=tick, clock_id=clock_id,
                        session_id=lane['session_id'], observer_id=lane['observer_id'])
        if event == 'wall_start':
            expected.update(brief_sha256=lane['brief']['sha256'], source_sha256=lane['source']['sha256'])
        elif event == 'formal_endpoint':
            endpoint = lane['endpoint']
            expected.update(gate=endpoint['gate'], verdict=endpoint['verdict'],
                            artifact_sha256=endpoint['artifact']['sha256'])
        for key, value in expected.items():
            actual = observed.get(key)
            if type(actual) is not type(value) or actual != value:
                raise ValueError(f'{label}: {key} does not match the trace claim')
    wall_start, conti_start, conti_end, reached = ticks
    return (reached - wall_start) / 1e9, (conti_end - conti_start) / 1e9


def check_traces(project: Path, rows: list) -> dict:
    root = project.resolve(strict=True)
    if not root.is_dir() or not isinstance(rows, list):
        raise ValueError('expected a project directory and JSON trace array')
    issues, lanes = [], {}
    seen, sessions, observers, settings = set(), set(), set(), set()
    sources = {variant: set() for variant in GATE}
    targets = {scenario: set() for scenario in BRIEF_HASH}
    for number, row in enumerate(rows, 1):
        label = f'row {number}'
        try:
            row = object_value(row, 'lane')
            scenario = text(row.get('scenario'), 'scenario')
            variant = text(row.get('variant'), 'variant')
            if scenario not in BRIEF_HASH or variant not in GATE:
                raise ValueError('unknown scenario or variant')
            label = f'{scenario}/{variant}'
            if label in seen:
                raise ValueError('duplicate lane')
            seen.add(label)
            session = text(row.get('session_id'), 'session_id')
            observers.add(text(row.get('observer_id'), 'observer_id'))
            if session in sessions:
                raise ValueError('duplicate session_id')
            sessions.add(session)
            settings.add(tuple(text(row.get(key), key) for key in ('model', 'reasoning')))
            checked_file(root, row.get('brief'), 'brief')
            if row['brief']['sha256'] != BRIEF_HASH[scenario]:
                raise ValueError(f'expected unchanged {scenario} brief')
            checked_file(root, row.get('source'), 'source')
            sources[variant].add(row['source']['sha256'])
            endpoint = object_value(row.get('endpoint'), 'endpoint')
            gate, verdict = endpoint.get('gate'), endpoint.get('verdict')
            if gate != GATE[variant]:
                raise ValueError(f'endpoint: expected {GATE[variant]}')
            if verdict not in ('PASS', 'REVISE', 'RETHINK'):
                raise ValueError('endpoint: expected reached verdict (PASS, REVISE or RETHINK)')
            checked_file(root, endpoint.get('artifact'), 'endpoint.artifact')
            elapsed, conti = check_timing(root, row)
            targets[scenario].add(check_provider(root, row))
            lanes[label] = dict(elapsed_s=elapsed, conti_s=conti, gate=gate, verdict=verdict)
        except (OSError, ValueError, RuntimeError) as error:
            issues.append(f'{label}: {error}')
    expected = {f'{scenario}/{variant}' for scenario in BRIEF_HASH for variant in GATE}
    issues.extend(f'{label}: missing lane' for label in sorted(expected - seen))
    if observers & sessions:
        issues.append('observer_id is an execution session')
    if len(settings) > 1:
        issues.append('evaluator settings differ across lanes')
    for variant, hashes in sources.items():
        if len(hashes) > 1:
            issues.append(f'source differs within {variant}')
    if sources['v1'] & sources['v2']:
        issues.append('v1 and v2 source snapshots must be distinct')
    for scenario, target_set in targets.items():
        if len(target_set) > 1:
            issues.append(f'{scenario}: provider target differs within pair')
    return dict(status='unverified' if issues else 'trace_checked', issues=issues, lanes={} if issues else lanes)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--traces', required=True, help='project-relative trace JSON path')
    args = parser.parse_args()
    try:
        root = args.project.resolve(strict=True)
        try:
            rows = decode_json(local_file(root, args.traces, 'traces').read_text(encoding='utf-8'))
        except ValueError as error:
            raise ValueError(f'expected JSON trace array: {error}') from error
        result = check_traces(root, rows)
    except (OSError, ValueError, RuntimeError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result['status'] == 'trace_checked' else 3


if __name__ == '__main__':
    raise SystemExit(main())
