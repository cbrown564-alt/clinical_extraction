import json
from pathlib import Path

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments import (
    claim_table_component_ablation,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.llm_only_claim_table_selector import (
    PROMPT_VERSION,
    REQUIRED_ABLATIONS_BEFORE_LADDER,
)


def _row() -> dict:
    return {
        "source_row_index": 10,
        "structured_record": {
            "claims": [
                {
                    "claim_id": "c1",
                    "cluster_axis": "cadence_and_burden",
                    "boundary_state": "ordinary_frequency",
                }
            ],
            "final_query": {
                "selector_decision": "preserve_cluster_axis",
                "cluster_axis": "cadence_and_burden",
                "boundary_state": "ordinary_frequency",
                "final_label": "1 cluster per month, 6 to 7 per cluster",
            },
        },
        "score_layers": {
            "raw": {
                "final_label": "1 cluster per month, 6 to 7 per cluster",
                "scorable": True,
                "purist_correct": True,
                "pragmatic_correct": True,
            },
            "strict_format": {
                "final_label": "1 cluster per month, 6 to 7 per cluster",
                "scorable": True,
                "purist_correct": True,
                "pragmatic_correct": True,
            },
            "clean_scorer_facing": {
                "final_label": "1 cluster per month, 6 to 7 per cluster",
                "scorable": True,
                "purist_correct": True,
                "pragmatic_correct": True,
            },
        },
        "reference": {"gold_label": "1 cluster per month, 6 to 7 per cluster"},
        "evidence_summary": {"selected_evidence_valid": True},
        "parse_errors": [],
    }


def test_build_claim_table_component_ablation_blocks_validation_ladder() -> None:
    result = claim_table_component_ablation.build_claim_table_component_ablation(
        [_row()],
        source_jsonl="saved.jsonl",
    )

    assert result["prompt_version"] == PROMPT_VERSION
    assert result["validation_ladder_status"] == {
        "state": "blocked_until_required_ablations_exist",
        "blocked_ladder_sizes": [25, 50, 250],
        "required_ablations_before_ladder_runs": REQUIRED_ABLATIONS_BEFORE_LADDER,
    }
    assert [condition["name"] for condition in result["conditions"]] == [
        "raw_model_claim_table",
        "strict_schema_repair",
        "constrained_selector_state",
        "clean_scorer_facing_policy",
    ]
    selector = result["conditions"][2]
    assert selector["summary"]["selector_state_complete"] == 1
    assert selector["rows"][0]["selector_decision"] == "preserve_cluster_axis"
    assert selector["rows"][0]["final_query_cluster_axis"] == "cadence_and_burden"
    assert selector["rows"][0]["final_query_boundary_state"] == "ordinary_frequency"
    assert selector["rows"][0]["claim_cluster_axis_present"] is True
    assert selector["rows"][0]["claim_boundary_state_present"] is True


def test_claim_table_component_ablation_report_names_pre_ladder_gate(tmp_path: Path) -> None:
    result = claim_table_component_ablation.build_claim_table_component_ablation(
        [],
        source_jsonl=None,
    )
    report_path = tmp_path / "report.md"

    claim_table_component_ablation.write_claim_table_component_ablation_report(
        result,
        report_path,
    )

    report = report_path.read_text(encoding="utf-8")
    assert "Pre-Ladder Component Ablation" in report
    assert "blocked until required ablations exist" in report
    assert "`raw_model_claim_table`" in report
    assert "cluster-axis state" in report
    assert "boundary-state field" in report

    json.dumps(result)
