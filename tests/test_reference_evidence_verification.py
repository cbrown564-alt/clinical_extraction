from __future__ import annotations

from pathlib import Path

import pytest

from clinical_extraction.core.retained_evidence import load_retained_evidence_manifest
from clinical_extraction.reference_evidence_verification import (
    ReferenceEvidenceMismatch,
    assert_expected_metrics,
    verify_reference_cells,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "experiments" / "retained_evidence_manifest.json"


def test_all_six_retained_reference_cells_replay_without_model_calls() -> None:
    results = verify_reference_cells(
        load_retained_evidence_manifest(MANIFEST), repo_root=ROOT
    )

    assert set(results) == {
        "exectv2_rules_reference",
        "exectv2_llm_only_reference",
        "exectv2_hybrid_reference",
        "gan2026_rules_reference",
        "gan2026_llm_only_reference",
        "gan2026_hybrid_reference",
    }


def test_reference_replay_reports_metric_drift() -> None:
    with pytest.raises(ReferenceEvidenceMismatch, match="headline_f1"):
        assert_expected_metrics(
            "example",
            actual={"headline_f1": 0.8},
            expected={"headline_f1": 0.9},
        )
