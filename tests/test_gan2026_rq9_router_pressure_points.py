from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    rq9_router_pressure_points as pressure,
)


def _row(
    *,
    source_row_index: int,
    action: str = "human_review",
    reason: str = "cluster_projection_boundary",
    final_label: str = "1 cluster per month, multiple per cluster",
    purist_correct: bool = True,
    human_class: str | None = None,
    gold_kind: str = "frequency",
) -> dict:
    return {
        "source_row_index": source_row_index,
        "selective_action": action,
        "primary_reason": reason,
        "source_candidate": {
            "final_label": final_label,
            "purist_correct": purist_correct,
        },
        "development_accounting": {
            "gold_label_kind": gold_kind,
            "human_simple_class": human_class,
            "codex_ambiguity_reasons": ["cluster_or_per_cluster_convention"],
        },
    }


def test_pressure_summary_splits_rescue_value_from_over_review() -> None:
    rows = [
        _row(source_row_index=1, purist_correct=True, human_class="correct"),
        _row(source_row_index=2, purist_correct=False, human_class="ambiguous"),
        _row(
            source_row_index=3,
            reason="benchmark_convention_boundary",
            final_label="no seizure frequency reference",
            purist_correct=True,
            human_class="correct",
            gold_kind="no_reference",
        ),
    ]

    summary = pressure.summarize_pressure_points(rows)

    assert summary["metrics"]["nonprediction_rows"] == 3
    assert summary["metrics"]["blocked_wrong_predictions"] == 1
    assert summary["metrics"]["blocked_likely_correct_predictions"] == 2
    assert summary["by_reason"]["cluster_projection_boundary"]["reviewed_correct_rows"] == 1
    assert summary["by_reason"]["cluster_projection_boundary"]["reviewed_noncorrect_rows"] == 1
    assert summary["by_reason"]["cluster_projection_boundary"]["source_wrong_rate"] == 0.5


def test_label_buckets_distinguish_cluster_projection_from_plain_frequency() -> None:
    rows = [
        _row(source_row_index=1, final_label="1 cluster per month, multiple per cluster"),
        _row(source_row_index=2, final_label="1 per month", purist_correct=False),
        _row(source_row_index=3, final_label="seizure free for multiple year"),
        _row(source_row_index=4, final_label="no seizure frequency reference"),
    ]

    cluster_summary = pressure.summarize_pressure_points(rows)["by_reason"][
        "cluster_projection_boundary"
    ]

    assert cluster_summary["by_source_label_bucket"]["label_contains_cluster"]["rows"] == 1
    assert (
        cluster_summary["by_source_label_bucket"]["label_plain_frequency"]["source_wrong_rows"] == 1
    )
    assert cluster_summary["by_source_label_bucket"]["label_seizure_free"]["rows"] == 1
    assert cluster_summary["by_source_label_bucket"]["label_no_reference"]["rows"] == 1
