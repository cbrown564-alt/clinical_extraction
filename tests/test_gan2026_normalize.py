import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    FrequencyLabelKind,
    label_to_frequency_record,
    label_to_monthly_frequency,
    parse_label_bounds,
    repair_prediction_label,
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
