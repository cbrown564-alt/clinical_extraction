from __future__ import annotations

import json
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports import (
    robustness_panels,
)


def test_robustness_panel_covers_predeclared_minimum_and_scores_controls() -> None:
    payload = robustness_panels.build_robustness_panel_payload(generated_on="2026-06-25")

    counts = payload["panel_coverage"]["by_perturbation_family"]
    assert counts["sf_current_vs_historical"] >= 1
    assert counts["sf_current_vs_future"] >= 1
    assert counts["prescription_current_vs_plan"] >= 1
    assert counts["investigations_result_state"] >= 1
    assert counts["diagnosis_assertion_hierarchy"] >= 1
    assert counts["evidence_paraphrase"] >= 1
    assert counts["evidence_deletion"] >= 1
    assert payload["holdout_guardrail"]["full_200_or_holdout_rows_loaded"] is False

    arms = {arm["arm_id"]: arm for arm in payload["prediction_arms"]}
    assert arms["reference_oracle"]["overall"]["f1"] == 1.0
    assert arms["reference_oracle"]["schema_validity_rate"] == 1.0
    assert arms["reference_oracle"]["evidence_validity_rate"] == 1.0
    assert arms["targeted_failure_control"]["overall"]["f1"] < 0.75
    assert arms["targeted_failure_control"]["evidence_validity_rate"] < 1.0

    diagnosis_failure = next(
        row for row in arms["targeted_failure_control"]["by_family"] if row["family"] == "Diagnosis"
    )
    assert diagnosis_failure["companion_metrics"]["assertion_f1"] < 1.0


def test_robustness_panel_can_redact_case_text_for_scorecard_payload() -> None:
    payload = robustness_panels.build_robustness_panel_payload(include_case_text=False)

    case = payload["cases"][0]
    assert "perturbed_note" not in case
    assert "baseline_note" not in case
    assert case["expected_mentions"] == []
    assert case["failure_mentions"] == []


def test_render_and_write_robustness_panel_artifacts(tmp_path: Path) -> None:
    json_path = tmp_path / "panel.json"
    markdown_path = tmp_path / "panel.md"

    paths = robustness_panels.write_robustness_panel_artifacts(
        json_path=json_path,
        markdown_path=markdown_path,
        generated_on="2026-06-25",
    )

    assert paths["json"] == json_path
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["artifact_kind"] == "exectv2_robustness_panel_preflight"

    markdown = markdown_path.read_text(encoding="utf-8")
    assert "# ExECTv2 Robustness Panels Preflight" in markdown
    assert "aggregate-only validation-ready panel" in markdown
    assert "full-200 or holdout row-level inspection" in markdown
