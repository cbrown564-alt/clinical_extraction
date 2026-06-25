from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    robustness_validation,
)


def test_robustness_validation_promotes_aggregate_current_code_surface() -> None:
    audit = robustness_validation.build_robustness_validation_audit()

    assert audit["surface"] == "rich-schema holistic assembly reliability scorecard"
    assert audit["eligible_validation_artifacts"] == 1
    assert audit["stop_rule_outcome"]["status"] == (
        "completed_current_code_surface_validation"
    )
    assert audit["stop_rule_outcome"]["validation_run_executed"] is True
    assert audit["stop_rule_outcome"]["promotion_decision"] == "promoted"

    validation = audit["validation_readout"]
    assert validation["rows"] == 200
    assert validation["eligible_cells"] > 500
    assert validation["hard_slice_cells"] > 0
    assert validation["schema_validity_rate"] == 1.0
    assert validation["evidence_validity_rate"] == 1.0

    by_perturbation = {
        row["perturbation_family"]: row
        for row in validation["by_perturbation_family"]
    }
    assert by_perturbation["sf_current_vs_historical"]["cells"] > 0
    assert by_perturbation["sf_current_vs_future"]["cells"] > 0
    assert by_perturbation["prescription_current_vs_plan"]["cells"] > 0
    assert by_perturbation["investigations_result_state"]["cells"] > 0
    assert by_perturbation["diagnosis_assertion_hierarchy"]["cells"] > 0
    assert by_perturbation["evidence_paraphrase"]["cells"] == 0
    assert by_perturbation["evidence_deletion"]["cells"] == 0

    assert all(gate["outcome"] == "pass" for gate in audit["promotion_gates"])


def test_robustness_validation_report_is_aggregate_only() -> None:
    audit = robustness_validation.build_robustness_validation_audit()
    markdown = robustness_validation.render_markdown(audit)

    assert "letter_id" not in markdown
    assert "predicted_mentions" not in markdown
    assert "gold_mentions" not in markdown
    assert "evidence spans" in markdown
    assert "Aggregate Validation Readout" in markdown
    assert "Evidence paraphrase/deletion remain adversarial fixture" in markdown
