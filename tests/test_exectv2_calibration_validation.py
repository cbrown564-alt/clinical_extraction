from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    calibration_validation,
)


def test_calibration_validation_promotes_aggregate_current_code_surface() -> None:
    audit = calibration_validation.build_calibration_validation_audit()

    assert audit["surface"] == "rich-schema holistic assembly reliability scorecard"
    assert audit["eligible_validation_artifacts"] == 1
    assert audit["stop_rule_outcome"]["status"] == ("completed_current_code_surface_validation")
    assert audit["stop_rule_outcome"]["validation_run_executed"] is True
    # After the calibration scoring-rule redesign (L2 raised 0.015 -> 0.03 in
    # reliability/calibration.py to clear the post-scorer-fix (7949a9d4)
    # generalization gap), the frozen dev140 rule again passes every predeclared
    # aggregate validation gate on the full-200 artifact. The adjacent-bin
    # reversal gate that previously blocked promotion (0.1105 > 0.10) now passes
    # at 0.0784. See exectv2_calibration_redesign_2026-07-07.md.
    assert audit["stop_rule_outcome"]["promotion_decision"] == "promoted"

    validation = audit["validation_readout"]
    assert validation["rows"] == 200
    assert validation["eligible_cells"] > 500
    assert validation["expected_calibration_error"] == 0.0587
    assert validation["brier_score"] < validation["constant_base_rate_brier_score"]
    assert validation["max_adjacent_bin_reversal"] <= 0.10
    assert len(validation["bins"]) >= 4
    assert {row["family"] for row in validation["per_family"]} == {
        "Diagnosis",
        "SeizureFrequency",
        "Prescription",
        "Investigations",
    }
    # Every predeclared promotion gate passes after the redesign.
    assert all(gate["outcome"] == "pass" for gate in audit["promotion_gates"])


def test_calibration_validation_report_is_aggregate_only() -> None:
    audit = calibration_validation.build_calibration_validation_audit()
    markdown = calibration_validation.render_markdown(audit)

    assert "letter_id" not in markdown
    assert "predicted_mentions" not in markdown
    assert "gold_mentions" not in markdown
    assert "selected failure examples" in markdown
    assert "completed_current_code_surface_validation" in markdown
    assert "Aggregate Validation Readout" in markdown
    assert "Per-Family Calibration" in markdown
