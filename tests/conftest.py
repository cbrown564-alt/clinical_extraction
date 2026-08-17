"""Shared pytest fixtures for the clinical_extraction test suite."""

from __future__ import annotations

from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
_LOCAL_CORPUS_ROOTS = ("data", "docs", "experiments")


def local_corpus_present() -> bool:
    """True when the gitignored research trees are on disk."""

    return all((_REPO_ROOT / name).is_dir() for name in _LOCAL_CORPUS_ROOTS)


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Skip corpus-backed tests on a public clone that has no local trees."""

    del config
    if local_corpus_present():
        return
    skip = pytest.mark.skip(
        reason="local data/, docs/, and experiments/ are not in this checkout"
    )
    for item in items:
        if item.get_closest_marker("local_corpus"):
            item.add_marker(skip)


@pytest.fixture
def repo_root() -> Path:
    """Repository root (parent of the tests/ package)."""
    return _REPO_ROOT


@pytest.fixture
def tmp_experiments(tmp_path: Path) -> Path:
    """Isolated experiments directory under pytest's tmp_path."""
    experiments = tmp_path / "experiments"
    experiments.mkdir()
    return experiments
