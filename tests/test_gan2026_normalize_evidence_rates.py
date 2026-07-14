"""Invariant-focused tests for gan2026 normalize evidence rates."""

import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules import (
    benchmark_repair,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    repair_prediction_label,
    repair_prediction_label_with_evidence,
)

validate_benchmark_repair_steps = benchmark_repair.validate_benchmark_repair_steps


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (None, "no seizure frequency reference"),
        ("", "no seizure frequency reference"),
        ("twice weekly", "2 per week"),
        ("many per month", "multiple per month"),
        ("many per week", "multiple per week"),
        ("3-5/mo", "3 to 5 per month"),
        ("seizure-free since 2020", "seizure free for multiple year"),
        ("seizure free for 1.5 years", "seizure free for 1.5 year"),
        ("2 clusters per month 3 per cluster", "2 cluster per month, 3 per cluster"),
        ("2 per 0 month", "unknown"),
        ("no frequency mentioned", "no seizure frequency reference"),
    ],
)
def test_repair_prediction_label_ports_author_prediction_repairs(
    raw: str | None,
    expected: str,
) -> None:
    assert repair_prediction_label(raw) == expected


def test_repair_prediction_label_with_evidence_normalizes_common_output_shapes() -> None:
    assert repair_prediction_label("1 every 2 days") == "1 per 2 day"


def test_repair_prediction_label_with_evidence_preserves_selected_upper_bound() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "multiple per week",
            "overall a frequency of ≤ four seizures per week",
        )
        == "4 per week"
    )


def test_repair_prediction_label_with_evidence_uses_bare_selected_rate() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "multiple_per_day",
            "four per day",
        )
        == "4 per day"
    )


def test_repair_prediction_label_with_evidence_preserves_quarter_window() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "2 to 3 per month",
            "Current estimated seizure frequency is 12 to 30 per quarter",
        )
        == "12 to 30 per 3 month"
    )


def test_repair_prediction_label_with_evidence_keeps_upper_bound_with_clustering_context() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "≤ 6 to 7 per year",
            "Seizure frequency currently reported as ≤ 6 to 7 per year, "
            "typically clustering around periods of jet lag.",
        )
        == "6 to 7 per year"
    )


def test_repair_prediction_label_with_evidence_repairs_once_twice_upper_bounds() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "≤ once per month",
            "Over the past five months, events have reduced to ≤ once per month",
        )
        == "1 per month"
    )
    assert (
        repair_prediction_label_with_evidence(
            "≤ twice per week",
            "Over the past month, the overall frequency has been ≤ twice per week",
        )
        == "2 per week"
    )


def test_repair_prediction_label_with_evidence_repairs_daily_singular_statements() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "multiple per day",
            "He reports events occur daily, most commonly during the late dinner rush.",
        )
        == "1 per day"
    )
    assert (
        repair_prediction_label_with_evidence(
            "multiple per day",
            "She now describes seizures every night.",
        )
        == "1 per day"
    )


def test_repair_prediction_label_with_evidence_repairs_bimonthly_as_every_two_months() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "2 per month",
            "She notes the events are occurring bimonthly on average.",
        )
        == "1 per 2 month"
    )


def test_repair_prediction_label_with_evidence_repairs_q_interval_shorthand() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "2 to 3 per week",
            "He estimates the frequency currently as qtwo - threewk.",
        )
        == "1 per 2 to 3 week"
    )
    assert (
        repair_prediction_label_with_evidence(
            "1 to 2 per day",
            "He reports continuing episodes occurring at a frequency of q1 - 2d.",
        )
        == "1 per 1 to 2 day"
    )


def test_repair_prediction_label_with_evidence_repairs_median_interseizure_interval() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "2 to 3 per month",
            "Importantly, the median inter-seizure interval ≈ six weeks.",
        )
        == "1 per 6 week"
    )


