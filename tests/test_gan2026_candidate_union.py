from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    candidate_union,
)


def _saved_row() -> dict:
    note = (
        "Clinic Date: 01 January 2026. At present she has 3 focal seizures per "
        "month. Seizures happen when sleep deprived only."
    )
    return {
        "source_row_index": 101,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "reference": {"gold_normalized_label": "unknown"},
        "typed_input": {"note_text": note},
        "policy_replay": {"revised_deterministic_projected_label": "unknown"},
        "structured_record": {
            "selected_state": {
                "state_kind": "unknown",
                "selected_evidence": "Seizures happen when sleep deprived only.",
                "currentness": "current",
                "assertion_status": "asserted",
                "applies_to": "focal seizures",
                "raw_model_label_hint": "trigger-only seizures",
                "raw_source_phrase": "Seizures happen when sleep deprived only.",
                "selection_reason": "Trigger-only state lacks an absolute cadence.",
                "ambiguity_flags": ["exclusive conditionality"],
                "rate": {},
                "cluster": {"has_cluster_pattern": False},
                "seizure_free_boundary": {"has_no_event_claim": False},
                "conditionality_note": "sleep deprived only",
                "competing_state_summary": "3 focal seizures per month also appears",
            }
        },
    }


def test_saved_candidate_union_preserves_replayed_boundary_proposal_recall() -> None:
    rows, metadata = candidate_union.build_candidate_union_rows(
        [_saved_row()],
        panel_rows=[
            {
                "source_row_index": 101,
                "hidden_families": ["unknown_boundary", "rate_bucket_or_denominator"],
            }
        ],
    )

    row = rows[0]
    assert row["gold_state_recall_summary"]["llm_boundary_candidate_recall"] is True
    assert row["gold_state_recall_summary"]["union_verified_candidate_recall"] is True
    assert row["llm_boundary_candidate_proposals"][0]["exact_evidence"] is True
    assert row["llm_boundary_candidate_proposals"][0]["source_id_status"] == "valid"
    assert row["union_verified_candidates"]
    assert metadata["metrics"]["llm_recall_rescue_rows"] >= 0
    assert metadata["by_hidden_family"]["unknown_boundary"]["rows"] == 1


def test_candidate_union_rejects_non_exact_saved_proposal() -> None:
    saved = _saved_row()
    saved["structured_record"]["selected_state"]["selected_evidence"] = "not in the note"

    rows, metadata = candidate_union.build_candidate_union_rows([saved])

    rejected = rows[0]["rejected_candidates"]
    assert any("non_exact_evidence" in candidate["gate_failures"] for candidate in rejected)
    assert metadata["gate_failure_counts"]["non_exact_evidence"] == 1
