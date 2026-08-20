from __future__ import annotations

import pytest

from clinical_extraction.reference_evidence_verification import (
    ReferenceEvidenceMismatch,
    assert_expected_metrics,
)


def test_reference_replay_reports_metric_drift() -> None:
    with pytest.raises(ReferenceEvidenceMismatch, match="headline_f1"):
        assert_expected_metrics(
            "example",
            actual={"headline_f1": 0.8},
            expected={"headline_f1": 0.9},
        )
