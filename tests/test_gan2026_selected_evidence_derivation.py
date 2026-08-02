from clinical_extraction.tasks.seizure_frequency.gan2026.selected_evidence import (
    selected_evidence_derivation,
)


def test_selected_evidence_derives_vague_count_over_period() -> None:
    assert (
        selected_evidence_derivation.prediction_label_from_selected_evidence(
            "many generalized convulsions in past month"
        )
        == "multiple per month"
    )


def test_selected_evidence_derives_explicit_times_per_day() -> None:
    assert (
        selected_evidence_derivation.prediction_label_from_selected_evidence(
            "He still has simple partial seizures 4 times per day, drop attacks "
            "occurring in batches, and tonic-clonic seizures 2 times per month."
        )
        == "4 per day"
    )


def test_selected_evidence_prefers_recent_yesterday_count_over_lower_weekly_rate() -> None:
    assert (
        selected_evidence_derivation.prediction_label_from_selected_evidence(
            "Yesterday he experienced three tonic-clonic seizures yesterday; "
            "He describes interictal brief auras occurring approximately once "
            "or twice per week without progression."
        )
        == "1 per day"
    )
