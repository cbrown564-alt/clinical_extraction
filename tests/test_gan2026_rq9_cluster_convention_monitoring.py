from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    rq9_cluster_convention_monitoring as monitoring,
)


def _row(
    *,
    source_row_index: int,
    final_label: str = "1 cluster per week, multiple per cluster",
    purist_correct: bool = True,
    reasons: list[str] | None = None,
    evidence: str = "weekly clusters reported",
) -> dict:
    return {
        "source_row_index": source_row_index,
        "selective_action": "predict",
        "primary_reason": "plain_predictable_frequency",
        "final_label": final_label,
        "source_candidate": {
            "final_label": final_label,
            "purist_correct": purist_correct,
            "selected_evidence": evidence,
        },
        "development_accounting": {
            "gold_label_kind": "frequency",
            "human_simple_class": None,
            "codex_ambiguity_reasons": reasons or ["cluster_or_per_cluster_convention"],
        },
    }


def test_cluster_structured_prediction_is_monitoring_not_verifier_priority() -> None:
    row = monitoring.interpret_cluster_row(_row(source_row_index=10003))

    assert row["monitoring_group"] == "cluster_structured_prediction"
    assert row["verifier_priority"] == "routine_monitoring"
    assert row["keep_prediction_bearing"] is True


def test_plain_frequency_with_cluster_context_is_high_priority_verifier() -> None:
    row = monitoring.interpret_cluster_row(
        _row(
            source_row_index=15593,
            final_label="2 per 6 month",
            purist_correct=False,
            evidence="two nocturnal episodes over the past six months after clusters",
        )
    )

    assert row["monitoring_group"] == "plain_frequency_with_cluster_context"
    assert row["verifier_priority"] == "high_priority_verifier"
    assert row["development_unsafe_if_predicted"] is True


def test_no_reference_unknown_boundary_is_high_priority_verifier() -> None:
    row = monitoring.interpret_cluster_row(
        _row(
            source_row_index=10183,
            final_label="no seizure frequency reference",
            reasons=["unknown_gold_boundary", "cluster_or_per_cluster_convention"],
            evidence="brief morning clusters reported but frequency unclear",
        )
    )

    assert row["monitoring_group"] == "sentinel_no_reference_with_cluster_context"
    assert row["verifier_priority"] == "high_priority_verifier"


def test_summary_preserves_prediction_bearing_policy_and_counts_verifier_queue() -> None:
    rows, summary = monitoring.interpret_cluster_rows(
        [
            _row(source_row_index=1),
            _row(
                source_row_index=2,
                final_label="1 per month",
                purist_correct=False,
                evidence="monthly clusters",
            ),
            _row(source_row_index=3, final_label="seizure free for multiple year"),
        ]
    )

    assert len(rows) == 3
    assert summary["metrics"]["eligible_prediction_bearing_rows"] == 3
    assert summary["metrics"]["keep_prediction_bearing_rows"] == 3
    assert summary["metrics"]["high_priority_verifier_rows"] == 2
    assert summary["decision"] == "keep_prediction_bearing_with_verifier_monitoring"
