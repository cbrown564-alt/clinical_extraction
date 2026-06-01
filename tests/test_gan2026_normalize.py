import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026 import benchmark_prediction_repair
from clinical_extraction.tasks.seizure_frequency.gan2026.gold_policy import (
    CLEAN_SCORER_FACING_GOLD_NORMALIZATION_RULES as GOLD_POLICY_RULES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.label_parser import (
    FrequencyLabelKind,
    label_to_frequency_record,
    label_to_monthly_frequency,
    parse_label_bounds,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    BENCHMARK_REPAIR_RULES,
    BENCHMARK_REPAIR_STEPS,
    CLEAN_SCORER_FACING_GOLD_NORMALIZATION_RULES,
    FORMAT_PRESERVING_BENCHMARK_REPAIR_RULES,
    FORMAT_PRESERVING_BENCHMARK_REPAIR_STEPS,
    repair_prediction_label,
    repair_prediction_label_clean_scorer_facing,
    repair_prediction_label_clean_scorer_facing_with_trace,
    repair_prediction_label_format_preserving,
    repair_prediction_label_with_evidence,
    repair_prediction_label_with_trace,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.rule_metadata import (
    AblationConfig,
    Portability,
    RuleGroup,
    validate_rule_registry,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.rules.benchmark_repair import (
    validate_benchmark_repair_steps,
)


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("seizure free for multiple month", 0.0),
        ("seizure free for 1.5 year", 0.0),
        ("unknown", 1000.0),
        ("no seizure frequency reference", 1000.0),
        ("1 per month", 365 / 30 / 12),
        ("2 to 4 per week", 3 * 365 / 7 / 12),
        ("1 per 2 month", 365 / (2 * 30) / 12),
        ("2 cluster per month, 6 per cluster", 12 * 365 / 30 / 12),
    ],
)
def test_label_to_monthly_frequency_preserves_author_policy(label: str, expected: float) -> None:
    assert label_to_monthly_frequency(label) == pytest.approx(expected)


def test_parse_label_bounds_keeps_lower_and_upper_yearly_bounds() -> None:
    assert parse_label_bounds("2 to 4 per 3 to 6 month") == pytest.approx(
        (2 * 365 / (6 * 30), 4 * 365 / (3 * 30))
    )


def test_parse_label_bounds_rejects_unparsable_labels() -> None:
    with pytest.raises(ValueError, match="Unparsable label"):
        parse_label_bounds("weekly-ish")


def test_label_to_frequency_record_preserves_no_reference_semantics_before_scoring() -> None:
    unknown = label_to_frequency_record("unknown")
    no_reference = label_to_frequency_record("no seizure frequency reference")

    assert unknown.kind is FrequencyLabelKind.UNKNOWN
    assert no_reference.kind is FrequencyLabelKind.NO_REFERENCE
    assert unknown.monthly_frequency == no_reference.monthly_frequency == 1000.0


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (None, "no seizure frequency reference"),
        ("", "no seizure frequency reference"),
        ("twice weekly", "2 per week"),
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


def test_format_preserving_repair_keeps_units_and_event_word_cleanup() -> None:
    assert repair_prediction_label_format_preserving("2 seizures per 4 months") == (
        "2 per 4 month"
    )
    assert repair_prediction_label_format_preserving("1 every other day") == "1 per 2 day"


def test_format_preserving_repair_preserves_no_reference_sentinel() -> None:
    assert (
        repair_prediction_label_format_preserving("no seizure frequency reference")
        == "no seizure frequency reference"
    )
    assert (
        repair_prediction_label_format_preserving("no frequency mentioned")
        == "no seizure frequency reference"
    )


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("up to 4 per day", "4 per day"),
        ("<= 4 per week", "4 per week"),
        ("\u2264 6 to 7 per year", "6 to 7 per year"),
        ("1 per month or less", "1 per month"),
        ("12 to 30 per quarter", "12 to 30 per 3 month"),
    ],
)
def test_format_preserving_repair_accepts_strict_benchmark_surface_forms(
    raw: str,
    expected: str,
) -> None:
    repaired = repair_prediction_label_format_preserving(raw)

    assert repaired == expected
    parse_label_bounds(repaired)


@pytest.mark.parametrize(
    "raw",
    [
        "1 cluster per week",
        "1 cluster per 4 weeks",
        "2 clusters per month, each five absences",
    ],
)
def test_format_preserving_repair_leaves_cluster_only_labels_as_raw_failures(
    raw: str,
) -> None:
    repaired = repair_prediction_label_format_preserving(raw)

    assert "cluster" in repaired
    assert repaired != "unknown"
    with pytest.raises(ValueError):
        label_to_frequency_record(repaired)


