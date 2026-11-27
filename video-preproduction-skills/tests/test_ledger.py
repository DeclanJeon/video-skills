import pytest
from cp2.ledger import Ledger


def test_register_persist_and_propagate(tmp_path):
    book = Ledger.load(tmp_path)
    for artifact, version, deps in [('SCR', 1, []), ('CNT', 1, ['SCR@v1']), ('STB', 1, ['CNT@v1'])]:
        file = tmp_path / f'{artifact}-{version}.md'
        file.write_text(artifact)
        book.register(artifact, file, version, deps)
    assert Ledger.load(tmp_path).status('STB') == 'current'
    file = tmp_path / 'SCR-2.md'
    file.write_text('revision')
    book.register('SCR', file, 2, [])
    assert Ledger.load(tmp_path).status('CNT') == 'stale'
    assert Ledger.load(tmp_path).status('STB') == 'stale'
    assert book.status('SCR') == 'current'
    with pytest.raises(ValueError):
        book.register('VPR-01', file, 1, ['CNT@v1'])


def test_scoped_anchor_and_draft(tmp_path):
    book = Ledger.load(tmp_path)
    doc = tmp_path / 'doc.md'
    doc.write_text('fixture')
    book.register('CHR-01', doc, 1, [])
    book.register('CNT', doc, 1, ['CHR-01@v1#anchor'])
    book.register('STB', doc, 1, ['CHR-01@v1#persona'])
    assert book.mark_stale('CHR-01@draft#anchor') == []
    assert book.mark_stale('CHR-01#anchor') == ['CNT']
    assert Ledger.load(tmp_path).status('STB') == 'current'


def test_no_rewrite_or_unpinned_dependency(tmp_path):
    book = Ledger.load(tmp_path)
    doc = tmp_path / 'brief.md'
    doc.write_text('fixture')
    book.register('BRF', doc, 1, [])
    with pytest.raises(ValueError):
        book.register('BRF', doc, 1, [])
    with pytest.raises(ValueError):
        book.register('SYN', doc, 1, ['BRF'])
    with pytest.raises(ValueError):
        book.register('SYN', doc, 1, ['BRF@v3'])
    assert book.status('SYN') == 'missing'
