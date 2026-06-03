from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    atlas_hard_slice_diagnostic,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)


def test_run_atlas_hard_slice_diagnostic_counts_llm_sidecar_rescue(
    tmp_path,
    monkeypatch,
) -> None:
    artifact_path = tmp_path / "artifact.jsonl"
    artifact_path.write_text(
        _jsonl(
            {
                "source_row_index": 1,
                "score_layers": {
                    "deterministic_top_candidate": {
                        "final_label": "seizure free for multiple year",
                        "purist_correct": False,
                        "scorable": True,
                    },
                    "llm_candidate_selector_raw": {
                        "final_label": "unknown",
                        "purist_correct": True,
                        "scorable": True,
                    },
                    "hybrid_adjudicator_with_adapters": {
                        "final_label": "seizure free for multiple year",
                        "purist_correct": False,
                        "scorable": True,
                    },
                },
                "diagnostics": {
                    "deterministic_correct": False,
                    "llm_candidate_correct": True,
                    "selected_source_ids_exist": True,
                },
            }
        ),
        encoding="utf-8",
    )
    manifest = {
        "artifact_kind": "unit_manifest",
        "split_manifest": "gan2026_split_v1",
        "source_atlas_csv": "atlas.csv",
        "slices": [
            {
                "slice_name": "candidate_generation_rescue",
                "members": [
                    {
                        "artifact_name": "artifact.jsonl",
                        "source_row_index": 1,
                        "primary_layer": "hybrid_adjudicator_with_adapters",
                        "gold_label": "unknown",
                        "predicted_label": "seizure free for multiple year",
                        "hidden_families": ["unknown_boundary"],
                        "first_failure_owner": "candidate_generation",
                        "first_failure_reason": "gold state absent from candidate set",
                        "evidence_exact": True,
                    }
                ],
            }
        ],
    }

    rows, metadata = atlas_hard_slice_diagnostic.run_atlas_hard_slice_diagnostic(
        manifest,
        artifact_dir=tmp_path,
    )

    assert rows[0]["llm_candidate_rescue"] is True
    summary = metadata["summary"]["slices"]["candidate_generation_rescue"]
    assert summary["llm_sidecar_rescues"] == 1
    assert summary["baseline_correct"] == 0
    assert metadata["would_change_rows"]["llm_candidate_sidecar_rescues"] == [
        {
            "artifact_name": "artifact.jsonl",
            "current_final_label": "seizure free for multiple year",
            "deterministic_label": "seizure free for multiple year",
            "gold_label": "unknown",
            "hidden_families": ["unknown_boundary"],
            "llm_sidecar_label": "unknown",
            "llm_sidecar_purist_correct": True,
            "slice_names": ["candidate_generation_rescue"],
            "source_row_index": 1,
            "why": (
                "LLM candidate selector raw layer is Purist-correct while deterministic "
                "safety-floor final label is Purist-wrong."
            ),
        }
    ]


def test_run_atlas_hard_slice_diagnostic_replays_projection_variants(tmp_path) -> None:
    artifact_path = tmp_path / "artifact.jsonl"
    artifact_path.write_text(
        _jsonl(
            {
                "source_row_index": 2,
                "reference": {
                    "gold_label_kind": "unknown",
                    "gold_monthly_frequency": 1000.0,
                },
                "score_layers": {
                    "hybrid_adjudicator_with_adapters": {
                        "final_label": "2 per month",
                        "purist_correct": False,
                        "scorable": True,
                    }
                },
                "component_inputs": {
                    "state_graph_nodes": [
                        _graph_node("sg-001", "2 per month", "frequency", 2.0),
                        _graph_node("sg-002", "unknown", "unknown", 1000.0),
                    ]
                },
                "diagnostics": {"selected_source_ids_exist": True},
            }
        ),
        encoding="utf-8",
    )
    manifest = {
        "artifact_kind": "unit_manifest",
        "split_manifest": "gan2026_split_v1",
        "source_atlas_csv": "atlas.csv",
        "slices": [
            {
                "slice_name": "projection_arbitration",
                "members": [
                    {
                        "artifact_name": "artifact.jsonl",
                        "source_row_index": 2,
                        "primary_layer": "hybrid_adjudicator_with_adapters",
                        "gold_label": "unknown",
                        "predicted_label": "2 per month",
                        "hidden_families": ["unknown_boundary"],
                        "first_failure_owner": "projection",
                        "first_failure_reason": (
                            "gold appears representable but projection is wrong"
                        ),
                        "evidence_exact": True,
                    }
                ],
            }
        ],
    }

    rows, metadata = atlas_hard_slice_diagnostic.run_atlas_hard_slice_diagnostic(
        manifest,
        artifact_dir=tmp_path,
    )

    projection = rows[0]["projection_arbitration"]
    assert projection["baseline_v0"]["final_label"] == "2 per month"
    assert projection["boundary_state_priority"]["final_label"] == "unknown"
    summary = metadata["summary"]["slices"]["projection_arbitration"]
    assert summary["graph_projection_replay_rows"] == 1
    assert summary["best_non_oracle_projection_corrections"] == 1
    assert metadata["would_change_rows"]["projection_variant_corrections"][0][
        "correct_variants"
    ] == {"boundary_state_priority": "unknown"}


def test_write_diagnostic_report_includes_would_change_and_interpretation_note(
    tmp_path,
) -> None:
    report_path = tmp_path / "report.md"
    atlas_hard_slice_diagnostic.write_diagnostic_report(
        [],
        {
            "split_manifest": "gan2026_split_v1",
            "row_count": 1,
            "unique_source_rows": 1,
            "summary": {
                "slices": {},
                "projection_variants": {},
            },
            "would_change_rows": {
                "llm_candidate_sidecar_rescues": [
                    {
                        "source_row_index": 1,
                        "gold_label": "unknown",
                        "current_final_label": "seizure free for multiple year",
                        "deterministic_label": "seizure free for multiple year",
                        "llm_sidecar_label": "unknown",
                        "hidden_families": ["unknown_boundary"],
                        "why": "unit reason",
                    }
                ],
                "projection_variant_corrections": [],
            },
        },
        report_path,
        jsonl_path=tmp_path / "rows.jsonl",
        json_path=tmp_path / "summary.json",
    )

    text = report_path.read_text(encoding="utf-8")
    assert "## Rows That Would Change" in text
    assert "LLM Candidate Sidecar Rescues" in text
    assert "## Interpretation Required After Generation" in text


def _jsonl(row: dict) -> str:
    import json

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
