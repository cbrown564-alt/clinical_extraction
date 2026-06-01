import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments import (
    architecture_component_ablation as component_ablation,
)

Architecture = component_ablation.Architecture
ConditionSpec = component_ablation.ConditionSpec
compare_condition_rows = component_ablation.compare_condition_rows
condition_from_hybrid_rows = (
    component_ablation.condition_from_hybrid_rules_candidates_llm_adjudicator_rows
)
condition_from_llm_rows = component_ablation.condition_from_llm_rows
load_jsonl = component_ablation.load_jsonl
summarize_condition = component_ablation.summarize_condition
write_component_ablation_report = component_ablation.write_component_ablation_report


def test_condition_from_llm_rows_accepts_direct_and_structured_artifacts() -> None:
    condition = condition_from_llm_rows(
        [
            {
                "source_row_index": 1,
                "decision_record": {"final_label": "2 per month"},
                "reference": {"gold_label": "2 per month", "gold_monthly_frequency": 2.0},
                "comparison": {"purist_correct": True, "pragmatic_correct": True},
                "evidence_valid": True,
                "parse_errors": [],
            },
            {
                "source_row_index": 2,
                "structured_record": {"selection": {"final_label": "unknown"}},
                "reference": {"gold_label": "1 per week", "gold_monthly_frequency": 4.345238095},
                "comparison": {"purist_correct": False, "pragmatic_correct": False},
                "evidence_valid": False,
                "parse_errors": ["unscorable_final_label: unknown"],
            },
        ],
        spec=ConditionSpec(
            architecture=Architecture.LLM_THEN_DETERMINISTIC,
            name="llm_after_format_repair",
            component_role="llm_selection_plus_format_repair",
            prediction_source="saved LLM JSONL",
            components_enabled=("LLM selector", "format repair"),
        ),
    )

    summary = summarize_condition(condition)

    assert summary["rows"] == 2
    assert summary["purist_correct"] == 1
    assert summary["evidence_valid"] == 1
    assert summary["parse_or_validation_issues"] == 1
    assert condition.rows[1].prediction_label == "unknown"


def test_hybrid_conditions_split_deterministic_top_from_llm_adjudicator() -> None:
    source_rows = [
        {
            "source_row_index": 10,
            "scores": {
                "deterministic_top": {
                    "final_label": "1 per day",
                    "purist_correct": False,
                    "pragmatic_correct": False,
                },
                "adjudicator": {
                    "final_label": "2 per month",
                    "purist_correct": True,
                    "pragmatic_correct": True,
                },
            },
            "reference": {"gold_label": "2 per month", "gold_monthly_frequency": 2.0},
            "deterministic_diagnostics": {"evidence_valid": True},
            "parse_errors": [],
        }
    ]

    deterministic, adjudicator = condition_from_hybrid_rows(source_rows)

    assert deterministic.architecture == Architecture.DETERMINISTIC_THEN_LLM
    assert deterministic.name == "deterministic_candidate_generator_top"
    assert adjudicator.name == "llm_adjudicator_final"
    assert summarize_condition(adjudicator)["purist_accuracy"] == 1.0
    assert compare_condition_rows(deterministic, adjudicator)["wrong_to_correct"] == 1


def test_report_and_jsonl_helpers(tmp_path: Path) -> None:
    path = tmp_path / "rows.jsonl"
    path.write_text(
        json.dumps({"source_row_index": 1, "value": "a"})
        + "\n\n"
        + json.dumps({"source_row_index": 2, "value": "b"})
        + "\n",
        encoding="utf-8",
    )
    rows = load_jsonl(path)
    assert [row["source_row_index"] for row in rows] == [1, 2]

    condition = condition_from_llm_rows(
        [
            {
                "source_row_index": 1,
                "decision_record": {"final_label": "2 per month"},
                "reference": {"gold_label": "2 per month", "gold_monthly_frequency": 2.0},
                "comparison": {"purist_correct": True, "pragmatic_correct": True},
                "evidence_valid": True,
                "parse_errors": [],
            }
        ],
        spec=ConditionSpec(
            architecture=Architecture.LLM_THEN_DETERMINISTIC,
            name="llm_final",
            component_role="prediction",
            prediction_source="unit test",
            components_enabled=("LLM",),
        ),
    )
    report_path = tmp_path / "report.md"
    write_component_ablation_report([condition], report_path, split="validation")

    report = report_path.read_text(encoding="utf-8")
    assert "Gan 2026 Architecture Component Ablation" in report
    assert "llm_final" in report
