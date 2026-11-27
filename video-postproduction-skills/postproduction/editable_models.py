"""Source native projections and qualified local reopen inputs; no promise of universal interchange."""
from postproduction.backends.base import CapabilitySnapshot
from postproduction.common import Frozen, Nonempty, Pin


class NativeProjection(Frozen):
    source: Pin
    destination: Nonempty
    capability: CapabilitySnapshot
    frame_count: int


class EditableInventory(Frozen):
    projects: tuple[NativeProjection, ...]
    media: tuple[Pin, ...]
