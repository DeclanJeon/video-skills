"""Structural regression checks only; these do not prove agent compliance or media QA."""
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / 'docs/design/13-execution-safety-contract.md'


@pytest.mark.parametrize('field', [
    'visual_style', 'voice_direction', 'first_allowed_cut', 'allowed_reference_ids',
    'audio_policy', 'dialogue_source', 'pilot_result', 'artifact_sha256',
    'human_listening', 'boundary_playback', 'reference_cut', 'observed_interval',
    'resource_busy', 'revision_conflict', 'queue_full',
])
def test_contract_requires_failure_specific_fields(field: str) -> None:
    assert CONTRACT.is_file(), 'Missing execution safety contract'
    assert field in CONTRACT.read_text(encoding='utf-8')


@pytest.mark.parametrize('skill', [
    'production-director', 'concept-benchmark', 'image-prompt-engineer',
    'video-prompt-engineer', 'storyboard-artist', 'sound-designer', 'production-qa',
])
def test_owning_departments_reach_safety_contract(skill: str) -> None:
    assert '13-execution-safety-contract.md' in (ROOT / skill / 'SKILL.md').read_text()


def test_contract_has_explicit_review_boundary() -> None:
    assert CONTRACT.is_file()
    text = CONTRACT.read_text()
    assert 'review/' in text and 'final/' in text
    assert 'ASR' in text and '미검증' in text


def test_template_keeps_style_neutral_and_pilot_undecided() -> None:
    path = ROOT / 'production-director/assets/execution-safety-template.json'
    assert path.is_file()
    import json
    data = json.loads(path.read_text())
    assert data['visual_style']['value'] is None
    assert data['voice_direction']['value'] is None
    assert data['pilot_result']['status'] == 'not_assessed'
    assert data['pilot_result']['decision_ref'] is None
    assert data['delivery_review']['human_listening']['status'] == 'unverified'


def test_optional_checks_have_explicit_skip_paths() -> None:
    text = CONTRACT.read_text(encoding='utf-8')
    assert '기존 산출물로 판단 가능하면 추가 산출물을 만들지 않는다' in text
    assert '리듬을 판단할 수 없는 구간만 임시 편집' in text
    assert '`not_needed`' in text
    assert '판단이 불확실하고 실패 시 재작업이 큰 경우' in text
    assert '판정 근거는 기존 문서 한 줄로 충분' in text
