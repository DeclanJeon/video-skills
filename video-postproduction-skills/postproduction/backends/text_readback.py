"""Actual saved native sourceText document and native font inventory, not a requested-font string alone."""
from typing import Literal

from pydantic import Field, JsonValue, TypeAdapter

from postproduction.backends.effect_models import EffectPlan, EffectRun
from postproduction.backends.text_models import TextRecipe
from postproduction.errors import ContractError
from postproduction.probe_models import Projection


class FontFamily(Projection):
    family: str
    styles: tuple[str, ...]
    origin: Literal["bundled","system","user"]


class FontInventory(Projection):
    families: tuple[FontFamily, ...]


class NativeDocument(Projection):
    text: str
    font: str
    style: str
    size: float
    apply_fill: bool
    apply_stroke: bool


class TextValue(Projection):
    t: Literal["Text"]
    v: NativeDocument


class PropertyNode(Projection):
    match_name: str = Field(alias="match",default="")
    children: tuple["PropertyNode", ...] = ()
    value: JsonValue = None


class NativeLayer(Projection):
    id: int
    props: PropertyNode


class NativeKind(Projection):
    layers: tuple[NativeLayer, ...] = ()


class NativeItem(Projection):
    id: int
    kind: NativeKind


class NativeDocumentFile(Projection):
    items: dict[str,NativeItem]


def text_readback(plan: EffectPlan, ids: tuple[int,int]) -> NativeDocument:
    """The actual font family/style is system registered and native text attributes equal current approved source."""
    recipe,settings = plan.recipe,plan.text_settings
    if not isinstance(recipe,TextRecipe) or settings is None:
        raise ContractError("text", "native text inspection requires an actual admitted text recipe")
    run = EffectRun.model_validate_json((plan.workspace/"stage1.stdout").read_bytes())
    raw = next((s.result for s in run.result if s.command=="text.fonts"),None)
    inventory = FontInventory.model_validate_json(TypeAdapter(JsonValue).dump_json(raw))
    if not any(f.family==settings.family and settings.style in f.styles and f.origin=="system" for f in inventory.families):
        raise ContractError("font", "actual native font inventory does not resolve requested existing system family/style")
    document = NativeDocumentFile.model_validate_json((plan.workspace/"native.ecproj").read_bytes())
    comp = next((i for i in document.items.values() if i.id==ids[0]),None)
    layer = next((l for l in comp.kind.layers if l.id==ids[1]),None) if comp is not None else None
    if layer is None:
        raise ContractError("readback", "actual native text composition/layer ID missing")
    group = next((g for g in layer.props.children if g.match_name=="text"),None)
    prop = next((p for p in group.children if p.match_name=="sourceText"),None) if group is not None else None
    if prop is None:
        raise ContractError("readback", "actual native text document property missing")
    actual = TextValue.model_validate_json(TypeAdapter(JsonValue).dump_json(prop.value)).v
    if (actual.text,actual.font,actual.style,actual.size,actual.apply_fill,actual.apply_stroke) != (
        recipe.caption.text,settings.family,settings.style,settings.size,True,False):
        raise ContractError("caption", "actual saved text/font/style differs; fallback/rewrite is not a successful caption")
    return actual
