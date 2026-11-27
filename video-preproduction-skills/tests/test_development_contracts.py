from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('skill,markers', [
    ('concept-benchmark', ('BRF', 'BMK', 'BOR', 'unknown', 'observed', '차용/변주/고유')),
    ('story-writer', ('SYN', 'PLT', 'SCR', 'Dnnn', '±10%', 'QA1')),
    ('audience-reaction-qa', ('hypothesis', 'reviewer_mode', 'REVISE', 'RETHINK', 'fix_id')),
])
def test_contract_is_authored_but_not_auto_enabled(skill, markers):
    body = (ROOT / skill / 'SKILL.md').read_text()
    assert '미구현 골격' not in body
    assert 'disable-model-invocation: true' in body
    assert all(m in body for m in markers)
