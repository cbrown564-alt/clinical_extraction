"""Governing contract for Decision 0049 always-on / deep pytest tiers."""

from __future__ import annotations

import tomllib
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]


def _pytest_ini_options() -> dict[str, object]:
    data = tomllib.loads((_REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    ini = data["tool"]["pytest"]["ini_options"]
    assert isinstance(ini, dict)
    return ini


def test_default_addopts_exclude_deep_tier() -> None:
    ini = _pytest_ini_options()
    addopts = ini.get("addopts", [])
    if isinstance(addopts, str):
        tokens = addopts.split()
    else:
        assert isinstance(addopts, list)
        tokens = [str(part) for part in addopts]
    assert tokens == ["-m", "not deep"]


def test_deep_marker_is_registered() -> None:
    ini = _pytest_ini_options()
    markers = ini.get("markers", [])
    assert isinstance(markers, list)
    assert any(str(marker).startswith("deep:") for marker in markers)