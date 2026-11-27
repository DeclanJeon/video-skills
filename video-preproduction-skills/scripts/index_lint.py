#!/usr/bin/env python3
"""Validate a project's indexed storyboard against its local production ledger."""
import argparse
from collections import defaultdict
import csv
from hashlib import sha256
import json
from pathlib import Path
import re

from cp2.ids import RefError, parse_cut, parse_ref
from cp2.ledger import Ledger, artifact_key
from timeline_check import DIALOGUE, LCUT

STAGES = ('bible', 'board', 'sheet', 'prompt')
HEADER_SINGLE = 'BRF BOR SYN PLT SCR DNT WLD SND'.split()
REF_FIELDS = dict(beats='PLT', scene='SCR', speakers_onscreen='CHR', speakers_offscreen='CHR',
                  characters_visible='CHR', wardrobe='WRD', location='LOC SET ENV', props='PRP',
                  camera='CAM', lighting='LGT', look='LOOK', performance='CNT', voice='VOC',
                  ambience='AMB', sfx='SFX', music='MUS', vfx='VFX', continuity='CTY CNT',
                  scene_note='DNT', world_rules='WLD', sheet='SHT', audio_prompt='APR', gen='GEN')
REQUIRED = (set(REF_FIELDS) - {'world_rules', 'sheet', 'audio_prompt', 'gen'}) | {
    'cut', 't_start', 't_end', 'dialogue', 'transition_in', 'transition_out', 'panels'}
LINES = re.compile(r'^\s*(?:-\s+)?(D[0-9]{3}):[ \t]*(.+?)\s*$', re.M)


def is_none(value: str) -> bool:
    return bool(re.fullmatch(r'none(?:\([^\n]+\))?|—', value))


