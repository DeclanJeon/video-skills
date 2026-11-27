#!/usr/bin/env python3
"""Validate the v2 package layout; this is not a behavioral or install check."""
import argparse
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from budget_descriptions import est
from leak_scan import scan_root

DIRECTOR = 'production-director'
DIRECTOR_HEADINGS = ('역할', '단계표', '콜시트', '게이트', '승인', '직행', '마감')
CREW_HEADINGS = ('역할', '입력', '절차', '산출물', '다른 부서와의 경계', '자체 점검', '납품')


def validate(root: Path) -> dict:
    findings = []

    def add(code: str, path: Path, message: str) -> None:
        findings.append(dict(code=code, path=str(path.relative_to(root)), message=message,
                             severity='warning' if code == 'SK05' else 'error'))

    manifest = root / 'manifest.json'
    skills = sorted(root.glob('*/SKILL.md'))
    installed = {file.parent.name for file in skills}
    try:
        declared = json.loads(manifest.read_text(encoding='utf-8'))['skills']
        if (not isinstance(declared, list) or not all(isinstance(x, str) for x in declared)
                or not declared or len(declared) != len(installed) or set(declared) != installed):
            raise ValueError('skills must list the skill folders exactly once')
    except (OSError, TypeError, KeyError, ValueError) as error:
        add('SK04', manifest, str(error))

    total = 0
    for file in skills:
        name = file.parent.name
        match = re.fullmatch(r'---\n(.*?)\n---\n(.*)', file.read_text(encoding='utf-8'), re.S)
        header, body = match.groups() if match else ('', '')
        fields = dict(re.findall(r'^([a-z-]+):\s*([^\n]+)$', header, re.M))
        if fields.get('name') != name:
            add('SK01', file, 'frontmatter name must match directory')
        headings = tuple(re.findall(r'^##\s+([^\n]+)$', body, re.M))
        expected = DIRECTOR_HEADINGS if name == DIRECTOR else CREW_HEADINGS
        if headings != expected:
            add('SK02', file, 'expected headings: ' + ', '.join(expected))
        desc = fields.get('description', '')
        tokens, words = est(desc)
        total += tokens
        word_limit = 80 if name == DIRECTOR else 40
        if (not desc or words > word_limit or len(re.findall('[가-힣]', desc)) > 120
                or (name != DIRECTOR and DIRECTOR not in desc)):
            add('SK03', file, 'description exceeds budget or lacks required role pointer')
        for doc in sorted(file.parent.rglob('*.md')):
            for link in re.findall(r'\]\(([^\s)]+)\)', doc.read_text(encoding='utf-8')):
                target = urlsplit(link)
                if not target.scheme and not target.netloc and target.path and not target.path.startswith('/'):
                    if not (doc.parent / unquote(target.path)).exists():
                        add('SK06', doc, f'broken link: {link}')
    if total > 2500:
        add('SK05', manifest, f'description estimate {total} > 2500')
    for layer, file, detail in scan_root(root):
        if Path(file).parts[0] in installed | {'tests', 'evals'}:
            add('SK07', root / file, f'{layer}: {detail}')
    return dict(skills=len(skills), estimated_description_tokens=total, findings=findings)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    if not args.root.is_dir():
        parser.error('--root must be a directory')
    result = validate(args.root.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else result)
    return int(any(item['severity'] == 'error' for item in result['findings']))


if __name__ == '__main__':
    raise SystemExit(main())
