from __future__ import annotations

import csv
import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    rq1_rq2_control_panels,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments import (
    single_task_control_prompts,
)


def test_balanced_panel_respects_gold_kind_targets_and_family_coverage() -> None:
    records = []
    rows = [
        ("frequency", "1 per month", ["rate_bucket_or_denominator"]),
        ("frequency", "2 per week", ["cluster_burden"]),
        ("seizure_free", "seizure free for multiple month", ["seizure_free_duration"]),
        ("unknown", "unknown", ["unknown_boundary"]),
        ("no_reference", "no seizure frequency reference", ["unknown_no_reference_boundary"]),
        ("unresolved_multiple", "multiple per month", ["benchmark_format_convention"]),
    ]
    for index, (kind, label, families) in enumerate(rows, start=1):
        records.append(
            {
                "source_row_index": index,
                "split": "validation",
                "gold_label": label,
                "gold_kind": kind,
                "gold_reference": f"reference {index}",
                "row_ok": True,
                "hidden_families": families,
            }
        )

    panel = rq1_rq2_control_panels.build_balanced_validation_panel(
        records,
        target_size=6,
        kind_targets={
            "frequency": 2,
            "seizure_free": 1,
            "unknown": 1,
            "no_reference": 1,
            "unresolved_multiple": 1,
        },
        family_targets={
            "cluster_burden": 1,
            "rate_bucket_or_denominator": 1,
        },
    )

    assert [row["source_row_index"] for row in panel] == [1, 2, 3, 4, 5, 6]
    summary = rq1_rq2_control_panels.summarize_panel_rows(panel)
    assert summary["by_panel_id"]["balanced_validation50"]["source_rows"] == 6
    assert summary["by_panel_id"]["balanced_validation50"]["gold_kind_counts"] == {
        "frequency": 2,
        "no_reference": 1,
        "seizure_free": 1,
        "unknown": 1,
        "unresolved_multiple": 1,
    }


