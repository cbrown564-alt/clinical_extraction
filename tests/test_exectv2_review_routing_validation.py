from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    review_routing_validation,
)


def test_review_routing_validation_stops_without_same_surface_artifact() -> None:
    audit = review_routing_validation.build_review_routing_validation_audit()

    assert audit["surface"] == "rich-schema holistic assembly reliability scorecard"
    assert audit["eligible_validation_artifacts"] == 0
    assert audit["stop_rule_outcome"]["status"] == (
        "blocked_no_same_surface_full200_artifact"
    )
    assert audit["stop_rule_outcome"]["validation_run_executed"] is False
    assert audit["stop_rule_outcome"]["promotion_decision"] == "not_promoted"

    candidates = {row["id"]: row for row in audit["candidate_operating_points"]}
    assert candidates["high_recall_predeclared"]["review_burden"] == 0.9408
    assert candidates["high_recall_predeclared"]["catch_rate"] == 0.8897
    assert candidates["balanced_dev_candidate"]["review_burden"] == 0.7567
    assert candidates["balanced_dev_candidate"]["catch_rate"] == 0.8028
    assert candidates["balanced_dev_candidate"]["false_alarms_per_caught_error"] < (
        candidates["high_recall_predeclared"]["false_alarms_per_caught_error"]
    )


def test_review_routing_validation_report_is_aggregate_only() -> None:
    audit = review_routing_validation.build_review_routing_validation_audit()
    markdown = review_routing_validation.render_markdown(audit)

    assert "letter_id" not in markdown
    assert "predicted_mentions" not in markdown
    assert "gold_mentions" not in markdown
    assert "evidence spans" in markdown
    assert "blocked_no_same_surface_full200_artifact" in markdown
    assert "exectv2_audit_llm_only_all_entities_full200_gpt41mini_20260612.jsonl" in markdown
