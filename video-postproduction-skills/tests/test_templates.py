"""Conceptual recipes reuse existing exact font files; no MOGRT/binary/font installation or fake metrics."""
import json,hashlib
from pathlib import Path
import pytest
from conftest import require
from support import json_pin

FONT=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')


def recipe(root,**changes):
    rights=json_pin(root,"font-rights.json",{"scope":"reported technical fixture using installed font; no redistribution"})
    data={"format":"post-style/1","id":"CONCEPT-STRIP","family":"concept-filmstrip","reference_use":"concept_only",
        "width":320,"height":180,"fps":{"num":24,"den":1},
        "font":{"path":str(FONT),"sha256":hashlib.sha256(FONT.read_bytes()).hexdigest(),"family":"DejaVu Sans","style":"Book","version":155320,"face_index":0,"license_evidence":rights.model_dump()},
        "font_size":24,"safe_bounds":{"left":10,"top":10,"right":310,"bottom":170},"protected_bounds":[],
        "max_lines":2,"max_characters_per_second":20,"metrics":[],**changes}
    path=root/'style.json';path.write_text(json.dumps(data));return path,data


def test_recipe_when_exact_actual_font_can_shape_literal_text_without_installing(tmp_path):
    path,raw=recipe(tmp_path)
    value=require("templates","load_recipe")(path,tmp_path)
    measured=require("typography","measure_text")(value,"Hello",tmp_path)
    assert 55<measured.width<70
    assert measured.font_family=="DejaVu Sans"


@pytest.mark.parametrize("family",["Paperlogy-6SemiBold","HakgyoansimBareonbatangB"])
def test_recipe_when_missing_requested_face_cannot_hide_fallback(tmp_path,family):
    path,raw=recipe(tmp_path);raw['font']['family']=family;path.write_text(json.dumps(raw))
    with pytest.raises(require("errors","ContractError"),match="font"):
        require("templates","load_recipe")(path,tmp_path)


def test_recipe_when_actual_font_has_no_required_korean_glyphs_cannot_render_tofu(tmp_path):
    path,raw=recipe(tmp_path)
    value=require("templates","load_recipe")(path,tmp_path)
    with pytest.raises(require("errors","ContractError"),match="glyph"):
        require("typography","measure_text")(value,"한글",tmp_path)


def test_recipe_when_real_measured_bounds_overflow_or_occlude_protected_mask(tmp_path):
    path,raw=recipe(tmp_path,protected_bounds=[{"left":100,"top":100,"right":220,"bottom":160}])
    value=require("templates","load_recipe")(path,tmp_path)
    bounds=require("backends.effect_models","PixelBounds")(left=130,top=120,right=190,bottom=145)
    with pytest.raises(require("errors","ContractError"),match="bounds"):
        require("templates","verify_style_bounds")(value,bounds)


def test_recipe_when_fractional_font_size_would_be_silently_truncated_by_independent_measurement(tmp_path):
    path,raw=recipe(tmp_path,font_size=24.5)
    with pytest.raises(require("errors","ContractError")):
        require("templates","load_recipe")(path,tmp_path)


def test_recipe_when_performance_number_has_no_real_evidence_is_not_copied_from_preview(tmp_path):
    path,raw=recipe(tmp_path,metrics=[{"name":"views","value":120000}])
    with pytest.raises(require("errors","ContractError")):
        require("templates","load_recipe")(path,tmp_path)
