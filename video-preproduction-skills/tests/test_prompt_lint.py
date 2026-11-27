from copy import deepcopy
from hashlib import sha256

import pytest
from cp2.ledger import Ledger
from cp2.prompt_parse import normalized_hash
from prompt_lint import lint


@pytest.fixture
def packet(tmp_path):
    script = tmp_path / 'SCR.md'
    script.write_text('- D001: 기다려.\n', encoding='utf-8')
    Ledger.load(tmp_path).register('SCR', script, 1, [])
    blocks = {f'B{i}': '설명' for i in range(1, 9)}
    blocks.update(B5='“기다려.”', B7='No captions, no text, no watermarks.')
    side = dict(duration_s=2, screenplay='SCR@v1', dialogue_language='ko', labels={'CHR-01': '진행자'},
                block_markers={b: f'[{b}]' for b in blocks},
                fixed_block_hash={b: normalized_hash(blocks[b]) for b in ('B1','B3','B4','B6','B7')},
                shots=[dict(t=[0,2],segments=[dict(t=[0,2],dialogue=['D001'],speaker='CHR-01',onscreen=False)])])
    return tmp_path, blocks, side


def codes(packet):
    root, blocks, side = packet
    prompt = '\n'.join(f'{side["block_markers"][key]}\n{value}' for key, value in blocks.items())
    return {f['code'] for f in lint('video', prompt, deepcopy(side), root)}


@pytest.mark.parametrize('change, expected', [
    (lambda b,s: b.update(B5='“멈춰.”'), 'L2'),
    (lambda b,s: s['shots'][0]['segments'][0].update(t=[0.5,2]), 'L1'),
    (lambda b,s: s['shots'][0]['segments'][0].pop('onscreen'), 'L4'),
    (lambda b,s: b.update(B3='새 인물'), 'L5'),
    (lambda b,s: b.update(B7='No captions.'), 'L7'),
    (lambda b,s: b.update(B2='Use CHR-01'), 'L8'),
    (lambda b,s: b.pop('B8'), 'L12'),
])
def test_specific_failure(packet, change, expected):
    change(packet[1], packet[2])
    assert expected in codes(packet)


def test_whitespace_does_not_trigger_fixed_block_mismatch(packet):
    pin_baseline(packet)
    packet[1]['B3'] = '\n 설명  '
    assert not (codes(packet) & {'L1','L2','L3','L4','L5','L7','L8','L12'})


def test_script_drift_fails(packet):
    (packet[0] / 'SCR.md').write_text('- D001: 변경.\n', encoding='utf-8')
    assert 'L2' in codes(packet)


def test_missing_coverage_is_not_pass(packet):
    packet[2]['shots'] = []
    assert 'L1' in codes(packet)


