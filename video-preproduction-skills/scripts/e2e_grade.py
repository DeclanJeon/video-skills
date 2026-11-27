#!/usr/bin/env python3
"""Aggregate manually evidenced WO-13 scores; does not run or judge agents."""
import argparse
import json
import math
from pathlib import Path
import re

SCENARIOS = ('X-1', 'X-2', 'X-3')
VARIANTS = ('v1', 'v2')
CHECKS = {str(i) for i in range(1, 14)}


def grade(root: Path, rows: list[dict]) -> dict:
    root = root.resolve(strict=True)
    issues = []
    pairs = {}
    run_ids = set()
    output = {}
    for row in rows:
        key = row.get('scenario'), row.get('variant')
        if key[0] not in SCENARIOS or key[1] not in VARIANTS or key in pairs:
            issues.append(f'unexpected or duplicate run: {key}')
            continue
        pairs[key] = row
        for name in ('run_id', 'reviewer_id', 'model', 'reasoning'):
            if not isinstance(row.get(name), str) or not row[name].strip():
                issues.append(f'{key}: missing {name}')
        if row.get('run_id') in run_ids or row.get('run_id') == row.get('reviewer_id'):
            issues.append(f'{key}: duplicate run or non-independent reviewer')
        run_ids.add(row.get('run_id'))
        if not re.fullmatch(r'[0-9a-f]{64}', str(row.get('brief_sha256', ''))):
            issues.append(f'{key}: invalid brief hash')
        for name in ('input_tokens', 'output_tokens'):
            if type(row.get(name)) is not int or row[name] <= 0:
                issues.append(f'{key}: invalid {name}')
        elapsed, conti = row.get('elapsed_s'), row.get('conti_s')
        if (not all(type(t) in (int, float) and math.isfinite(t) for t in (elapsed, conti))
                or not 0 <= conti <= elapsed or elapsed <= 0):
            issues.append(f'{key}: invalid timing metrics')
        checks = row.get('checks')
        if not isinstance(checks, dict) or checks.keys() != CHECKS:
            issues.append(f'{key}: all 13 rubric entries required')
            continue
        for n, check in checks.items():
            if not isinstance(check, dict) or type(check.get('score')) is not int or check['score'] not in (0, 1):
                issues.append(f'{key}/{n}: score must be 0 or 1')
                continue
            ref = check.get('evidence')
            path = (root / ref).resolve() if isinstance(ref, str) and ref.strip() and not Path(ref).is_absolute() else root
            if not path.is_relative_to(root) or not path.is_file() or not path.stat().st_size:
                issues.append(f'{key}/{n}: missing, empty or out-of-root evidence')
    for key, row in pairs.items():
        if row.get('reviewer_id') in run_ids:
            issues.append(f'{key}: reviewer is an execution session')
    for scenario in SCENARIOS:
        one, two = (pairs.get((scenario, name)) for name in VARIANTS)
        if one is None or two is None:
            issues.append(f'{scenario}: requires both v1 and v2 evidence')
        elif any(one.get(field) != two.get(field) for field in ('model', 'reasoning', 'brief_sha256')):
            issues.append(f'{scenario}: runs are not comparable')
    if issues:
        return dict(status='unverified', issues=issues, scenarios=output)
    for scenario in SCENARIOS:
        runs = {name: pairs[(scenario, name)] for name in VARIANTS}
        scores = {name: sum(c['score'] for c in run['checks'].values()) for name, run in runs.items()}
        metrics = {name: {f: run[f] for f in ('input_tokens','output_tokens','elapsed_s','conti_s')}
                   for name, run in runs.items()}
        output[scenario] = dict(scores=scores, metrics=metrics, meets_threshold=scores['v2'] >= 12 and scores['v2'] > scores['v1'])
    return dict(status='threshold_met' if all(x['meets_threshold'] for x in output.values()) else 'threshold_not_met',
                issues=[], scenarios=output)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence-root', type=Path, required=True)
    parser.add_argument('--runs', type=Path, required=True)
    args = parser.parse_args()
    try:
        rows = json.loads(args.runs.read_text(encoding='utf-8'))
        if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
            raise ValueError('runs must be a JSON array of objects')
        result = grade(args.evidence_root, rows)
    except (OSError, ValueError, TypeError, KeyError, RuntimeError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return {'threshold_met': 0, 'threshold_not_met': 1, 'unverified': 3}[result['status']]


if __name__ == '__main__':
    raise SystemExit(main())
