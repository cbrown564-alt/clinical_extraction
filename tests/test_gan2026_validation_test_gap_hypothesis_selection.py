from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    validation_test_gap_hypothesis_selection,
)


def test_hypothesis_selection_picks_three_controlled_hypotheses() -> None:
    rows = [
        _matrix_row(
            score_layer="final_policy",
            component_owner="deterministic_adapter",
            purist_correct=True,
            evidence_exact=True,
            source_ids_valid=True,
        ),
        _matrix_row(
            score_layer="final_policy",
            component_owner="deterministic_adapter",
            purist_correct=False,
            evidence_exact=True,
            source_ids_valid=True,
            hidden_families=["current_vs_historical"],
        ),
        _matrix_row(
            score_layer="final_policy",
            component_owner="safety_floor",
            purist_correct=None,
            changed_from_baseline=True,
            hidden_families=["unknown_boundary"],
        ),
        _matrix_row(
            score_layer="abstain_review_monitor",
            component_owner="safety_floor",
            purist_correct=None,
            abstain_review_monitor_action="abstain",
            abstain_review_monitor_reason="trigger_conditioned_frequency",
        ),
    ]
    surface_map = {
        "candidate_gap_summary": [
            {
                "candidate_name": "fewshot_train_exemplar",
                "validation_final_purist_proxy": 0.968,
                "test_final_purist_proxy": 0.7933,
                "validation_minus_test_gap": 0.1747,
            }
        ]
    }
    validation_selective = {
        "slice_summary": [
            {
                "variant": "selective_safety_floor_gate_v0",
                "rows": 750,
                "changed_rows": 21,
                "wrong_to_correct": 11,
                "correct_to_wrong": 0,
                "precision": 1.0,
            }
        ]
    }
    test_selective = {
        "slice_summary": [
            {
                "variant": "selective_safety_floor_gate_v0",
                "rows": 450,
                "changed_rows": 14,
                "wrong_to_correct": 8,
                "correct_to_wrong": 0,
                "precision": 0.8889,
            }
        ]
    }

    selection = validation_test_gap_hypothesis_selection.build_hypothesis_selection(
        rows,
        surface_map=surface_map,
        validation_selective=validation_selective,
        test_selective=test_selective,
    )

    assert [item["hypothesis_id"] for item in selection["selected_hypotheses"]] == [
        "H2",
        "H4",
        "H6",
    ]
    assert len(selection["selected_hypotheses"]) == 3
    assert selection["matrix_summary"]["locked_test_row_level_artifacts_used"] == 0
    assert selection["surface_gap_summary"][0]["candidate_name"] == "fewshot_train_exemplar"
    assert selection["selective_action_summary"][1]["inspection_policy"] == (
        "locked_test_aggregate_only"
    )


def test_hypothesis_selection_summarizes_owner_family_and_evidence_rows() -> None:
    rows = [
        _matrix_row(
            score_layer="final_policy",
            component_owner="deterministic_adapter",
            purist_correct=False,
            evidence_exact=True,
            source_ids_valid=True,
            hidden_families=["seizure_free_duration"],
        ),
        _matrix_row(
            score_layer="final_policy",
            component_owner="safety_floor",
            purist_correct=None,
            changed_from_baseline=True,
            hidden_families=["seizure_free_duration"],
        ),
    ]

    selection = validation_test_gap_hypothesis_selection.build_hypothesis_selection(rows)

    owner_summary = {
        item["name"]: item for item in selection["component_owner_summary"]
    }
    assert owner_summary["deterministic_adapter"]["incorrect_rows"] == 1
    assert owner_summary["safety_floor"]["nonprediction_rows"] == 1
    family_summary = {item["name"]: item for item in selection["hidden_family_summary"]}
    assert family_summary["seizure_free_duration"]["rows"] == 2
    evidence_summary = {item["name"]: item for item in selection["evidence_summary"]}
    assert evidence_summary["exact_evidence_and_source_ids"]["incorrect_rows"] == 1
    assert evidence_summary["nonprediction_no_selected_evidence"]["nonprediction_rows"] == 1


def _matrix_row(
    *,
    score_layer: str,
    component_owner: str,
    purist_correct: bool | None,
    evidence_exact: bool | None = None,
    source_ids_valid: bool | None = None,
    hidden_families: list[str] | None = None,
    changed_from_baseline: bool = False,
    abstain_review_monitor_action: str = "",
    abstain_review_monitor_reason: str = "",
) -> dict[str, object]:
    return {
        "score_layer": score_layer,
        "component_owner": component_owner,
        "split_manifest": "gan2026_split_v1",
        "distribution": "validation750",
        "source_artifact_id": "component_matrix",
        "purist_correct": purist_correct,
        "evidence_exact": evidence_exact,
        "source_ids_valid": source_ids_valid,
        "hidden_families": hidden_families or [],
        "changed_from_baseline": changed_from_baseline,
        "wrong_to_correct": False,
        "correct_to_wrong": False,
        "abstain_review_monitor_action": abstain_review_monitor_action,
        "abstain_review_monitor_reason": abstain_review_monitor_reason,
    }