def lint_project(project: Path, stage: str) -> list[dict]:
    book = Ledger.load(project)
    root = book.root / '04_board'
    result = []
    used = set()
    documents = {}

    def add(code: str, target: str, message: str) -> None:
        result.append(dict(code=code, target=target, message=message))

    def resolve(value: str, target: str, prefixes: str) -> str | None:
        try:
            pin = parse_ref(value)
        except RefError:
            add('IX02', target, f'invalid reference {value}')
            return None
        if pin.prefix not in prefixes.split():
            add('IX02', target, f'{value} is not a {prefixes} reference')
            return None
        if pin.draft:
            add('IX03', target, f'draft reference is not accepted at gate: {value}')
            return None
        if pin.version is None:
            add('IX07', target, f'missing version pin: {value}')
            return None
        item = book.resolve(value)
        if not item:
            add('IX02', target, f'unregistered {value}')
            return None
        if item['status'] != 'current':
            add('IX03', target, f'{value} is {item["status"]}')
            return None
        key = artifact_key(value)
        version = (key, pin.version)
        if version not in documents:
            file = (book.root / item['path']).resolve()
            if not file.is_relative_to(book.root) or not file.is_file():
                add('IX02', target, f'artifact file missing or outside project: {value}')
                return None
            raw = file.read_bytes()
            if sha256(raw).hexdigest() != item['sha256']:
                add('IX03', target, f'artifact differs from registered hash: {value}')
                return None
            documents[version] = raw.decode('utf-8') if file.suffix.lower() in {'.md', '.txt'} else ''
        text = documents[version]
        locator = '.'.join(part for part in (pin.anchor, pin.item) if part)
        if locator and not (re.search(rf'^#+[ \t]+{re.escape(locator)}(?:\s|$)', text, re.M)
                            or re.search(rf'\bid=["\']{re.escape(locator)}["\']', text)):
            add('IX02', target, f'locator is not declared: {value}')
            return None
        used.add(key)
        return text

    if stage == 'bible':
        inventory = book.root / 'bible-inventory.json'
        if not inventory.is_file():
            add('IX07', 'bible', 'bible-inventory.json is missing')
            return result
        data = json.loads(inventory.read_text(encoding='utf-8'))
        if not isinstance(data, dict) or not isinstance(data.get('entries'), list):
            raise ValueError('invalid bible inventory')
        screenplay = data.get('screenplay')
        if not isinstance(screenplay, str):
            add('IX07', 'bible.screenplay', 'screenplay pin is required')
        else:
            resolve(screenplay, 'bible.screenplay', 'SCR')
        for entry in data['entries']:
            entity, kind = entry['entity'], entry['kind']
            if kind not in {'CHR', 'LOC', 'SET', 'ENV', 'PRP', 'WRD', 'VOC'}:
                add('IX02', entity, f'invalid bible kind: {kind}')
            elif not entry.get('ref'):
                add('IX01', entity, 'screenplay entity lacks an assigned bible reference')
            else:
                resolve(entry['ref'], entity, kind)
        return result

    header_file = root / 'index-header.json'
    if not header_file.is_file():
        add('IX07', 'header', 'index-header.json is missing')
        return result
    header = json.loads(header_file.read_text(encoding='utf-8'))
    if not isinstance(header, dict):
        raise ValueError('index header must be a JSON object')
    script = None
    for key in HEADER_SINGLE:
        value = header.get(key)
        if isinstance(value, str) and value.strip():
            text = resolve(value, key, key)
            if key == 'SCR':
                script = text
        else:
            add('IX07', key, 'missing header reference')
    for key in ('LOOK', 'BMK', 'QAR'):
        values = header.get(key, [] if key == 'QAR' else None)
        if (not isinstance(values, list) or any(not isinstance(v, str) for v in values)
                or (not values and (key == 'LOOK' or (key == 'BMK' and not header.get('bmk_unknown_reason'))))):
            add('IX07', key, 'invalid reference list or missing benchmark reason')
            continue
        for value in values:
            resolve(value, key, key)
    for key in ('runtime_s', 'aspect', 'fps', 'audio_path'):
        if not header.get(key):
            add('IX07', key, 'missing header field')
    index = root / 'index.csv'
    if not index.is_file():
        add('IX01', 'index', 'index.csv is missing')
        return result
    with index.open(newline='', encoding='utf-8-sig') as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        add('IX01', 'index', 'index has no cuts')
    source = {}
    for line, text in LINES.findall(script or ''):
        if line in source:
            add('IX05', line, 'dialogue ID repeated in screenplay')
        source[line] = text
    seen, allocations, links = set(), defaultdict(list), set()
    for row in rows:
        cut = row.get('cut') or ''
        try:
            if parse_cut(cut)[2] is not None or cut in seen:
                raise RefError(cut)
            seen.add(cut)
        except RefError:
            add('IX02', cut, 'expected a unique cut ID')
        required = REQUIRED | ({'sheet'} if stage in {'sheet', 'prompt'} else set())
        if stage == 'prompt':
            required |= {'gen'} | ({'audio_prompt'} if header.get('audio_path') == 'separate' else set())
        for field in sorted(required):
            if not (row.get(field) or '').strip() or row[field].strip() == 'TBD':
                add('IX01', f'{cut}.{field}', 'required value missing')
        panel_value = (row.get('panels') or '').strip()
        if panel_value and panel_value != 'TBD':
            parts = [p.strip() for p in panel_value.split(';')]
            panels = [f'{cut}-{p}' if p.startswith('P') and i else p for i, p in enumerate(parts)]
            if len(set(panels)) != len(panels) or any(
                not re.fullmatch(rf'{re.escape(cut)}-P[1-9][0-9]*', panel) for panel in panels
            ):
                add('IX02', f'{cut}.panels', 'panel IDs must be unique and belong to the cut')
        for field, kinds in REF_FIELDS.items():
            value = (row.get(field) or '').strip()
            if not value or is_none(value) or value == 'TBD':
                continue
            for part in value.split(';'):
                # Parenthetical display modifiers are not artifact locators.
                resolve(part.strip().split('(', 1)[0].strip(), f'{cut}.{field}', kinds)
        for token in (row.get('segments') or '').split(';'):
            if match := LCUT.fullmatch(token.strip()):
                line, target = match.groups()
                links.add((line, cut, target))
        dialogue = (row.get('dialogue') or '').strip()
        ids = [i.strip() for i in dialogue.split(';')] if dialogue and not is_none(dialogue) else []
        if ids and is_none(row.get('voice') or ''):
            add('IX01', f'{cut}.voice', 'dialogue requires a voice reference')
        if ids and script is not None:
            try:
                snippets = json.loads(row.get('dialogue_text') or '{}')
            except json.JSONDecodeError:
                snippets = None
            if not isinstance(snippets, dict) or set(snippets) != set(ids) or any(snippets[i] != source.get(i) for i in ids):
                add('IX06', cut, 'dialogue_text must match the screenplay by ID')
        for line in ids:
            if not DIALOGUE.fullmatch(line) or (script is not None and line not in source):
                add('IX05', cut, f'undeclared screenplay line: {line}')
            allocations[line].append(cut)
    for line in sorted(set(source) - allocations.keys()):
        add('IX05', line, 'dialogue is not allocated to a cut')
    order = {row.get('cut'): i for i, row in enumerate(rows)}
    for line, cuts in allocations.items():
        if any(order[b] != order[a] + 1 or (line, a, b) not in links for a, b in zip(cuts, cuts[1:])):
            add('IX05', line, 'duplicate dialogue without adjacent L-cut')
    for artifact in sorted(book.artifacts.keys() - used):
        if parse_ref(artifact).prefix in {'CHR', 'LOC', 'PRP', 'WRD', 'VOC'} and book.status(artifact) == 'current':
            add('IX04', artifact, 'active bible artifact is not used by the board')
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, type=Path)
    parser.add_argument('--stage', required=True, choices=STAGES)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    try:
        findings = lint_project(args.project, args.stage)
    except (OSError, ValueError, TypeError, KeyError) as error:
        parser.error(str(error))
    print(json.dumps(findings, ensure_ascii=False, indent=2) if args.json else '\n'.join(
        f'{item["code"]} {item["target"]}: {item["message"]}' for item in findings) or 'index OK')
    return int(bool(findings))


if __name__ == '__main__':
    raise SystemExit(main())
