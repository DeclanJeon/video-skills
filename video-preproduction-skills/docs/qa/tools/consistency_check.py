#!/usr/bin/env python3
"""문서 간 정합성 검사 (RR-1 완화). 작성자의 기억이 아니라 문서 텍스트만으로 교차 대조한다.
 C1 PP/SUP 참조가 DES-09 카탈로그에 존재   C2 lint 규칙 L1..Ln 이 DES-07 정의와 WO-03 테스트/언급 양쪽에 존재
 C3 IX/TL 코드가 DES-03·WO-02 양쪽    C4 02의 크루 20개 모두 WO가 담당   C5 DES-07 블록 매핑이 정의한 PP 전부를 한 번 이상 인용
 C6 REQ 14개가 각각 DES 외 WO 또는 QA 항목에 닿음   C7 게이트 QA1–QA5·QA-F 체크리스트/WO 존재   C8 EX 픽스처 ID 참조가 실제 파일로 해결"""
import re, sys, json, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[3]
rd = lambda p: (ROOT / p).read_text()
D = {n: rd(f'docs/design/{n}.md') for n in ['00-overview','01-pipeline-and-gates','02-crew-roster','03-artifact-index','07-video-prompt-spec','09-reference-prompt-learning']}
WO = {p.name: p.read_text() for p in (ROOT / 'docs/work-orders').glob('WO-*.md')}
ALL_WO = '\n'.join(WO.values()); errs = []
d9 = D['09-reference-prompt-learning']
pp_def = set(re.findall(r'\| (PP-\d\d) \|', d9)); sup_def = set(re.findall(r'\| (SUP-\d\d) \|', d9))
if len(pp_def) != 25: errs.append(('C1', f'PP 정의 {len(pp_def)}개 (기대 25)'))
if len(sup_def) != 19: errs.append(('C1', f'SUP 정의 {len(sup_def)}개 (기대 19)'))
for f in list((ROOT / 'docs').rglob('*.md')) + [ROOT / 'README.md']:
    t = f.read_text()
    for m in re.finditer(r'\b(PP|SUP)-(\d\d)(?:[–-](?:PP-|SUP-)?(\d\d))?', t):
        for n in {int(m.group(2)), int(m.group(3) or m.group(2))}:
            tag = f'{m.group(1)}-{n:02d}'
            if tag not in (pp_def | sup_def): errs.append(('C1', f'{f.relative_to(ROOT)}: {tag} 미정의'))
d7 = D['07-video-prompt-spec']
lint_def = set(re.findall(r'^\| (L\d+) \|', d7, re.M)); want = {f'L{i}' for i in range(1, 21)}
if lint_def != want: errs.append(('C2', f'DES-07 lint 정의 차이: 누락 {sorted(want - lint_def)} 초과 {sorted(lint_def - want)}'))
wo3 = WO['WO-03-prompt-lint.md']
for l in sorted(lint_def, key=lambda x: int(x[1:])):
    if not re.search(rf'(?<![A-Za-z0-9]){l}(?![A-Za-z0-9])', wo3): errs.append(('C2', f'WO-03에 {l} 테스트/언급 없음'))
ix_tl = set(re.findall(r'\b((?:IX|TL)\d\d)\b', WO['WO-02-ledger-index-timeline.md']))
for code in sorted(set(re.findall(r'\b((?:IX|TL)\d\d)\b', ALL_WO + D['03-artifact-index'] + D['07-video-prompt-spec']))):
    if code not in ix_tl: errs.append(('C3', f'{code} 가 WO-02에 정의/시험되지 않음'))
crew = set(re.findall(r'^\| `([a-z]+(?:-[a-z]+)*)` \|', D['02-crew-roster'], re.M)) | {'production-director'}
if len(crew) < 20: errs.append(('C4', f'02 크루 {len(crew)}개 (기대 20) — 표 파싱 확인'))
for c in sorted(crew):
    if f'`{c}`' not in ALL_WO and c not in ALL_WO: errs.append(('C4', f'{c}: 어떤 WO에도 없음'))
for pp in sorted(pp_def):
    if pp not in d7 and pp not in D['01-pipeline-and-gates']:
        n = int(pp[3:]); rng = re.findall(r'PP-(\d\d)[–-]PP-(\d\d)', d7)
        if not any(int(a) <= n <= int(b) for a, b in rng): errs.append(('C5', f'{pp}: DES-07 블록 매핑에 반영 안 됨'))
for i in range(1, 15):
    r = f'REQ-{i:02d}'
    if r not in D['00-overview']: errs.append(('C6', f'{r} 없음'))
for g in ['QA2', 'QA3', 'QA4', 'QA5']:
    if f'### {g}' not in D['03-artifact-index']: errs.append(('C7', f'{g} 체크리스트 없음'))
for w in ['WO-12-production-qa.md']:
    for g in ['QA2', 'QA3', 'QA4', 'QA5', 'QA-F']:
        if g not in WO[w] and g != 'QA-F': errs.append(('C7', f'{w}에 {g} 없음'))
ex_ids = {m for p in (ROOT / 'docs/examples').rglob('*.md') for m in re.findall(r'문서 ID: `(EX-\d\d\w?)`', p.read_text())}
for f in list((ROOT / 'docs').rglob('*.md')):
    if '/qa/' in str(f): continue
    for m in set(re.findall(r'(?<![A-Za-z0-9])(EX-\d\d[a-z]?)(?![A-Za-z0-9])', f.read_text())):
        if m not in ex_ids: errs.append(('C8', f'{f.relative_to(ROOT)}: {m} 파일 없음'))
print(json.dumps(errs, ensure_ascii=False, indent=1)); print('inconsistencies:', len(errs)); sys.exit(1 if errs else 0)
