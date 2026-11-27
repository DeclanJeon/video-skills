"""Caption/style/current work authority admission before any native text layer can be created."""
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import assert_never

from postproduction.backends.text_models import TextRecipe, TextSettings
from postproduction.backends.effect_models import MotionRecipe
from postproduction.caption_models import ApprovedCaption, SourceCaption
from postproduction.captions import map_cues, verify_mapped_cues
from postproduction.clock import map_frame
from postproduction.edit_models import Change
from postproduction.errors import ContractError
from postproduction.files import read_model, verified_file
from postproduction.state_models import PostState
from postproduction.templates import load_recipe
from postproduction.timeline_map import FILM_CLOCK
from postproduction.typography import measure_text
from postproduction.work_models import WorkOrder


@dataclass(frozen=True,slots=True)
class TextContract:
    state: PostState
    root: Path

    def settings(self, order: WorkOrder, recipe: MotionRecipe | TextRecipe) -> TextSettings | None:
        match recipe:
            case MotionRecipe():
                return None
            case TextRecipe():
                return self.check(order,recipe)
        assert_never(recipe)

    def check(self, order: WorkOrder, recipe: TextRecipe) -> TextSettings:
        """Exact source quote and current mapped cue, physical style/font and declared safe bounds."""
        if Change.CAPTIONS not in self.state.intake.authority.allowed_changes:
            raise ContractError("caption", "explicit caption authority required; composition alone cannot rewrite dialogue")
        timeline = next(t for t in self.state.timelines if t.branch==order.branch)
        verify_mapped_cues((recipe.caption,),timeline)
        approved = read_model(self.root,recipe.caption.source_approval,ApprovedCaption)
        cue = SourceCaption(format=approved.format,id=approved.id,source=approved.source,source_range=approved.source_range,
            text=approved.text,speaker=approved.speaker,kind=approved.kind,words=approved.words,
            timing_evidence=approved.timing_evidence,approval_kind=approved.approval_kind,
            approval=recipe.caption.source_approval,word_highlight=recipe.caption.word_highlight)
        if map_cues((cue,),timeline) != (recipe.caption,) or cue.source not in order.source_refs:
            raise ContractError("caption", "native caption differs from actual approved text/speaker/source/current timing")
        if cue.word_highlight:
            raise ContractError("word", "initial native text route does not invent per-word highlights; use supported explicit animator")
        _ = verified_file(self.root,recipe.style)
        style = load_recipe(self.root/recipe.style.path,self.root)
        _ = verified_file(self.root,recipe.style)
        required = (recipe.style,cue.approval,style.font.license_evidence,*style.references)
        if any(p not in order.dependencies or p not in self.state.intake.authority.assets for p in required):
            raise ContractError("authority", "actual text/style/rights inputs must bind the work and exact asset grant")
        if approved.timing_evidence is not None:
            _ = verified_file(self.root,approved.timing_evidence)
        start = map_frame(recipe.caption.master_range.start,FILM_CLOCK,recipe.fps,rounding="exact")
        duration = map_frame(recipe.caption.master_range.length,FILM_CLOCK,recipe.fps,rounding="exact")
        if (style.width,style.height,style.fps,start,duration) != (
            recipe.width,recipe.height,recipe.fps,recipe.start_frame,recipe.frame_count):
            raise ContractError("caption", "native text style canvas/clock or display duration differs from approved cue")
        seconds = Fraction(recipe.frame_count*recipe.fps.den,recipe.fps.num)
        if len(cue.text)/seconds > style.max_characters_per_second:
            raise ContractError("caption", "literal source exceeds the explicit reading policy; do not abbreviate without approval")
        metrics = measure_text(style,cue.text,self.root)
        safe = style.safe_bounds
        if metrics.width > safe.right-safe.left or metrics.height > safe.bottom-safe.top:
            raise ContractError("bounds", "actual source glyph advance overflows supplied safe mask")
        for x,y in (recipe.start_position,recipe.end_position):
            if not safe.left <= x-metrics.width/2 < x+metrics.width/2 <= safe.right or not safe.top <= y-style.font_size < y <= safe.bottom:
                raise ContractError("bounds", "planned glyph advance/baseline overflows supplied safe mask")
        return TextSettings(family=style.font.family,style=style.font.style,size=style.font_size,color=recipe.color)
