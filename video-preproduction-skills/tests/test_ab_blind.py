import pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / 'scripts'))
from ab_blind import plan, decide
P = ['PP-10', 'PP-12']
def _scores(key, a_good, b_good):
    return {lab: ({'lip': 1, 'beat': 1, 'drift': 1, 'ban': 1} if (k['arm'] == 'A') == a_good else {'lip': 0, 'beat': 0, 'drift': 1, 'ban': 1})
            for lab, k in key.items() if k['pattern'] == 'PP-10'}
def test_plan_size_and_blinding():
    labels, key = plan(P, 3, 7); assert len(labels) == 12 == len(set(labels))
    assert all(l.startswith('T') and not any(x in l for x in 'AB') for l in labels)       # 라벨에 군 정보 없음
def test_plan_deterministic_by_seed(): assert plan(P, 3, 7) == plan(P, 3, 7) and plan(P, 3, 7) != plan(P, 3, 8)
def test_pattern_validated_when_A_wins_all():
    _, key = plan(P, 3, 1); sc = {lab: {'lip': 1, 'beat': 1, 'drift': 1} if k['arm'] == 'A' else {'lip': 0, 'beat': 0, 'drift': 1} for lab, k in key.items()}
    assert decide(sc, key)['PP-10']['verdict'] == 'validated'
def test_pattern_rejected_when_B_wins():
    _, key = plan(P, 3, 1); sc = {lab: {'lip': 0, 'beat': 0} if k['arm'] == 'A' else {'lip': 1, 'beat': 1} for lab, k in key.items()}
    assert decide(sc, key)['PP-12']['verdict'] == 'rejected'
def test_ties_are_undecided_not_validated():
    _, key = plan(P, 3, 1); sc = {lab: {'lip': 1, 'beat': 1} for lab in key}
    assert decide(sc, key)['PP-10']['verdict'] == 'undecided(ties)'
def test_A_wins_but_one_item_clearly_worse_blocks_adoption():
    _, key = plan(['PP-10'], 3, 1)
    sc = {lab: ({'beat': 1, 'drift': 0} if k['arm'] == 'A' else {'beat': 0, 'drift': 1}) for lab, k in key.items()}   # A 은 beat 개선, drift 는 3건 나빠짐
    r = decide(sc, key)['PP-10']; assert r['verdict'] != 'validated' and 'drift' in r['items_A_clearly_worse']


def test_incomplete_pairs_never_validate():
    _, key = plan(['PP-10'], 3, 1)
    scores = {label: {'beat': int(k['arm'] == 'A')} for label, k in key.items() if k['pair'] == 0}
    assert decide(scores, key)['PP-10']['verdict'] == 'undecided(incomplete)'
