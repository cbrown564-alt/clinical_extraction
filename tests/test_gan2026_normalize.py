import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    BENCHMARK_REPAIR_RULES,
    BENCHMARK_REPAIR_STEPS,
    FrequencyLabelKind,
    label_to_frequency_record,
    label_to_monthly_frequency,
    parse_label_bounds,
    repair_prediction_label,
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
    validate_rule_registry(BENCHMARK_REPAIR_RULES)
    assert BENCHMARK_REPAIR_STEPS
    assert BENCHMARK_REPAIR_RULES
    assert {
        (step.group, step.portability) for step in BENCHMARK_REPAIR_STEPS
    } == {(RuleGroup.BENCHMARK_REPAIR, Portability.BENCHMARK_FORMAT)}
    assert {
        (rule.group, rule.portability) for rule in BENCHMARK_REPAIR_RULES
    } == {(RuleGroup.BENCHMARK_REPAIR, Portability.BENCHMARK_FORMAT)}


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
