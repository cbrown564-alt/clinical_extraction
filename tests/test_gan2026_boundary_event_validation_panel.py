from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    boundary_event_validation_panel,
)


def test_boundary_event_validation_panel_emits_typed_rows_without_note_text() -> None:
    rows = boundary_event_validation_panel.build_validation_panel_rows(
        [
            _record(1, "unknown", "Last seizure on 25 December 2023"),
            _record(2, "multiple per week", "Several episodes per week"),
        ]
    )

    assert len(rows) == 2
    boundary_row = next(row for row in rows if row["slice_id"] == "last_event_only")
    renderer_row = next(row for row in rows if row["slice_id"] == "vague_multiple_frequency")

    assert boundary_row["policy_name"] == "gan2026_boundary_event_validation_panel_v1"
    assert boundary_row["clinical_event"] == {
        "event_target": "seizure",
        "event_kind": "last_event_only",
        "event_state": "last_event_only",
        "component_owner": "typed_boundary_classifier",
    }
    assert boundary_row["projection_policy"]["projection_owner"] == (
        "boundary_projection_policy"
    )
    assert boundary_row["source_note_text"] is None
    assert boundary_row["source_note_text_present"] is False
    assert boundary_row["final_label_policy_connected"] is False
    assert boundary_row["exact_evidence"] is True

    assert renderer_row["clinical_event"]["event_kind"] == "benchmark_format_convention"
    assert renderer_row["selected_frequency_state"] == "vague_multiple_current_events"
    assert renderer_row["projection_policy"]["projection_owner"] == "benchmark_renderer"
    assert renderer_row["gan_rendered_label"] == "multiple per week"


def test_boundary_event_validation_panel_suppresses_unsupported_records() -> None:
    rows, summary = boundary_event_validation_panel.build_rows_and_summary(
        [
            _record(1, "unknown", "Last seizure on 25 December 2023"),
            _record(2, "multiple per week", "Several episodes per week"),
            _record(3, "weekly", "Medication unchanged"),
        ]
    )

    assert len(rows) == 2
    assert summary["decision"] == "boundary_event_validation_panel_v1_ready"
    assert summary["source_record_count"] == 3
    assert summary["suppressed_source_records"] == 1
    assert summary["unsupported_candidate_rows"] == 0
    assert summary["source_note_text_rows"] == 0


def test_boundary_event_validation_panel_summary_requires_complete_metadata() -> None:
    rows = boundary_event_validation_panel.build_validation_panel_rows(
        [
            _record(1, "unknown", "Last seizure on 25 December 2023"),
            _record(2, "multiple per week", "Several episodes per week"),
        ]
    )
    summary = boundary_event_validation_panel.summarize_validation_panel_rows(
        rows,
        source_record_count=2,
    )

    assert summary["row_count"] == 2
    assert summary["typed_event_complete_rows"] == 2
    assert summary["projection_policy_complete_rows"] == 2
    assert summary["exact_evidence_rows"] == 2
    assert summary["final_label_policy_connected"] is False
    assert summary["decision"] == "boundary_event_validation_panel_v1_ready"


def _record(source_row_index: int, gold_label: str, gold_reference: str) -> dict[str, object]:
    return {
        "source_row_index": source_row_index,
        "note_text": f"Clinical note. {gold_reference}. Medication unchanged.",
        "gold_label": gold_label,
        "gold_reference": gold_reference,
    }
