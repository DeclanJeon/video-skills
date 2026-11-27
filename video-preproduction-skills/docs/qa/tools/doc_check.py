#!/usr/bin/env python3
"""설계 문서 기계 검사: 링크·앵커, 스킬 이름 일관성, ID 접두사 선언, REQ 추적."""
import re, sys, pathlib, json
ROOT = pathlib.Path(__file__).resolve().parents[3]
DOCS = [p for p in ROOT.rglob('*.md') if '/qa/tools/' not in str(p)]
SKILLS = ["production-director","concept-benchmark","story-writer","audience-reaction-qa","world-designer",
 "character-designer","costume-designer","production-designer","sound-designer","assistant-director",
 "performance-director","cinematographer","lighting-director","vfx-supervisor","film-editor",
 "storyboard-artist","image-prompt-engineer","video-prompt-engineer","production-qa","production-ledger"]
V1_OK = {"creative-production","concept-intake-design","topic-demand-selection","searching-social-media",
 "developing-video-synopses","orchestrating-video-preproduction","designing-video-character-sheets",
 "designing-character-personas","storyboarding-video","video-production-assets","camera-spatial-design",
 "ai-camera-control","camera-motion-reference-analysis","blender-previsualization","open-3d-production",
 "animatic-direction","silent-visual-storytelling","storytelling-with-still-images","silent-satire-animatic",
 "community-shorts-stills-pipeline","recording-production-history","suno-music","codex-imagen",
 "fal-video-production","flucto-media-research","higgsfield-generate"}
def slug(h):
    h = re.sub(r'[`*]', '', h.strip()).lower()
    h = re.sub(r'[^\w\- ]', '', h)
    return h.replace(' ', '-')
def anchors(p):
    out=set(); inside=False
    for line in p.read_text().splitlines():
        if line.startswith('```'): inside=not inside; continue
        m=re.match(r'^(#{1,6})\s+(.*)$', line)
        if m and not inside: out.add(slug(m.group(2)))
    return out
errs=[]
for p in DOCS:
    text=p.read_text()
    for m in re.finditer(r'\]\(([^)\s]+)\)', text):
        link=m.group(1)
        if link.startswith(('http','mailto')): continue
        path,_,frag=link.partition('#')
        tgt=(p.parent/path).resolve() if path else p
        if not tgt.exists(): errs.append(('LINK',str(p.relative_to(ROOT)),link)); continue
        if frag and tgt.suffix=='.md' and frag not in anchors(tgt):
            errs.append(('ANCHOR',str(p.relative_to(ROOT)),link))
# skill names: backticked kebab words that look like skills
found=set()
for p in [d for d in DOCS if '/docs/qa/' not in str(d)]:  # QA 보고는 발견 사항을 인용하므로 제외
    for m in re.finditer(r'`([a-z0-9]+(?:-[a-z0-9]+)+)`', p.read_text()):
        found.add((m.group(1), str(p.relative_to(ROOT))))
unknown=sorted({(n,f) for n,f in found if n not in SKILLS and n not in V1_OK and re.search(r'(director|designer|writer|qa|engineer|artist|editor|supervisor|ledger|benchmark|grapher)$',n)})
for n,f in unknown: errs.append(('SKILLNAME',f,n))
roster=(ROOT/'docs/design/02-crew-roster.md').read_text()
for s in SKILLS:
    if f'`{s}`' not in roster: errs.append(('ROSTER_MISSING','02-crew-roster.md',s))
# ID prefixes used vs declared in DES-03 table
des03=(ROOT/'docs/design/03-artifact-index.md').read_text()
declared=set(re.findall(r'`([A-Z]{2,4})(?:-|`|\.|@|x)', des03.split('## 2.')[0]))
declared|={'S','C','P','D','B','F'}
used=set()
for p in DOCS:
    if 'source-prompt' in p.name or '/docs/qa/' in str(p): continue
    for m in re.finditer(r'\b([A-Z]{2,4})-(?:\d|nn|F|self|REF|S0|CHR|LOC|\*|x)', p.read_text()):
        used.add(m.group(1))
skip={'REQ','DES','WO','EX','PP','SUP','PPL','RR','AP','CK','QA','SK','IX','TL','GEN','VPR','IMG','REF','TAK','SHT','RUL','QAR','CALL','DLV','AU','RFC','PRJ','UTF','SHA','AD'}
for u in sorted(used-declared-skip): errs.append(('ID_UNDECLARED','*',u))
for u in sorted({'GEN','VPR','IMG','REF','TAK','SHT','RUL','QAR'}-declared): errs.append(('ID_UNDECLARED_CORE','03',u))
# 백틱 안의 단독 대문자 토큰(예: `DLG`)도 선언 여부 확인
for p in DOCS:
    if 'source-prompt' in p.name or '/docs/qa/' in str(p): continue
    for m in re.finditer(r'`([A-Z]{3,4})`', p.read_text()):
        tok=m.group(1)
        if tok not in declared and tok not in skip|{'TBD','PASS','JSON','YAML','FAIL','UNVERIFIED','REVISE','RETHINK','DLV','CALL','ECU','OTS','MCU','EDL','BGM','TTS'}:
            errs.append(('BARE_TOKEN',str(p.relative_to(ROOT)),tok))
# REF_LEAK: scripts/leak_scan.py (단어·번역 개념·원문 조각 3겹, DES-09 §5 Q-5)
sys.path.insert(0, str(ROOT / 'scripts'))
import leak_scan
for layer, f, what in leak_scan.scan_root(ROOT): errs.append(('REF_LEAK/'+layer, f, what))
# REQ traceability
ov=(ROOT/'docs/design/00-overview.md').read_text()
for i in range(1,15):
    if f'REQ-{i:02d}' not in ov: errs.append(('REQ','00',f'REQ-{i:02d}'))
print(json.dumps(errs,ensure_ascii=False,indent=1)); print('errors:',len(errs))
sys.exit(1 if errs else 0)
