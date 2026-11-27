import csv
import json
from pathlib import Path

from cp2.prompt_parse import split_blocks
from index_lint import REQUIRED, HEADER_SINGLE

ROOT = Path(__file__).resolve().parents[1]


def asset(skill, name):
    return ROOT / skill / 'assets' / name


def test_storyboard_templates_follow_index_lint():
    with asset('storyboard-artist', 'index-template.csv').open() as stream:
        headers = next(csv.reader(stream))
    assert len(set(headers)) == len(headers)
    assert REQUIRED | {'dialogue_text', 'segments', 'sheet', 'gen', 'adopted_take', 'audio_prompt'} <= set(headers)
    header = json.loads(asset('storyboard-artist', 'index-header-template.json').read_text())
    assert set(HEADER_SINGLE) | {'BMK','LOOK','runtime_s','aspect','fps','audio_path'} <= header.keys()


def test_prompt_templates_share_markers_with_sidecars():
    for skill, prefix, expected in [('video-prompt-engineer','VPR',{f'B{i}' for i in range(1,9)}),
                                    ('image-prompt-engineer','IMG',{'identity','composition','style','negative'})]:
        side = json.loads(asset(skill, f'{prefix}-map-template.json').read_text())
        blocks = split_blocks(asset(skill, f'{prefix}-template.md').read_text(), side['block_markers'])
        assert expected <= blocks.keys()
        assert all(blocks[key].strip() for key in expected)


def test_writer_and_bible_anchor_conventions():
    assert '```speech-timing\n[]\n```' in asset('story-writer','SCR-template.md').read_text()
    assert '\n## anchor\n' in asset('character-designer','CHR-template.md').read_text()
    assert '\n## prompt\n' in asset('costume-designer','WRD-template.md').read_text()
