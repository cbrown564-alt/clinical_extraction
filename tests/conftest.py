"""Shared pytest fixtures for the clinical_extraction test suite."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def repo_root() -> Path:
    """Repository root (parent of the tests/ package)."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def tmp_experiments(tmp_path: Path) -> Path:
    """Isolated experiments directory under pytest's tmp_path."""
    experiments = tmp_path / "experiments"
    experiments.mkdir()
    return experiments