@pytest.mark.parametrize('case, duration, expected_exit, blockers', [
    ('ex02-defect-30s', 30, 1, 3), ('ex02-fixed-34s', 34, 3, 0),
])
def test_ex02_cli(tmp_path, case, duration, expected_exit, blockers):
    import csv
    import json
    from pathlib import Path
    import subprocess
    import sys
    from timeline_check import read_speech
    from index_lint import LINES

    root = Path(__file__).resolve().parents[1]
    fixture = root / 'tests/fixtures' / case
    reference = root / 'docs/examples/synthetic-laundromat-34s/fixture.md'
    import re
    lines = dict(re.findall(r'^\| (D\d+) \| [^|]+ \| ([^|]+?) \| \d+ \|$', reference.read_text(), re.M))
    script = tmp_path / 'SCR.md'
    script.write_text(''.join(f'- {line}: {text}\n' for line, text in lines.items()), encoding='utf-8')
    Ledger.load(tmp_path).register('SCR', script, 1, [])
    shots = []
    cues = read_speech(fixture/'SCR.md')
    with (fixture/'index.csv').open() as stream:
        for row in csv.DictReader(stream):
            start, end = float(row['t_start']), float(row['t_end'])
            segments, cursor = [], start
            for cue in cues:
                if not start <= cue['start'] < cue['end'] <= end:
                    continue
                if cursor < cue['start']:
                    segments.append({'t': [cursor, cue['start']]})
                segments.append(dict(t=[cue['start'], cue['end']], dialogue=cue['ids'], pauses=cue['pauses'],
                                     speaker='CHR-01', onscreen=True))
                cursor = cue['end']
            if cursor < end:
                segments.append({'t': [cursor, end]})
            shots.append(dict(t=[start, end], segments=segments))
    blocks = {f'B{i}':'연출 메모' for i in range(1, 9)}
    blocks['B5'] = '\n'.join(f'“{lines[line]}”' for cue in cues for line in cue['ids'])
    blocks['B7'] = 'No captions, no text, no watermark.'
    markers = {b:f'[{b}]' for b in blocks}
    side = dict(duration_s=duration, shots=shots, screenplay='SCR@v1', dialogue_language='ko',
                labels={'CHR-01':'진행자'}, block_markers=markers,
                fixed_block_hash={b:normalized_hash(blocks[b]) for b in ('B1','B3','B4','B6','B7')})
    prompt = tmp_path/'VPR.md'
    prompt.write_text('\n'.join(f'{markers[b]}\n{v}' for b,v in blocks.items()), encoding='utf-8')
    manifest = tmp_path/'VPR.map.json'
    manifest.write_text(json.dumps(side), encoding='utf-8')
    result = subprocess.run([sys.executable, str(root/'scripts/prompt_lint.py'), '--kind', 'video', '--project', str(tmp_path),
                             '--prompt', str(prompt), '--map', str(manifest), '--json'], capture_output=True, text=True)
    assert result.returncode == expected_exit, result.stderr
    errors = [f['code'] for f in json.loads(result.stdout) if f['severity']=='error']
    assert errors == ['L3'] * blockers


def test_reaction_before_word_is_blocked(packet):
    shot = packet[2]['shots'][0]
    speaking = shot['segments'][0]
    speaking['t'] = [1, 2]
    shot['segments'].insert(0, dict(t=[0, 1], reaction_to={'dialogue': 'D001', 'word': '기다려'}))
    rows = findings(packet)
    assert any(f['code'] == 'L9' and f['severity'] == 'error' for f in rows)


def test_reaction_after_line_is_verified(packet):
    shot = packet[2]['shots'][0]
    shot['segments'][0]['t'] = [0, 1]
    shot['segments'].append(dict(t=[1, 2], reaction_to={'dialogue': 'D001', 'word': '기다려'}))
    assert not any(f['code'] == 'L9' for f in findings(packet))


def findings(packet):
    root, blocks, side = packet
    prompt = '\n'.join(f'{side["block_markers"][key]}\n{value}' for key, value in blocks.items())
    return lint('video', prompt, deepcopy(side), root)


def pin_baseline(packet):
    import json
    project, _, side = packet
    path = project / 'GEN-01.baseline.json'
    path.write_text(json.dumps({'fixed_block_hash': side['fixed_block_hash']}))
    Ledger.load(project).register('GEN-01', path, 1, [])
    side['fixed_block_baseline'] = 'GEN-01@v1'


def test_pinned_shared_baseline_disallows_per_packet_rehash(packet):
    pin_baseline(packet)
    packet[1]['B3'] = '다른 외모'
    packet[2]['fixed_block_hash']['B3'] = normalized_hash('다른 외모')
    assert any(f['code'] == 'L5' and f['severity'] == 'error' for f in findings(packet))


def test_pinned_shared_baseline_accepts_equivalent_whitespace(packet):
    pin_baseline(packet)
    packet[1]['B3'] = ' 설명  '
    assert not any(f['code'] == 'L5' for f in findings(packet))


def test_missing_baseline_is_not_verified(packet):
    assert any(f['code'] == 'L5' and f['severity'] == 'unverified' for f in findings(packet))


