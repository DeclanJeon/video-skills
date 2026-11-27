#!/usr/bin/env python3
"""Read-only local inventory; never installs, edits configuration or approves cutover."""
import argparse
import json
from pathlib import Path
import re


def preflight(source: Path, target: Path, equipment: list[str]) -> list[dict]:
    manifest = json.loads((source/'manifest.json').read_text(encoding='utf-8'))
    findings = []

    def add(code, target_name, detail):
        findings.append(dict(code=code, target=target_name, detail=detail))

    if manifest.get('version') != '1.0.0' or manifest.get('status') != 'released':
        add('package', str(source), 'manifest is not a release; WO-13 evidence and cutover authorization are separate')
    names = manifest['skills']
    if not isinstance(names, list) or not names or any(
        not isinstance(name, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) for name in names
    ) or len(set(names)) != len(names):
        raise ValueError('invalid manifest skills list')
    for name in names:
        folder = source/name
        if not (folder/'SKILL.md').is_file():
            add('source', name, 'SKILL.md unavailable')
        dest = target/name
        if dest.exists() or dest.is_symlink():
            if not (dest.is_symlink() and (folder/'SKILL.md').is_file() and dest.resolve() == folder.resolve()):
                add('collision', name, 'path is already occupied, including dangling links')
    for name in sorted(set(equipment)):
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name):
            raise ValueError(f'invalid equipment name: {name}')
        if not (target/name/'SKILL.md').is_file():
            add('equipment', name, 'not found at this target; runtime support remains unverified')
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--target', type=Path, required=True)
    parser.add_argument('--equipment', action='append', default=[])
    args = parser.parse_args()
    try:
        findings = preflight(args.source, args.target, args.equipment)
    except (OSError, KeyError, ValueError, TypeError) as error:
        parser.error(str(error))
    print(json.dumps(findings, ensure_ascii=False, indent=2))
    return int(bool(findings))


if __name__ == '__main__':
    raise SystemExit(main())