def test_hidden_family_panel_uses_hard_slices_and_followup_without_duplicates(
    tmp_path: Path,
) -> None:
    atlas_slices = tmp_path / "slices.json"
    followup = tmp_path / "followup.jsonl"
    atlas_csv = tmp_path / "atlas.csv"
    atlas_slices.write_text(
        json.dumps(
            {
                "slices": [
                    {
                        "slice_name": "candidate_generation_rescue",
                        "members": [
                            {
                                "source_row_index": 10,
                                "gold_label": "unknown",
                                "hidden_families": ["unknown_boundary"],
                                "first_failure_owner": "candidate_generation",
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    followup.write_text(
        json.dumps(
            {
                "source_row_index": 10,
                "panel_role": "changed_row",
                "component_name": "llm_heavy_selected_fact",
                "hidden_families": ["seizure_free_duration"],
                "first_failure_owner": "projection_policy",
            }
        )
        + "\n"
        + json.dumps(
            {
                "source_row_index": 20,
                "panel_role": "typed_operand_incomplete",
                "component_name": "llm_heavy_selected_fact",
                "gold_label": "2 per week",
                "hidden_families": ["rate_bucket_or_denominator"],
                "first_failure_owner": "operand_exposure",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    with atlas_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "source_row_index",
                "gold_label",
                "hidden_families",
                "first_failure_owner",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                "source_row_index": 20,
                "gold_label": "2 per week",
                "hidden_families": "cluster_burden",
                "first_failure_owner": "projection",
            }
        )

    panel = rq1_rq2_control_panels.build_hidden_family_hard_panel(
        hard_slice_manifest_path=atlas_slices,
        followup_panel_path=followup,
        atlas_csv_path=atlas_csv,
        target_size=10,
    )

    assert [row["source_row_index"] for row in panel] == [10, 20]
    assert panel[0]["predeclared_slices"] == ["candidate_generation_rescue"]
    assert panel[1]["selection_sources"] == ["component_projection_followup_panel"]
    assert panel[1]["hidden_families"] == [
        "rate_bucket_or_denominator",
        "cluster_burden",
    ]


def test_component_control_matrix_expands_isolated_and_overload_conditions() -> None:
    panel_rows = [
        {
            "panel_id": "balanced_validation50",
            "source_row_index": 10,
            "split": "validation",
            "gold_label": "1 per month",
            "gold_kind": "frequency",
            "hidden_families": ["rate_bucket_or_denominator"],
        }
    ]

    rows, metadata = rq1_rq2_control_panels.build_component_control_matrix(panel_rows)

    assert [row["condition_id"] for row in rows] == [
        "candidate_only",
        "gold_query_evidence_only",
        "candidate_conditioned_evidence_only",
        "projection_only",
        "projection_only_instruction_heavy",
        "candidate_plus_evidence",
        "evidence_plus_projection",
        "candidate_plus_evidence_plus_projection",
    ]
    assert rows[0]["prompt_name"] == "candidate_only"
    assert rows[0]["component_task"] == "candidate_generation"
    assert rows[-1]["overload_condition"] is True
    assert metadata["condition_count"] == 8
    assert metadata["by_condition"]["projection_only"]["component_task"] == "projection"
    assert metadata["by_condition"]["projection_only_instruction_heavy"][
        "component_task"
    ] == "projection"


def test_instruction_heavy_projection_prompt_adds_policy_without_row_examples() -> None:
    record = _record("multiple per day")
    candidate = {
        "candidate_id": "c1",
        "source_id": "note",
        "evidence": "multiple seizures in the past day",
        "candidate_kind": "frequency_rate",
        "temporality": "recent",
        "assertion_status": "asserted",
        "applies_to": "seizures",
        "components": {
            "count": "multiple",
            "timeframe": "past day",
            "unit": "seizures",
            "rate_time_basis": "day",
            "cluster_cadence": None,
            "per_cluster_burden": None,
            "seizure_free_duration": None,
        },
        "ambiguity_reasons": [],
        "normalization_note": None,
        "confidence": "high",
        "rationale": "The evidence states multiple seizures in the past day.",
    }
    evidence = {
        "evidence_id": "e1",
        "source_id": "note",
        "evidence": "multiple seizures in the past day",
        "role": "decisive",
        "support_status": "supports_candidate",
        "applies_to": "seizures",
        "extracted_components": candidate["components"],
        "missing_components": [],
        "conflict_notes": [],
        "ambiguity_reasons": [],
        "confidence": "high",
        "rationale": "The evidence supports the candidate.",
    }

    payload = json.loads(
        single_task_control_prompts.build_projection_only_instruction_heavy_prompt_input(
            record,
            [candidate],
            [evidence],
            input_source="deterministic",
        )
    )
    instructions = "\n".join(payload["instructions"])

    assert payload["task"].startswith("Choose the current seizure-frequency")
    assert "conditional" in instructions
    assert "Cluster information can describe two separate things" in instructions
    assert "multiple seizures in a day" in instructions
    assert "row" not in instructions.lower()
    assert "gold" not in instructions.lower()


def test_hidden_family_panel_uses_repo_label_parser_for_gold_kind(tmp_path: Path) -> None:
    atlas_slices = tmp_path / "slices.json"
    followup = tmp_path / "followup.jsonl"
    atlas_csv = tmp_path / "atlas.csv"
    atlas_slices.write_text(
        json.dumps(
            {
                "slices": [
                    {
                        "slice_name": "candidate_generation_rescue",
                        "members": [
                            {
                                "source_row_index": 30,
                                "gold_label": "unknown, multiple per cluster",
                                "hidden_families": ["cluster_burden"],
                            }
                        ],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    followup.write_text("", encoding="utf-8")
    _write_empty_atlas(atlas_csv)

    panel = rq1_rq2_control_panels.build_hidden_family_hard_panel(
        hard_slice_manifest_path=atlas_slices,
        followup_panel_path=followup,
        atlas_csv_path=atlas_csv,
    )

    assert panel[0]["gold_kind"] == "unknown"


def _write_empty_atlas(path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "source_row_index",
                "gold_label",
                "hidden_families",
                "first_failure_owner",
            ],
        )
        writer.writeheader()


def _record(label: str) -> object:
    return type(
        "Record",
        (),
        {
            "source_row_index": 1,
            "note_text": "Clinic note: multiple seizures in the past day.",
            "gold_label": label,
        },
    )()
