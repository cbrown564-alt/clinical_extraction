from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_gan2026_efficiency_comparison.py"


def _load_checker() -> ModuleType:
    spec = importlib.util.spec_from_file_location("gan_efficiency_checker", CHECKER)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_selected_gan_efficiency_comparison_is_reproducible() -> None:
    _load_checker().validate()

