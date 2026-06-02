from __future__ import annotations

from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import GanFrequencyRecord
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments import (
    state_graph_diagnostics,
)


def test_state_graph_diagnostics_separates_oracle_coverage_from_projection() -> None:
    records = [
        _record(
            source_row_index=1,
            note_text=(
                "She has no tonic-clonic seizures for one year, "
                "but still has three focal seizures per month."
            ),
            gold_label="3 per month",
        ),
        _record(
            source_row_index=2,
            note_text="Seizures are discussed but no frequency is quantified.",
            gold_label="1 per day",
        ),
    ]

    rows, metadata = state_graph_diagnostics.run_state_graph_diagnostics(
        records,
        split="validation",
        split_manifest="gan2026_split_v1",
        surface_note="test surface",
    )

    assert len(rows) == 2
    assert metadata["summary"]["oracle_coverage"]["representable_count"] == 1
    assert metadata["summary"]["projection"]["exact_label_matches"] == 1
    assert rows[0]["oracle_representable"] is True
    assert rows[0]["projection"]["final_label"] == "3 per month"
    assert rows[1]["oracle_representable"] is False


def test_state_graph_diagnostics_writes_markdown_report(tmp_path: Path) -> None:
    records = [
        _record(
            source_row_index=1,
            note_text="Current frequency: two seizures per week.",
            gold_label="2 per week",
        )
    ]
    rows, metadata = state_graph_diagnostics.run_state_graph_diagnostics(
        records,
        split="validation",
        split_manifest="gan2026_split_v1",
        surface_note="test surface",
    )
    report_path = tmp_path / "report.md"

    state_graph_diagnostics.write_state_graph_report(
        rows,
        metadata,
        report_path,
        jsonl_path=tmp_path / "rows.jsonl",
        json_path=tmp_path / "summary.json",
    )

    text = report_path.read_text(encoding="utf-8")
    assert "Oracle Coverage" in text
    assert "Projection Diagnostics" in text
    assert "not a benchmark result" in text


def _record(
    *,
    source_row_index: int,
    note_text: str,
    gold_label: str,
) -> GanFrequencyRecord:
    parsed = label_to_frequency_record(gold_label)
    return GanFrequencyRecord(
        source_row_index=source_row_index,
        note_text=note_text,
        gold_label=gold_label,
        gold_reference="",
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
        gold_normalized_label=parsed.normalized_label,
        gold_label_kind=parsed.kind,
        gold_yearly_bounds=parsed.yearly_bounds,
        gold_monthly_frequency=parsed.monthly_frequency,
    )
