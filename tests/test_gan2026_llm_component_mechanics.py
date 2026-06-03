from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    llm_component_mechanics,
)


def test_build_mechanics_rows_extracts_llm_candidate_win_and_evidence_regression(
    tmp_path: Path,
) -> None:
    rq1 = tmp_path / "rq1.jsonl"
    rq2 = tmp_path / "rq2.jsonl"
    rq4 = tmp_path / "rq4.jsonl"
    rq1.write_text(
        _jsonl(
            {
                "source_row_index": 1,
                "split": "validation",
                "generator_name": "deterministic_candidates_all",
                "gold_label": "unknown",
                "candidate_label": "seizure free",
                "candidate_evidence": "no events",
                "gold_match_status": "no_match",
                "hidden_families": ["unknown_boundary"],
            }
        )
        + _jsonl(
            {
                "source_row_index": 1,
                "split": "validation",
                "generator_name": "llm_candidate_selector_raw",
                "gold_label": "unknown",
                "candidate_label": "unknown",
                "candidate_evidence": "unclear whether spells are seizures",
                "gold_match_status": "exact_label",
                "hidden_families": ["unknown_boundary"],
            }
        ),
        encoding="utf-8",
    )
    rq2.write_text(
        _jsonl(
            {
                "source_row_index": 2,
                "split": "validation",
                "candidate_name": "hybrid_adjudicator_raw",
                "gold_label": "1 per day",
                "candidate_label": "unknown",
                "baseline_label": "1 per day",
                "selected_evidence": "daily jerks",
                "evidence_status": "exact",
                "source_id_status": "valid",
                "purist_correct": False,
                "correct_to_wrong": True,
            }
        ),
        encoding="utf-8",
    )
    rq4.write_text("", encoding="utf-8")

    rows, metadata = llm_component_mechanics.build_llm_component_mechanics_rows(
        rq1_matrix_path=rq1,
        rq2_matrix_path=rq2,
        rq4_matrix_path=rq4,
    )

    buckets = {row["mechanism_bucket"] for row in rows}
    assert "rq1_llm_candidate_win_over_deterministic_miss" in buckets
    assert "rq2_llm_correct_to_wrong" in buckets
    assert "rq2_exact_evidence_but_wrong_state" in buckets
    assert metadata["source_row_count"] == 2


def test_write_mechanics_report(tmp_path: Path) -> None:
    rows = [
        {
            "clinical_subproblem": "projection",
            "mechanism_bucket": "rq4_projection_wrong_to_correct",
            "component_name": "boundary_state_priority",
            "source_row_index": 1,
            "gold_label": "unknown",
            "candidate_label": "unknown",
            "evidence_snippet": "uncertain frequency",
            "hidden_families": ["unknown_boundary"],
        }
    ]
    metadata = llm_component_mechanics.summarize_mechanics_rows(rows)
    jsonl_path = tmp_path / "mechanics.jsonl"
    report_path = tmp_path / "mechanics.md"

    llm_component_mechanics.write_mechanics_jsonl(rows, jsonl_path)
    llm_component_mechanics.write_mechanics_report(
        rows,
        metadata,
        report_path,
        jsonl_path=jsonl_path,
    )

    assert json.loads(jsonl_path.read_text(encoding="utf-8"))["source_row_index"] == 1
    report = report_path.read_text(encoding="utf-8")
    assert "Gan 2026 LLM Component Mechanics Rows" in report
    assert "rq4_projection_wrong_to_correct" in report


def _jsonl(row: dict) -> str:
    return json.dumps(row) + "\n"
