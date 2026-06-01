from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments import (
    synthetic_hard_case_component_stress as stress,
)


def test_load_synthetic_hard_cases_as_scored_records(tmp_path: Path) -> None:
    path = tmp_path / "hard_cases.jsonl"
    path.write_text(
        json.dumps(
            {
                "case_id": "v02_temporal_conflict_01",
                "failure_family": "temporal_conflict",
                "source_note_text": (
                    "Historically daily seizures, but currently about 2 per month."
                ),
                "expected_final_label": "2 per month",
                "expected_answer_kind": "frequency",
                "expected_evidence_substring": "currently about 2 per month",
                "deterministic_failure_rationale": "Historical burden may outrank current rate.",
                "allowed_llm_action": "change",
            }
        )
        + "\n",
        encoding="utf-8",
    )

    cases = stress.load_synthetic_hard_cases(path)
    records = stress.synthetic_records_from_cases(cases)

    assert cases[0]["case_id"] == "v02_temporal_conflict_01"
    assert records[0].source_row_index == stress.SYNTHETIC_SOURCE_INDEX_BASE
    assert records[0].gold_label == "2 per month"
    assert records[0].gold_reference == "currently about 2 per month"
    assert records[0].raw["failure_family"] == "temporal_conflict"
    assert (
        records[0].gold_monthly_frequency
        == label_to_frequency_record("2 per month").monthly_frequency
    )


def test_component_stress_result_summarizes_hybrid_conditions() -> None:
    rows = [
        {
            "source_row_index": stress.SYNTHETIC_SOURCE_INDEX_BASE,
            "scores": {
                "deterministic_top": {
                    "final_label": "1 per day",
                    "purist_correct": False,
                    "pragmatic_correct": False,
                    "scorable": True,
                },
                "raw_adjudicator": {
                    "final_label": "2 per month",
                    "purist_correct": True,
                    "pragmatic_correct": True,
                    "scorable": True,
                },
                "conservative_adjudicator": {
                    "final_label": "1 per day",
                    "purist_correct": False,
                    "pragmatic_correct": False,
                    "scorable": True,
                },
            },
            "reference": {"gold_label": "2 per month"},
            "deterministic_diagnostics": {"evidence_valid": True},
            "parse_errors": [],
            "hard_case": {
                "case_id": "v02_temporal_conflict_01",
                "failure_family": "temporal_conflict",
                "allowed_llm_action": "change",
            },
            "conservative_gate": {
                "used_deterministic_fallback": True,
                "fired_gates": ["label_support_overreach"],
            },
        }
    ]

    result = stress.build_component_stress_result(
        rows,
        split=stress.SYNTHETIC_SPLIT_NAME,
        split_manifest=stress.SYNTHETIC_SPLIT_MANIFEST,
        artifact_path="experiments/example.jsonl",
    )

    assert result["split"] == stress.SYNTHETIC_SPLIT_NAME
    condition_by_name = {condition["name"]: condition for condition in result["conditions"]}
    assert condition_by_name["deterministic_candidate_generator_top"]["summary"][
        "purist_correct"
    ] == 0
    assert condition_by_name["raw_llm_adjudicator_final"]["summary"]["purist_correct"] == 1
    assert condition_by_name["conservative_llm_adjudicator_final"]["summary"][
        "purist_correct"
    ] == 0
    assert result["family_summaries"]["temporal_conflict"]["rows"] == 1
    assert result["family_summaries"]["temporal_conflict"]["raw_wrong_to_correct"] == 1
