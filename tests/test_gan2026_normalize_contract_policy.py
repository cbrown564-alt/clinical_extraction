"""Invariant-focused tests for gan2026 normalize contract policy."""

import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.gold_policy import (
    CLEAN_SCORER_FACING_GOLD_NORMALIZATION_RULES as GOLD_POLICY_RULES,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
    label_to_frequency_record,
    label_to_monthly_frequency,
    parse_label_bounds,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import (
    Portability,
    RuleGroup,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rules import (
    benchmark_repair,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    CLEAN_SCORER_FACING_GOLD_NORMALIZATION_RULES,
    repair_prediction_label,
    repair_prediction_label_clean_scorer_facing,
    repair_prediction_label_clean_scorer_facing_with_trace,
    repair_prediction_label_format_preserving,
)

validate_benchmark_repair_steps = benchmark_repair.validate_benchmark_repair_steps


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


def test_format_preserving_repair_keeps_units_and_event_word_cleanup() -> None:
    assert repair_prediction_label_format_preserving("2 seizures per 4 months") == ("2 per 4 month")
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
    assert repair_prediction_label_format_preserving("a handful per month") == ("handful per month")
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
    assert {rule.group for rule in CLEAN_SCORER_FACING_GOLD_NORMALIZATION_RULES} == {
        RuleGroup.GOLD_NORMALIZATION_POLICY
    }
    assert {rule.portability for rule in CLEAN_SCORER_FACING_GOLD_NORMALIZATION_RULES} == {
        Portability.GAN2026_SPECIFIC
    }


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