@pytest.mark.parametrize('body,error', [('짧은 머리.\n남색 코트.', False), ('긴 머리.\n남색 코트.', True)])
def test_image_identity_matches_pinned_anchor_and_wardrobe(tmp_path, body, error):
    book = Ledger.load(tmp_path)
    for artifact, content in [('CHR-01', '## anchor\n짧은 머리.\n## notes\n별도 메모.\n'), ('WRD-01a', '# 의상\n## prompt\n남색 코트.\n')]:
        path = tmp_path/f'{artifact}.md'; path.write_text(content, encoding='utf-8')
        book.register(artifact, path, 1, [])
    side = {'block_markers': {'identity': '[Identity]'},
            'identity_sources': ['CHR-01@v1#anchor', 'WRD-01a@v1#prompt']}
    result = lint('image', f'[Identity]\n{body}', side, tmp_path)
    assert [x['severity'] for x in result if x['code'] == 'I1'] == (['error'] if error else [])


def register_json(root, artifact, value):
    import json
    path = root / f'{artifact}.json'; path.write_text(json.dumps(value))
    Ledger.load(root).register(artifact, path, 1, [])
    return f'{artifact}@v1'


def test_axis_and_light_are_compared_per_cut(packet):
    root, blocks, side = packet
    shot = side['shots'][0]
    shot.update(cut='S01-C01', lighting='LGT-01@v1')
    side['axis_source'] = register_json(root, 'CTY', {'axis_by_cut': {'S01-C01': 'Axis: subject faces screen left.'}})
    register_json(root, 'LGT-01', {'light_by_cut': {'S01-C01': 'Light: key from screen right.'}})
    blocks['B5'] = 'Shot 1\n' + blocks['B5'] + '\nAxis: subject faces screen left.\nLight: key from screen right.'
    assert not ({'L6', 'L17'} & codes(packet))
    blocks['B5'] = blocks['B5'].replace('faces screen left', 'faces screen right').replace('from screen right', 'from screen left')
    assert {'L6', 'L17'} <= codes(packet)


def test_image_count_and_style_are_checked_against_registered_sheet(tmp_path):
    pin = register_json(tmp_path, 'SHT-01', {'visible_by_panel': {'S01-C01-P1': ['CHR-01']},
                                          'style_hash': normalized_hash('Soft watercolor.')})
    side = dict(panel='S01-C01-P1', sheet_baseline=pin,
                block_markers={'composition': '[Composition]', 'style': '[Style]'})
    good = '[Composition]\nVisible people: 1\n[Style]\nSoft watercolor.\nNo text, no watermark.'
    # The style block excludes the separate prohibition block.
    good = good.replace('\nNo text', '\n[Negative]\nNo text')
    side['block_markers']['negative'] = '[Negative]'
    assert not any(x['code'] in {'I2','I3'} for x in lint('image', good, side, tmp_path))
    bad = good.replace('people: 1', 'people: 2').replace('watercolor', 'ink')
    assert {'I2','I3'} <= {x['code'] for x in lint('image', bad, side, tmp_path)}


def test_free_text_flags_and_literal_text_conflict(packet):
    _, blocks, side = packet
    blocks['B5'] = 'Shot 1\nBeat 1\nEmotion: tense.\nTurn left.\nThe sign reads OPEN.\n“기다려.”\nBeat 2\nAction: opens the door.\nProps: empty hands.'
    blocks['B6'] = 'Music rises in the last 2 seconds.'
    first = side['shots'][0]['segments'][0]
    first.update(t=[0,1], intensity=3)
    side['shots'][0]['segments'].append(dict(t=[1,2], intensity=3))
    rows = {f['code']:f['severity'] for f in findings(packet)}
    assert {k:rows[k] for k in ('L11','L13','L14','L16','L19','L20')} == {
        'L11':'warning', 'L13':'warning', 'L14':'warning', 'L16':'warning', 'L19':'warning', 'L20':'error'}


def test_qualified_content_avoids_free_text_warning(packet):
    _, blocks, side = packet
    blocks['B5'] = 'Shot 1\nBeat 1\nEmotion: tense.\nAction: faces screen left.\nProps: empty hands.\n“기다려.”'
    blocks['B6'] = 'Music follows the final frame of shot 1.'
    assert not ({'L11','L13','L14','L16','L19','L20'} & codes(packet))


