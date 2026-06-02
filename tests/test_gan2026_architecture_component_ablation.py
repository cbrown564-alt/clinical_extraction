import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
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


def test_condition_from_llm_rows_accepts_claim_table_score_layers() -> None:
    condition = condition_from_llm_rows(
        [
            {
                "source_row_index": 10,
                "structured_record": {
                    "final_query": {
                        "final_label": "2 per month",
                        "cluster_axis": "none",
                        "boundary_state": "ordinary_frequency",
                    }
                },
                "score_layers": {
                    "clean_scorer_facing": {
                        "final_label": "2 per month",
                        "scorable": True,
                        "purist_correct": True,
                        "pragmatic_correct": True,
                    }
                },
                "reference": {"gold_label": "2 per month"},
                "evidence_summary": {"selected_evidence_valid": True},
                "parse_errors": [],
            }
        ],
        spec=ConditionSpec(
            architecture=Architecture.LLM_THEN_DETERMINISTIC,
            name="claim_table_v5_clean_scorer_facing",
            component_role="claim_table_plus_constrained_selector",
            prediction_source="saved claim-table JSONL",
            components_enabled=("LLM claim table", "constrained selector", "clean scorer policy"),
        ),
    )

    assert condition.rows[0].prediction_label == "2 per month"
    assert condition.rows[0].purist_correct is True
    assert condition.rows[0].evidence_valid is True


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
                "raw_adjudicator": {
                    "final_label": "unknown",
                    "purist_correct": False,
                    "pragmatic_correct": False,
                },
                "conservative_adjudicator": {
                    "final_label": "2 per month",
                    "purist_correct": True,
                    "pragmatic_correct": True,
                },
            },
            "reference": {"gold_label": "2 per month", "gold_monthly_frequency": 2.0},
            "deterministic_diagnostics": {"evidence_valid": True},
            "conservative_gate": {
                "used_deterministic_fallback": False,
                "fired_gates": [],
            },
            "parse_errors": [],
        }
    ]

    deterministic, raw_adjudicator, adjudicator = condition_from_hybrid_rows(source_rows)

    assert deterministic.architecture == Architecture.DETERMINISTIC_THEN_LLM
    assert deterministic.name == "deterministic_candidate_generator_top"
    assert raw_adjudicator.name == "raw_llm_adjudicator_final"
    assert adjudicator.name == "conservative_llm_adjudicator_final"
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
