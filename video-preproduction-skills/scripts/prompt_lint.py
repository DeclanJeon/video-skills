#!/usr/bin/env python3
"""Validate structural prompt contracts. Unimplemented checks do not imply approval."""
import argparse
from decimal import InvalidOperation
from hashlib import sha256
import json
from pathlib import Path
import re

from cp2.ledger import Ledger
from cp2.model_facts import effective_status
from cp2.prompt_parse import extract_quotes, normalized_hash, split_blocks
from cp2.speech import count_units, rate_verdict
from index_lint import LINES
from timeline_check import DIALOGUE, seconds

VIDEO = {f'B{i}' for i in range(1, 9)}
FIXED = ('B1', 'B3', 'B4', 'B6', 'B7')
INTERNAL_ID = re.compile(r'\b(?:[A-Z]{2,4}-\d|[SCBP]\d{2}\b|D\d{3}\b)')
BANS = (
    r'\b(?:no|without) (?:subtitles?|captions?)\b|자막\s*(?:금지|없음)',
    r'\b(?:no|without) (?:readable )?text\b|(?:글자|텍스트)\s*(?:금지|없음)',
    r'\b(?:no|without) watermarks?\b|워터마크\s*(?:금지|없음)',
)


def interval(item: dict) -> tuple:
    start, end = map(seconds, item['t'])
    return start, end


def covers(items: list[dict], start, end) -> bool:
    if not items:
        return False
    cursor = start
    for item in items:
        left, right = interval(item)
        if left != cursor or not left < right <= end:
            return False
        cursor = right
    return cursor == end


def pinned_bytes(root: Path, pin: str, artifact: str) -> bytes:
    book = Ledger.load(root)
    if not re.fullmatch(rf'{re.escape(artifact)}@v[1-9][0-9]*', pin):
        raise ValueError(f'a pinned {artifact} record is required')
    record = book.resolve(pin)
    if not record or record['status'] != 'current':
        raise ValueError(f'{pin} is not current in the ledger')
    path = (book.root / record['path']).resolve()
    if not path.is_relative_to(book.root):
        raise ValueError('registered artifact path escapes project')
    raw = path.read_bytes()
    if sha256(raw).hexdigest() != record['sha256']:
        raise ValueError(f'{pin} hash changed since registration')
    return raw


def screenplay(root: Path, pin: str) -> dict[str, str]:
    rows = LINES.findall(pinned_bytes(root, pin, 'SCR').decode('utf-8'))
    if len(rows) != len(dict(rows)):
        raise ValueError('duplicate screenplay dialogue IDs')
    return dict(rows)


def canonical_json(project: Path, pin: str, pattern: str) -> dict:
    match = re.fullmatch(rf'({pattern})@v[1-9][0-9]*', pin)
    if not match:
        raise ValueError(f'invalid evidence pin: {pin}')
    raw = pinned_bytes(project, pin, match[1]).decode('utf-8')
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        blocks = re.findall(r'^```prompt-evidence[ \t]*\r?\n(.*?)^```[ \t]*\r?$', raw, re.M | re.S)
        if len(blocks) != 1:
            raise ValueError(f'{pin} must have exactly one prompt-evidence block if not JSON') from None
        data = json.loads(blocks[0])
    if not isinstance(data, dict):
        raise ValueError(f'{pin} must contain a JSON object')
    return data


def direction_matches(body: str, prefix: str, expected: str) -> bool:
    if not expected.startswith(prefix) or len(expected.splitlines()) != 1:
        raise ValueError(f'canonical statement must be one {prefix} line')
    lines = [line.strip() for line in body.splitlines() if line.strip().startswith(prefix)]
    return lines == [expected]


