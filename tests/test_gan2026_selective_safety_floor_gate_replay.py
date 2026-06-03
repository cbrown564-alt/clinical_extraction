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


def test_projection_gate_does_not_make_deterministic_correct_row_wrong(
    tmp_path: Path,
) -> None:
    artifact_path = tmp_path / "artifact.jsonl"
    artifact_path.write_text(
        _jsonl(
            {
                "source_row_index": 5,
                "reference": {
                    "gold_label": "1 per month",
                    "gold_label_kind": "frequency",
                    "gold_monthly_frequency": 1.0,
                },
                "score_layers": {
                    "hybrid_adjudicator_with_adapters": {
                        "final_label": "1 per month",
                        "purist_correct": True,
                        "pragmatic_correct": True,
                        "scorable": True,
                    },
                    "state_graph_projection": {
                        "final_label": "2 per month",
                        "purist_correct": False,
                        "pragmatic_correct": False,
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
                    "deterministic_correct": True,
                    "selected_evidence_exact": True,
                    "selected_source_ids_exist": True,
                },
            }
        ),
        encoding="utf-8",
    )

    rows, metadata = replay.run_selective_safety_floor_gate_replay(
        _manifest("projection_arbitration", 5, "1 per month"),
        artifact_dir=tmp_path,
    )

    projection = rows[0]["gate_variants"][replay.PROJECTION_VARIANT]
    combined = rows[0]["gate_variants"][replay.COMBINED_VARIANT]
    summary = metadata["slice_summary"]["projection_arbitration"]["variant_summary"]
    assert projection["changed"] is False
    assert projection["fallback_reason"] == "deterministic_correct_regression_guard"
    assert combined["final_label"] == "1 per month"
    assert summary[replay.PROJECTION_VARIANT]["deterministic_correct_regressions"] == 0
    assert summary[replay.COMBINED_VARIANT]["deterministic_correct_regressions"] == 0


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


def test_validation_cycle_manifest_replays_full_saved_validation_artifact(
    tmp_path: Path,
) -> None:
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
                    "selected_evidence_exact": True,
                    "selected_source_ids_exist": True,
                },
            }
        )
        + _jsonl(
            {
                "source_row_index": 4,
                "reference": {
                    "gold_label": "1 per month",
                    "gold_label_kind": "frequency",
                    "gold_monthly_frequency": 1.0,
                },
                "score_layers": {
                    "hybrid_adjudicator_with_adapters": {
                        "final_label": "1 per month",
                        "purist_correct": True,
                        "pragmatic_correct": True,
                        "scorable": True,
                    },
                    "llm_candidate_selector_raw": {
                        "final_label": "unknown",
                        "purist_correct": False,
                        "pragmatic_correct": False,
                        "scorable": True,
                    },
                },
                "component_inputs": {"state_graph_nodes": []},
                "diagnostics": {
                    "deterministic_correct": True,
                    "selected_evidence_exact": True,
                    "selected_source_ids_exist": True,
                },
            }
        ),
        encoding="utf-8",
    )

    rows, metadata = replay.run_selective_safety_floor_gate_replay(
        {
            "artifact_kind": "gan2026_validation_cycle_candidate_manifest",
            "candidate_name": "selective_safety_floor_gate_v0",
            "split_manifest": "gan2026_split_v1",
            "source_artifacts": {"validation_source_jsonl": "artifact.jsonl"},
        },
        artifact_dir=tmp_path,
        manifest_path="candidate_manifest.json",
    )

    assert metadata["artifact_kind"] == "gan2026_selective_safety_floor_gate_v0_replay"
    assert metadata["row_count"] == 2
    assert metadata["slice_summary"]["validation750"]["rows"] == 2
    summary = metadata["slice_summary"]["validation750"]["variant_summary"]
    assert summary[replay.SELECTIVE_CANDIDATE_VARIANT]["wrong_to_correct"] == 1
    assert summary[replay.SELECTIVE_CANDIDATE_VARIANT]["deterministic_correct_regressions"] == 0
    assert rows[0]["gate_variants"][replay.SELECTIVE_CANDIDATE_VARIANT]["final_label"] == "unknown"


def test_full_artifact_slice_name_can_label_frozen_test_surface(tmp_path: Path) -> None:
    artifact_path = tmp_path / "artifact.jsonl"
    artifact_path.write_text(
        _jsonl(
            {
                "source_row_index": 31,
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
                    "selected_evidence_exact": True,
                    "selected_source_ids_exist": True,
                },
                "llm_candidate_prompt_input_json": json.dumps(
                    {"note_text": "The current picture is unclear and variable."}
                ),
            }
        ),
        encoding="utf-8",
    )

    rows, metadata = replay.run_selective_safety_floor_gate_replay(
        {
            "artifact_kind": "gan2026_validation_cycle_candidate_manifest",
            "candidate_name": "selective_safety_floor_gate_v0",
            "split_manifest": "gan2026_split_v1",
            "source_artifacts": {"validation_source_jsonl": "artifact.jsonl"},
        },
        artifact_dir=tmp_path,
        manifest_path="candidate_manifest.json",
        full_artifact_slice_name="test450",
    )

    assert rows[0]["slice_name"] == "test450"
    assert metadata["slice_summary"]["test450"]["rows"] == 1
    assert "gold_kind:unknown" in metadata["predeclared_test_slice_summary"]
    assert "text_marker:current_state" in metadata["predeclared_test_slice_summary"]
    assert "text_marker:ambiguity" in metadata["predeclared_test_slice_summary"]


