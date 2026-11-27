#!/usr/bin/env python3
"""레퍼런스 내용 누출 검사 (DES-09 §5 Q-5, RR-7). 세 겹:
 L-A 고유 단어(leak-terms.txt)  L-B 번역·의역 개념(leak-concepts.txt)  L-C 원문 조각 겹침(영어 4단어·중국어 6자 shingle)
레퍼런스 폴더(docs/examples/<ref>/) 안은 검사하지 않는다. 종료 코드 1=누출 발견."""
import re, sys, pathlib, json
TEXT_EXT = {'.md', '.json', '.csv', '.txt', '.py', '.yaml', '.yml'}
EXEMPT = {'leak_scan.py', 'doc_check.py', 'test_leak_scan.py'}
def _norm(s): return re.sub(r'\s+', ' ', s.lower())
def _en_shingles(s, n=4):
    w = re.findall(r"[a-z]+(?:'[a-z]+)?", s.lower()); return {' '.join(w[i:i+n]) for i in range(len(w) - n + 1)}
def _zh_shingles(s, n=6):
    z = re.sub(r'[^\u4e00-\u9fff]', '', s); return {z[i:i+n] for i in range(len(z) - n + 1)}
def _lines(p): return [l.strip() for l in p.read_text().splitlines() if l.strip() and not l.startswith('#')]
def load_ref(ref_dir):
    terms = [t.lower() for t in _lines(ref_dir / 'leak-terms.txt')] if (ref_dir / 'leak-terms.txt').exists() else []
    cf = ref_dir / 'leak-concepts.txt'
    concepts = [[x.lower() for x in l.split('|')] for l in _lines(cf)] if cf.exists() else []
    en, zh = set(), set()
    for src in ref_dir.glob('source-*'):
        t = src.read_text(); en |= _en_shingles(t); zh |= _zh_shingles(t)
    return terms, concepts, en, zh
def scan_text(text, ref):
    terms, concepts, en, zh = ref; low = _norm(text); hits = []
    hits += [('L-A', t) for t in terms if t in low]
    hits += [('L-B', c[0]) for c in concepts if any(x in low for x in c)]
    e = _en_shingles(text) & en
    if len(e) >= 2: hits.append(('L-C', f'en shingles x{len(e)}: {sorted(e)[0]!r}'))
    z = _zh_shingles(text) & zh
    if len(z) >= 2: hits.append(('L-C', f'zh shingles x{len(z)}'))
    return hits
def scan_root(root):
    root = pathlib.Path(root); found = []
    for ref_file in root.glob('docs/examples/*/leak-terms.txt'):
        home = ref_file.parent; ref = load_ref(home)
        for f in root.rglob('*'):
            if (not f.is_file() or f.suffix not in TEXT_EXT or home in f.parents or f.name in EXEMPT
                    or '/.git/' in str(f) or '/__pycache__/' in str(f)): continue
            for layer, what in scan_text(f.read_text(errors='ignore'), ref):
                found.append((layer, str(f.relative_to(root)), what))
    return found
if __name__ == '__main__':
    root = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else pathlib.Path(__file__).resolve().parents[1]
    found = scan_root(root)
    print(json.dumps(found, ensure_ascii=False, indent=1)); print('leaks:', len(found)); sys.exit(1 if found else 0)
