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
