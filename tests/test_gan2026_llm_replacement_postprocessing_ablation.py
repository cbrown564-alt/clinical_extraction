import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    llm_replacement_postprocessing_ablation as replacement_ablation,
)


def _saved_row() -> dict:
    return {
        "source_row_index": 10,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "reused_raw_output": True,
        "structured_record": {
            "final_answer": {
                "raw_llm_final_label": "twice per month",
                "raw_llm_final_kind": "frequency",
            }
        },
        "reference": {
            "gold_label": "2 per month",
            "gold_purist_category": "seizure_freq_1topermonth",
            "gold_pragmatic_category": "seizure_controlled",
        },
        "evidence_summary": {
            "selected_evidence_valid": True,
            "selected_event_evidence_valid": True,
            "event_evidence_valid": 3,
            "event_evidence_total": 3,
        },
        "component_status": {"selected_event_trace": "ok"},
        "parse_errors": [],
        "score_layers": {
            "raw_llm": {
                "final_label": "twice per month",
                "scorable": False,
                "purist_correct": False,
                "pragmatic_correct": False,
                "predicted_purist_category": None,
                "predicted_pragmatic_category": None,
            },
            "format_only": {
                "final_label": "2 per month",
                "scorable": True,
                "purist_correct": True,
                "pragmatic_correct": True,
                "predicted_purist_category": "seizure_freq_1topermonth",
                "predicted_pragmatic_category": "seizure_controlled",
                "repair_mode_metadata": {
                    "repair_mode": "format_only",
                    "repair_family": "format_preserving_label_repair",
                    "semantic_selection_owner": "llm",
                },
            },
            "selected_evidence_arithmetic": {
                "final_label": "2 per month",
                "scorable": True,
                "purist_correct": True,
                "pragmatic_correct": True,
                "predicted_purist_category": "seizure_freq_1topermonth",
                "predicted_pragmatic_category": "seizure_controlled",
                "repair_mode_metadata": {
                    "repair_mode": "selected_evidence_arithmetic",
                    "repair_family": "selected_evidence_arithmetic_only",
                    "semantic_selection_owner": (
                        "llm_selected_evidence_then_deterministic_arithmetic"
                    ),
                },
            },
            "benchmark_aligned": {
                "final_label": "2 per month",
                "scorable": True,
                "purist_correct": True,
                "pragmatic_correct": True,
                "predicted_purist_category": "seizure_freq_1topermonth",
                "predicted_pragmatic_category": "seizure_controlled",
            },
        },
    }


def _trace_mismatch_row() -> dict:
    row = json.loads(json.dumps(_saved_row()))
    row["source_row_index"] = 11
    row["reused_raw_output"] = False
    row["component_status"] = {"selected_event_trace": "mismatch"}
    row["evidence_summary"]["selected_evidence_valid"] = False
    row["parse_errors"] = ["selected_event_trace: final_answer ids differ from selection ids"]
    for layer in row["score_layers"].values():
        layer["purist_correct"] = False
        layer["pragmatic_correct"] = False
    return row


def test_build_replacement_ablation_reports_required_condition_rows() -> None:
    rows, metadata = replacement_ablation.build_replacement_ablation(
        [_saved_row(), _trace_mismatch_row()],
        source_jsonl="saved.jsonl",
        split="validation",
        split_manifest="gan2026_split_v1",
    )

    assert metadata["artifact_kind"] == "llm_replacement_postprocessing_ablation"
    assert metadata["summary"]["row_count"] == 2
    assert metadata["summary"]["replay_variance"]["reused_raw_output_rows"] == 1
    assert [condition["condition"] for condition in metadata["conditions"]] == [
        "raw_model_selected_label",
        "format_only_repair",
        "selected_evidence_arithmetic_only",
        "benchmark_aligned_adapter",
    ]
    assert metadata["conditions"][1]["repair_attribution"]["raw_wrong_to_condition_correct"] == 1
    assert metadata["conditions"][0]["evidence_validity"]["selected_event_trace_mismatches"] == 1
    format_row = next(
        row
        for row in rows
        if row["source_row_index"] == 10 and row["condition"] == "format_only_repair"
    )
    assert format_row["prediction_owner"] == "llm"
    assert format_row["repair_mode"] == "format_only"
    assert format_row["raw_label"] == "twice per month"
    assert format_row["final_label"] == "2 per month"
    assert format_row["changed_from_raw"] is True
    assert format_row["transition_reason"] == "format_preserving_label_repair"
    assert format_row["selected_evidence_valid"] is True
    assert format_row["event_or_node_evidence_valid"] is True


def test_replacement_ablation_writes_jsonl_json_markdown_and_registry_entry(
    tmp_path: Path,
) -> None:
    rows, metadata = replacement_ablation.build_replacement_ablation(
        [_saved_row()],
        source_jsonl="saved.jsonl",
        split="validation",
        split_manifest="gan2026_split_v1",
    )
    jsonl_path = tmp_path / "rows.jsonl"
    json_path = tmp_path / "summary.json"
    report_path = tmp_path / "report.md"

    replacement_ablation.write_replacement_ablation_outputs(
        rows,
        metadata,
        jsonl_path=jsonl_path,
        json_path=json_path,
        markdown_path=report_path,
    )
    entry = replacement_ablation.registry_entry_for_replacement_ablation(
        metadata,
        artifact_paths=("experiments/rows.jsonl", "experiments/summary.json"),
    )

    assert len(jsonl_path.read_text(encoding="utf-8").splitlines()) == 4
    assert json.loads(json_path.read_text(encoding="utf-8"))["summary"]["row_count"] == 1
    report = report_path.read_text(encoding="utf-8")
    assert "LLM-Replacement Post-Processing Ablation" in report
    assert "`selected_evidence_arithmetic_only`" in report
    assert entry.run_id == "gan2026_llm_replacement_postprocessing_ablation_validation1_2026-06-02"
    assert entry.replay_status == "saved_output_replay"
    assert entry.primary_metrics["format_only_repair_purist_correct"] == 1
