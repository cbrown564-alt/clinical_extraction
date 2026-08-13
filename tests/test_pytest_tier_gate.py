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


def test_six_cell_reference_replay_is_deep_not_always_on() -> None:
    from tests.test_reference_evidence_verification import (
        test_all_six_retained_reference_cells_replay_without_model_calls as replay,
    )

    mark_names = [
        getattr(mark, "name", None)
        or getattr(getattr(mark, "mark", None), "name", None)
        for mark in getattr(replay, "pytestmark", [])
    ]
    assert "deep" in mark_names