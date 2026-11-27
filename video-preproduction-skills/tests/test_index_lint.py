import csv
import json

import pytest
from cp2.ledger import Ledger
from index_lint import lint_project


@pytest.fixture
def board(tmp_path):
    root = tmp_path / '04_board'
    root.mkdir()
    book = Ledger.load(tmp_path)
    header = dict(BMK=[], bmk_unknown_reason='fixture', runtime_s=2, aspect='9:16', fps=24, audio_path='native')
    for key in ('BRF','BOR','SYN','PLT','SCR','DNT','WLD','SND','LOOK-01','CAM-01'):
        path = tmp_path / f'{key}.md'
        path.write_text({'SCR':'## S01\n- D001: 잠깐.\n', 'PLT':'## B01\n', 'DNT':'## S01\n'}.get(key, '# Fixture\n'))
        book.register(key, path, 1, [])
        if key != 'CAM-01':
            header['LOOK' if key == 'LOOK-01' else key] = [f'{key}@v1'] if key == 'LOOK-01' else f'{key}@v1'
    row = dict.fromkeys('speakers_onscreen speakers_offscreen characters_visible wardrobe location props lighting performance ambience sfx music vfx continuity'.split(), 'none(테스트)')
    row.update(cut='S01-C01',t_start='0',t_end='2',beats='PLT@v1.B01',scene='SCR@v1.S01',dialogue='D001',
               dialogue_text='{"D001":"잠깐."}', voice='VOC-01@v1',camera='CAM-01@v1',look='LOOK-01@v1',transition_in='hardcut',
               transition_out='hardcut',panels='S01-C01-P1',scene_note='DNT@v1#S01',audio_prompt='',adopted_take='')
    voice = tmp_path/'VOC-01.md'; voice.write_text('# Voice\n'); book.register('VOC-01',voice,1,[])
    return tmp_path, root, book, header, row


