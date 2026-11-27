"""Read sidecar-defined prompt blocks without changing dialogue text."""
from hashlib import sha256
import re


def split_blocks(text: str, markers: dict[str, str]) -> dict[str, str]:
    by_marker = {}
    for block, marker in markers.items():
        marker = marker.strip()
        if not marker or marker in by_marker or len(marker.splitlines()) != 1:
            raise ValueError('each block marker must be unique and occupy one line')
        by_marker[marker] = block
    parts: dict[str, list[str]] = {}
    current = None
    for line in text.splitlines():
        if line.strip() in by_marker:
            current = by_marker[line.strip()]
            if current in parts:
                raise ValueError(f'repeated marker for {current}')
            parts[current] = []
        elif current is not None:
            parts[current].append(line)
    return {key: '\n'.join(lines).strip() for key, lines in parts.items()}


_QUOTES = re.compile(r'"([^"\n]*)"|“([^”\n]*)”|「([^」\n]*)」')


def extract_quotes(text: str) -> list[str]:
    return [next(group for group in match.groups() if group is not None) for match in _QUOTES.finditer(text)]


def normalized_hash(block: str) -> str:
    return sha256(' '.join(block.split()).encode('utf-8')).hexdigest()
