from __future__ import annotations

from pathlib import Path

from clinical_extraction_local.input import read_notes
from clinical_extraction_local.versions import version_record


def test_synthetic_input_and_version_assets_are_self_contained() -> None:
    root = Path(__file__).resolve().parents[1]
    notes = read_notes(root / "examples" / "seizure_frequency" / "notes.jsonl")
    assert notes[0].note_id.startswith("synthetic-")
    record = version_record()
    assert set(record["asset_sha256"]) == {
        "seizure_frequency_prompt",
        "seizure_frequency_schema",
        "clinical_findings_prompt",
        "clinical_findings_schema",
    }
