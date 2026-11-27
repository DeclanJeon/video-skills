#!/usr/bin/env python3
"""패턴 효과 A/B 실험의 눈가림·판정 도구 (RR-9, DES-09 §6).
plan   : 패턴×군(A=적용, B=해당 패턴만 제거)×반복 n 의 생성 목록을 무작위 순서·무의미 라벨로 만든다. key 는 채점 뒤에만 연다.
decide : 라벨별 채점 CSV(label,item1..k = 1/0)와 key 를 합쳐 패턴마다 채택/기각/미결을 낸다.
규칙   : 쌍(pair)마다 A 총점>B 총점이면 A승. 채택 = A승 >= 과반이고 어느 단일 항목도 A가 B보다 2건 이상 나쁘지 않음. 동수 많으면 '미결(표본 부족)'."""
import random, json, csv, sys, collections
def plan(patterns, n=3, seed=0):
    rng = random.Random(seed); runs = []
    for p in patterns:
        for i in range(n):
            for arm in 'AB': runs.append({'pattern': p, 'pair': i, 'arm': arm})
    rng.shuffle(runs); labels = rng.sample(range(100, 100 + len(runs) * 3), len(runs))
    key = {f'T{l}': r for l, r in zip(labels, runs)}
    return sorted(key), key                                   # (생성 순서대로 줄 라벨 목록, 비공개 key)
def decide(scores, key):
    """scores: {label: {item: 0/1}}"""
    pairs = collections.defaultdict(dict); items = collections.defaultdict(lambda: collections.Counter())
    for lab, sc in scores.items():
        k = key[lab]; pairs[(k['pattern'], k['pair'])][k['arm']] = sum(sc.values())
        for it, v in sc.items(): items[k['pattern']][(k['arm'], it)] += v
    out = {}
    for p in sorted({entry['pattern'] for entry in key.values()}):
        expected = {label for label, entry in key.items() if entry['pattern'] == p}
        if not expected <= scores.keys():
            out[p] = {'verdict': 'undecided(incomplete)', 'missing': sorted(expected - scores.keys())}
            continue
        res = [(a['A'] > a['B']) - (a['A'] < a['B']) for (pp, _), a in pairs.items() if pp == p and 'A' in a and 'B' in a]
        wins, loss, ties = res.count(1), res.count(-1), res.count(0)
        names = {it for (arm, it) in items[p]}
        worse = [it for it in names if items[p][('B', it)] - items[p][('A', it)] >= 2]
        if ties > len(res) / 2: v = 'undecided(ties)'
        elif wins > len(res) / 2 and not worse: v = 'validated'
        elif loss >= wins: v = 'rejected'
        else: v = 'undecided'
        out[p] = {'A_wins': wins, 'B_wins': loss, 'ties': ties, 'items_A_clearly_worse': sorted(worse), 'verdict': v}
    return out
if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'plan':
        pats = sys.argv[2].split(','); labels, key = plan(pats, int(sys.argv[3]), int(sys.argv[4]))
        json.dump(key, open('ab-key.PRIVATE.json', 'w'), indent=1); print('\n'.join(labels))
    elif cmd == 'decide':
        key = json.load(open(sys.argv[2])); rows = list(csv.DictReader(open(sys.argv[3])))
        scores = {r['label']: {k: int(v) for k, v in r.items() if k != 'label'} for r in rows}
        print(json.dumps(decide(scores, key), ensure_ascii=False, indent=1))
