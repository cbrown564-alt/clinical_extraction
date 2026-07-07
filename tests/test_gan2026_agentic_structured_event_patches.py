from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.structured_event_patches import (
    StructuredEventPatch,
    apply_selection_patch,
    propose_selection_patch,
    propose_selection_patches,
    run_patch_replay,
    summarize_patch_rows,
)


def _row(
    *,
    source_row_index: int = 123,
    baseline_label: str,
    baseline_kind: str = "frequency",
    baseline_correct: bool = False,
    candidate_label: str = "multiple per day",
    candidate_kind: str = "frequency",
    candidate_monthly: float = 1000.0,
    candidate_event_kind: str = "frequency_rate",
    candidate_temporality: str = "current",
    candidate_assertion_status: str = "asserted",
    gold_monthly: float = 1000.0,
) -> dict:
    return {
        "source_row_index": source_row_index,
        "structured_record": {
            "events": [
                {
                    "event_id": "e1",
                    "kind": "frequency_rate",
                    "evidence": "baseline evidence",
                    "temporality": "current",
                    "assertion_status": "asserted",
                },
                {
                    "event_id": "e2",
                    "kind": candidate_event_kind,
                    "evidence": "candidate evidence",
                    "temporality": candidate_temporality,
                    "assertion_status": candidate_assertion_status,
                },
            ],
            "selection": {
                "selected_event_ids": ["e1"],
                "final_kind": baseline_kind,
                "final_label": baseline_label,
                "evidence": "baseline evidence",
                "confidence": "high",
                "rationale": "baseline",
            },
        },
        "normalized_events": [
            {
                "event_id": "e1",
                "normalized_label": baseline_label,
                "semantic_kind": baseline_kind,
                "monthly_frequency": 1.0,
                "yearly_bounds": [12.0, 12.0],
                "repair_applied": False,
                "validation_errors": [],
            },
            {
                "event_id": "e2",
                "normalized_label": candidate_label,
                "semantic_kind": candidate_kind,
                "monthly_frequency": candidate_monthly,
                "yearly_bounds": [candidate_monthly * 12.0, candidate_monthly * 12.0],
                "repair_applied": False,
                "validation_errors": [],
            },
        ],
        "comparison": {
            "purist_correct": baseline_correct,
            "pragmatic_correct": baseline_correct,
        },
        "reference": {"gold_monthly_frequency": gold_monthly},
    }


def test_selection_patch_accepts_higher_burden_existing_event() -> None:
    row = _row(baseline_label="1 per month", candidate_label="multiple per day")
    patch = StructuredEventPatch(
        action="select_existing_event",
        patch_family="raise_current_burden",
        selected_event_ids=["e2"],
        confidence="high",
        evidence="candidate evidence",
        rationale="The candidate event is the higher current burden.",
    )

    patched = apply_selection_patch(row, patch)

    assert patched["agentic_patch"]["accepted"] is True
    assert patched["agentic_patch"]["reason"] == "accepted_raise_current_burden"
    assert patched["patched_final_label"] == "multiple per day"
    assert patched["patched_comparison"]["purist_correct"] is True


def test_selection_patch_accepts_cluster_restore_event() -> None:
    row = _row(
        baseline_label="1 per month",
        candidate_label="1 cluster per month, multiple per cluster",
        candidate_monthly=30.0,
        candidate_event_kind="cluster_frequency",
        gold_monthly=30.0,
    )
    patch = StructuredEventPatch(
        action="select_existing_event",
        patch_family="restore_cluster_burden",
        selected_event_ids=["e2"],
        confidence="high",
        evidence="candidate evidence",
        rationale="The candidate preserves cluster cadence and events per cluster.",
    )

    patched = apply_selection_patch(row, patch)

    assert patched["agentic_patch"]["accepted"] is True
    assert patched["agentic_patch"]["reason"] == "accepted_restore_cluster_burden"
    assert patched["patched_final_label"] == "1 cluster per month, multiple per cluster"


def test_selection_patch_accepts_recent_unresolved_frequency_event() -> None:
    row = _row(
        baseline_label="1 per 1 to 2 week",
        candidate_label="multiple per day",
        candidate_kind="unresolved_multiple",
        candidate_temporality="recent",
        gold_monthly=1000.0,
    )
    patch = StructuredEventPatch(
        action="select_existing_event",
        patch_family="restore_recent_unresolved_burden",
        selected_event_ids=["e2"],
        confidence="high",
        evidence="candidate evidence",
        rationale="The candidate preserves a recent asserted vague frequency event.",
    )

    patched = apply_selection_patch(row, patch)

    assert patched["agentic_patch"]["accepted"] is True
    assert patched["agentic_patch"]["reason"] == "accepted_restore_recent_unresolved_burden"
    assert patched["patched_final_label"] == "multiple per day"
    assert patched["patched_comparison"]["purist_correct"] is True


