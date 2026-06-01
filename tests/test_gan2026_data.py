from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    DEFAULT_SPLIT_MANIFEST_PATH,
    load_records,
    load_records_for_split,
    load_records_with_monthly_frequency,
    load_split_manifest,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.label_parser import FrequencyLabelKind

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
    assert records[0].gold_normalized_label == "2 cluster per month, 6 per cluster"
    assert records[0].gold_label_kind is FrequencyLabelKind.FREQUENCY
    assert records[0].gold_yearly_bounds == (146.0, 146.0)
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
    assert all(
        record.gold_label_kind is FrequencyLabelKind.NO_REFERENCE
        for record in row_not_ok_records
        if record.gold_label == "no seizure frequency reference"
    )
    assert all(record.gold_monthly_frequency is not None for record in row_not_ok_records)


def test_load_split_manifest_exposes_locked_gan2026_v1_splits() -> None:
    manifest = load_split_manifest(DEFAULT_SPLIT_MANIFEST_PATH)

    assert manifest["name"] == "gan2026_split_v1"
    assert manifest["seed"] == 20260531
    assert set(manifest["splits"]) == {"train", "validation", "test"}
    assert len(manifest["splits"]["train"]["source_row_indices"]) == 300
    assert len(manifest["splits"]["validation"]["source_row_indices"]) == 750
    assert len(manifest["splits"]["test"]["source_row_indices"]) == 450

    all_indices = [
        source_row_index
        for split in manifest["splits"].values()
        for source_row_index in split["source_row_indices"]
    ]
    assert len(all_indices) == 1500
    assert len(set(all_indices)) == 1500


def test_per_split_manifests_match_master_manifest() -> None:
    manifest = load_split_manifest(DEFAULT_SPLIT_MANIFEST_PATH)
    split_dir = DEFAULT_SPLIT_MANIFEST_PATH.parent

    for split_name in ("train", "validation", "test"):
        split_manifest = load_split_manifest(split_dir / f"{split_name}_v1.json")

        assert split_manifest["parent_manifest_name"] == manifest["name"]
        assert split_manifest["split"] == split_name
        assert split_manifest["count"] == manifest["splits"][split_name]["count"]
        assert (
            split_manifest["source_row_indices"]
            == manifest["splits"][split_name]["source_row_indices"]
        )


def test_load_records_for_split_returns_manifest_ordered_records() -> None:
    validation_records = load_records_for_split(
        "validation", DATA_PATH, DEFAULT_SPLIT_MANIFEST_PATH
    )
    manifest = load_split_manifest(DEFAULT_SPLIT_MANIFEST_PATH)

    assert len(validation_records) == 750
    assert [record.source_row_index for record in validation_records[:5]] == manifest["splits"][
        "validation"
    ]["source_row_indices"][:5]
    assert sum(record.row_ok for record in validation_records) == 718


def test_load_records_for_split_rejects_unknown_split() -> None:
    try:
        load_records_for_split("development", DATA_PATH, DEFAULT_SPLIT_MANIFEST_PATH)
    except ValueError as exc:
        assert str(exc) == "Unknown split 'development'. Expected one of: test, train, validation"
    else:
        raise AssertionError("unknown split did not raise")
