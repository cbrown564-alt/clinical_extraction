from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    load_records,
    load_records_with_monthly_frequency,
)

DATA_PATH = Path("data/Gan (2026)/synthetic_data_subset_1500.json")


def test_load_records_smoke() -> None:
    records = load_records(DATA_PATH)
    assert len(records) == 1500
    assert records[0].source_row_index
    assert "Clinic Date:" in records[0].note_text


def test_load_records_exposes_gold_label_and_quality_flags() -> None:
    records = load_records(DATA_PATH)

    first = records[0]
    assert first.source_row_index == 11118
    assert first.note_text.startswith("Department of Neurology")
    assert first.gold_label == "2 cluster per month, 6 per cluster"
    assert first.gold_reference == "Cluster days twice this month; typically six seizures in 24 h"
    assert first.row_ok is True
    assert first.labels_match_all_categories is True
    assert first.quotes_ok_all_categories is True


def test_load_records_with_monthly_frequency_matches_author_parser_for_gold_labels() -> None:
    records = load_records_with_monthly_frequency(DATA_PATH)

    assert len(records) == 1500
    assert records[0].gold_monthly_frequency == 12 * 365 / 30 / 12
    assert sum(record.row_ok for record in records) == 1435
    assert sum(not record.row_ok for record in records) == 65


def test_row_not_ok_records_remain_in_evaluation_surface() -> None:
    records = load_records_with_monthly_frequency(DATA_PATH)
    row_not_ok_records = [record for record in records if not record.row_ok]

    assert len(row_not_ok_records) == 65
    assert sum(
        record.gold_label == "no seizure frequency reference" for record in row_not_ok_records
    ) == 54
    assert all(record.gold_monthly_frequency is not None for record in row_not_ok_records)
