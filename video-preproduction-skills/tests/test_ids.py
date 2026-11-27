import pytest

from cp2.ids import Ref, RefError, parse_cut, parse_ref


def test_pinned_anchor():
    assert parse_ref('CHR-01@v2#anchor') == Ref('CHR', '01', None, 2, 'anchor', None)


def test_wardrobe_and_take_suffix():
    assert parse_ref('WRD-02a').suffix == 'a'
    assert parse_ref('TAK-01-2@v1').suffix == '-2'


def test_anchor_item_and_draft():
    result = parse_ref('CNT@draft#S01-C02.perf')
    assert result.draft and result.version is None
    assert (result.anchor, result.item) == ('S01-C02', 'perf')
    assert parse_ref('PLT@v2.B03').item == 'B03'
    assert not parse_ref('CNT').draft


def test_planned_image_ids_and_final_report():
    assert parse_ref('IMG-REF-CHR-01-front').suffix == '-REF-CHR-01-front'
    assert parse_ref('IMG-S01-C02-P1').prefix == 'IMG'
    assert parse_ref('QAR-F').suffix == '-F'


def test_cut_and_segment():
    assert parse_cut('S01-C02') == (1, 2, None)
    assert parse_cut('S01-C02.b3') == (1, 2, 3)


@pytest.mark.parametrize('value', ['CHR-1', 'CHR-01@v0', '../CHR-01', 'SCR@draft@v1', 'S1-C02.b3', 'S01-C02.b0', 'WRD-02', 'TAK-01'])
def test_invalid(value):
    with pytest.raises(RefError):
        (parse_cut if value.startswith('S') and '-C' in value else parse_ref)(value)
