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


def test_selected_evidence_derives_episode_count_after_window_phrase() -> None:
    assert (
        selected_evidence_derivation.prediction_label_from_selected_evidence(
            "Over the past six weeks, four episodes have occurred"
        )
        == "4 per 6 week"
    )


def test_selected_evidence_sums_episode_and_aura_counts_after_window_phrase() -> None:
    assert (
        selected_evidence_derivation.prediction_label_from_selected_evidence(
            "Clustering over the past six weeks "
            "(four focal impaired-awareness episodes and two focal aware auras)."
        )
        == "6 per 6 week"
    )


def test_selected_evidence_does_not_derive_count_from_including_example() -> None:
    assert (
        selected_evidence_derivation.prediction_label_from_selected_evidence(
            "These events have been occurring multiple times in past week, "
            "including two episodes witnessed by a friend."
        )
        is None
    )


def test_selected_evidence_derives_explicit_times_per_day() -> None:
    assert (
        selected_evidence_derivation.prediction_label_from_selected_evidence(
            "He still has simple partial seizures 4 times per day, drop attacks "
            "occurring in batches, and tonic-clonic seizures 2 times per month."
        )
        == "4 per day"
    )


def test_selected_evidence_derives_explicit_absences_per_day() -> None:
    assert (
        selected_evidence_derivation.prediction_label_from_selected_evidence(
            "She has 4 absences per day. She experiences one to two "
            "generalised tonic-clonic seizures monthly."
        )
        == "4 per day"
    )


def test_selected_evidence_prefers_daily_attack_burden_over_lower_window_rate() -> None:
    assert (
        selected_evidence_derivation.prediction_label_from_selected_evidence(
            "Seizure frequency remains unchanged over the last six months; "
            "he continues to have up to 3 or 4 generalised tonic-clonic seizures "
            "per week. He also has daily drop attacks."
        )
        == "1 per day"
    )


def test_selected_evidence_derives_upper_bound_with_intervening_seizure_words() -> None:
    assert (
        selected_evidence_derivation.prediction_label_from_selected_evidence(
            "Absence seizures remain infrequent, usually no more than twice weekly, "
            "and myoclonic jerks are reported only occasionally."
        )
        == "2 per week"
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


def test_selected_evidence_derives_hourly_rate() -> None:
    assert (
        selected_evidence_derivation.prediction_label_from_selected_evidence("9 per hour")
        == "multiple per day"
    )
    assert (
        selected_evidence_derivation.prediction_label_from_selected_evidence("4/h")
        == "multiple per day"
    )
    assert (
        selected_evidence_derivation.prediction_label_from_selected_evidence(
            "multiple seizures per hr"
        )
        == "multiple per day"
    )