def test_format_preserving_repair_does_not_apply_semantic_basic_fallbacks() -> None:
    assert repair_prediction_label("several per week") == "multiple per week"
    assert repair_prediction_label_format_preserving("several per week") == "several per week"
    assert repair_prediction_label("a handful per month") == "no seizure frequency reference"
    assert repair_prediction_label_format_preserving("a handful per month") == (
        "handful per month"
    )
    assert repair_prediction_label("most weekdays") == "no seizure frequency reference"
    assert repair_prediction_label_format_preserving("most weekdays") == "most weekdays"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("1 cluster per 4 weeks", "1 per 4 week"),
        ("clusters every 4 days", "1 per 4 day"),
        ("clusters every 2-4 days", "1 per 2 to 4 day"),
        ("most weekdays", "multiple per week"),
        ("brief absences occurring on most weekdays", "multiple per week"),
        ("bimonthly", "1 per 2 month"),
        ("bi-monthly", "1 per 2 month"),
    ],
)
def test_clean_scorer_facing_gold_policy_normalizes_first_slice(
    raw: str,
    expected: str,
) -> None:
    repaired = repair_prediction_label_clean_scorer_facing(raw)

    assert repaired == expected
    parse_label_bounds(repaired)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("several per week", "multiple per week"),
        ("several last week", "multiple per week"),
        ("several times each week", "multiple per week"),
        ("multiple in past day", "multiple per day"),
        ("q1-2d", "1 per 1 to 2 day"),
        ("q two - three wk", "1 per 2 to 3 week"),
        ("Xfour/wk", "4 per week"),
        ("X7/mo", "7 per month"),
        (
            "2 cluster days per month, 6 seizures per cluster day",
            "2 cluster per month, 6 per cluster",
        ),
        (
            "1 cluster per week, 4 events per cluster",
            "1 cluster per week, 4 per cluster",
        ),
        ("7 in past 3 months", "7 per 3 month"),
        ("7 over 3 months", "7 per 3 month"),
    ],
)
def test_clean_scorer_facing_gold_policy_normalizes_table_backed_families(
    raw: str,
    expected: str,
) -> None:
    repaired = repair_prediction_label_clean_scorer_facing(raw)

    assert repaired == expected
    parse_label_bounds(repaired)


@pytest.mark.parametrize(
    "raw",
    [
        "most weeks",
        "several evenings per fortnight",
        "bimonthly, twice per month",
        "monthly clusters, typically 6 to 7 seizures over 24 h",
    ],
)
def test_clean_scorer_facing_gold_policy_preserves_table_boundaries(raw: str) -> None:
    assert repair_prediction_label_clean_scorer_facing(raw) == (
        repair_prediction_label_format_preserving(raw)
    )


def test_clean_scorer_facing_gold_policy_trace_names_policy_layer() -> None:
    trace = repair_prediction_label_clean_scorer_facing_with_trace("most weekdays")

    assert trace.final_label == "multiple per week"
    assert [event.rule_id for event in trace.events] == [
        "gold_normalization_policy.vague_weekday_cadence"
    ]
    assert all(event.group is RuleGroup.GOLD_NORMALIZATION_POLICY for event in trace.events)
    assert all(event.portability is Portability.GAN2026_SPECIFIC for event in trace.events)


def test_clean_scorer_facing_gold_policy_rules_have_dedicated_owner() -> None:
    assert CLEAN_SCORER_FACING_GOLD_NORMALIZATION_RULES is GOLD_POLICY_RULES
    assert {
        rule.group for rule in CLEAN_SCORER_FACING_GOLD_NORMALIZATION_RULES
    } == {RuleGroup.GOLD_NORMALIZATION_POLICY}
    assert {
        rule.portability for rule in CLEAN_SCORER_FACING_GOLD_NORMALIZATION_RULES
    } == {Portability.GAN2026_SPECIFIC}


@pytest.mark.parametrize(
    "raw",
    [
        "up to 4 per day",
        "<= once per month",
        "2 cluster per month, 6 per cluster",
        "monthly clusters, typically 6 to 7 seizures over 24 h",
        "bimonthly, twice per month",
    ],
)
def test_clean_scorer_facing_gold_policy_leaves_named_modules_out(raw: str) -> None:
    assert repair_prediction_label_clean_scorer_facing(raw) == (
        repair_prediction_label_format_preserving(raw)
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


def test_repair_prediction_label_with_evidence_repairs_cluster_on_multiple_days() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "multiple per month",
            (
                "Over the past month, the patient reports a cluster of short events "
                "on multiple days, each beginning with a brief sense of disconnection"
            ),
        )
        == "multiple cluster per month, multiple per cluster"
    )


