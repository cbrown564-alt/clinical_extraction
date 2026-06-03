from __future__ import annotations

import json
from pathlib import Path

import pytest

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    selective_safety_floor_gate_replay as replay,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)


def test_projection_boundary_and_combined_gate_fire_before_llm_sidecar(tmp_path: Path) -> None:
    artifact_path = tmp_path / "artifact.jsonl"
    artifact_path.write_text(
        _jsonl(
            {
                "source_row_index": 2,
                "reference": {
                    "gold_label": "unknown",
                    "gold_label_kind": "unknown",
                    "gold_monthly_frequency": 1000.0,
                },
                "score_layers": {
                    "hybrid_adjudicator_with_adapters": {
                        "final_label": "2 per month",
                        "purist_correct": False,
                        "pragmatic_correct": False,
                        "scorable": True,
                    },
                    "state_graph_projection": {
                        "final_label": "2 per month",
                        "purist_correct": False,
                        "pragmatic_correct": False,
                        "scorable": True,
                    },
                    "llm_candidate_selector_raw": {
                        "final_label": "seizure free for multiple year",
                        "purist_correct": False,
                        "pragmatic_correct": True,
                        "scorable": True,
                    },
                },
                "component_inputs": {
                    "state_graph_nodes": [
                        _graph_node("sg-001", "2 per month", "frequency", 2.0),
                        _graph_node("sg-002", "unknown", "unknown", 1000.0),
                    ]
                },
                "diagnostics": {
                    "deterministic_correct": False,
                    "selected_evidence_exact": True,
                    "selected_source_ids_exist": True,
                },
            }
        ),
        encoding="utf-8",
    )

    rows, metadata = replay.run_selective_safety_floor_gate_replay(
        _manifest("projection_arbitration", 2, "unknown"),
        artifact_dir=tmp_path,
    )

    row = rows[0]
    projection = row["gate_variants"][replay.PROJECTION_VARIANT]
    llm_sidecar = row["gate_variants"][replay.LLM_VARIANT]
    combined = row["gate_variants"][replay.COMBINED_VARIANT]
    assert projection["final_label"] == "unknown"
    assert projection["changed"] is True
    assert projection["purist_correct"] is True
    assert llm_sidecar["final_label"] == "seizure free for multiple year"
    assert combined["final_label"] == "unknown"
    assert combined["label_source"] == "combined_from_projection"

    summary = metadata["slice_summary"]["projection_arbitration"]["variant_summary"]
    assert summary[replay.PROJECTION_VARIANT]["wrong_to_correct"] == 1
    assert summary[replay.COMBINED_VARIANT]["wrong_to_correct"] == 1
    assert summary[replay.COMBINED_VARIANT]["deterministic_correct_regressions"] == 0


def test_llm_sidecar_requires_valid_evidence_and_source_ids(tmp_path: Path) -> None:
    artifact_path = tmp_path / "artifact.jsonl"
    artifact_path.write_text(
        _jsonl(
            {
                "source_row_index": 3,
                "reference": {
                    "gold_label": "unknown",
                    "gold_label_kind": "unknown",
                    "gold_monthly_frequency": 1000.0,
                },
                "score_layers": {
                    "hybrid_adjudicator_with_adapters": {
                        "final_label": "seizure free for multiple year",
                        "purist_correct": False,
                        "pragmatic_correct": False,
                        "scorable": True,
                    },
                    "llm_candidate_selector_raw": {
                        "final_label": "unknown",
                        "purist_correct": True,
                        "pragmatic_correct": True,
                        "scorable": True,
                    },
                },
                "component_inputs": {"state_graph_nodes": []},
                "diagnostics": {
                    "deterministic_correct": False,
                    "selected_evidence_exact": False,
                    "selected_source_ids_exist": True,
                },
            }
        ),
        encoding="utf-8",
    )

    rows, _metadata = replay.run_selective_safety_floor_gate_replay(
        _manifest("candidate_generation_rescue", 3, "unknown"),
        artifact_dir=tmp_path,
    )

    llm_sidecar = rows[0]["gate_variants"][replay.LLM_VARIANT]
    assert llm_sidecar["changed"] is False
    assert llm_sidecar["fallback_reason"] == "selected_evidence_not_exact"
    assert llm_sidecar["final_label"] == "seizure free for multiple year"


def test_write_replay_report_has_valid_would_change_table(tmp_path: Path) -> None:
    report_path = tmp_path / "report.md"
    metadata = {
        "source_artifact": "artifact.jsonl",
        "slice_manifest": "slices.json",
        "split_manifest": "gan2026_split_v1",
        "row_count": 1,
        "hidden_family_summary": {},
        "would_change_rows": {
            replay.PROJECTION_VARIANT: [
                {
                    "source_row_index": 1,
                    "slice_name": "projection_arbitration",
                    "gold_label": "unknown",
                    "baseline_label": "2 per month",
                    "proposed_label": "unknown",
                    "hidden_families": ["unknown_boundary"],
                    "rationale": "unit rationale",
                }
            ],
            replay.LLM_VARIANT: [],
            replay.COMBINED_VARIANT: [],
        },
    }

    replay.write_replay_report(
        [],
        metadata,
        report_path,
        jsonl_path=tmp_path / "rows.jsonl",
        json_path=tmp_path / "summary.json",
    )

    text = report_path.read_text(encoding="utf-8")
    assert "| Row | Slice | Gold | Baseline | Variant | Families | Why |" in text
    assert "| --- | --- | --- | --- | --- | --- | --- |" in text


def test_missing_manifest_rows_fail_with_clear_error(tmp_path: Path) -> None:
    (tmp_path / "artifact.jsonl").write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="missing source artifact rows: artifact.jsonl:99"):
        replay.run_selective_safety_floor_gate_replay(
            _manifest("candidate_generation_rescue", 99, "unknown"),
            artifact_dir=tmp_path,
        )


def _manifest(slice_name: str, source_row_index: int, gold_label: str) -> dict:
    return {
        "artifact_kind": "unit_manifest",
        "split_manifest": "gan2026_split_v1",
        "slices": [
            {
                "slice_name": slice_name,
                "members": [
                    {
                        "artifact_name": "artifact.jsonl",
                        "source_row_index": source_row_index,
                        "primary_layer": "hybrid_adjudicator_with_adapters",
                        "gold_label": gold_label,
                        "predicted_label": "2 per month",
                        "hidden_families": ["unknown_boundary"],
                        "first_failure_owner": "projection",
                        "first_failure_reason": "unit",
                        "evidence_exact": True,
                    }
                ],
            }
        ],
    }


def _jsonl(row: dict) -> str:
    return json.dumps(row) + "\n"


def _graph_node(
    node_id: str,
    label: str,
    semantic_kind: str,
    monthly_frequency: float,
) -> dict:
    kind = {
        "frequency": "frequency_rate",
        "unknown": "unknown_frequency",
    }[semantic_kind]
    parsed = label_to_frequency_record(label)
    return {
        "node_id": node_id,
        "kind": kind,
        "normalized_label": parsed.normalized_label,
        "semantic_kind": semantic_kind,
        "monthly_frequency": monthly_frequency,
        "evidence": label,
        "assertion_status": "asserted",
        "temporality": "current",
        "certainty": "certain",
        "graph_errors": [],
    }
