from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PAPER_SOURCES = (
    ROOT / "docs" / "research" / "paper_manuscript_2026-06-26.md",
    ROOT
    / "literature"
    / "IEEE"
    / "IEEE-conference-template-062824"
    / "IEEE-conference-template-062824.tex",
)


@pytest.mark.parametrize("source_path", PAPER_SOURCES)
def test_surviving_paper_sources_use_retained_results(source_path: Path) -> None:
    source = source_path.read_text(encoding="utf-8")

    for retained_value in (
        "0.9189",
        "0.3548",
        "0.7393",
        "364/450",
        "379/450",
        "0.2225",
        "0.2340",
        "0.0587",
        "0.0389",
        "0.0293",
    ):
        assert retained_value in source

    for retired_value in (
        "0.9155",
        "0.0432",
        "0.2245",
        "0.2387",
        "0.3877",
        "0.6972",
        "0.8680",
        "0.8566",
        "0.8356",
        "0.8197",
        "6 of 9",
    ):
        assert retired_value not in source


@pytest.mark.parametrize("source_path", PAPER_SOURCES)
def test_surviving_paper_sources_preserve_claim_boundaries(source_path: Path) -> None:
    source = source_path.read_text(encoding="utf-8").lower()

    assert "not an independent holdout" in source
    assert "six-model" in source
    assert "incomplete" not in source
    assert "general model superiority" in source
    assert "does not support a cross-task over-reading claim" in source