def run(board):
    project, root, _, header, row = board
    (root/'index-header.json').write_text(json.dumps(header))
    with (root/'index.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(row))
        writer.writeheader(); writer.writerow(row)
    return {item['code'] for item in lint_project(project, 'board')}


def test_valid_and_later_fields_optional(board):
    assert run(board) == set()


@pytest.mark.parametrize('field,value,code', [
    ('camera','','IX01'), ('location','LOC-09@v1','IX02'), ('performance','CNT@draft','IX03'),
    ('scene_note','DNT@v1#S99','IX02'), ('dialogue','none','IX05'),
    ('dialogue_text','{"D001":"당장."}','IX06'), ('camera','CAM-01','IX07'),
])
def test_bad_rows(board, field, value, code):
    board[-1][field] = value
    assert code in run(board)


def test_missing_header_pin(board):
    del board[-2]['SYN']
    assert 'IX07' in run(board)


def test_superseded_ref(board):
    project, _, book, _, _ = board
    path = project/'cam-v2.md'; path.write_text('# New camera\n'); book.register('CAM-01',path,2,[])
    assert 'IX03' in run(board)


def test_orphan_bible(board):
    project, _, book, _, _ = board
    path = project/'prop.md'; path.write_text('# Prop\n'); book.register('PRP-03',path,1,[])
    assert 'IX04' in run(board)


def test_bible_gate_precedes_storyboard(board):
    project, _, _, _, _ = board
    data = {'screenplay': 'SCR@v1', 'entries': [{'entity': 'speaker', 'kind': 'CHR', 'ref': None}]}
    (project / 'bible-inventory.json').write_text(json.dumps(data))
    findings = lint_project(project, 'bible')
    assert [(f['code'], f['target']) for f in findings] == [('IX01', 'speaker')]


def test_panels_belong_to_the_cut(board):
    board[-1]['panels'] = 'S01-C02-P1'
    assert 'IX02' in run(board)


def test_board_to_sheet_to_image_prompt_handoff(board):
    Image = pytest.importorskip("PIL.Image")
    from assemble_sheet import assemble
    from cp2.prompt_parse import normalized_hash
    from prompt_lint import lint

    project, root, book, _, row = board
    character = project / 'CHR-01.md'
    character.write_text('## anchor\nA short-haired adult.\n', encoding='utf-8')
    book.register('CHR-01', character, 1, [])
    row['characters_visible'] = 'CHR-01@v1'
    assert run(board) == set()
    panel = row['panels']
    Image.new('RGB', (16, 16), 'navy').save(root / f'{panel}.png')
    sheet_path = root / 'SHT-01.png'
    cells = assemble(root/'index.csv', root, sheet_path, 1, 1, 'id')
    assert cells[0]['panel'] == panel
    style = 'Restrained ink wash.'
    baseline = root / 'sheet-baseline.json'
    baseline.write_text(json.dumps({'visible_by_panel': {panel: ['CHR-01']},
                                    'style_hash': normalized_hash(style),
                                    'axis_by_panel': {panel: 'Axis: faces screen left.'}}))
    book.register('SHT-01', baseline, 1, ['CHR-01@v1'])
    side = dict(panel=panel, sheet_baseline='SHT-01@v1', identity_sources=['CHR-01@v1#anchor'],
                block_markers={'identity':'[identity]', 'composition':'[composition]',
                               'style':'[style]', 'negative':'[negative]'})
    prompt = f'[identity]\nA short-haired adult.\n[composition]\nVisible people: 1\nAxis: faces screen left.\n[style]\n{style}\n[negative]\nNo text, no watermark.'
    assert lint('image', prompt, side, project) == []
    character_v2 = project/'CHR-01-v2.md'
    character_v2.write_text('## anchor\nA long-haired adult.\n', encoding='utf-8')
    book.register('CHR-01', character_v2, 2, [])
    assert {item['code'] for item in lint('image', prompt, side, project)} >= {'I1', 'I2', 'I3', 'I7'}


def test_asset_bible_to_conti_board_and_timeline(board):
    from timeline_check import check_timeline

    project, _, book, _, row = board

    def register(artifact, text, depends=(), version=1):
        path = project / f'{artifact}-v{version}.md'
        path.write_text(text, encoding='utf-8')
        book.register(artifact, path, version, list(depends))

    register('CHR-01', '## anchor\nShort-haired clerk.\n', ('SCR@v1',))
    register('WRD-01a', '## prompt\nNavy jacket.\n', ('CHR-01@v1',))
    register('LOC-01', '## plan\nA window behind a desk.\n', ('WLD@v1',))
    register('SET-01', '# Desk\n', ('LOC-01@v1',))
    register('ENV-01', '# Dusk\n', ('LOC-01@v1',))
    register('PRP-01', '## state-a\nClosed notebook.\n', ('LOC-01@v1',))
    register('LGT-01', '# Key from window\n', ('LOC-01@v1', 'CAM-01@v1'))
    register('AMB-01', '# Quiet room tone\n', ('SND@v1',))
    register('CTY', '## axis-01\nDirection stays screen left.\n', ('CAM-01@v1', 'LOC-01@v1'))
    register('CNT', '## S01-C01.perf\nPlaces the notebook on the desk.\n',
             ('SCR@v1', 'DNT@v1', 'CHR-01@v1', 'WRD-01a@v1', 'LOC-01@v1', 'SET-01@v1',
              'ENV-01@v1', 'PRP-01@v1', 'LGT-01@v1', 'AMB-01@v1', 'VOC-01@v1', 'CTY@v1'))
    entries = [(k, f'{v}@v1') for k, v in [('CHR','CHR-01'), ('WRD','WRD-01a'), ('LOC','LOC-01'),
               ('SET','SET-01'), ('ENV','ENV-01'), ('PRP','PRP-01'), ('VOC','VOC-01')]]
    (project/'bible-inventory.json').write_text(json.dumps({'screenplay':'SCR@v1', 'entries':[
        {'entity': kind, 'kind': kind, 'ref': ref} for kind, ref in entries]}))
    assert lint_project(project, 'bible') == []
    row.update(characters_visible='CHR-01@v1', speakers_onscreen='CHR-01@v1', wardrobe='WRD-01a@v1',
               location='LOC-01@v1;SET-01@v1;ENV-01@v1', props='PRP-01@v1#state-a', lighting='LGT-01@v1',
               ambience='AMB-01@v1', continuity='CTY@v1#axis-01', performance='CNT@v1#S01-C01.perf', segments='b1:0-2')
    assert run(board) == set()
    timings = [{'ids':['D001'], 'start':'0.5', 'end':'1.5', 'text':'잠깐.', 'lang':'ko'}]
    assert check_timeline([row], '2', timings) == []
    register('PRP-01', '## state-a\nOpened notebook.\n', ('LOC-01@v1',), version=2)
    assert book.status('CNT') == 'stale'
    assert 'IX03' in {finding['code'] for finding in lint_project(project, 'bible')}
    assert 'IX03' in run(board)
