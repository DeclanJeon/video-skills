import pytest
from assemble_sheet import assemble


def test_order_caption_and_mapping(tmp_path):
    image = pytest.importorskip('PIL.Image')
    images = tmp_path/'img'; images.mkdir()
    index = tmp_path/'index.csv'
    index.write_text('cut,panels,t_start,t_end\nS01-C01,S01-C01-P2;P1,0,2\n')
    for number in (1,2):
        image.new('RGB', (20, 10), 'red').save(images/f'S01-C01-P{number}.png')
    out = tmp_path/'SHT-01.png'
    cells = assemble(index, images, out, 2, 1, 'time')
    assert [row['panel'] for row in cells] == ['S01-C01-P2','S01-C01-P1']
    assert out.is_file() and out.with_suffix('.cells.json').is_file()


def test_missing_images_cannot_produce_complete_sheet(tmp_path):
    index = tmp_path/'index.csv'; index.write_text('cut,panels\nS01-C01,P1\n')
    out = tmp_path/'SHT-01.png'
    with pytest.raises(ValueError, match='missing PNG'):
        assemble(index, tmp_path, out, 1, 1, 'id')
    assert not out.exists()


def test_html_fallback_escapes_index_caption_and_maps_cells(tmp_path, monkeypatch):
    import json
    import sys

    monkeypatch.setitem(sys.modules, 'PIL', None)
    index = tmp_path/'index.csv'
    index.write_text('cut,panels,dialogue\nS01-C01,P1,<대사 & 자막>\n')
    (tmp_path/'S01-C01-P1.png').write_bytes(b'html path fixture')
    out = tmp_path/'SHT-01.png'
    assemble(index, tmp_path, out, 1, 1, 'dialogue')
    html = out.with_suffix('.html').read_text()
    assert '&lt;대사 &amp; 자막&gt;' in html
    assert '<대사 & 자막>' not in html
    assert not out.exists()
    data = json.loads(out.with_suffix('.cells.json').read_text())
    assert data['sheet'] == 'SHT-01.html'
    assert data['cells'][0]['panel'] == 'S01-C01-P1'


def test_html_fallback_declares_device_width_viewport(tmp_path, monkeypatch):
    import sys

    monkeypatch.setitem(sys.modules, 'PIL', None)
    index = tmp_path/'index.csv'
    index.write_text('cut,panels\nS01-C01,P1\n')
    (tmp_path/'S01-C01-P1.png').write_bytes(b'html path fixture')
    out = tmp_path/'SHT-01.png'

    assemble(index, tmp_path, out, 4, 2, 'id')

    html = out.with_suffix('.html').read_text(encoding='utf-8')
    assert '<meta name="viewport" content="width=device-width, initial-scale=1">' in html


@pytest.mark.parametrize('other', ['.html', '.png'])
def test_sheet_id_cannot_be_reused_across_output_formats(tmp_path, monkeypatch, other):
    import sys

    if other == '.png':
        monkeypatch.setitem(sys.modules, 'PIL', None)
    else:
        pytest.importorskip('PIL.Image')
    index = tmp_path/'index.csv'; index.write_text('cut,panels\nS01-C01,P1\n')
    (tmp_path/'S01-C01-P1.png').write_bytes(b'fixture')
    out = tmp_path/'SHT-01.png'
    out.with_suffix(other).write_text('prior output')
    with pytest.raises(ValueError, match='refusing to replace'):
        assemble(index, tmp_path, out, 1, 1, 'id')
    assert not out.with_suffix('.cells.json').exists()
