from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis import (
    rq9_selective_action_router as router,
)


def _source_row(
    *,
    source_row_index: int = 1,
    final_label: str = "unknown",
    purist_correct: bool = True,
    selected_evidence: str = "Only with sleep deprivation",
    scorable: bool = True,
) -> dict:
    return {
        "source_row_index": source_row_index,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "structured_adjudicator_record": {
            "final_label": final_label,
            "final_kind": "unknown" if final_label == "unknown" else "frequency",
            "selected_evidence": selected_evidence,
            "rationale": "saved source rationale",
            "selected_source_ids": ["det:event_1"],
        },
        "score_layers": {
            router.DEFAULT_SOURCE_LAYER: {
                "final_label": final_label,
                "purist_correct": purist_correct,
                "pragmatic_correct": purist_correct,
                "scorable": scorable,
            }
        },
        "component_status": {"selected_evidence_exactness": "ok"},
        "diagnostics": {"selected_evidence_exact": True},
        "reference": {
            "gold_label": "unknown",
            "gold_label_kind": "unknown",
            "gold_normalized_label": "unknown",
        },
    }


def _inventory_row(
    *,
    source_row_index: int = 1,
    gold_label: str = "unknown",
    gold_label_kind: str = "unknown",
    reasons: str = "unknown_gold_boundary;conditional_or_trigger_bound",
    reference: str = "Only with sleep deprivation",
    context: str = "",
) -> dict:
    return {
        "source_row_index": str(source_row_index),
        "split": "validation",
        "gold_label": gold_label,
        "gold_label_kind": gold_label_kind,
        "gold_reference": reference,
        "codex_initial_ambiguity_label": "ambiguous" if reasons else "clear",
        "codex_ambiguity_reasons": reasons,
        "reference_context": context,
        "note_text_single_line": context or reference,
    }


def test_router_abstains_trigger_only_unknown_without_leaking_gold() -> None:
    rows, metadata = router.build_selective_action_router_rows(
        [_source_row()],
        [_inventory_row()],
        [{"source_row_index": 1, "split": "validation", "simple_class": "ambiguous"}],
    )

    row = rows[0]
    assert row["selective_action"] == "abstain"
    assert row["primary_reason"] == "trigger_conditioned_frequency"
    assert row["final_label"] is None
    assert "gold_label" not in row["router_packet"]
    assert row["development_accounting"]["gold_label"] == "unknown"
    assert metadata["metrics"]["abstained_rows"] == 1


def test_router_predicts_convertible_drop_attack_frequency() -> None:
    rows, metadata = router.build_selective_action_router_rows(
        [
            _source_row(
                final_label="2 to 3 per 2 week",
                selected_evidence="2 to 3 drop attacks during the last two weeks",
            )
        ],
        [
            _inventory_row(
                gold_label="2 to 3 per 2 week",
                gold_label_kind="frequency",
                reasons="range_or_upper_bound",
                reference="2 to 3 drop attacks during the last two weeks",
            )
        ],
        [{"source_row_index": 1, "split": "validation", "simple_class": "correct"}],
    )

    row = rows[0]
    assert row["selective_action"] == "predict"
    assert row["primary_reason"] == "plain_predictable_frequency"
    assert row["final_label"] == "2 to 3 per 2 week"
    assert metadata["metrics"]["covered_rows"] == 1
    assert metadata["metrics"]["selective_accuracy"] == 1.0


def test_router_routes_uncertain_drop_attack_since_anchor_to_review() -> None:
    rows, metadata = router.build_selective_action_router_rows(
        [
            _source_row(
                final_label="unknown",
                selected_evidence="several drop attacks since ketogenic diet",
            )
        ],
        [
            _inventory_row(
                reasons=(
                    "unknown_gold_boundary;vague_count_or_period;"
                    "last_event_or_seizure_free_boundary;calendar_or_diary_arithmetic"
                ),
                reference="several drop attacks since ketogenic diet",
                context="brief loss of tone and several drop attacks since ketogenic diet",
            )
        ],
        [{"source_row_index": 1, "split": "validation", "simple_class": "ambiguous"}],
    )

    row = rows[0]
    assert row["selective_action"] == "human_review"
    assert row["primary_reason"] == "drop_attack_boundary"
    assert row["secondary_reasons"] == ["missing_denominator_anchor"]
    assert metadata["metrics"]["human_review_rows"] == 1


def test_latest_human_decision_is_used_for_over_review_accounting() -> None:
    rows, metadata = router.build_selective_action_router_rows(
        [_source_row(selected_evidence="Last seizure on 05-Aug, with none since")],
        [
            _inventory_row(
                reasons="unknown_gold_boundary;last_event_or_seizure_free_boundary",
                reference="Last seizure on 05-Aug, with none since",
            )
        ],
        [
            {"source_row_index": 1, "split": "validation", "simple_class": "ambiguous"},
            {"source_row_index": 1, "split": "validation", "simple_class": "correct"},
        ],
    )

    assert rows[0]["selective_action"] == "human_review"
    assert rows[0]["development_accounting"]["human_simple_class"] == "correct"
    assert metadata["metrics"]["reviewed_human_correct_nonprediction_rows"] == 1
