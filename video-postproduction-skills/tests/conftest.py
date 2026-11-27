"""Shared test entry seam; absent modules fail explicit RED rather than collection."""
from importlib import import_module
import pytest


def require(module, name):
    try:
        loaded = import_module(f"postproduction.{module}")
    except ModuleNotFoundError as exc:
        pytest.fail(f"implementation module missing: {exc}")
    if not hasattr(loaded,name):
        pytest.fail(f"public contract missing: {module}.{name}")
    return getattr(loaded,name)
