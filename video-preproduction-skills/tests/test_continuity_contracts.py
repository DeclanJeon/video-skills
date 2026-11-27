"""Exercise the existing ledger/index seam with the actual CTY template.

Natural-language continuity decisions are evaluated by behavioral QA, not here.
"""
from pathlib import Path
from typing import Final, TypeAlias

import pytest
from cp2.ledger import Ledger
from test_index_lint import board as board, run

ROOT: Final = Path(__file__).resolve().parents[1]
Board: TypeAlias = tuple[
    Path, Path, Ledger, dict[str, str | int | list[str]], dict[str, str]
]


def test_cty_cut_contract_resolves_from_existing_continuity_column(board: Board) -> None:
    # Given: a registered real template with its cut anchor filled in.
    project, _, book, _, row = board
    template = (ROOT / 'assistant-director/assets/CTY-template.md').read_text(encoding='utf-8')
    path = project / 'CTY.md'
    path.write_text(template.replace('Snn-Cnn', 'S01-C01'), encoding='utf-8')
    book.register('CTY', path, 1, [])
    row['continuity'] = 'CTY@v1#S01-C01'

    # When: the existing board gate resolves the new per-cut contract pin.
    findings = run(board)

    # Then: no new column or pin parser is necessary.
    assert findings == set()


@pytest.mark.parametrize('pin, expected', [
    ('CTY@v1#S01-C99', 'IX02'),
    ('CTY@draft#S01-C01', 'IX03'),
    ('CTY#S01-C01', 'IX07'),
])
def test_invalid_cut_contract_pins_are_blocked(board: Board, pin: str, expected: str) -> None:
    # Given: a registered CTY contract and a bad consuming reference.
    project, _, book, _, row = board
    path = project / 'CTY.md'
    path.write_text('## S01-C01\n', encoding='utf-8')
    book.register('CTY', path, 1, [])
    row['continuity'] = pin

    # When: the board gate resolves the reference.
    findings = run(board)

    # Then: the existing gate rejects it for the specific reason.
    assert expected in findings


def test_changed_cty_blocks_old_contract_reference(board: Board) -> None:
    # Given: a board referencing v1 and a newly registered contract version.
    project, _, book, _, row = board
    first = project / 'CTY-v1.md'
    first.write_text('## S01-C01\n', encoding='utf-8')
    book.register('CTY', first, 1, [])
    row['continuity'] = 'CTY@v1#S01-C01'
    second = project / 'CTY-v2.md'
    second.write_text('## S01-C01\nUpdated state.\n', encoding='utf-8')
    book.register('CTY', second, 2, [])

    # When: the board gate inspects the old reference.
    findings = run(board)

    # Then: the superseded contract cannot be accepted as current.
    assert 'IX03' in findings