def test_free_text_in_dialogue_does_not_create_visual_conflict(packet):
    root, blocks, side = packet
    script = root / 'SCR-v2.md'; script.write_text('- D001: The sign reads OPEN.\n')
    Ledger.load(root).register('SCR', script, 2, [])
    side.update(screenplay='SCR@v2', dialogue_language='en')
    blocks['B5'] = '“The sign reads OPEN.”'
    assert not any(f['code'] == 'L20' and f['severity'] == 'error' for f in findings(packet))


def test_two_generation_packets_use_local_time_and_same_registered_baseline(packet):
    root, blocks, side = packet
    script = root/'SCR-v2.md'; script.write_text('- D001: 기다려.\n- D002: 이제 가.\n')
    Ledger.load(root).register('SCR', script, 2, [])
    side.update(screenplay='SCR@v2', global_offset_s=0)
    blocks['B5'] = 'Shot 1\nBeat 1\nAction: waits.\nProps: none.\n“기다려.”'
    pin_baseline(packet)
    other_blocks, other_side = deepcopy(blocks), deepcopy(side)
    other_side['global_offset_s'] = 2
    other_side['shots'][0]['segments'][0]['dialogue'] = ['D002']
    other_blocks['B5'] = 'Shot 1\nBeat 1\nAction: steps away.\nProps: none.\n“이제 가.”'
    for item in (packet, (root, other_blocks, other_side)):
        assert not [row for row in findings(item) if row['severity'] == 'error']
    other_blocks['B3'] += ' 새 외모.'
    other_side['fixed_block_hash']['B3'] = normalized_hash(other_blocks['B3'])
    assert any(row['code'] == 'L5' and row['severity'] == 'error' for row in findings((root, other_blocks, other_side)))


@pytest.mark.parametrize('word_end,expected', [(10.7, 'error'), (10.5, None), (10.3, 'unverified')])
def test_registered_word_end_distinguishes_reaction_order(tmp_path, word_end, expected):
    from prompt_lint import reaction_order

    pin = register_json(tmp_path, 'CNT', {'screenplay':'SCR@v1', 'gen':'GEN-02', 'word_events':[
        {'dialogue':'D001', 'word':'기다려', 'start_s':10.4, 'end_s':word_end},
    ]})
    assert reaction_order(tmp_path, dict(gen='GEN-02', screenplay='SCR@v1', global_offset_s=10,
                                stimulus_source=pin), 'D001', '기다려', 0.5, (0, 1)) == expected


def test_bare_scene_id_is_not_allowed_in_image_prompt(tmp_path):
    rows = lint('image', '[style]\nScene S01, 16:9.', {'block_markers': {'style':'[style]'}}, tmp_path)
    assert any(row['code'] == 'I4' for row in rows)


def test_zero_cast_requires_registered_empty_roster(tmp_path):
    panel = 'S01-C01-P1'
    pin = register_json(tmp_path, 'SHT-01', {'visible_by_panel': {panel:[]},
                         'style_hash':normalized_hash('Ink.'), 'axis_by_panel':{panel:'Axis: static.'}})
    side = dict(panel=panel, sheet_baseline=pin, identity_sources=[], identity_na_reason='Empty foyer.',
                block_markers={k:f'[{k}]' for k in ('identity','composition','style','negative')})
    body = '[composition]\nVisible people: 0\nAxis: static.\n[style]\nInk.\n[negative]\nNo text, no watermark.'
    assert lint('image', body, side, tmp_path) == []
    assert any(row['code']=='I1' for row in lint('image', body+'\n[identity]\nA person.', side, tmp_path))
    side['panel'] = 'S01-C01-P2'
    assert any(row['code']=='I1' for row in lint('image', body, side, tmp_path))


def test_registered_directions_allow_markdown_with_explicit_data_block(tmp_path):
    from prompt_lint import canonical_json
    path = tmp_path / 'CTY.md'
    path.write_text('## axis-01\nEditor notes.\n\n```prompt-evidence\n{"axis_by_cut": {"S01-C01": "Axis: static."}}\n```\n')
    Ledger.load(tmp_path).register('CTY', path, 1, [])
    assert canonical_json(tmp_path, 'CTY@v1', 'CTY')['axis_by_cut']['S01-C01'] == 'Axis: static.'