def prose_findings(blocks: dict, shots: list, shot_text: dict, dialogue: list[str], add) -> None:
    # Strip only verified dialogue; quoted signs and other visual text remain.
    def without_dialogue(body: str) -> str:
        for line in set(dialogue):
            for left, right in (('"', '"'), ('“', '”'), ('「', '」')):
                body = body.replace(f'{left}{line}{right}', '')
        return body

    visual = without_dialogue('\n'.join(blocks.get(f'B{i}', '') for i in range(1, 6)))
    direction = re.compile(r'\b(?:turns?|moves?|looks?|faces?)\s+(?:to\s+the\s+)?(?:left|right)\b|(?:왼쪽|오른쪽)(?:을|으로)\s*(?:본다|돈다|향한다)', re.I)
    for line in visual.splitlines():
        if direction.search(line) and not re.search(r'\bscreen\b|\bcamera\b|\bcharacter(?:[’\x27]s)?\b|화면|인물 기준', line, re.I):
            add('L13', 'direction cue may lack a screen/character reference', 'warning')
            break
    if re.search(r'\b(?:first|last)\s+\d+(?:\.\d+)?\s+seconds?\b|(?:처음|마지막)\s*\d+(?:\.\d+)?\s*초|초반|후반', blocks.get('B6', ''), re.I):
        add('L14', 'check B6 for global relative timing', 'warning')

    for i, shot in enumerate(shots, 1):
        segments = shot.get('segments', [])
        intensities = [seg.get('intensity') for seg in segments]
        if len(intensities) > 1:
            if any(type(n) is not int or not 1 <= n <= 5 for n in intensities):
                add('L16', f'shot {i}: incomplete intensity values', 'unverified')
            elif len(set(intensities)) == 1:
                add('L16', f'shot {i}: all intensities are equal', 'warning')
        beats = split_blocks(shot_text.get(str(i), ''), {str(n): f'Beat {n}' for n in range(1, len(segments)+1)})
        if segments and len(beats) != len(segments):
            for rule in ('L11', 'L19'):
                add(rule, f'shot {i}: beat prose is not mapped to all segments', 'unverified')
        for n, beat in beats.items():
            text = without_dialogue(beat)
            if re.search(r'^(?:Emotion|감정):', text, re.M | re.I) and not re.search(r'^(?:Action|동작):[ \t]*\S', text, re.M | re.I):
                add('L11', f'shot {i}, beat {n}: emotion without explicit observable action', 'warning')
            if not re.search(r'^(?:Props|Hands|소품|손):[ \t]*\S', text, re.M | re.I):
                add('L19', f'shot {i}, beat {n}: hand/prop statement missing', 'warning')

    # Block only affirmative, stand-alone visual requirements; open-ended
    # semantic contradictions still require the QA reviewer.
    if re.search(BANS[1], blocks.get('B7', ''), re.I) and re.search(
        r'^\s*(?:the |a )?(?:sign|envelope|label)\s+(?:clearly\s+)?reads\s+[^\n]+$',
        visual, re.M | re.I
    ):
        add('L20', 'a visual object explicitly displays text forbidden by B7')


def reaction_order(project: Path, side: dict, line: str, word: str, reaction_at, window) -> str | None:
    """Check a linked reaction against cue bounds and optional pinned word timing."""
    reaction_at = seconds(reaction_at)
    start, end = map(seconds, window)
    if reaction_at < start:
        return 'error'
    if reaction_at >= end:
        return None
    try:
        event_map = canonical_json(project, side['stimulus_source'], 'CNT')
        if not side.get('screenplay') or not side.get('gen') or any(
            event_map.get(key) != side[key] for key in ('screenplay', 'gen')
        ):
            return 'unverified'
        events = [event for event in event_map['word_events']
                  if event['dialogue'] == line and event['word'] == word]
        if len(events) != 1:
            return 'unverified'
        offset = seconds(side['global_offset_s'])
        left, right = (seconds(events[0][key]) - offset for key in ('start_s', 'end_s'))
        if not start <= left < right <= end:
            return 'unverified'
    except (OSError, KeyError, TypeError, ValueError, InvalidOperation, AttributeError):
        return 'unverified'
    return 'error' if reaction_at < right else None