def test_repair_prediction_label_with_evidence_repairs_recurrence_cluster_window() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "4 to 6 per day",
            (
                "He can sometimes go nearly two week without seizures, but when "
                "they recur he tends to have several in one day, often between 4 and 6."
            ),
        )
        == "1 cluster per 2 week, 4 to 6 per cluster"
    )


def test_repair_prediction_label_with_evidence_repairs_no_definite_events_window() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "unknown",
            "no definite epileptic events documented in the past two months",
        )
        == "seizure free for 2 month"
    )


def test_repair_prediction_label_with_evidence_repairs_current_non_epileptic_events() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "unknown",
            (
                "Seizure-like episodes are currently non-epileptic in nature and "
                "appear less troublesome."
            ),
        )
        == "seizure free for multiple year"
    )


def test_repair_prediction_label_with_evidence_repairs_plural_daily_events() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "1 per day",
            "They described daily brief events with preserved awareness.",
        )
        == "multiple per day"
    )


def test_repair_prediction_label_with_evidence_preserves_dozens_per_day() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "multiple per day",
            "Petit mal occur on a near-daily basis, sometimes dozens in a day.",
        )
        == "multiple per day"
    )


def test_repair_prediction_label_with_evidence_does_not_count_daily_no_event_entries() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "seizure free for 4 month",
            "The diary shows steady daily entries with no recorded spells suggestive of "
            "seizure activity.",
        )
        == "seizure free for 4 month"
    )


def test_repair_prediction_label_with_evidence_repairs_monthly_cluster_multiple() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "1 cluster per month",
            "events tend to gather into bursts roughly once each month, "
            "with several episodes over a few days",
        )
        == "1 cluster per month, multiple per cluster"
    )


def test_repair_prediction_label_with_evidence_repairs_weekly_cluster_multiple() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "1 cluster per week",
            "Weekly morning clusters reported; number per cluster not documented.",
        )
        == "1 cluster per week, multiple per cluster"
    )


def test_repair_prediction_label_with_evidence_repairs_quarter_cluster_multiple() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "2 clusters per quarter",
            "Patient reports two clusters this quarter with several brief episodes.",
        )
        == "2 cluster per 3 month, multiple per cluster"
    )


def test_repair_prediction_label_with_evidence_repairs_weekly_cluster_count() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "1 cluster per week",
            "cluster burden increased; now weekly, 2 - 3 per cluster",
        )
        == "1 cluster per week, 2 to 3 per cluster"
    )


def test_repair_prediction_label_with_evidence_repairs_grouped_weekly_clusters() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "multiple per week",
            "events occurring on 3-4 nights per week, with several brief episodes "
            "grouped together during the night",
        )
        == "3 to 4 cluster per week, multiple per cluster"
    )


def test_repair_prediction_label_with_evidence_repairs_several_fortnight_clusters() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "multiple per week",
            "clusters arise on several evenings per fortnight, each cluster with about "
            "five spells",
        )
        == "multiple cluster per 2 week, 5 per cluster"
    )


def test_repair_prediction_label_with_evidence_repairs_monthly_bursts() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "1 per month",
            "brief bursts occurring roughly once a month, typically soon after waking",
        )
        == "1 cluster per month, multiple per cluster"
    )


def test_repair_prediction_label_with_evidence_repairs_cluster_days_size_unknown() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "2 cluster days per month",
            "Seizure diary shows 2 cluster days this month; sizes unrecorded",
        )
        == "2 cluster per month, multiple per cluster"
    )


def test_repair_prediction_label_with_evidence_repairs_weekly_cluster_or_more() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "1 cluster per week",
            "Weekly clusters, usually 6 or more events within ~2 h",
        )
        == "1 cluster per week, 6 per cluster"
    )


def test_repair_prediction_label_with_evidence_repairs_cluster_days_with_count() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "2 cluster days per month, 3 to 4 seizures per cluster",
            "Cluster days twice this month; typically three - four seizures in 24 h",
        )
        == "2 cluster per month, 3 to 4 per cluster"
    )


def test_repair_prediction_label_with_evidence_repairs_cluster_times_month() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "3 per month",
            "Morning clusters 3×/month; ~three - four events over 90 min",
        )
        == "3 cluster per month, 3 to 4 per cluster"
    )


