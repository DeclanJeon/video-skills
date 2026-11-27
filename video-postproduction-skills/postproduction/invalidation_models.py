"""Append-only scoped revocation signal; old process/output history is never erased."""
from postproduction.common import Frozen, Nonempty, Pin


class Invalidation(Frozen):
    id: Nonempty
    changed_pins: tuple[Pin, ...]
    order_ids: tuple[Nonempty, ...]