def identity_text(project: Path, refs: list[str]) -> str:
    if not isinstance(refs, list) or not refs:
        raise ValueError('identity_sources must be a nonempty list')
    chunks = []
    for ref in refs:
        match = re.fullmatch(r'((CHR-[0-9]{2}|WRD-[0-9]{2}[a-z])@v[1-9][0-9]*)#(anchor|prompt)', ref)
        if not match:
            raise ValueError(f'invalid identity source: {ref}')
        pin, artifact, anchor = match.groups()
        if anchor != ('anchor' if artifact.startswith('CHR-') else 'prompt'):
            raise ValueError(f'invalid identity locator: {ref}')
        text = pinned_bytes(project, pin, artifact).decode('utf-8')
        sections = re.findall(rf'^##[ \t]+{anchor}[ \t]*\n(.*?)(?=^#{{1,2}}[ \t]|\Z)', text, re.M | re.S)
        if len(sections) != 1 or not sections[0].strip():
            raise ValueError(f'identity source section missing or ambiguous: {ref}')
        chunks.append(sections[0].strip())
    return '\n'.join(chunks)


def lint(kind: str, prompt: str, side: dict, project: Path) -> list[dict]:
    results = []

    def add(code: str, message: str, severity: str = 'error') -> None:
        results.append(dict(code=code, message=message, severity=severity))

    blocks = split_blocks(prompt, side['block_markers'])
    if kind == 'image':
        if INTERNAL_ID.search(prompt) or extract_quotes(prompt):
            add('I4', 'internal ID or quoted text found in image prompt')
        if not all(re.search(p, prompt, re.I) for p in BANS[1:]):
            add('I5', 'explicit text and watermark exclusions are required')
        if re.search(r'\bthen\b', prompt, re.I):
            add('I6', 'inspect possible temporal chaining', 'warning')
        if 'identity_sources' not in side:
            add('I1', 'identity source pins not supplied', 'unverified')
        elif side['identity_sources'] == []:
            reason = side.get('identity_na_reason')
            try:
                evidence = canonical_json(project, side['sheet_baseline'], r'SHT-[0-9]{2}')
                empty_roster = evidence['visible_by_panel'][side['panel']] == []
            except (OSError, ValueError, KeyError, TypeError, AttributeError):
                empty_roster = False
            if not (empty_roster and isinstance(reason, str) and reason.strip() and not blocks.get('identity')):
                add('I1', 'zero-cast exception requires an empty registered panel roster, a reason, and no identity text')
        else:
            try:
                expected_identity = identity_text(project, side['identity_sources'])
            except (OSError, ValueError, KeyError, TypeError) as error:
                add('I1', str(error))
            else:
                if blocks.get('identity') != expected_identity:
                    add('I1', 'identity block differs from pinned character and wardrobe text')
        if not side.get('sheet_baseline'):
            for rule in ('I2', 'I3', 'I7'):
                add(rule, 'registered sheet baseline not supplied', 'unverified')
        else:
            try:
                sheet = canonical_json(project, side['sheet_baseline'], r'SHT-[0-9]{2}')
            except (OSError, ValueError, KeyError, TypeError) as error:
                for rule in ('I2', 'I3', 'I7'):
                    add(rule, str(error))
            else:
                panel = side.get('panel')
                composition = blocks.get('composition', '')
                visible = sheet.get('visible_by_panel', {}).get(panel)
                counts = [line.strip() for line in composition.splitlines() if line.strip().startswith('Visible people:')]
                if not isinstance(visible, list) or any(not isinstance(ref, str) for ref in visible):
                    add('I2', 'panel roster is absent or invalid')
                elif len(set(visible)) != len(visible) or counts != [f'Visible people: {len(visible)}']:
                    add('I2', 'prompt count differs from registered panel roster')
                digest = sheet.get('style_hash')
                if not re.fullmatch(r'[0-9a-f]{64}', str(digest)):
                    add('I3', 'registered style hash is invalid')
                elif not blocks.get('style') or normalized_hash(blocks['style']) != digest:
                    add('I3', 'panel style differs from the registered sheet style')
                axis = sheet.get('axis_by_panel', {}).get(panel)
                if not axis:
                    add('I7', 'registered axis statement not supplied', 'unverified')
                elif not direction_matches(composition, 'Axis:', axis):
                    add('I7', 'composition axis differs from sheet baseline')
        return results

    duration = seconds(side['duration_s'])
    shots = side['shots']
    if not covers(shots, 0, duration):
        add('L1', 'shots must cover the generation interval in order')
    segments = []
    for shot in shots:
        children = shot.get('segments', [])
        if not covers(children, *interval(shot)):
            add('L1', f'segments must cover shot {shot.get("cut", shot["t"])}')
        segments.extend(children)
    expected = []
    declared = [line for seg in segments for line in seg.get('dialogue', [])]
    try:
        source = screenplay(project, side.get('screenplay', '')) if declared or side.get('screenplay') else {}
    except (OSError, ValueError, KeyError) as error:
        add('L2', str(error))
        source = {}
    labels = side.get('labels', {})
    for seg in segments:
        ids = seg.get('dialogue', [])
        if not ids:
            continue
        if not seg.get('speaker') or type(seg.get('onscreen')) is not bool:
            add('L4', f'{ids}: speaker and explicit onscreen boolean are required')
        if not labels.get(seg.get('speaker')):
            add('L18', f'{ids}: sidecar speaker is not in labels')
        if not all(DIALOGUE.fullmatch(line) and line in source for line in ids):
            add('L2', f'{ids}: unknown screenplay dialogue ID')
            continue
        expected.extend(source[line] for line in ids)
        t0, t1 = interval(seg)
        try:
            lang = side['dialogue_language']
            units, trusted = count_units(' '.join(source[line] for line in ids), lang)
            pauses = seg.get('pauses', 0)
            if type(pauses) is not int or pauses < 0:
                raise ValueError('pauses must be a nonnegative integer')
            verdict = rate_verdict(units, float(t1-t0), lang, seg.get('mode', 'normal'), pauses, trusted and units > 0)
        except (ValueError, KeyError) as error:
            add('L3', f'{ids}: {error}', 'unverified')
        else:
            if verdict != 'ok':
                add('L3', f'{ids}: estimated speech rate {verdict}',
                    {'block': 'error', 'warn': 'warning', 'unverified': 'unverified'}[verdict])
    if extract_quotes(blocks.get('B5', '')) != expected:
        add('L2', 'B5 quoted dialogue differs from sidecar-assigned screenplay lines')
    if len(declared) != len(set(declared)):
        add('L2', 'dialogue is assigned more than once in this generation')
    local_hashes = side.get('fixed_block_hash', {})
    baseline = None
    if side.get('fixed_block_baseline'):
        try:
            baseline = json.loads(pinned_bytes(project, side['fixed_block_baseline'], 'GEN-01'))['fixed_block_hash']
            if not isinstance(baseline, dict) or any(
                not re.fullmatch(r'[0-9a-f]{64}', str(baseline.get(name, ''))) for name in FIXED
            ):
                raise ValueError('baseline is missing valid fixed block hashes')
        except (OSError, ValueError, KeyError, TypeError) as error:
            add('L5', str(error))
            baseline = None
    else:
        add('L5', 'project baseline not pinned; local sidecar hashes are not independent evidence', 'unverified')
    for name in FIXED:
        actual = normalized_hash(blocks.get(name, ''))
        local = local_hashes.get(name)
        if local and local != actual:
            add('L5', f'{name} differs from the local sidecar hash')
        if baseline is not None and actual != baseline[name]:
            add('L5', f'{name} differs from the registered project baseline')

    cues = {}
    for seg in segments:
        for line in seg.get('dialogue', []):
            cues.setdefault(line, []).append(interval(seg))
    for seg in segments:
        link = seg.get('reaction_to', seg.get('stimulus'))
        if not link:
            continue
        line, word = link.get('dialogue'), link.get('word')
        windows = cues.get(line, [])
        if len(windows) != 1 or line not in source or not isinstance(word, str) or not word or word not in source[line]:
            add('L9', f'{line}: stimulus line, word or interval cannot be resolved', 'unverified')
            continue
        reaction_at, _ = interval(seg)
        verdict = reaction_order(project, side, line, word, reaction_at, windows[0])
        if verdict == 'error':
            add('L9', f'{line}: reaction precedes the resolved stimulus boundary')
        elif verdict == 'unverified':
            add('L9', f'{line}: within-cue reaction lacks unique pinned word timing', 'unverified')
    if not all(re.search(p, blocks.get('B7', ''), re.I) for p in BANS):
        add('L7', 'B7 requires explicit caption, text and watermark exclusions')
    if INTERNAL_ID.search(prompt):
        add('L8', 'an internal ID appears in the final prompt')
    missing = sorted(VIDEO - {key for key, text in blocks.items() if text})
    if missing:
        add('L12', f'missing or empty blocks: {", ".join(missing)}')
    if side.get('audio_path') == 'separate' and re.search(
        r'\b(?:generate|synthesize) (?:the )?(?:dialogue|voice)\b|대사는 원생 생성한다', blocks.get('B6', ''), re.I
    ):
        add('L15', 'B6 requests dialogue generation on a separate audio path')
    facts = side.get('model_facts', {})
    limit = facts.get('max_duration_s')
    ratios = facts.get('aspects')
    if not (isinstance(limit, dict) and isinstance(ratios, dict) and
            all(effective_status(x, 30) == 'verified' for x in (limit, ratios)) and side.get('aspect')):
        add('L10', 'model duration or aspect evidence is not verified', 'unverified')
    elif duration > seconds(limit['value']) or side['aspect'] not in ratios['value']:
        add('L10', 'requested duration or aspect exceeds verified model support')
    shot_text = split_blocks(blocks.get('B5', ''), {str(i): f'Shot {i}' for i in range(1, len(shots) + 1)})
    for i, shot in enumerate(shots, 1):
        for rule, pin, pattern, key, prefix in (
            ('L6', side.get('axis_source'), 'CTY', 'axis_by_cut', 'Axis:'),
            ('L17', shot.get('lighting'), r'LGT-[0-9]{2}', 'light_by_cut', 'Light:'),
        ):
            if not pin:
                add(rule, f'shot {i}: no registered direction source', 'unverified')
                continue
            try:
                canon = canonical_json(project, pin, pattern)
                expected_direction = canon[key][shot['cut']]
                if not direction_matches(shot_text.get(str(i), ''), prefix, expected_direction):
                    add(rule, f'shot {i}: direction line missing, repeated, or differs from {pin}',
                        'warning' if rule == 'L17' else 'error')
            except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
                add(rule, f'shot {i}: {error}', 'unverified')
    prose_findings(blocks, shots, shot_text, expected, add)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kind', choices=('video', 'image'), required=True)
    parser.add_argument('--prompt', type=Path, required=True)
    parser.add_argument('--map', dest='sidecar', type=Path, required=True)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    try:
        findings = lint(args.kind, args.prompt.read_text(encoding='utf-8'),
                        json.loads(args.sidecar.read_text(encoding='utf-8')), args.project)
    except (OSError, ValueError, KeyError, TypeError, InvalidOperation, AttributeError) as error:
        parser.error(str(error))
    print(json.dumps(findings, ensure_ascii=False, indent=2) if args.json else '\n'.join(
        f'{f["severity"]} {f["code"]}: {f["message"]}' for f in findings) or 'prompt checks OK')
    if any(f['severity'] == 'error' for f in findings):
        return 1
    return 3 if any(f['severity'] == 'unverified' for f in findings) else 0


if __name__ == '__main__':
    raise SystemExit(main())
