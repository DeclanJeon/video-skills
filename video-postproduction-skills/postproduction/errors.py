"""Typed domain failures propagated to explicit application boundaries."""


class ContractError(Exception):
    """Failure stage/detail; exceptions remain mutable for Python traceback handling."""

    stage: str
    detail: str

    def __init__(self, stage: str, detail: str) -> None:
        self.stage = stage
        self.detail = detail
        super().__init__(f"{stage}: {detail}")
