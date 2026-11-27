"""Real file/ledger/index checks; no assertion of listening or legal clearance."""
from __future__ import annotations

import csv
from hashlib import sha256
from pathlib import Path
from typing import Final, Literal, TypeAlias, assert_never
import wave

import pytest
from cp2.ledger import Ledger
from test_index_lint import board as board, run

ROOT: Final = Path(__file__).resolve().parents[1]
Board: TypeAlias = tuple[
    Path, Path, Ledger, dict[str, str | int | list[str]], dict[str, str]
]
SoundChain: TypeAlias = tuple[Board, Path]


def write_wav(path: Path) -> None:
    """Write a tiny local synthetic fixture, not a sourced/cleared media asset."""
    with wave.open(str(path), 'wb') as stream:
        stream.setnchannels(1)
        stream.setsampwidth(2)
        stream.setframerate(8000)
        stream.writeframes(b'\x00\x00' * 80)


def test_source_manifest_can_carry_current_registration_pins() -> None:
    # Given: the actual machine-readable manifest template used in the fixture below.
    template = ROOT / 'sound-designer/assets/audio-source-manifest-template.csv'
    with template.open(newline='', encoding='utf-8') as stream:
        fields = next(csv.reader(stream))
    # When: checking that a source row can encode the documented registration DAG.
    required = {'cue_ref', 'rights_ref', 'review_ref', 'use_stage'}
    # Then: the real DictWriter can carry pins/usage without inventing a board column.
    assert required <= set(fields)


@pytest.fixture
def sound_chain(board: Board) -> SoundChain:
    project, _, book, header, row = board
    rights = project / 'rights-v1.md'
    rights.write_text('# Synthetic rights record; not legal clearance\n', encoding='utf-8')
    book.register('REF-MUS-01-rights', rights, 1, [])
    media = project / 'MUS-01-v1.wav'
    write_wav(media)
    book.register('MUS-01', media, 1, ['REF-MUS-01-rights@v1'])
    review = project / 'review-v1.md'
    review.write_text('# Fixture observation; not an audition\n', encoding='utf-8')
    book.register('REF-MUS-01-review', review, 1, ['MUS-01@v1'])
    template = ROOT / 'sound-designer/assets/audio-source-manifest-template.csv'
    with template.open(newline='', encoding='utf-8') as stream:
        fields = next(csv.reader(stream))
    manifest = project / 'sources-v1.csv'
    with manifest.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerow({'cue_id': 'MUS-01', 'cue_ref': 'MUS-01@v1',
                         'rights_ref': 'REF-MUS-01-rights@v1',
                         'review_ref': 'REF-MUS-01-review@v1', 'use_stage': 'post_only',
                         'local_path': media.name, 'sha256': sha256(media.read_bytes()).hexdigest()})
    book.register('REF-SOUND-SOURCES', manifest, 1,
                  ['MUS-01@v1', 'REF-MUS-01-rights@v1', 'REF-MUS-01-review@v1'])
    snd = project / 'SND-v2.md'
    snd.write_text('# Sound fixture\n', encoding='utf-8')
    book.register('SND', snd, 2, ['REF-SOUND-SOURCES@v1'])
    cnt = project / 'CNT-v1.md'
    cnt.write_text('## sound\n', encoding='utf-8')
    book.register('CNT', cnt, 1, ['SND@v2'])
    vpr = project / 'VPR-01-v1.md'
    vpr.write_text('# Prompt fixture\n', encoding='utf-8')
    book.register('VPR-01', vpr, 1, ['CNT@v1'])
    header['SND'] = 'SND@v2'
    row['music'] = 'MUS-01@v1'
    return board, media


@pytest.mark.parametrize('prefix,field', [('AMB', 'ambience'), ('SFX', 'sfx'), ('MUS', 'music')])
def test_audio_media_uses_existing_board_fields(board: Board, prefix: str, field: str) -> None:
    # Given: a real binary file registered under an existing sound prefix.
    project, _, book, _, row = board
    media = project / f'{prefix}-01.wav'
    write_wav(media)
    book.register(f'{prefix}-01', media, 1, [])
    row[field] = f'{prefix}-01@v1'
    # When: resolving the existing board field; rights/hearing are intentionally absent.
    findings = run(board)
    # Then: structural PASS alone does not certify acquired-source readiness.
    assert findings == set()


def test_current_source_dependency_graph_is_accepted(sound_chain: SoundChain) -> None:
    # Given: the acyclic rights -> media -> review -> manifest -> SND/CNT graph.
    fixture, _ = sound_chain
    # When: the actual board validator resolves current direct refs.
    findings = run(fixture)
    # Then: existing syntax/fields work; no new parser is required.
    assert findings == set()


