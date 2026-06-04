from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    selected_state_union_replay as replay,
)


def _saved_row() -> dict:
    return {
        "source_row_index": 15593,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "reference": {"gold_normalized_label": "1 cluster per 5 day, 2 to 4 per cluster"},
        "typed_input": {
            "note_text": (
                "She can occasionally manage five days without seizures, though this is "
                "usually followed by a day of clustering with two to four focal seizures."
            )
        },
        "policy_replay": {
            "revised_deterministic_projected_label": (
                "1 cluster per 5 day, 2 to 4 per cluster"
            )
        },
    }


def _boundary_row() -> dict:
    return {
        "source_row_index": 15593,
        "call_status": "ok",
        "parse_errors": [],
        "retained_candidates": [
            {
                "candidate_id": "live-boundary-001",
                "candidate_kind": "cluster_frequency",
                "normalized_label": "1 cluster per day, 2 to 4 per cluster",
                "evidence": (
                    "She can occasionally manage five days without seizures, though this is "
                    "usually followed by a day of clustering with two to four focal seizures."
                ),
                "currentness": "current",
                "assertion_status": "asserted",
                "semiology": "focal seizures",
                "source_id": "note",
                "source_id_status": "valid",
                "exact_evidence": True,
                "gate_failures": [],
                "provenance": ["live_llm_boundary_proposal"],
                "metadata": {
                    "evidence_quote": (
                        "She can occasionally manage five days without seizures, though this is "
                        "usually followed by a day of clustering with two to four focal seizures."
                    ),
                    "rate": {
                        "count_low": 1,
                        "count_high": None,
                        "count_is_multiple": False,
                        "time_count_low": 1,
                        "time_count_high": None,
                        "time_unit": "day",
                        "rate_text": "a day of clustering",
                    },
                    "cluster": {
                        "has_cluster_pattern": True,
                        "cluster_cadence_text": "a day of clustering",
                        "seizures_per_cluster_low": 2,
                        "seizures_per_cluster_high": 4,
                    },
                    "seizure_free": {},
                    "ambiguity_flags": [],
                    "reason": "The candidate repeats the known v3 cadence error.",
                },
            }
        ],
    }


def test_replay_carries_known_v3_model_error_without_safety_regression() -> None:
    rows, metadata = replay.build_selected_state_union_replay_rows(
        [_saved_row()],
        [_boundary_row()],
    )

    row = rows[0]
    assert row["primary_v3_selected_state_replay"]["label"] == (
        "1 cluster per day, 2 to 4 per cluster"
    )
    assert row["comparison"]["primary_v3_c_to_w_against_comparator"] is True
    assert row["comparison"]["safety_c_to_w_against_comparator"] is False
    assert row["projection_source_id_consistency"]["consistent"] is True
    assert metadata["policy_name"] == "staged_hybrid_assembly_validation_development_v0"
    assert metadata["metrics"]["projection_source_id_inconsistent_rows"] == 0
    assert metadata["known_real_model_error_source_row_indices"] == [15593]
