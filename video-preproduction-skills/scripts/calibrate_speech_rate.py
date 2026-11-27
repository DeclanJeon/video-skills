#!/usr/bin/env python3
"""실측 보정 (RR-3). 입력 CSV: lang,text,seconds,pauses,mode  (seconds=발화 구간 실측, 생성 테이크·TTS 파일에서 측정)
언어별 표본 >=30건일 때만 제안값을 낸다: normal=P75, heated=P90, block=max(P97, heated*1.05). 부족하면 'insufficient'."""
import csv, sys, json, statistics, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from cp2.speech import count_units, rate, load_rates
MIN_N = 30
def pct(xs, p):
    xs = sorted(xs); k = (len(xs) - 1) * p; f = int(k); c = min(f + 1, len(xs) - 1)
    return xs[f] + (xs[c] - xs[f]) * (k - f)
def calibrate(rows, pause_s=0.3):
    by = {}
    for r in rows:
        u, ok = count_units(r['text'], r['lang'])
        if not ok: continue
        by.setdefault(r['lang'], []).append(rate(u, float(r['seconds']), int(r.get('pauses') or 0), pause_s))
    out = {}
    for lang, xs in by.items():
        if len(xs) < MIN_N: out[lang] = {'status': 'insufficient', 'n': len(xs), 'need': MIN_N}; continue
        h = round(pct(xs, .90), 2)
        out[lang] = {'status': 'proposed', 'n': len(xs), 'normal': round(pct(xs, .75), 2), 'heated': h,
                     'block': round(max(pct(xs, .97), h * 1.05), 2), 'median': round(statistics.median(xs), 2)}
    return out
if __name__ == '__main__':
    rows = list(csv.DictReader(open(sys.argv[1], newline='', encoding='utf-8')))
    res = calibrate(rows, load_rates()['pause_seconds']); print(json.dumps(res, ensure_ascii=False, indent=1))