def test_deleted_sound_file_is_blocked(sound_chain: SoundChain) -> None:
    # Given: registered bytes no longer exist.
    fixture, media = sound_chain
    media.unlink()
    # When / Then: the real index gate rejects the missing sound file.
    assert 'IX02' in run(fixture)


def test_changed_sound_bytes_are_blocked(sound_chain: SoundChain) -> None:
    # Given: the registered path is silently overwritten instead of versioned.
    fixture, media = sound_chain
    media.write_bytes(media.read_bytes() + b'changed')
    # When / Then: the real index gate rejects the current hash mismatch.
    assert 'IX03' in run(fixture)


@pytest.mark.parametrize('changed', ['rights', 'media', 'review'])
def test_sound_replacement_invalidates_consuming_artifacts(
    sound_chain: SoundChain, changed: Literal['rights', 'media', 'review']
) -> None:
    # Given: a current source/evidence chain and a new immutable version.
    fixture, _ = sound_chain
    project, _, book, _, _ = fixture
    match changed:
        case 'rights':
            path = project / 'rights-v2.md'
            path.write_text('# Changed fixture scope\n', encoding='utf-8')
            book.register('REF-MUS-01-rights', path, 2, [])
        case 'media':
            path = project / 'MUS-01-v2.wav'
            write_wav(path)
            book.register('MUS-01', path, 2, ['REF-MUS-01-rights@v1'])
        case 'review':
            path = project / 'review-v2.md'
            path.write_text('# Revised fixture observation\n', encoding='utf-8')
            book.register('REF-MUS-01-review', path, 2, ['MUS-01@v1'])
        case unreachable:
            assert_never(unreachable)
    # When: reloading persisted status, not just trusting an in-memory return.
    current = Ledger.load(project)
    # Then: source readiness cannot survive the changed proof/source snapshot.
    assert {aid for aid in ['REF-SOUND-SOURCES', 'SND', 'CNT', 'VPR-01']
            if current.status(aid) == 'stale'} == {'REF-SOUND-SOURCES', 'SND', 'CNT', 'VPR-01'}


def test_review_update_does_not_make_source_consume_its_own_review(sound_chain: SoundChain) -> None:
    # Given: review is downstream of the media, never the reverse.
    fixture, _ = sound_chain
    project, _, book, _, _ = fixture
    path = project / 'review-v2.md'
    path.write_text('# New observation only\n', encoding='utf-8')
    book.register('REF-MUS-01-review', path, 2, ['MUS-01@v1'])
    # When / Then: the underlying media remains current without a dependency cycle.
    assert Ledger.load(project).status('MUS-01') == 'current'


def test_new_review_rejects_stale_media_after_rights_update(sound_chain: SoundChain) -> None:
    # Given: new rights invalidate the media that consumed the old version.
    fixture, _ = sound_chain
    project, _, book, _, _ = fixture
    rights = project / 'rights-v2.md'
    rights.write_text('# Changed fixture permission scope\n', encoding='utf-8')
    book.register('REF-MUS-01-rights', rights, 2, [])
    review = project / 'review-v2.md'
    review.write_text('# New fixture observation\n', encoding='utf-8')
    # When / Then: the actual writer rejects a review consuming the stale source pin.
    with pytest.raises(ValueError, match='dependency must be a different current pinned artifact'):
        book.register('REF-MUS-01-review', review, 2, ['MUS-01@v1'])


def test_media_refresh_under_new_rights_allows_current_review(sound_chain: SoundChain) -> None:
    # Given: unchanged media bytes have a new version consuming the new rights pin.
    fixture, media = sound_chain
    project, _, book, _, _ = fixture
    rights = project / 'rights-v2.md'
    rights.write_text('# Changed fixture permission scope\n', encoding='utf-8')
    book.register('REF-MUS-01-rights', rights, 2, [])
    current_media = project / 'MUS-01-v2.wav'
    current_media.write_bytes(media.read_bytes())
    book.register('MUS-01', current_media, 2, ['REF-MUS-01-rights@v2'])
    review = project / 'review-v2.md'
    review.write_text('# New fixture observation\n', encoding='utf-8')
    # When: the new review consumes that current media version.
    book.register('REF-MUS-01-review', review, 2, ['MUS-01@v2'])
    # Then: it registers without a cycle or stale dependency.
    assert Ledger.load(project).status('REF-MUS-01-review') == 'current'


def test_index_gate_does_not_recursively_clear_deleted_rights(sound_chain: SoundChain) -> None:
    # Given: a rights attachment disappears without a version/mark-stale event.
    fixture, _ = sound_chain
    project, _, _, _, _ = fixture
    (project / 'rights-v1.md').unlink()
    # When: only the direct board-reference checker runs.
    findings = run(fixture)
    # Then: PASS is structural only; the documented separate proof-file check is essential.
    assert findings == set()
