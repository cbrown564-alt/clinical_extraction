import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    label_to_monthly_frequency,
    parse_label_bounds,
)


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("seizure free for multiple month", 0.0),
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
