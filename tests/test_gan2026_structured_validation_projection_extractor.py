from __future__ import annotations

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    structured_validation_projection_extractor,
)


def test_validation_projection_extractor_emits_hard_seed_candidate() -> None:
    panel_row = _panel_row(
        panel_role="hard",
        seed_family="yearly_to_daily",
        expected_action="emit_candidate",
        expected_label="1 per day",
        current_label="4 per year",
        gold_label="1 per day",
        evidence=(
            "nightly generalised tonic-clonic seizures and intermittent tonic "
            "seizures four times per year"
        ),
    )
    record = {"note_text": f"Clinical note. {panel_row['evidence']}."}

    row = structured_validation_projection_extractor.build_extractor_row(
        panel_row,
        record,
    )

    assert row["generator_action"] == "emit_candidate"
    assert row["candidate_label"] == "1 per day"
    assert row["projection_owner"] == "rate_projection_policy"
    assert row["transition"] == "W_to_C"
    assert row["expected_action_matched"] is True
    assert row["source_note_text"] is None


def test_validation_projection_extractor_suppresses_matched_control() -> None:
    panel_row = _panel_row(
        panel_role="control",
        seed_family="cluster_completion",
        expected_action="suppress_candidate",
        expected_label=None,
        current_label="1 per month",
        gold_label="1 per month",
        evidence="one seizure per month and no clustering",
    )
    record = {"note_text": f"Clinical note. {panel_row['evidence']}."}

    row = structured_validation_projection_extractor.build_extractor_row(
        panel_row,
        record,
    )

    assert row["generator_action"] == "suppress_candidate"
    assert row["candidate_label"] is None
    assert row["projection_owner"] == "cluster_projection_policy"
    assert row["expected_action_matched"] is True
    assert row["prediction_bearing"] is False


def test_validation_projection_extractor_suppresses_no_regression_case() -> None:
    panel_row = _no_regression_row()
    record = {"note_text": "Clinical note. Last seizure on 03-Sep-2017."}

    row = structured_validation_projection_extractor.build_extractor_row(
        panel_row,
        record,
    )

    assert row["panel_role"] == "no_regression"
    assert row["generator_action"] == "suppress_candidate"
    assert row["expected_generator_action"] == "suppress_candidate"
    assert row["expected_action_matched"] is True
    assert row["candidate_label"] is None
    assert row["no_regression_case"] is True
    assert row["would_have_regressed_transition"] == "C_to_W"


def test_validation_projection_extractor_summary_passes_smoke_but_blocks_test() -> None:
    rows = [
        {
            "panel_role": "hard",
            "seed_family": "yearly_to_daily",
            "projection_owner": "rate_projection_policy",
            "generator_action": "emit_candidate",
            "expected_action_matched": True,
            "exact_evidence": True,
            "prediction_bearing": True,
            "transition": "W_to_C",
            "contract_issues": [],
            "no_regression_case": False,
            "source_note_text_present": False,
        },
        {
            "panel_role": "control",
            "seed_family": "yearly_to_daily",
            "projection_owner": "rate_projection_policy",
            "generator_action": "suppress_candidate",
            "expected_action_matched": True,
            "exact_evidence": True,
            "prediction_bearing": False,
            "transition": "not_selected",
            "contract_issues": [],
            "no_regression_case": False,
            "source_note_text_present": False,
        },
        {
            "panel_role": "no_regression",
            "seed_family": None,
            "projection_owner": "boundary_projection_policy",
            "generator_action": "suppress_candidate",
            "expected_action_matched": True,
            "exact_evidence": True,
            "prediction_bearing": False,
            "transition": "not_selected",
            "contract_issues": [],
            "no_regression_case": True,
            "source_note_text_present": False,
        },
    ]

    summary = structured_validation_projection_extractor.summarize_extractor_rows(rows)

    assert summary["row_count"] == 3
    assert summary["hard_emit_rows"] == 1
    assert summary["control_suppressed_rows"] == 1
    assert summary["no_regression_suppressed_rows"] == 1
    assert summary["validation_smoke_passed"] is True
    assert summary["frozen_test_audit_ready"] is False
    assert summary["gate_failures"] == ["coverage_below_150", "w_to_c_below_25"]


def _panel_row(
    *,
    panel_role: str,
    seed_family: str,
    expected_action: str,
    expected_label: str | None,
    current_label: str,
    gold_label: str,
    evidence: str,
) -> dict[str, object]:
    return {
        "source_row_index": 1,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "panel_source": "structured_seed_validation_panel_v0",
        "panel_role": panel_role,
        "seed_family": seed_family,
        "generator_action": expected_action,
        "current_label": current_label,
        "gold_label": gold_label,
        "proposed_label": expected_label or "",
        "evidence": evidence,
        "projection_owner": (
            "rate_projection_policy"
            if seed_family == "yearly_to_daily"
            else "cluster_projection_policy"
        ),
        "projection_ownership_basis": seed_family,
        "projection_stage": "clinical_event_to_benchmark_label",
        "clinical_event_owner": "typed_event_extractor",
        "clinical_event_kind": "frequency_rate",
        "projection_policy_id": "gan2026_rate_projection_policy_v0",
        "benchmark_format_rule_id": "none_rate_projection_only",
        "no_regression_case": False,
        "projection_ownership_explicit": True,
    }


def _no_regression_row() -> dict[str, object]:
    return {
        "source_row_index": 2,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "panel_source": "structured_event_projection_audit_v0",
        "panel_role": "no_regression",
        "seed_family": None,
        "generator_action": "no_regression_control",
        "current_label": "seizure free for 16 month",
        "gold_label": "seizure free for 16 month",
        "proposed_label": "unknown",
        "evidence": "Last seizure on 03-Sep-2017",
        "projection_owner": "boundary_projection_policy",
        "projection_ownership_basis": "seizure_free_boundary_event_v0",
        "projection_stage": "clinical_event_to_benchmark_label",
        "clinical_event_owner": "typed_boundary_classifier",
        "clinical_event_kind": "last_event_only",
        "projection_policy_id": "gan2026_boundary_projection_policy_v0",
        "benchmark_format_rule_id": "none_boundary_state_only",
        "transition": "C_to_W",
        "no_regression_case": True,
        "projection_ownership_explicit": True,
    }
