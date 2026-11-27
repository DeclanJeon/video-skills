import pytest
from cp2.prompt_parse import extract_quotes, normalized_hash, split_blocks


def test_multilingual_literal_markers():
    assert split_blocks('【概览】\r\n概要\r\n  【반응】  \r\n고개를 든다.',
                        {'B1': '【概览】', 'B3': '【반응】'}) == {'B1': '概要', 'B3': '고개를 든다.'}


def test_only_standalone_markers_are_split():
    assert split_blocks('Overview\nSay Overview aloud.\nStill here.', {'B1': 'Overview'}) == {
        'B1': 'Say Overview aloud.\nStill here.'}


def test_repeated_marker_is_ambiguous():
    with pytest.raises(ValueError):
        split_blocks('Overview\na\nOverview\nb', {'B1': 'Overview'})


def test_quote_styles_preserve_content():
    assert extract_quotes('She said “I won’t.” 「잠깐.」 "Now!"') == ['I won’t.', '잠깐.', 'Now!']


def test_hash_normalizes_only_whitespace():
    assert normalized_hash('one   two\r\n three ') == normalized_hash('one two three')
    assert normalized_hash('one two!') != normalized_hash('one two')
