#!/usr/bin/env python3
"""v2 스킬 설명문의 상시 컨텍스트 부하 추정 (RR-2). 추정식은 v1 기준선 측정과 동일: 영어 단어*1.3 + 한글 글자*0.9."""
import json, re, sys, pathlib
HERE = pathlib.Path(__file__).resolve().parents[1]
def est(s):
    w = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9\-'/_.]*", s)); h = len(re.findall(r'[가-힣]', s))
    return round(w * 1.3 + h * 0.9), w
def main():
    src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / 'docs/design/skill-descriptions.json'
    d = json.loads(src.read_text()); limit_crew, limit_dir, budget = 40, 80, 2500
    tot, errs = 0, []
    for name, desc in d.items():
        n, w = est(desc); tot += n
        lim = limit_dir if name == 'production-director' else limit_crew
        if w > lim: errs.append(f'SK03 {name}: {w} words > {lim}')
        if name != 'production-director' and 'production-director' not in desc: errs.append(f'SK03 {name}: missing "production-director"')
        print(f'{name:24s} words={w:3d} tokens~{n}')
    print(f'TOTAL skills={len(d)} tokens~{tot} budget={budget}')
    if tot > budget: errs.append(f'SK05 total {tot} > {budget}')
    for e in errs: print(e)
    return 1 if errs else 0
if __name__ == '__main__': sys.exit(main())
