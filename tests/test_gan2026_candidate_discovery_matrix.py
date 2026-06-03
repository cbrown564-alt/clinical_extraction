from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    candidate_discovery_matrix,
)


def test_build_matrix_extracts_candidate_sources_and_gold_match_tiers(
    tmp_path: Path,
) -> None:
    artifact_path = tmp_path / "artifact.jsonl"
    note_text = (
        "Current seizures are 4 per day. He has been seizure free from tonic-clonic "
        "events for six months. Partner reports uncertain nocturnal spells."
    )
    artifact_path.write_text(
        _jsonl(
            {
                "source_row_index": 10,
                "split": "validation",
                "split_manifest": "gan2026_split_v1",
                "reference": {
                    "gold_label": "4 per day",
                    "gold_label_kind": "frequency",
                    "gold_monthly_frequency": 121.6666666667,
                    "gold_normalized_label": "4 per day",
                },
                "component_inputs": {
                    "note_text": note_text,
                    "deterministic_candidates": [
                        {
                            "event_id": "event_1",
                            "source_id": "det:event_1",
                            "kind": "frequency_rate",
                            "normalized_label": "4 per day",
                            "evidence": "4 per day",
                            "temporality": "current",
                            "assertion_status": "asserted",
                            "match_groups": {"count": "4", "unit": "day"},
                        }
                    ],
                    "deterministic_top": {
                        "final_label": "4 per day",
                        "final_kind": "frequency",
                        "evidence": "4 per day",
                        "selected_event_ids": ["event_1"],
                    },
                    "state_graph_nodes": [
                        {
                            "node_id": "sg-1",
                            "source_id": "graph:sg-1",
                            "kind": "seizure_free",
                            "normalized_label": "seizure free for 6 month",
                            "evidence": "seizure free from tonic-clonic events for six months",
                            "temporality": "current",
                            "assertion_status": "asserted",
                            "certainty": "certain",
                        }
                    ],
                    "llm_candidates": [
                        {
                            "candidate_id": "llm-1",
                            "source_id": "llm:llm-1",
                            "kind": "unknown_frequency",
                            "normalized_label": "unknown",
                            "evidence": "Partner reports uncertain nocturnal spells",
                            "temporality": "current",
                            "assertion_status": "uncertain",
                        }
                    ],
                },
            }
        ),
        encoding="utf-8",
    )
    atlas_csv = tmp_path / "atlas.csv"
    atlas_csv.write_text(
        "\n".join(
            [
                "artifact_name,source_row_index,hidden_families,first_failure_owner",
                "artifact.jsonl,10,rate_bucket_or_denominator;current_vs_historical,candidate_generation",
            ]
        ),
        encoding="utf-8",
    )

    rows, metadata = candidate_discovery_matrix.build_candidate_discovery_matrix(
        [artifact_path],
        atlas_csv_path=atlas_csv,
    )

    assert {row["generator_name"] for row in rows} == {
        "deterministic_candidates_all",
        "deterministic_top_candidate",
        "state_graph_nodes",
        "llm_candidate_selector_raw",
    }
    deterministic = _row_for(rows, "deterministic_candidates_all")
    assert deterministic["gold_match_status"] == "exact_label"
    assert deterministic["evidence_status"] == "exact"
    assert deterministic["hidden_families"] == [
        "rate_bucket_or_denominator",
        "current_vs_historical",
    ]
    assert deterministic["first_failure_owner"] == "candidate_generation"

    llm = _row_for(rows, "llm_candidate_selector_raw")
    assert llm["gold_match_status"] == "no_match"
    assert llm["metadata_missing_fields"] == []

    summary = metadata["by_generator"]
    assert summary["deterministic_candidates_all"]["candidate_rows"] == 1
    assert summary["deterministic_candidates_all"]["gold_state_recall_rows"] == 1
    assert summary["deterministic_candidates_all"]["gold_state_recalled_source_rows"] == 1
    assert summary["deterministic_candidates_all"]["gold_state_recall_rate"] == 1.0
    assert summary["llm_candidate_selector_raw"]["exact_evidence_rows"] == 1


def test_llm_selected_state_can_match_semantic_state_when_label_is_not_parseable(
    tmp_path: Path,
) -> None:
    artifact_path = tmp_path / "llm_heavy.jsonl"
    artifact_path.write_text(
        _jsonl(
            {
                "source_row_index": 20,
                "split": "validation",
                "reference": {
                    "gold_label": "4 per day",
                    "gold_label_kind": "frequency",
                    "gold_monthly_frequency": 121.6666666667,
                },
                "typed_input": {
                    "note_text": "Observed frequency is four per day in the current log."
                },
                "structured_record": {
                    "selected_fact": {
                        "fact_id": "fact-1",
                        "clinical_kind": "frequency",
                        "evidence": "Observed frequency is four per day",
                        "raw_value": "four per day",
                        "temporality": "current",
                        "assertion_status": "asserted",
                    },
                    "raw_model_answer": {
                        "raw_model_parser_label": "frequency",
                        "selected_evidence": "Observed frequency is four per day",
                    },
                },
            }
        ),
        encoding="utf-8",
    )

    rows, _metadata = candidate_discovery_matrix.build_candidate_discovery_matrix(
        [artifact_path]
    )

    assert len(rows) == 1
    assert rows[0]["generator_name"] == "llm_selected_state_or_evidence"
    assert rows[0]["candidate_label"] == "frequency"
    assert rows[0]["gold_match_status"] == "semantic_state"
    assert rows[0]["metadata_missing_fields"] == ["denominator_or_window"]


def test_write_outputs_include_summary_and_rows(tmp_path: Path) -> None:
    rows = [
        {
            "source_row_index": 1,
            "generator_name": "deterministic_top_candidate",
            "evidence_status": "exact",
            "gold_match_status": "exact_label",
            "hidden_families": ["unknown_boundary"],
        }
    ]
    metadata = candidate_discovery_matrix.summarize_candidate_rows(rows)
    jsonl_path = tmp_path / "matrix.jsonl"
    report_path = tmp_path / "matrix.md"

    candidate_discovery_matrix.write_matrix_jsonl(rows, jsonl_path)
    candidate_discovery_matrix.write_matrix_report(
        rows,
        metadata,
        report_path,
        jsonl_path=jsonl_path,
    )

    assert json.loads(jsonl_path.read_text(encoding="utf-8"))["source_row_index"] == 1
    report = report_path.read_text(encoding="utf-8")
    assert "Gan 2026 RQ1 Candidate-Discovery Matrix" in report
    assert "deterministic_top_candidate" in report


def _row_for(rows: list[dict], generator_name: str) -> dict:
    return next(row for row in rows if row["generator_name"] == generator_name)


def _jsonl(row: dict) -> str:
    return json.dumps(row) + "\n"
