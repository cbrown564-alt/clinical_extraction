from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path

import pytest

from scripts.build_exectv2_semantic_support_review_substrate import (
    FAMILIES,
    SAMPLE_PER_MODEL_FAMILY,
    build_review_substrate,
    validate_review_substrate,
)
from scripts.build_shared_reliability_scorecard import (
    CRITERIA,
    REQUIRED_MEASUREMENT_FIELDS,
    build_scorecard,
    render_report,
    validate_report,
    validate_scorecard,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "experiments" / "retained_evidence_manifest.json"
PAPER_SOURCES = (
    ROOT / "docs" / "research" / "paper_manuscript_2026-06-26.md",
    ROOT
    / "literature"
    / "IEEE"
    / "IEEE-conference-template-062824"
    / "IEEE-conference-template-062824.tex",
)
TASKS = {"gan2026", "exectv2"}
TEXT_SUFFIXES = frozenset({".json", ".jsonl", ".md", ".py", ".txt", ".yaml", ".yml"})


def _canonical_sha256(path: Path) -> str:
    content = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES:
        content = content.replace(b"\r\n", b"\n")
    return hashlib.sha256(content).hexdigest()


@pytest.fixture(scope="module")
def scorecard() -> dict[str, object]:
    result = build_scorecard(ROOT)
    validate_scorecard(result, repo_root=ROOT)
    return result


def _measurement(scorecard: dict[str, object], measurement_id: str) -> dict[str, object]:
    return next(
        record
        for record in scorecard["measurements"]  # type: ignore[index]
        if record["measurement_id"] == measurement_id
    )


def _keys(value: object) -> set[str]:
    if isinstance(value, dict):
        result = set(value)
        for child in value.values():
            result.update(_keys(child))
        return result
    if isinstance(value, list):
        result: set[str] = set()
        for child in value:
            result.update(_keys(child))
        return result
    return set()


def test_framework_has_exactly_eight_stable_criteria(scorecard: dict[str, object]) -> None:
    expected = {
        "clinical_correctness_generalization",
        "clinical_selection_unsupported_inference",
        "evidence_support_faithfulness",
        "uncertainty_selective_action",
        "robustness_stability",
        "component_attribution_correction_safety",
        "coverage_clinical_slice_behavior",
        "operational_reliability",
    }

    assert {criterion["id"] for criterion in CRITERIA} == expected
    assert {criterion["id"] for criterion in scorecard["criteria"]} == expected  # type: ignore[index]


def test_both_tasks_have_one_state_for_every_criterion(
    scorecard: dict[str, object],
) -> None:
    cells = scorecard["task_criteria"]  # type: ignore[index]
    pairs = [(cell["task"], cell["criterion_id"]) for cell in cells]

    assert len(pairs) == 16
    assert len(set(pairs)) == 16
    assert {task for task, _ in pairs} == TASKS
    assert {cell["result_state"] for cell in cells} <= {
        "measured",
        "not_measured",
        "not_applicable",
        "not_measurable_current_data",
    }


def test_every_measurement_has_assurance_metadata(scorecard: dict[str, object]) -> None:
    for measurement in scorecard["measurements"]:  # type: ignore[index]
        assert REQUIRED_MEASUREMENT_FIELDS <= set(measurement), measurement["measurement_id"]
        assert measurement["source_artifacts"]
        assert measurement["source_hashes"]
        assert measurement["claim_boundary"]
        assert measurement["reproducibility_command"]


def test_zero_or_invalid_denominator_cannot_emit_a_rate(
    scorecard: dict[str, object],
) -> None:
    invalid = deepcopy(scorecard)
    measurement = _measurement(invalid, "exectv2_sf_unknown_only_active_rate_overread_rate")
    measurement["value"] = 0.0

    with pytest.raises(ValueError, match="zero or invalid denominator"):
        validate_scorecard(invalid, repo_root=ROOT)


def test_exect_empty_gold_is_not_relabelled_as_unknown(
    scorecard: dict[str, object],
) -> None:
    measurement = _measurement(scorecard, "exectv2_sf_unknown_only_active_rate_overread_rate")

    assert measurement["denominator"] == 0
    assert measurement["value"] is None
    assert measurement["result_state"] == "not_measurable_current_data"
    assert measurement["empty_gold_substitution_allowed"] is False
    assert "annotation omission" in measurement["not_measured_reason"]


def test_textual_grounding_and_semantic_support_are_separate_measurements(
    scorecard: dict[str, object],
) -> None:
    ids = {
        measurement["measurement_id"]
        for measurement in scorecard["measurements"]  # type: ignore[index]
        if measurement["criterion_id"] == "evidence_support_faithfulness"
    }

    assert "gan2026_textual_grounding_rate" in ids
    assert "gan2026_semantic_support_review" in ids
    assert "exectv2_final_exact_evidence_rate" in ids
    assert "exectv2_semantic_support_review" in ids


def test_exect_uncertainty_results_keep_historical_model_scope(
    scorecard: dict[str, object],
) -> None:
    measurement = _measurement(
        scorecard, "exectv2_historical_model_reported_confidence_failure_auroc"
    )

    assert measurement["model_scope"] == [
        "openai/gpt-4.1-mini",
        "deepseek/deepseek-chat",
        "ollama_chat/qwen3.6:35b",
    ]
    assert "six-model" in measurement["claim_boundary"]
    assert "not" in measurement["claim_boundary"]


def test_repeated_letters_across_models_are_not_independent_rows(
    scorecard: dict[str, object],
) -> None:
    measurement = _measurement(scorecard, "exectv2_six_model_sf_correction_transitions")

    assert measurement["pooling_unit"] == "model_letter"
    assert measurement["unique_rows"] == 140
    assert measurement["model_row_count"] == 840
    assert measurement["independence_claim"] is False


def test_non_direct_comparisons_never_emit_numeric_deltas(
    scorecard: dict[str, object],
) -> None:
    for comparison in scorecard["cross_task_matrix"]:  # type: ignore[index]
        if comparison["comparability"] != "direct":
            assert comparison["numeric_delta"] is None


def test_no_composite_reliability_value_exists(scorecard: dict[str, object]) -> None:
    forbidden = {
        "composite_reliability",
        "composite_reliability_score",
        "overall_reliability_score",
        "weighted_reliability_index",
    }
    assert not (forbidden & _keys(scorecard))


def test_locked_artifacts_contribute_aggregates_only(
    scorecard: dict[str, object],
) -> None:
    sealed = [
        measurement
        for measurement in scorecard["measurements"]  # type: ignore[index]
        if measurement["row_scope"] == "aggregate_only_rows_sealed"
    ]

    assert sealed
    for measurement in sealed:
        assert "rows" not in measurement
        assert "row_records" not in measurement
        assert "aggregate" in measurement["row_inspection_rule"]


def test_source_paths_and_hashes_match_retained_manifest(
    scorecard: dict[str, object],
) -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    retained = {
        artifact["path"]: artifact["sha256"]
        for collection in (manifest["reference_cells"], manifest["evidence_packages"])
        for record in collection
        for artifact in record["artifacts"]
    }

    for measurement in scorecard["measurements"]:  # type: ignore[index]
        for path in measurement["source_artifacts"]:
            assert path in retained
            assert measurement["source_hashes"][path] == retained[path]


def test_report_reproduces_machine_values(scorecard: dict[str, object]) -> None:
    report = render_report(scorecard)
    validate_report(scorecard, report)

    assert "373/450" in report
    assert "0.8047" in report
    assert "54" in report
    assert "zero" in report.lower()


def test_claim_language_snapshots_preserve_required_limits() -> None:
    for source_path in PAPER_SOURCES:
        source = source_path.read_text(encoding="utf-8").lower()
        assert "not the published" in source
        assert "clinical validation" in source
        assert "hosted" in source and "local" in source
        assert "does not support a cross-task over-reading claim" in source
        assert "eight reliability" in source
        assert "no composite" in source


def test_semantic_review_substrate_is_stratified_and_uncertified() -> None:
    substrate = build_review_substrate(ROOT)
    validate_review_substrate(substrate, repo_root=ROOT)

    items = substrate["review_items"]
    assert substrate["split"] == "dev140"
    assert substrate["review_status"] == "pending_independent_clinical_review"
    assert len(items) == 6 * len(FAMILIES) * SAMPLE_PER_MODEL_FAMILY
    assert {item["family"] for item in items} == set(FAMILIES)
    assert all(item["semantic_support"] is None for item in items)
    assert all(item["reviewer_id"] is None for item in items)
    assert all(item["evidence_valid"] is True for item in items)
    assert all("test60" not in item["source_artifact"] for item in items)


def test_semantic_review_source_hashes_match_selected_dev_artifacts() -> None:
    substrate = build_review_substrate(ROOT)

    for path, expected in substrate["source_hashes"].items():
        digest = _canonical_sha256(ROOT / path)
        assert digest == expected
