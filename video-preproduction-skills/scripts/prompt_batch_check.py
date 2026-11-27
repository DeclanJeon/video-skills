#!/usr/bin/env python3
"""Check a complete video-prompt batch without generating media or modifying files."""
import argparse
import csv
from decimal import InvalidOperation
import json
from pathlib import Path

from cp2.prompt_batch import check_batch
from prompt_lint import lint


def check(project: Path, manifest: Path) -> dict:
    root = project.resolve(strict=True)

    def local(path) -> Path:
        candidate = (root / path).resolve(strict=True)
        if not candidate.is_relative_to(root) or not candidate.is_file():
            raise ValueError(f'expected project-local file: {path}')
        return candidate

    plan = json.loads(local(manifest.resolve()).read_text(encoding='utf-8'))
    with local(plan['index']).open(newline='', encoding='utf-8-sig') as stream:
        board = list(csv.DictReader(stream))
    packets, findings = [], {}
    for entry in plan['packets']:
        side = json.loads(local(entry['map']).read_text(encoding='utf-8'))
        text = local(entry['prompt']).read_text(encoding='utf-8')
        packets.append(side)
        findings.setdefault(side['gen'], []).extend(lint('video', text, side, root))
    return dict(batch=check_batch(board, packets, plan['runtime_s']), packets=findings)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    try:
        result = check(args.project, args.manifest)
    except (OSError, ValueError, TypeError, KeyError, InvalidOperation, AttributeError) as error:
        parser.error(str(error))
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for key, rows in (('batch', result['batch']), *result['packets'].items()):
            print(f'{key}: {len(rows)} findings')
            for row in rows:
                print(f'  {row["severity"]} {row["code"]}: {row["message"]}')
    findings = result['batch'] + [row for rows in result['packets'].values() for row in rows]
    if any(row['severity'] == 'error' for row in findings):
        return 1
    return 3 if any(row['severity'] == 'unverified' for row in findings) else 0


if __name__ == '__main__':
    raise SystemExit(main())
