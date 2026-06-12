from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    repair_prediction_label,
    repair_prediction_label_with_evidence,
)


def test_hourly_frequency_renders_as_multiple_per_day() -> None:
    assert repair_prediction_label("9 per hour") == "multiple per day"
    assert repair_prediction_label("4/h") == "multiple per day"


def test_vague_frequency_mentions_preserve_frequency_semantics() -> None:
    assert repair_prediction_label("rare") == "multiple per year"
    assert repair_prediction_label("occasional per month") == "multiple per month"
    assert repair_prediction_label("occasional per unspecified time") == (
        "multiple per month"
    )
    assert repair_prediction_label("frequent per 6 week") == "multiple per 6 week"


def test_vague_seizure_evidence_does_not_become_no_reference() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "rare",
            "Patient states that seizures happen rare, typically brief episodes "
            "with impaired awareness lasting under two minutes.",
        )
        == "multiple per year"
    )


def test_cluster_context_does_not_demote_frequency_to_unknown() -> None:
    assert repair_prediction_label("8 per 4 month clustered") == "8 per 4 month"
    assert repair_prediction_label("2 clusters per month, 5 absences per cluster") == (
        "2 cluster per month, 5 per cluster"
    )
    assert repair_prediction_label("2 per month cluster of 5 events") == (
        "2 cluster per month, 5 per cluster"
    )


def test_unparseable_seizure_frequency_phrase_is_unknown_not_no_reference() -> None:
    assert repair_prediction_label(
        "brief generalised tonic-clonic seizures after nights of curtailed sleep"
    ) == "unknown"


def test_explicit_no_reference_sentinel_is_preserved() -> None:
    assert repair_prediction_label("no seizure frequency reference") == (
        "no seizure frequency reference"
    )


def test_underscore_separated_model_labels_are_format_repaired() -> None:
    assert repair_prediction_label("multiple_per_day") == "multiple per day"
    assert repair_prediction_label("multiple_per_week") == "multiple per week"
    assert repair_prediction_label("twice_per_year") == "2 per year"