def test_repair_prediction_label_with_evidence_repairs_quarterly_cluster_episode() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "1 cluster per 3 months",
            "Quarterly clusters with one convulsions per episode",
        )
        == "1 cluster per 3 month, 1 per cluster"
    )


def test_repair_prediction_label_with_evidence_uses_clinic_date_for_year_to_date() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "5 per year",
            "just five generalised tonic-clonic seizures documented this year to date",
            context_text="Clinic Date: 24 February 2016",
        )
        == "5 per 2 month"
    )


def test_repair_prediction_label_with_evidence_uses_clinic_date_for_so_far_year() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "4 per year",
            "four tonic seizures documented in 2015 so far",
            context_text="Clinic Date: 24 January 2015",
        )
        == "4 per month"
    )


def test_repair_prediction_label_with_evidence_does_not_count_window_as_event_count() -> None:
    assert (
        repair_prediction_label_with_evidence(
            "abs monthly",
            "Over the past six months he describes brief events occurring abs monthly",
        )
        == "1 per month"
    )


def test_benchmark_repair_steps_are_valid_and_benchmark_format_only() -> None:
    validate_benchmark_repair_steps(BENCHMARK_REPAIR_STEPS)
    validate_benchmark_repair_steps(FORMAT_PRESERVING_BENCHMARK_REPAIR_STEPS)
    validate_rule_registry(BENCHMARK_REPAIR_RULES)
    validate_rule_registry(FORMAT_PRESERVING_BENCHMARK_REPAIR_RULES)
    validate_rule_registry(CLEAN_SCORER_FACING_GOLD_NORMALIZATION_RULES)
    assert BENCHMARK_REPAIR_STEPS
    assert BENCHMARK_REPAIR_RULES
    assert FORMAT_PRESERVING_BENCHMARK_REPAIR_STEPS
    assert FORMAT_PRESERVING_BENCHMARK_REPAIR_RULES
    assert len(FORMAT_PRESERVING_BENCHMARK_REPAIR_STEPS) < len(BENCHMARK_REPAIR_STEPS)
    assert {
        (step.group, step.portability) for step in BENCHMARK_REPAIR_STEPS
    } == {(RuleGroup.BENCHMARK_REPAIR, Portability.BENCHMARK_FORMAT)}
    assert {
        (rule.group, rule.portability) for rule in BENCHMARK_REPAIR_RULES
    } == {(RuleGroup.BENCHMARK_REPAIR, Portability.BENCHMARK_FORMAT)}
    assert {
        (rule.group, rule.portability)
        for rule in CLEAN_SCORER_FACING_GOLD_NORMALIZATION_RULES
    } == {(RuleGroup.GOLD_NORMALIZATION_POLICY, Portability.GAN2026_SPECIFIC)}


def test_benchmark_prediction_repair_owns_rule_tables() -> None:
    assert BENCHMARK_REPAIR_STEPS is benchmark_prediction_repair.BENCHMARK_REPAIR_STEPS
    assert BENCHMARK_REPAIR_RULES is benchmark_prediction_repair.BENCHMARK_REPAIR_RULES
    assert (
        FORMAT_PRESERVING_BENCHMARK_REPAIR_STEPS
        is benchmark_prediction_repair.FORMAT_PRESERVING_BENCHMARK_REPAIR_STEPS
    )
    assert (
        FORMAT_PRESERVING_BENCHMARK_REPAIR_RULES
        is benchmark_prediction_repair.FORMAT_PRESERVING_BENCHMARK_REPAIR_RULES
    )


def test_repair_prediction_label_trace_exposes_benchmark_repair_events() -> None:
    trace = repair_prediction_label_with_trace("about twice weekly")

    assert trace.final_label == "2 per week"
    assert repair_prediction_label("about twice weekly") == trace.final_label
    assert [event.rule_id for event in trace.events] == [
        "benchmark_repair.once_twice_thrice",
        "benchmark_repair.period_words",
        "benchmark_repair.drop_prediction_noise",
    ]
    assert all(event.group is RuleGroup.BENCHMARK_REPAIR for event in trace.events)
    assert all(event.portability is Portability.BENCHMARK_FORMAT for event in trace.events)


def test_repair_prediction_label_respects_rule_id_ablation() -> None:
    trace = repair_prediction_label_with_trace(
        "about twice weekly",
        AblationConfig(
            disabled_rule_ids=frozenset({"benchmark_repair.once_twice_thrice"})
        ),
    )

    assert trace.final_label == "1 per week"
    assert "benchmark_repair.once_twice_thrice" not in {
        event.rule_id for event in trace.events
    }
