from hashlib import sha256

import pytest
from check_sheet_evidence import check, snapshot, VISUAL_CHECKS


@pytest.fixture
def packet(tmp_path):
    image = pytest.importorskip('PIL.Image')
    index = tmp_path/'index.csv'
    index.write_text('cut,panels\nS01-C01,P1;P2\n')
    for name in ('SHT-01.png', 'S01-C01-P1.png', 'S01-C01-P2.png'):
        image.new('RGB', (40,40), 'navy').save(tmp_path/name)
    spec = {'index':'index.csv', 'evidence_kind':'production', 'sheets':[{'image':'SHT-01.png','cells':[
        {'cell':'cell-01','panel':'S01-C01-P1','image':'S01-C01-P1.png'},
        {'cell':'cell-02','panel':'S01-C01-P2','image':'S01-C01-P2.png'}]}]}
    return tmp_path, spec


def test_real_files_are_not_a_visual_pass(packet):
    root, spec = packet
    assert check(root, spec)['status'] == 'unverified'
    spec['review'] = {'snapshot': snapshot(root,spec), 'reviewer':'manual-review-fixture', 'mode':'inline',
                      'checks':{key:{'verdict':'PASS','note':'Synthetic test declaration.'} for key in VISUAL_CHECKS}}
    assert check(root, spec)['status'] == 'recorded_pass'
    (root/'index.csv').write_text('cut,panels\nS01-C01,P1;P2\n\n')
    assert check(root, spec)['status'] == 'unverified'


def test_missing_reordered_and_invalid_files_fail(packet):
    root, spec = packet
    cells = spec['sheets'][0]['cells']
    cells.reverse()
    assert check(root,spec)['status'] == 'blocked'
    cells.reverse()
    (root/'S01-C01-P1.png').unlink()
    assert check(root,spec)['status'] == 'blocked'
    (root/'S01-C01-P1.png').write_text('not a PNG')
    assert check(root,spec)['status'] == 'blocked'


def test_previs_review_cannot_be_reused_as_production_qa(packet):
    root, spec = packet
    spec['evidence_kind'] = 'previs'
    digest = snapshot(root, spec)
    spec['review'] = {'snapshot': digest, 'reviewer':'fixture', 'mode':'inline',
                      'checks':{key:{'verdict':'PASS','note':'Proxy test only.'} for key in VISUAL_CHECKS}}
    assert check(root, spec)['status'] == 'unverified'
    spec['evidence_kind'] = 'production'
    assert snapshot(root, spec) != digest
    assert check(root, spec)['status'] == 'unverified'


def test_replacing_reference_invalidates_review(packet):
    root, spec = packet
    from PIL import Image
    file = root/'reference.png'
    Image.new('RGB', (10, 10), 'red').save(file)
    spec['references'] = ['reference.png']
    before = snapshot(root, spec)
    Image.new('RGB', (10, 10), 'blue').save(file)
    assert snapshot(root, spec) != before
