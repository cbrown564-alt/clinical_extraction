from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    model_reported_confidence as confidence,
)


def _cell(confidence: str, final_correct: bool, source_correct: bool | None = None) -> dict:
    source = final_correct if source_correct is None else source_correct
    return {
        "confidence": confidence,
        "final_correct": final_correct,
        "source_correct": source,
        "source_final_changed": source != final_correct,
    }


def test_cell_confidence_uses_least_confident_usable_family_label() -> None:
    mentions = [
        {"entity": "Diagnosis", "confidence": "high"},
        {"entity": "Diagnosis", "confidence": "medium"},
        {"entity": "Prescription", "confidence": "low"},
    ]
    assert confidence.cell_confidence(mentions, "Diagnosis") == "medium"
    assert confidence.cell_confidence(mentions, "Investigations") == "missing"


def test_failure_auroc_handles_order_and_ties() -> None:
    assert confidence.failure_auroc([_cell("low", False), _cell("high", True)]) == 1.0
    assert confidence.failure_auroc([_cell("high", False), _cell("high", True)]) == 0.5
    assert confidence.failure_auroc([_cell("missing", False), _cell("high", True)]) is None


def test_summary_keeps_missing_separate_and_counts_change_direction() -> None:
    summary = confidence.summarize_cells(
        [
            _cell("low", False),
            _cell("medium", True),
            _cell("high", True, source_correct=False),
            _cell("missing", False, source_correct=True),
        ]
    )
    assert summary["usable_confidence_coverage"] == 0.75
    assert summary["by_confidence"][3]["confidence"] == "missing"
    assert summary["source_to_final"]["wrong_to_correct"] == 1
    assert summary["source_to_final"]["correct_to_wrong"] == 1
    assert summary["review_policies"][0]["review_burden"] == 0.5


def test_verdict_requires_all_three_frozen_gates() -> None:
    passing = {
        "usable_confidence_coverage": 0.9,
        "failure_auroc_usable_labels": 0.7,
        "review_policies": [{"id": "fixed", "catch_rate": 0.6, "review_burden": 0.2}],
    }
    assert confidence.verdict(passing)["informative"] is True
    failing = {**passing, "failure_auroc_usable_labels": 0.64}
    assert confidence.verdict(failing)["informative"] is False
