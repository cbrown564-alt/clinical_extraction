from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    review_routing_validation,
)


def test_review_routing_validation_runs_current_code_surface_without_promotion() -> None:
    audit = review_routing_validation.build_review_routing_validation_audit()

    assert audit["surface"] == "rich-schema holistic assembly reliability scorecard"
    assert audit["eligible_validation_artifacts"] == 1
    assert audit["stop_rule_outcome"]["status"] == (
        "completed_current_code_surface_validation"
    )
    assert audit["stop_rule_outcome"]["validation_run_executed"] is True
    assert audit["stop_rule_outcome"]["promotion_decision"] == "not_promoted"

    candidates = {row["id"]: row for row in audit["candidate_operating_points"]}
    assert candidates["high_recall_predeclared"]["review_burden"] == 0.9366
    assert candidates["high_recall_predeclared"]["catch_rate"] == 0.8712
    assert candidates["balanced_dev_candidate"]["review_burden"] == 0.7522
    assert candidates["balanced_dev_candidate"]["catch_rate"] == 0.8033
    assert candidates["balanced_dev_candidate"]["false_alarms_per_caught_error"] < (
        candidates["high_recall_predeclared"]["false_alarms_per_caught_error"]
    )
    validation = audit["validation_readout"]
    validation_points = {row["id"]: row for row in validation["operating_points"]}
    assert validation_points["balanced_dev_candidate"]["catch_rate"] >= 0.80
    assert validation_points["balanced_dev_candidate"]["review_burden"] > 0.95
    burden_gate = next(
        gate
        for gate in audit["promotion_gates"]
        if gate["gate"].startswith("Review burden")
    )
    assert burden_gate["outcome"] == "fail"


def test_review_routing_validation_report_is_aggregate_only() -> None:
    audit = review_routing_validation.build_review_routing_validation_audit()
    markdown = review_routing_validation.render_markdown(audit)

    assert "letter_id" not in markdown
    assert "predicted_mentions" not in markdown
    assert "gold_mentions" not in markdown
    assert "evidence spans" in markdown
    assert "completed_current_code_surface_validation" in markdown
    assert "Aggregate Validation Readout" in markdown
    assert "exectv2_audit_llm_only_all_entities_full200_gpt41mini_20260612.jsonl" in markdown
