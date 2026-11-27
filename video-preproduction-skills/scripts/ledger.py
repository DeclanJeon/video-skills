#!/usr/bin/env python3
"""Read or update the local production ledger as its designated single writer."""
import argparse
import json
from pathlib import Path

from cp2.ledger import Ledger


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True, type=Path)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('status').add_argument('artifact')
    commands.add_parser('mark-stale').add_argument('ref')
    register = commands.add_parser('register')
    register.add_argument('artifact')
    register.add_argument('path', type=Path)
    register.add_argument('version', type=int)
    register.add_argument('--consumes', action='append', default=[])
    args = parser.parse_args()
    try:
        book = Ledger.load(args.project)
        if args.command == 'register':
            book.register(args.artifact, args.path, args.version, args.consumes)
            result = {'status': book.status(args.artifact)}
        elif args.command == 'mark-stale':
            result = {'stale': book.mark_stale(args.ref)}
        else:
            result = {'status': book.status(args.artifact)}
    except (OSError, ValueError, TypeError) as error:
        parser.error(str(error))
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
