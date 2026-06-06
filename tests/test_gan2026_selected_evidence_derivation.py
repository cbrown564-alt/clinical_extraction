from clinical_extraction.tasks.seizure_frequency.gan2026.selected_evidence import (
    selected_evidence_derivation,
)


def test_selected_evidence_derives_vague_multiple_days_within_week_before_cluster_block() -> None:
    assert (
        selected_evidence_derivation.prediction_label_from_selected_evidence(
            "a brief cluster of events occurring on multiple days within the past week"
        )
        == "multiple per week"
    )


def test_selected_evidence_derives_vague_count_over_period() -> None:
    assert (
        selected_evidence_derivation.prediction_label_from_selected_evidence(
            "many generalized convulsions in past month"
        )
        == "multiple per month"
    )


def test_selected_evidence_derives_vague_weekday_burden() -> None:
    assert (
        selected_evidence_derivation.prediction_label_from_selected_evidence(
            "brief absences occurring on most weekdays"
        )
        == "multiple per week"
    )


def test_selected_evidence_derives_vague_daily_burden() -> None:
    assert (
        selected_evidence_derivation.prediction_label_from_selected_evidence(
            "several episodes per day"
        )
        == "multiple per day"
    )
    assert (
        selected_evidence_derivation.prediction_label_from_selected_evidence(
            "events occurring several times each day"
        )
        == "multiple per day"
    )
