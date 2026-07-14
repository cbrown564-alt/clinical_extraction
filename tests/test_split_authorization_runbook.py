from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNBOOK = ROOT / "docs/runbooks/gated_blockers_2026-06-18.md"


def test_runbook_keeps_gan_test450_locked() -> None:
    runbook = " ".join(RUNBOOK.read_text(encoding="utf-8").split())

    assert "Gan `test450` is a locked holdout" in runbook
    assert "may not inspect its row-level" in runbook
    assert "explicit user authorization for the run" in runbook
    assert "A holdout defect starts a new validation candidate" in runbook


def test_runbook_keeps_exect_test60_out_of_development() -> None:
    runbook = " ".join(RUNBOOK.read_text(encoding="utf-8").split())

    assert "`test60` is held out from row-level development" in runbook
    assert "development-inclusive aggregate audit" in runbook
    assert "not an independent holdout" in runbook
    assert "must not expose or use `test60` rows for tuning" in runbook