def test_frozen_test_report_suppresses_row_level_readout(tmp_path: Path) -> None:
    report_path = tmp_path / "report.md"
    row = {
        "slice_name": "test450",
        "artifact_name": "artifact.jsonl",
        "source_row_index": 31,
        "gold_label": "unknown",
        "gold_label_kind": "unknown",
        "baseline_label": "seizure free for multiple year",
        "deterministic_correct": False,
        "predeclared_text_markers": {"current_state": True},
        "gate_variants": {
            replay.BASELINE_VARIANT: {
                "final_label": "seizure free for multiple year",
                "purist_correct": False,
                "pragmatic_correct": False,
                "changed": False,
                "fallback": False,
            },
            replay.PROJECTION_VARIANT: {
                "final_label": "seizure free for multiple year",
                "purist_correct": False,
                "pragmatic_correct": False,
                "changed": False,
                "fallback": True,
            },
            replay.COMPETING_FREQUENCY_VARIANT: {
                "final_label": "seizure free for multiple year",
                "purist_correct": False,
                "pragmatic_correct": False,
                "changed": False,
                "fallback": True,
            },
            replay.LOWEST_FREQUENCY_VARIANT: {
                "final_label": "seizure free for multiple year",
                "purist_correct": False,
                "pragmatic_correct": False,
                "changed": False,
                "fallback": True,
            },
            replay.LLM_VARIANT: {
                "final_label": "unknown",
                "purist_correct": True,
                "pragmatic_correct": True,
                "changed": True,
                "fallback": False,
                "selected_evidence_exact": True,
                "selected_source_ids_exist": True,
            },
            replay.COMBINED_VARIANT: {
                "final_label": "unknown",
                "purist_correct": True,
                "pragmatic_correct": True,
                "changed": True,
                "fallback": False,
                "selected_evidence_exact": True,
                "selected_source_ids_exist": True,
            },
            replay.SELECTIVE_CANDIDATE_VARIANT: {
                "final_label": "unknown",
                "purist_correct": True,
                "pragmatic_correct": True,
                "changed": True,
                "fallback": False,
                "selected_evidence_exact": True,
                "selected_source_ids_exist": True,
            },
        },
    }
    metadata = {
        "artifact_kind": "gan2026_selective_safety_floor_gate_v0_replay",
        "source_artifact": "artifact.jsonl",
        "slice_manifest": "candidate_manifest.json",
        "input_manifest": "candidate_manifest.json",
        "split_manifest": "gan2026_split_v1",
        "row_count": 1,
        "slice_summary": replay._summarize_by_slice([row]),
        "predeclared_test_slice_summary": replay._summarize_predeclared_test_slices([row]),
        "hidden_family_summary": {},
        "would_change_rows": {
            replay.PROJECTION_VARIANT: [],
            replay.LLM_VARIANT: [{"source_row_index": 31}],
            replay.COMBINED_VARIANT: [{"source_row_index": 31}],
            replay.SELECTIVE_CANDIDATE_VARIANT: [{"source_row_index": 31}],
        },
        "scoring_convention_caveats": [
            {
                "source_row_index": 31,
                "gold_label": "unknown",
                "baseline_label": "seizure free for multiple year",
                "candidate_label": "unknown",
                "caveat": "unit caveat",
            }
        ],
    }

    replay.write_replay_report(
        [row],
        metadata,
        report_path,
        jsonl_path=tmp_path / "rows.jsonl",
        json_path=tmp_path / "summary.json",
        frozen_test_audit=True,
    )

    text = report_path.read_text(encoding="utf-8")
    assert "Frozen-Test Audit First Readout" in text
    assert "Predeclared Test Slice Summary" in text
    assert "Would-Change Rows" not in text
    assert "| Row | Slice | Gold | Baseline | Variant | Families | Why |" not in text
    assert "Scoring-Convention Caveats" not in text
    assert " 31 " not in text


def test_load_manifest_preserves_validation_cycle_manifest_without_predeclaration(
    tmp_path: Path,
) -> None:
    manifest_path = tmp_path / "candidate.json"
    predeclaration_path = tmp_path / "predeclaration.json"
    manifest_path.write_text(
        json.dumps(
            {
                "artifact_kind": "gan2026_validation_cycle_candidate_manifest",
                "candidate_name": "selective_safety_floor_gate_v0",
                "source_artifacts": {"validation_source_jsonl": "artifact.jsonl"},
            }
        ),
        encoding="utf-8",
    )
    predeclaration_path.write_text(
        json.dumps({"slice_manifest": "old_slices.json", "surfaces": []}),
        encoding="utf-8",
    )

    loaded = replay.load_manifest(manifest_path, predeclaration=predeclaration_path)

    assert loaded["candidate_name"] == "selective_safety_floor_gate_v0"
    assert "slices" not in loaded


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
