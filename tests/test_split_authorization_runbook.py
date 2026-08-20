from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DECISION = ROOT / "docs/paper/decisions/holdout-is-aggregate-only.md"

pytestmark = pytest.mark.local_corpus


def test_decision_keeps_holdout_splits_locked() -> None:
    decision = " ".join(DECISION.read_text(encoding="utf-8").split())

    assert "`test450` (Gan) and `test60` (ExECT) are locked" in decision
    assert "Cite aggregate scores only" in decision
    assert (
        "Do not inspect holdout identifiers, notes, predictions, evidence, errors, or changed rows"
        in decision
    )


def test_decision_forbids_holdout_repair_and_tuning() -> None:
    decision = " ".join(DECISION.read_text(encoding="utf-8").split())

    assert "A holdout defect starts a new development candidate" in decision
    assert (
        "It does not permit holdout repair, prompt change, or scorer change from those rows"
        in decision
    )
    assert "Do not retune from sealed `test450`, Real(300), or ExECT `test60`" in decision
