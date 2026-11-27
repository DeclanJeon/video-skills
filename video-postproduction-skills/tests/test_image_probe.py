"""Independent RGBA contract distinguishes anti-aliased glyph coverage from a promised opaque solid."""
import pytest
from PIL import Image
from conftest import require


def test_alpha_when_font_coverage_has_no_fully_opaque_pixel_still_requires_straight_rgb(tmp_path):
    path=tmp_path/"coverage.png";im=Image.new("RGBA",(8,8));im.putpixel((3,3),(255,255,255,239));im.save(path)
    actual=require("backends.image_probe","inspect_rgba")(path,"#ffffff","coverage")
    assert actual.straight_consistent is True
    with pytest.raises(require("errors","ContractError")):
        require("backends.image_probe","inspect_rgba")(path,"#ffffff")


def test_alpha_when_font_rgb_is_premultiplied_cannot_claim_straight_alpha(tmp_path):
    path=tmp_path/"premult.png";im=Image.new("RGBA",(8,8));im.putpixel((3,3),(128,128,128,128));im.save(path)
    with pytest.raises(require("errors","ContractError")):
        require("backends.image_probe","inspect_rgba")(path,"#ffffff","coverage")
