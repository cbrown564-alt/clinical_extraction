from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    FrequencyLabelKind,
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist


def test_multiple_per_week_projects_as_two_per_week() -> None:
    multiple = label_to_frequency_record("multiple per week")
    counted = label_to_frequency_record("2 per week")

    assert multiple.normalized_label == "multiple per week"
    assert multiple.kind is FrequencyLabelKind.UNRESOLVED_MULTIPLE
    assert multiple.monthly_frequency == counted.monthly_frequency
    assert map_purist(multiple.monthly_frequency) == "seizure_freq_more1week_less1day"
    assert map_pragmatic(multiple.monthly_frequency) == "seizure_frequent"


def test_author_eval_multiple_count_projections() -> None:
    assert label_to_frequency_record("multiple per day").monthly_frequency == (
        label_to_frequency_record("2 per day").monthly_frequency
    )
    assert label_to_frequency_record("multiple per month").monthly_frequency == (
        label_to_frequency_record("8 per month").monthly_frequency
    )
    assert label_to_frequency_record("multiple per year").monthly_frequency == (
        label_to_frequency_record("18 per year").monthly_frequency
    )
    assert label_to_frequency_record("1 per multiple month").monthly_frequency == (
        label_to_frequency_record("1 per 2 month").monthly_frequency
    )
    assert label_to_frequency_record("1 per multiple day").monthly_frequency == (
        label_to_frequency_record("1 per 2 day").monthly_frequency
    )
    assert label_to_frequency_record("multiple per 15 month").monthly_frequency == (
        label_to_frequency_record("8 per 15 month").monthly_frequency
    )
    assert label_to_frequency_record(
        "1 cluster per month, multiple per cluster"
    ).monthly_frequency == label_to_frequency_record("8 per month").monthly_frequency
    assert label_to_frequency_record(
        "1 cluster per week, multiple per cluster"
    ).monthly_frequency == label_to_frequency_record("2 per week").monthly_frequency


def test_unknown_and_no_reference_remain_scoring_sentinels() -> None:
    assert label_to_frequency_record("unknown").monthly_frequency == 1000.0
    assert label_to_frequency_record("no seizure frequency reference").monthly_frequency == (
        1000.0
    )
