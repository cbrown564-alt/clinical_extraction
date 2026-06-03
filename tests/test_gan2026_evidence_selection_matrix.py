from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    evidence_selection_matrix,
)


def test_build_matrix_extracts_hybrid_evidence_selection_components(tmp_path: Path) -> None:
    artifact_path = tmp_path / "hybrid.jsonl"
    note_text = "Current seizures are four per day. Older logs said one per month."
    artifact_path.write_text(
        _jsonl(
            {
                "source_row_index": 10,
                "split": "validation",
                "reference": {"gold_label": "4 per day"},
                "component_inputs": {
                    "note_text": note_text,
                    "deterministic_top": {
                        "final_label": "4 per day",
                        "evidence": "four per day",
                        "selected_event_ids": ["event_1"],
                    },
                    "state_graph_projection": {
                        "final_label": "4 per day",
                        "evidence": "four per day",
                        "selected_node_ids": ["sg-1"],
                    },
                    "llm_candidate_selection": {
                        "selected_evidence": "Older logs said one per month",
                        "selected_candidate_ids": ["llm-1"],
                    },
                },
                "diagnostics": {"selected_evidence_exact": True},
                "score_layers": {
                    "deterministic_top_candidate": {
                        "final_label": "4 per day",
                        "scorable": True,
                        "purist_correct": True,
                    },
                    "state_graph_projection": {
                        "final_label": "4 per day",
                        "scorable": True,
                        "purist_correct": True,
                    },
                    "llm_candidate_selector_raw": {
                        "final_label": "1 per month",
                        "scorable": True,
                        "purist_correct": False,
                    },
                    "hybrid_adjudicator_raw": {
                        "final_label": "4 per day",
                        "scorable": True,
                        "purist_correct": True,
                    },
                },
                "structured_adjudicator_record": {
                    "selected_evidence": "four per day",
                    "selected_source_ids": ["det:event_1", "graph:sg-1"],
                },
            }
        ),
        encoding="utf-8",
    )

    rows, metadata = evidence_selection_matrix.build_evidence_selection_matrix(
        [artifact_path],
        atlas_csv_path=None,
    )

    assert {row["candidate_name"] for row in rows} == {
        "deterministic_top_candidate",
        "state_graph_projection",
        "llm_candidate_selector_raw",
        "hybrid_adjudicator_raw",
    }
    llm = _row_for(rows, "llm_candidate_selector_raw")
    assert llm["evidence_status"] == "exact"
    assert llm["changed_from_deterministic"] is True
    assert llm["correct_to_wrong"] is True
    assert metadata["by_component"]["hybrid_adjudicator_raw"]["source_id_valid_rate"] == 1.0


def test_build_matrix_extracts_llm_heavy_and_claim_table_rows(tmp_path: Path) -> None:
    artifact_path = tmp_path / "llm_rows.jsonl"
    artifact_path.write_text(
        _jsonl(
            {
                "source_row_index": 20,
                "split": "validation",
                "pipeline_family": "llm_heavy_evidence_selection_with_deterministic_adapters",
                "reference": {"gold_label": "4 per day"},
                "typed_input": {"note_text": "Observed current frequency is four per day."},
                "evidence_summary": {
                    "selected_evidence_valid": True,
                    "selected_fact_evidence": "Observed current frequency is four per day.",
                },
                "mechanical_adapter": {"operand_complete": True},
                "score_layers": {
                    "raw_model_clinical_selection": {
                        "final_label": "4 per 1 day",
                        "scorable": True,
                        "purist_correct": True,
                    }
                },
                "structured_record": {
                    "selected_fact": {
                        "fact_id": "fact-1",
                        "evidence": "Observed current frequency is four per day.",
                    }
                },
            }
        )
        + _jsonl(
            {
                "source_row_index": 30,
                "split": "validation",
                "pipeline_name": "gan2026_llm_only_claim_table_selector_v5",
                "reference": {"gold_label": "unknown"},
                "evidence_summary": {
                    "selected_evidence": "not in note",
                    "selected_evidence_valid": False,
                },
                "score_layers": {
                    "raw": {
                        "final_label": "unknown",
                        "scorable": True,
                        "purist_correct": True,
                    }
                },
                "structured_record": {
                    "final_query": {
                        "evidence": "not in note",
                        "selected_claim_ids": ["c1"],
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    rows, metadata = evidence_selection_matrix.build_evidence_selection_matrix(
        [artifact_path],
        atlas_csv_path=None,
    )

    heavy = _row_for(rows, "llm_heavy_selected_fact")
    claim = _row_for(rows, "claim_table_final_query")
    assert heavy["evidence_status"] == "exact"
    assert heavy["operand_complete"] is True
    assert claim["evidence_status"] == "invalid"
    assert claim["source_id_status"] == "valid"
    assert metadata["by_component"]["llm_heavy_selected_fact"]["operand_complete_rate"] == 1.0


def test_write_outputs_include_component_summary(tmp_path: Path) -> None:
    rows = [
        {
            "source_row_index": 1,
            "candidate_name": "deterministic_top_candidate",
            "evidence_status": "exact",
            "source_id_status": "valid",
            "scorable": True,
            "purist_correct": True,
            "operand_complete": None,
            "changed_from_deterministic": False,
            "wrong_to_correct": False,
            "correct_to_wrong": False,
            "hidden_families": ["rate_denominator"],
        }
    ]
    metadata = evidence_selection_matrix.summarize_evidence_rows(rows)
    jsonl_path = tmp_path / "matrix.jsonl"
    report_path = tmp_path / "matrix.md"

    evidence_selection_matrix.write_matrix_jsonl(rows, jsonl_path)
    evidence_selection_matrix.write_matrix_report(
        rows,
        metadata,
        report_path,
        jsonl_path=jsonl_path,
    )

    assert json.loads(jsonl_path.read_text(encoding="utf-8"))["source_row_index"] == 1
    report = report_path.read_text(encoding="utf-8")
    assert "Gan 2026 RQ2 Evidence-Selection Matrix" in report
    assert "deterministic_top_candidate" in report


def _row_for(rows: list[dict], candidate_name: str) -> dict:
    return next(row for row in rows if row["candidate_name"] == candidate_name)


def _jsonl(row: dict) -> str:
    return json.dumps(row) + "\n"
