from decimal import Decimal

import pytest

from cp2.submission_gate import authorize, fingerprint, Review, Approval


@pytest.fixture
def approved(tmp_path):
    files = ('batch.json', 'index.csv', 'GEN-01.md', 'GEN-01.map.json', 'baseline.json')
    for file in files:
        (tmp_path / file).write_text(file)
    settings = {'model': 'model-a', 'endpoint': 'provider/task', 'variant': 'cut-a'}
    digest = fingerprint(tmp_path, files, settings)
    return tmp_path, files, settings, Review(0, 0, 'PASS', digest), Approval(digest, 'USD', Decimal('10'))


def check(case, *, review=None, approval=True, cost='9'):
    root, files, settings, accepted, allowed = case
    return authorize(root, files, settings, review or accepted, allowed if approval else None, 'USD', Decimal(cost))


def test_all_gates_and_current_bytes(approved):
    assert check(approved) == []


@pytest.mark.parametrize('index,batch,verdict,code', [(1,0,'PASS','index'), (0,1,'PASS','batch'), (0,2,'PASS','batch'),
                                                     (0,3,'PASS','batch'), (0,0,'REVISE','review')])
def test_machine_and_judgment_are_independent(approved, index, batch, verdict, code):
    assert code in check(approved, review=Review(index, batch, verdict, approved[3].digest))


def test_approval_and_budget_are_independent(approved):
    assert check(approved, approval=False) == ['approval']
    assert check(approved, cost='10.01') == ['budget']
    assert check(approved, cost='NaN') == ['budget']


@pytest.mark.parametrize('kind', ['text','sidecar','setting','missing'])
def test_post_review_change_closes_submit(approved, kind):
    root, _, settings, _, _ = approved
    if kind == 'setting':
        settings['endpoint'] = 'provider/other-task'
    elif kind == 'missing':
        (root / 'baseline.json').unlink()
    else:
        (root / ('GEN-01.md' if kind == 'text' else 'GEN-01.map.json')).write_text('modified')
    assert 'snapshot' in check(approved)


def test_fingerprint_rejects_paths_outside_project(tmp_path):
    with pytest.raises((OSError, ValueError)):
        fingerprint(tmp_path, ['../outside'], {})


def test_explicit_approval_without_user_cap(approved):
    root, files, settings, review, _ = approved
    no_user_cap = Approval(review.digest, 'USD', None)
    assert authorize(root, files, settings, review, no_user_cap, 'USD', Decimal('1000')) == []
    assert authorize(root, files, settings, review, no_user_cap, 'USD', Decimal('NaN')) == ['budget']
