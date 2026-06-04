from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.gold_audit_active_sampler import (  # noqa: E501
    build_sampling_model,
    enrich_rows_for_active_sampling,
    row_features,
)


def _row(
    source_row_index: int,
    *,
    kind: str,
    reasons: str,
    label: str = "ambiguous",
) -> dict[str, str]:
    return {
        "source_row_index": str(source_row_index),
        "split": "validation",
        "gold_label": "multiple per month" if kind == "unresolved_multiple" else "2 per month",
        "gold_label_kind": kind,
        "gold_reference": "many convulsions in past month",
        "codex_initial_ambiguity_label": label,
        "codex_ambiguity_reasons": reasons,
        "gold_monthly_frequency": "1000.0" if kind == "unresolved_multiple" else "2.0",
        "row_ok": "True",
        "labels_match_all_categories": "True",
        "quotes_ok_all_categories": "True",
        "reference_found_in_note": "True",
        "note_text_single_line": "The note says many convulsions in past month.",
    }


def test_row_features_are_interpretable() -> None:
    features = row_features(
        _row(
            1,
            kind="unresolved_multiple",
            reasons="unresolved_multiple_or_vague_count;vague_count_or_period",
        )
    )

    assert "kind=unresolved_multiple" in features
    assert "reason=unresolved_multiple_or_vague_count" in features
    assert "monthly_bucket=sentinel_or_very_high" in features
    assert "text_has=multiple" in features


def test_sampling_model_smooths_small_labeled_sets() -> None:
    rows = [
        _row(1, kind="unresolved_multiple", reasons="unresolved_multiple_or_vague_count"),
        _row(2, kind="frequency", reasons="", label="clear"),
        _row(3, kind="frequency", reasons="range_or_upper_bound"),
    ]
    decisions = [
        {"source_row_index": 1, "split": "validation", "simple_class": "ambiguous"},
        {"source_row_index": 2, "split": "validation", "simple_class": "correct"},
    ]

    model = build_sampling_model(rows, decisions)
    scored = model.score_row(rows[0])

    assert model.total_decisions == 2
    assert not model.is_calibrated_enough
    assert scored["predicted_ambiguous_prob"] > scored["predicted_wrong_prob"]
    assert 0.0 <= scored["prediction_uncertainty"] <= 1.0
    assert scored["active_learning_score"] > 0.0


def test_enrich_rows_marks_decided_and_prioritizes_unreviewed_rows() -> None:
    rows = [
        _row(1, kind="unresolved_multiple", reasons="unresolved_multiple_or_vague_count"),
        _row(2, kind="frequency", reasons="", label="clear"),
        _row(3, kind="frequency", reasons="range_or_upper_bound"),
    ]
    decisions = [
        {"source_row_index": 1, "split": "validation", "simple_class": "ambiguous"},
        {"source_row_index": 2, "split": "validation", "simple_class": "correct"},
    ]

    enriched, summary = enrich_rows_for_active_sampling(rows, decisions)

    assert summary["decision_count"] == 2
    assert enriched[0]["has_decision"] is True
    assert enriched[2]["has_decision"] is False
    assert "predicted_simple_class" in enriched[2]
    assert "active_learning_reason" in enriched[2]
