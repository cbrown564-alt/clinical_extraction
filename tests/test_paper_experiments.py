"""Always-on presence check for tracked paper fills."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_paper_hybrid_fills_are_present() -> None:
    fills = json.loads(
        (ROOT / "paper_experiments/current_stack/latest/fills.json").read_text(
            encoding="utf-8"
        )
    )
    assert "hybrid" in fills
    assert "gan_test450" in fills["hybrid"]
    assert "exect_dev140" in fills["hybrid"]
    assert "exect_test60" in fills["hybrid"]
    e5 = json.loads(
        (
            ROOT
            / "paper_experiments/exectv2_rules_only_campaign_e5_remeasure_20260815.json"
        ).read_text(encoding="utf-8")
    )
    assert "dev140" in e5
    assert "test60" in e5


def test_gemma_compact_paper_cells_have_raw_and_hybrid() -> None:
    root = ROOT / "paper_experiments/exectv2_compact_ledger/gemma4_26b"
    for split, rows in (("dev140", 140), ("test60", 59)):
        comparison = json.loads((root / split / "comparison.json").read_text(encoding="utf-8"))
        assert comparison["split"] == split
        assert comparison["row_count"] == rows
        assert comparison["model"] == "ollama_chat/gemma4:26b"
        if split == "test60":
            assert comparison["row_policy"] == "aggregate_only"
            assert "letter_ids" not in comparison
            assert "changed_rows" not in comparison
        for arm in ("compact_ledger", "full_ledger"):
            summary = comparison["arms"][arm]
            assert "raw_headline_f1" in summary
            assert "hybrid_headline_f1" in summary
            sidecar = root / split / arm / "structured.jsonl"
            text = sidecar.read_text(encoding="utf-8")
            lines = [line for line in text.splitlines() if line.strip()]
            assert len(lines) == rows
            row = json.loads(lines[0])
            assert set(row) == {"letter_id", "prompt_version", "raw_output"}