def test_repair_prediction_label_with_evidence_aggregates_month_logs() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "1 to 2 per month",
            "Seizure: 2022: Jan x1, Feb x0, Mar x1, Apr x2, May x1, Jun x1, Jul x1",
        )
        == "7 per 7 month"
    )


def test_repair_prediction_label_with_evidence_sums_month_colon_diary_counts() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "multiple per month",
            (
                "Seizures in 2014-2015: Mar: 12 days with more severe seizures "
                "Apr: 7 days with more severe seizures May: 4 days with seizures "
                "Jun: 10 days Jul: 1 days Aug: 5 days with seizures Sep: 3 days "
                "with more severe seizures Oct: 4 days with seizures Nov: 4 days "
                "Dec: 4 days Jan: 12 days Feb: 10 days."
            ),
        )
        == "76 per 12 month"
    )


def test_repair_prediction_label_with_evidence_sums_sleep_awake_month_counts() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "6 per month",
            "In March he had 3 in sleep and 2 while awake. "
            "In May he had 3 in sleep and 3 while awake.",
        )
        == "11 per 2 month"
    )


def test_repair_prediction_label_with_evidence_sums_general_month_diaries() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "multiple per month",
            "She has had a seizure so far this month, five in Aug, one in Jul and 5 in Jun",
        )
        == "12 per 4 month"
    )
    assert (
        repair_prediction_label_with_evidence(
            "6 per month",
            "This month, she has had six convulsions; 0 were in December and 5 in November",
        )
        == "11 per 3 month"
    )


def test_repair_prediction_label_with_evidence_preserves_ranges_in_selected_window() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "4 per month",
            "Over the past month, they estimate 3 to 4 seizures.",
        )
        == "3 to 4 per month"
    )
    assert (
        repair_prediction_label_with_evidence(
            "10 per 2 month",
            "They report 1 - 10 focal aware seizures during the last two months.",
        )
        == "1 to 10 per 2 month"
    )


def test_repair_prediction_label_with_evidence_does_not_count_seizure_free_days() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "1 per day",
            "He keeps a diary and notes TC one/d over the past month, "
            "with only two seizure-free days in that period.",
        )
        == "1 per day"
    )


def test_repair_prediction_label_with_evidence_repairs_yesterday_as_day_window() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "1 tonic-clonic seizure yesterday",
            "The patient reported 1 tonic-clonic seizures yesterday.",
        )
        == "1 per day"
    )


def test_repair_prediction_label_with_evidence_repairs_cluster_rate_only() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "1 cluster per 4 weeks",
            "he reports clusters of brief absence episodes every 4 weeks",
        )
        == "1 per 4 week"
    )


def test_repair_prediction_label_with_evidence_repairs_seizure_free_cluster_cycles() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "multiple per day",
            "On occasions she is seizure-free for four to five consecutive days, "
            "followed by a day with multiple events, typically two tonic seizures.",
        )
        == "1 cluster per 4 to 5 day, 2 per cluster"
    )
    assert (
        repair_prediction_label_with_evidence(
            "unknown",
            "He may go five days without seizures, but when they happen he often "
            "has them in batches, with 3 - 4 occurring within 24 hours.",
        )
        == "1 cluster per 5 day, 3 to 4 per cluster"
    )


def test_repair_prediction_label_with_evidence_repairs_event_days_per_week() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "3 days per week",
            "His absence seizures are now occurring on three days of the week",
        )
        == "3 per week"
    )


def test_repair_prediction_label_with_evidence_repairs_daily_myoclonic_clusters() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "multiple per week",
            "Since the head injury, she has experienced clusters of jumps almost daily",
        )
        == "1 per day"
    )


def test_repair_prediction_label_with_evidence_repairs_monthly_cluster_detail() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "monthly clusters, typically 6 to 7 seizures over 24 h",
            "Monthly clusters, typically 6 to 7 seizures over 24 h",
        )
        == "1 cluster per month, 6 to 7 per cluster"
    )


