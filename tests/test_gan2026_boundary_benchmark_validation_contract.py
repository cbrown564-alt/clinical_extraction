from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    boundary_benchmark_validation_contract,
    boundary_benchmark_validation_panel,
)


def test_validation_contract_replays_saved_typed_fields() -> None:
    panel_rows = boundary_benchmark_validation_panel.build_validation_panel_rows(
        [
            _record(
                source_row_index=1,
                gold_reference="Last seizure on 25 December 2023",
                gold_label="unknown",
            )
        ]
    )

    result = boundary_benchmark_validation_contract.build_contract_row(panel_rows[0])

    assert result["target_mechanism"] == "seizure_free_boundary_event_v0"
    assert result["component_owner"] == "typed_boundary_classifier"
    assert result["boundary_state"] == "last_event_only"
    assert result["clinical_final_state"] == "last_event_only"
    assert result["gan_rendered_label"] == "unknown"
    assert result["exact_evidence"] is True
    assert result["contract_matched"] is True
    assert result["source_note_text"] is None


def test_validation_renderer_contract_keeps_projection_transparent() -> None:
    panel_rows = boundary_benchmark_validation_panel.build_validation_panel_rows(
        [
            _record(
                source_row_index=2,
                gold_reference=(
                    "1 cluster per month; number per cluster not documented"
                ),
                gold_label="1 cluster per month, multiple per cluster",
            )
        ]
    )

    result = boundary_benchmark_validation_contract.build_contract_row(panel_rows[0])

    assert result["target_mechanism"] == "benchmark_convention_renderer_v0"
    assert result["component_owner"] == "benchmark_renderer"
    assert result["clinical_final_state"] == "cluster_frequency_with_unresolved_burden"
    assert result["gan_rendered_label"] == "1 cluster per month, multiple per cluster"
    assert result["format_only_change"] is True
    assert result["benchmark_format_rule_id"] == "gan_cluster_multiple_per_cluster"
    assert result["final_label_policy_connected"] is False


def test_validation_contract_summary_passes_current_panel() -> None:
    panel_rows = boundary_benchmark_validation_panel.build_validation_panel_rows(
        [
            _record(1, "Last seizure on 25 December 2023", "unknown"),
            _record(2, "Seizures with missed ASM doses", "unknown"),
            _record(3, "No events for 10 months", "seizure free for 10 month"),
            _record(4, "multiple focal seizures per week", "multiple per week"),
        ]
    )
    result_rows = boundary_benchmark_validation_contract.build_contract_rows(panel_rows)
    summary = boundary_benchmark_validation_contract.summarize_contract_rows(result_rows)

    assert summary["decision"] == "boundary_renderer_validation_contract_passed"
    assert summary["row_count"] == 4
    assert summary["contract_matched_rows"] == 4
    assert summary["exact_evidence_rows"] == 4
    assert summary["final_label_policy_connected"] is False
    assert summary["source_note_text_rows"] == 0


def test_validation_contract_flags_unmatched_mechanism_metadata() -> None:
    row = boundary_benchmark_validation_panel.build_validation_panel_rows(
        [_record(1, "Last seizure on 25 December 2023", "unknown")]
    )[0]
    row["expected_candidate_exposure"] = "typed_clinical_state_present"

    result = boundary_benchmark_validation_contract.build_contract_row(row)

    assert result["candidate_exposure"] == "typed_boundary_event_present"
    assert result["contract_matched"] is False
    assert "candidate_exposure_mismatch" in result["contract_issues"]


def _record(
    source_row_index: int,
    gold_reference: str,
    gold_label: str,
) -> dict[str, object]:
    return {
        "source_row_index": source_row_index,
        "gold_reference": gold_reference,
        "gold_label": gold_label,
        "note_text": f"History: {gold_reference}.",
    }
