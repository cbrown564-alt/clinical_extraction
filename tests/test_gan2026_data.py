from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.data import load_records


def test_load_records_smoke() -> None:
    records = load_records(Path("data/Gan (2026)/synthetic_data_subset_1500.json"))
    assert len(records) == 1500
    assert records[0].source_row_index
    assert "Clinic Date:" in records[0].note_text

