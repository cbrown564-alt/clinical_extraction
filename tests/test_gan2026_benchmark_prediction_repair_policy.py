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
    assert repair_prediction_label("occasional per unspecified time") == ("multiple per month")
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
    assert (
        repair_prediction_label(
            "brief generalised tonic-clonic seizures after nights of curtailed sleep"
        )
        == "unknown"
    )


def test_explicit_no_reference_sentinel_is_preserved() -> None:
    assert repair_prediction_label("no seizure frequency reference") == (
        "no seizure frequency reference"
    )


def test_underscore_separated_model_labels_are_format_repaired() -> None:
    assert repair_prediction_label("multiple_per_day") == "multiple per day"
    assert repair_prediction_label("multiple_per_week") == "multiple per week"
    assert repair_prediction_label("twice_per_year") == "2 per year"


def test_canonicalize_seizure_free_fuzzy_date_and_months() -> None:
    assert (
        repair_prediction_label("seizure free since shortly after 10 Jul")
        == "seizure free for multiple month"
    )
    assert repair_prediction_label("seizure free for multiple months") == (
        "seizure free for multiple month"
    )
    assert repair_prediction_label("seizure free since March") == "seizure free for multiple month"
    assert repair_prediction_label("seizure free for 3 years") == "seizure free for 3 year"


def test_multi_period_denominator_repair() -> None:
    assert repair_prediction_label("every 2 days on average") == "1 per 2 day"
    assert repair_prediction_label("every 4 weeks, usually over 1–2 days") == "1 per 4 week"
    assert repair_prediction_label("seizures every other week") == "1 per 2 week"
    assert repair_prediction_label("every 8 days on average") == "1 per 8 day"


def test_cluster_over_in_window_existing_per_cluster_clause() -> None:
    assert (
        repair_prediction_label("3 clusters in 6 weeks, 2 to 4 events per cluster")
        == "3 cluster per 6 week, 2 to 4 per cluster"
    )


def test_upper_bound_inequality_preserves_numeric_rate() -> None:
    assert repair_prediction_label("≤ 1 per month") == "1 per month"
    assert repair_prediction_label("up to 2 per week") == "2 per week"


def test_inexact_span_does_not_rewrite_unknown_to_a_rate() -> None:
    note = (
        "She has been better over the past seven months. There is also an "
        "unrelated mention of variable events in the distant past."
    )
    paraphrase = "one or three seizures last month"
    assert paraphrase not in note
    assert (
        repair_prediction_label_with_evidence(
            "unknown",
            paraphrase,
            context_text=note,
        )
        == "unknown"
    )


def test_exact_span_may_still_rewrite_unknown_to_the_quoted_rate() -> None:
    quote = "one or three seizures last month"
    note = f"She reports {quote} and no further events since."
    assert (
        repair_prediction_label_with_evidence(
            "unknown",
            quote,
            context_text=note,
        )
        == "1 to 3 per month"
    )


def test_inexact_span_may_still_render_the_same_parsed_family() -> None:
    note = (
        "Current pattern is seizures every other week, typically overnight, "
        "with post-ictal tiredness the following morning."
    )
    paraphrase = "the current pattern is roughly fortnightly"
    assert paraphrase not in note
    assert (
        repair_prediction_label_with_evidence(
            "1 per 2 weeks",
            paraphrase,
            context_text=note,
        )
        == "1 per 2 week"
    )




