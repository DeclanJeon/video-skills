#!/usr/bin/env python3
"""Check a QA3 PNG bundle and bind a reviewer declaration to its contents."""
import argparse
import csv
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import re

from cp2.ids import parse_cut

VISUAL_CHECKS = ('identity', 'continuity', 'framing', 'legibility', 'unwanted_text')


def snapshot(root: Path, spec: dict) -> str:
    from PIL import Image

    root = root.resolve(strict=True)
    hashes: dict[str, str] = {}

    def read(name: str, png: bool = False) -> bytes:
        if not isinstance(name, str) or Path(name).is_absolute():
            raise ValueError('use project-relative file paths')
        path = (root / name).resolve(strict=True)
        relative = path.relative_to(root).as_posix()
        if not path.is_file() or relative in hashes:
            raise ValueError(f'expected a distinct file: {name}')
        data = path.read_bytes()
        if png:
            with Image.open(BytesIO(data)) as image:
                if image.format != 'PNG' or getattr(image, 'n_frames', 1) != 1:
                    raise ValueError(f'expected a static PNG: {name}')
                image.load()
        hashes[relative] = sha256(data).hexdigest()
        return data

    expected = []
    index = read(spec['index']).decode('utf-8-sig')
    for row in csv.DictReader(index.splitlines()):
        cut = row['cut']
        if parse_cut(cut)[2] is not None:
            raise ValueError(f'index row does not name a cut: {cut}')
        for panel in row['panels'].split(';'):
            panel = panel.strip()
            if re.fullmatch(r'P[1-9][0-9]*', panel):
                panel = f'{cut}-{panel}'
            if not re.fullmatch(rf'{re.escape(cut)}-P[1-9][0-9]*', panel):
                raise ValueError(f'invalid panel: {panel}')
            expected.append(panel)
    actual = []
    for sheet in spec['sheets']:
        read(sheet['image'], png=True)
        cells = sheet['cells']
        if not 1 <= len(cells) <= 8:
            raise ValueError('sheet needs 1–8 cells')
        for position, cell in enumerate(cells, 1):
            if cell['cell'] != f'cell-{position:02}':
                raise ValueError('cell numbering is not sequential')
            panel = cell['panel']
            if Path(cell['image']).name != f'{panel}.png':
                raise ValueError(f'panel filename does not match its ID: {panel}')
            read(cell['image'], png=True)
            actual.append(panel)
    if not expected or expected != actual or len(set(actual)) != len(actual):
        raise ValueError('panel coverage or order does not match the index')
    references = spec.get('references', [])
    if not isinstance(references, list):
        raise ValueError('references must list project-relative PNG paths')
    for reference in references:
        read(reference, png=True)
    payload = {'files': hashes, 'index': spec['index'], 'sheets': spec['sheets'],
               'evidence_kind': spec.get('evidence_kind'), 'references': references}
    return sha256(json.dumps(payload, sort_keys=True, allow_nan=False).encode()).hexdigest()


def check(root: Path, spec: dict) -> dict:
    try:
        digest = snapshot(root, spec)
    except ImportError:
        return {'status':'unverified', 'reason':'Pillow is unavailable; PNG evidence was not decoded'}
    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as error:
        return {'status':'blocked', 'reason':str(error)}
    if spec.get('evidence_kind') != 'production':
        return {'status':'unverified', 'snapshot':digest,
                'reason':'final image evidence not declared; previs is spatial evidence only'}
    review = spec.get('review')
    result = {'status':'unverified', 'snapshot':digest, 'reason':'a visual review of this snapshot is required'}
    if not isinstance(review, dict) or review.get('snapshot') != digest or review.get('mode') not in {'inline','independent'}:
        return result
    reviewer, checks = review.get('reviewer'), review.get('checks')
    if not isinstance(reviewer, str) or not reviewer.strip() or not isinstance(checks, dict):
        return result
    if any(not isinstance(checks.get(key), dict) or not isinstance(checks[key].get('note'), str)
           or not checks[key]['note'].strip() for key in VISUAL_CHECKS):
        return result
    verdicts = [checks[key].get('verdict') for key in VISUAL_CHECKS]
    if 'FAIL' in verdicts:
        return {'status':'blocked', 'snapshot':digest, 'reason':'review records a visual failure'}
    if all(value == 'PASS' for value in verdicts):
        return {'status':'recorded_pass', 'snapshot':digest, 'reviewer_mode':review['mode']}
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, required=True)
    parser.add_argument('--spec', type=Path, required=True)
    args = parser.parse_args()
    try:
        spec = json.loads(args.spec.read_text(encoding='utf-8'))
        if not isinstance(spec, dict):
            raise ValueError('expected a JSON object')
        report = check(args.project, spec)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return {'recorded_pass':0, 'blocked':1, 'unverified':3}[report['status']]


if __name__ == '__main__':
    raise SystemExit(main())