def test_repair_prediction_label_repairs_event_description_per_window() -> None:
    assert (
        repair_prediction_label("2 nocturnal generalised tonic-clonic seizures per 4 months")
        == "2 per 4 month"
    )


def test_repair_prediction_label_with_evidence_preserves_parseable_raw_label() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "2 per 2 weeks",
            "The app logs indicate a regular pattern of seizures twice every two weeks",
        )
        == "2 per 2 week"
    )


def test_repair_prediction_label_with_evidence_sums_counts_in_selected_window() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "1 tonic-clonic and 6 petit mal in last week",
            "Over the past week she reports one tonic-clonic and six petit mal in last week",
        )
        == "7 per week"
    )


def test_repair_prediction_label_with_evidence_sums_word_counts_in_multi_month_window() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "six drop attacks and two absence seizures in the past two months",
            "Over the past two months she reports six drop attacks and two absence seizures",
        )
        == "8 per 2 month"
    )


def test_repair_prediction_label_with_evidence_repairs_single_last_period() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "1 isolated event last month",
            "He described a single very brief event last month",
        )
        == "1 per month"
    )


def test_repair_prediction_label_with_evidence_repairs_slash_week() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "4 per 7",
            "seizure frequency four/7",
        )
        == "4 per week"
    )


def test_repair_prediction_label_with_evidence_preserves_cluster_structure() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "2 clusters per month, each five absences",
            "Over the past four weeks he reports two clusters this month; "
            "each five absences in the morning.",
        )
        == "2 cluster per month, 5 per cluster"
    )


def test_repair_prediction_label_with_evidence_preserves_every_two_week_denominator() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "2 per month",
            "The app logs indicate a regular pattern of seizures twice every two weeks.",
        )
        == "2 per 2 week"
    )


def test_repair_prediction_label_with_evidence_repairs_every_other_month() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "2 to 3 per year",
            "Events are now occurring only every other month or so.",
        )
        == "1 per 2 month"
    )


def test_repair_prediction_label_with_evidence_repairs_count_this_year() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "less than 1 per month",
            "5 or 7 epileptic spasms this year",
        )
        == "5 to 7 per year"
    )


def test_repair_prediction_label_with_evidence_repairs_count_past_fortnight() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "3 per fortnight",
            "Over the past fortnight she describes three short episodes.",
        )
        == "3 per 2 week"
    )


def test_repair_prediction_label_with_evidence_repairs_slash_month() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "6 per month with clustering",
            "Seizure days: six/30 this month, clustering after late practice.",
        )
        == "6 per month"
    )


def test_repair_prediction_label_with_evidence_repairs_monthly_shorthand() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "2 to 3 per month",
            "The family reports abs 8 monthly over the past three months.",
        )
        == "8 per month"
    )


def test_repair_prediction_label_with_evidence_repairs_count_this_quarter() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "7 to 8 per quarter",
            "seven to eight absence seizures this quarter",
        )
        == "7 to 8 per 3 month"
    )


def test_repair_prediction_label_with_evidence_repairs_interval_range() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "1 cluster every 3 to 4 days",
            "intervals ranging three - four days between focal aware seizures",
        )
        == "1 per 3 to 4 day"
    )


def test_repair_prediction_label_with_evidence_repairs_single_count_over_window() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "3 events over 7 months",
            "Seizure events on 06-03, 06-13, 09-23 as recorded in the patient diary",
        )
        == "3 per 7 month"
    )


def test_repair_prediction_label_with_evidence_repairs_episode_count_after_window() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "4 in 6 weeks",
            "Over the past six weeks, four episodes have occurred",
        )
        == "4 per 6 week"
    )


def test_repair_prediction_label_with_evidence_repairs_up_to_count_in_bad_weeks() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "up to 7 per week",
            (
                "during flares he experiences multiple events, with a reported "
                "frequency of up to seven in bad weeks"
            ),
        )
        == "7 per week"
    )