def test_selection_patch_rejects_boundary_demotion_over_frequency_baseline() -> None:
    row = _row(
        baseline_label="multiple per day",
        baseline_correct=True,
        candidate_label="no seizure frequency reference",
        candidate_kind="no_reference",
        candidate_monthly=1000.0,
        gold_monthly=1000.0,
    )
    patch = StructuredEventPatch(
        action="select_existing_event",
        patch_family="other",
        selected_event_ids=["e2"],
        confidence="high",
        evidence="candidate evidence",
        rationale="The boundary event is tempting but unsafe.",
    )

    patched = apply_selection_patch(row, patch)

    assert patched["agentic_patch"]["accepted"] is False
    assert patched["agentic_patch"]["reason"] == "unsupported_boundary_demotion"
    assert patched["patched_final_label"] == "multiple per day"
    assert patched["patched_comparison"]["purist_correct"] is True


def test_recent_unresolved_policy_proposes_only_current_or_recent_asserted_events() -> None:
    row = _row(
        baseline_label="seizure free for multiple year",
        baseline_kind="seizure_free",
        candidate_label="multiple per day",
        candidate_kind="unresolved_multiple",
        candidate_temporality="recent",
    )

    patch = propose_selection_patch(row, policy="recent_unresolved_burden_v0")

    assert patch.action == "select_existing_event"
    assert patch.patch_family == "restore_recent_unresolved_burden"
    assert patch.selected_event_ids == ("e2",)


def test_recent_unresolved_policy_abstains_on_historical_or_boundary_candidates() -> None:
    historical_row = _row(
        baseline_label="seizure free for multiple year",
        baseline_kind="seizure_free",
        candidate_label="multiple per day",
        candidate_kind="unresolved_multiple",
        candidate_temporality="historical",
    )
    boundary_row = _row(
        baseline_label="2 per week",
        candidate_label="no seizure frequency reference",
        candidate_kind="no_reference",
        candidate_event_kind="cluster_frequency",
    )

    assert (
        propose_selection_patch(historical_row, policy="recent_unresolved_burden_v0").action
        == "keep"
    )
    assert (
        propose_selection_patch(boundary_row, policy="recent_unresolved_burden_v0").action == "keep"
    )


def test_propose_selection_patches_omits_keep_actions() -> None:
    rows = [
        _row(
            source_row_index=1,
            baseline_label="1 per month",
            candidate_label="multiple per day",
            candidate_kind="unresolved_multiple",
            candidate_temporality="recent",
        ),
        _row(
            source_row_index=2,
            baseline_label="1 per month",
            candidate_label="2 per month",
            candidate_kind="frequency",
        ),
    ]

    proposals = propose_selection_patches(rows, policy="recent_unresolved_burden_v0")

    assert set(proposals) == {1}
    assert proposals[1].patch_family == "restore_recent_unresolved_burden"


def test_patch_summary_counts_changed_label_precision() -> None:
    rescue_row = apply_selection_patch(
        _row(baseline_label="1 per month", candidate_label="multiple per day"),
        StructuredEventPatch(
            action="select_existing_event",
            patch_family="raise_current_burden",
            selected_event_ids=["e2"],
            confidence="high",
            evidence="candidate evidence",
            rationale="rescue",
        ),
    )
    rejected_row = apply_selection_patch(
        _row(
            baseline_label="multiple per day",
            baseline_correct=True,
            candidate_label="no seizure frequency reference",
            candidate_kind="no_reference",
            gold_monthly=1000.0,
        ),
        StructuredEventPatch(
            action="select_existing_event",
            patch_family="other",
            selected_event_ids=["e2"],
            confidence="high",
            evidence="candidate evidence",
            rationale="unsafe",
        ),
    )

    summary = summarize_patch_rows([rescue_row, rejected_row])

    assert summary["rows"] == 2
    assert summary["accepted_patches"] == 1
    assert summary["wrong_to_correct"] == 1
    assert summary["correct_to_wrong"] == 0
    assert summary["changed_label_precision"] == 1.0


def test_run_patch_replay_reports_baseline_and_patched_accuracy() -> None:
    rows = [
        _row(source_row_index=1, baseline_label="1 per month", candidate_label="multiple per day"),
        _row(
            source_row_index=2,
            baseline_label="multiple per day",
            baseline_correct=True,
            candidate_label="no seizure frequency reference",
            candidate_kind="no_reference",
            gold_monthly=1000.0,
        ),
    ]
    patches = {
        1: StructuredEventPatch(
            action="select_existing_event",
            patch_family="raise_current_burden",
            selected_event_ids=["e2"],
            confidence="high",
            evidence="candidate evidence",
            rationale="rescue",
        ),
        2: StructuredEventPatch(
            action="select_existing_event",
            patch_family="other",
            selected_event_ids=["e2"],
            confidence="high",
            evidence="candidate evidence",
            rationale="unsafe",
        ),
    }

    patched_rows, metadata = run_patch_replay(
        rows,
        patches,
        split="validation",
        split_manifest="gan2026_split_v1",
        source_artifact="unit-test.jsonl",
    )

    assert len(patched_rows) == 2
    assert metadata["summary"]["baseline_purist_correct"] == 1
    assert metadata["summary"]["patched_purist_correct"] == 2
    assert metadata["summary"]["patched_purist_accuracy"] == 1.0
    assert metadata["summary"]["wrong_to_correct"] == 1
