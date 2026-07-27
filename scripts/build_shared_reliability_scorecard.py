"""Build the no-call shared reliability scorecard for Gan 2026 and ExECTv2."""

from __future__ import annotations

import argparse
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from clinical_extraction.core.retained_evidence import _artifact_fingerprint
from clinical_extraction.core.shared_reliability_exect_measurements import (
    ExectMeasurementInputs,
    build_exectv2_measurements,
)
from clinical_extraction.core.shared_reliability_gan_measurements import (
    GanMeasurementInputs,
    build_gan2026_measurements,
)
from clinical_extraction.core.shared_reliability_report import render_report, validate_report
from clinical_extraction.core.shared_reliability_schema import (
    CRITERIA,
    REQUIRED_MEASUREMENT_FIELDS,
    SIX_MODELS,
    reliability_gaps,
    task_cells_for_measurements,
)

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = Path("docs/experiments/retained_evidence_manifest.json")
OUTPUT_JSON = Path("experiments/shared_reliability_scorecard_20260718.json")
OUTPUT_REPORT = Path("docs/research/shared_reliability_scorecard_2026-07-18.md")
REVIEW_SUBSTRATE = Path(
    "experiments/exectv2_semantic_support_review_substrate_dev140_20260718.json"
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_index(manifest: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for collection in (manifest["reference_cells"], manifest["evidence_packages"]):
        for record in collection:
            for artifact in record["artifacts"]:
                result[str(artifact["path"])] = dict(artifact)
    return result


def _packages(manifest: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {record["id"]: record for record in manifest["evidence_packages"]}


def _metric(master: Mapping[str, Any], dimension: str) -> str:
    record = next(item for item in master["dimensions"] if item["dimension"] == dimension)
    return str(record["metric"])


def _matched_numbers(text: str, pattern: str) -> tuple[float, ...]:
    match = re.search(pattern, text)
    if match is None:
        raise ValueError(f"retained Gan metric format changed: {text}")
    return tuple(float(value) for value in match.groups())


def _exect_dev_sources(
    repo_root: Path,
    fixed_package: Mapping[str, Any],
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    artifact_paths = [str(item["path"]) for item in fixed_package["artifacts"]]
    config_paths = [
        path for path in artifact_paths if path.startswith("configs/exectv2/six_model_comparison/")
    ]
    sources: dict[str, dict[str, Any]] = {}
    selected_paths: list[str] = []
    for config_path in config_paths:
        config = _read_json(repo_root / config_path)
        output_path = str(config["outputs"]["json"])
        if output_path not in artifact_paths:
            raise ValueError(f"six-model output is not retained: {output_path}")
        sources[str(config["model"])] = {
            "config": config,
            "scorecard": _read_json(repo_root / output_path),
            "config_path": config_path,
            "output_path": output_path,
        }
        selected_paths.extend((config_path, output_path))
    if list(sources) != SIX_MODELS:
        raise ValueError("retained ExECT six-model roster or order changed")
    return sources, selected_paths


def _runtime_maps(sources: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    return {
        model: {
            "runtime": source["config"]["runtime"],
            "metadata": source["config"]["runtime_metadata"],
        }
        for model, source in sources.items()
    }


def _temperatures(sources: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    return {model: source["config"]["temperature"] for model, source in sources.items()}


def _token_limits(sources: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    return {model: source["config"]["max_tokens"] for model, source in sources.items()}


def _family_f1(sources: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    return {
        model: {
            family: values["f1"]
            for family, values in source["scorecard"]["score_ladder"]["headline_target"][
                "by_indicator"
            ].items()
        }
        for model, source in sources.items()
    }


def _overall_f1(sources: Mapping[str, Mapping[str, Any]]) -> dict[str, float]:
    return {
        model: source["scorecard"]["score_ladder"]["headline_target"]["overall"]["f1"]
        for model, source in sources.items()
    }


def _stage_f1(sources: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for model, source in sources.items():
        ladder = source["scorecard"]["score_ladder"]
        surfaces = ladder["materialized_surfaces"]
        result[model] = {
            "raw": ladder["raw_lane_score"]["overall"]["f1"],
            "evidence_valid": surfaces["evidence_valid"]["overall"]["f1"],
            "dictionary_normalized": surfaces["dictionary_normalized"]["overall"]["f1"],
            "projected": ladder["cui_projection_companion"]["overall"]["f1"],
            "final": ladder["headline_target"]["overall"]["f1"],
        }
    return result


def _exact_evidence(
    sources: Mapping[str, Mapping[str, Any]],
) -> tuple[dict[str, Any], dict[str, int]]:
    rates: dict[str, Any] = {}
    denominators: dict[str, int] = {}
    for model, source in sources.items():
        diagnostics = source["scorecard"]["lane_diagnostics"]
        exact = sum(int(values["exact_evidence_mentions"]) for values in diagnostics.values())
        scored = sum(int(values["scored_mentions"]) for values in diagnostics.values())
        rates[model] = round(exact / scored, 4) if scored else None
        denominators[model] = scored
    return rates, denominators


def build_scorecard(repo_root: Path = ROOT) -> dict[str, Any]:
    """Build the shared scorecard from selected no-call evidence."""

    manifest = _read_json(repo_root / MANIFEST_PATH)
    artifact_index = _artifact_index(manifest)
    packages = _packages(manifest)
    hosted = _read_json(repo_root / "experiments/hosted_holdout_panels_20260715.json")
    gan_panel = _read_json(
        repo_root / "experiments/gan2026_matched_v05_test450_aggregate_20260716.json"
    )
    gan_conditions = list(gan_panel["conditions"].values())
    exect_panel = hosted["panels"]["exectv2_test60"]
    gan_master = _read_json(
        repo_root / "experiments/gan2026_reliability_master_scorecard_2026-06-17.json"
    )
    exect_sources, exect_dev_paths = _exect_dev_sources(
        repo_root,
        packages["exectv2_fixed_six_model_panel_subject"],
    )

    hosted_path = "experiments/gan2026_matched_v05_test450_aggregate_20260716.json"
    gan_master_path = "experiments/gan2026_reliability_master_scorecard_2026-06-17.json"
    sf_path = "experiments/exectv2_six_model_sf_overinference_dev140_20260718.json"
    component_path = "experiments/cross_task_shared_component_ablation_2026-06-27.json"
    regression_path = "experiments/exectv2_model_led_dev140_regression_analysis_20260715.json"
    confidence_path = "experiments/exectv2_model_reported_confidence_out_of_sample_20260715.json"
    calibration_paths = [
        "docs/experiments/exectv2/reliability/exectv2_calibration_validation_audit_2026-06-25.md",
        "docs/experiments/exectv2/reliability/exectv2_calibration_redesign_2026-07-07.md",
    ]
    review_paths = [
        REVIEW_SUBSTRATE.as_posix(),
        (
            "docs/experiments/exectv2/reliability/"
            "exectv2_semantic_support_review_substrate_protocol_2026-07-18.md"
        ),
    ]

    runtime_maps = _runtime_maps(exect_sources)
    temperatures = _temperatures(exect_sources)
    token_limits = _token_limits(exect_sources)
    dev_f1 = _overall_f1(exect_sources)
    test_f1 = {
        condition["model"]: condition["clinical_headline"]["f1"]
        for condition in exect_panel["conditions"]
    }
    exact_evidence, exact_evidence_denominators = _exact_evidence(exect_sources)

    task_correctness = _metric(gan_master, "Task correctness")
    gan_val, gan_test = _matched_numbers(
        task_correctness,
        r"Purist ([0-9]+(?:\.[0-9]+)?) val / ([0-9]+(?:\.[0-9]+)?) test",
    )
    gan_overread = _matched_numbers(
        _metric(gan_master, "Factuality (over-inference)"),
        r"rate ([0-9]+(?:\.[0-9]+)?) val / ([0-9]+(?:\.[0-9]+)?) test",
    )
    gan_grounding = _matched_numbers(
        _metric(gan_master, "Faithfulness"),
        r"rate ([0-9]+(?:\.[0-9]+)?) val / ([0-9]+(?:\.[0-9]+)?) test",
    )
    gan_calibration = _matched_numbers(
        _metric(gan_master, "Calibration"),
        (
            r"ECE ([0-9]+(?:\.[0-9]+)?), Brier ([0-9]+(?:\.[0-9]+)?), "
            r"failure AUROC ([0-9]+(?:\.[0-9]+)?)"
        ),
    )
    gan_risk = _matched_numbers(
        _metric(gan_master, "Abstention"),
        (
            r"AUC ([0-9]+(?:\.[0-9]+)?) \(oracle ([0-9]+(?:\.[0-9]+)?)\); "
            r"selective risk ([0-9]+(?:\.[0-9]+)?)% @ 50% coverage, "
            r"([0-9]+(?:\.[0-9]+)?)% @ 80%"
        ),
    )
    gan_robustness = _matched_numbers(
        _metric(gan_master, "Robustness"),
        (
            r"direct_labeler_v0_5 ([0-9]+(?:\.[0-9]+)?), "
            r"evidence_v0_6 ([0-9]+(?:\.[0-9]+)?), "
            r"evidence_v0_7 ([0-9]+(?:\.[0-9]+)?)"
        ),
    )
    gan_consistency = _matched_numbers(
        _metric(gan_master, "Consistency"),
        (
            r"n=([0-9]+) \(([0-9]+) residual\): mean label entropy "
            r"([0-9]+(?:\.[0-9]+)?), residual ([0-9]+(?:\.[0-9]+)?)"
        ),
    )
    gan_coverage = _matched_numbers(
        _metric(gan_master, "Fairness (clinical family)"),
        r"spread ([0-9]+(?:\.[0-9]+)?)%, CV ([0-9]+(?:\.[0-9]+)?)",
    )
    gan_operations = _matched_numbers(
        _metric(gan_master, "Operational reliability"),
        (
            r"([0-9]+) model render failures / ([0-9]+) recoverable repairs "
            r"across ([0-9]+) rows; offline est ~\$([0-9]+(?:\.[0-9]+)?)/1000"
        ),
    )

    gan_routes = {
        condition["model"]: (
            f"{condition['model']}; temperature={condition['temperature']}; "
            f"max_tokens={condition['max_tokens']}"
        )
        for condition in gan_conditions
    }
    gan_purist = {
        condition["model"]: {
            "correct": condition["purist_correct"],
            "accuracy": condition["purist_accuracy"],
        }
        for condition in gan_conditions
    }
    gan_pragmatic = {
        condition["model"]: {
            "correct": condition["pragmatic_correct"],
            "accuracy": condition["pragmatic_accuracy"],
        }
        for condition in gan_conditions
    }
    gan_ops = {
        condition["model"]: {
            "call_failures": condition["call_failures"],
            "parse_schema_label_issues": condition["parse_or_validation_failures"],
            "structured_records": condition["structured_records"],
            "exact_evidence": condition["evidence_valid"],
            "repair_notes": condition["repair_notes"],
        }
        for condition in gan_conditions
    }
    exect_ops = {
        condition["model"]: {
            "call_failures": condition["call_failures"],
            "blocking_parse_failures": condition["blocking_parse_failures"],
            "parse_schema_failures": condition.get("parse_schema_failures", 0),
        }
        for condition in exect_panel["conditions"]
    }

    common_gan = {
        "artifact_index": artifact_index,
        "task": "gan2026",
        "route_runtime": gan_routes,
        "temperature": "recorded_by_condition_in_route_runtime",
        "token_limit": "not_recorded_in_compact_aggregate",
        "cache_replay_mode": "cache disabled; aggregate-only retained readout",
        "row_inspection_rule": "aggregate-only test450; no locked-row inspection",
        "locked_row_controls": "test450 rows sealed; aggregate values only",
        "independent_clinical_review": "not_completed",
        "pooling_unit": "model_letter",
    }
    common_exect = {
        "artifact_index": artifact_index,
        "task": "exectv2",
        "route_runtime": runtime_maps,
        "temperature": temperatures,
        "token_limit": token_limits,
        "cache_replay_mode": "live retained calls with cache disabled; no-call scorecard replay",
        "locked_row_controls": "dev140 only for row analysis; test60 aggregate rows sealed",
        "independent_clinical_review": "not_completed",
        "pooling_unit": "model_letter",
    }

    calibration_summary = packages["exectv2_calibration_subject"]["result_summary"]
    confidence_summary = packages["exectv2_model_reported_confidence_subject"]["result_summary"]
    component_summary = packages["cross_task_component_ablation_subject"]["result_summary"]
    regression_summary = packages["exectv2_model_led_dev140_regression_subject"]["result_summary"]
    sf_summary = packages["exectv2_six_model_sf_overinference_subject"]["result_summary"]
    family_f1 = _family_f1(exect_sources)
    stage_f1 = _stage_f1(exect_sources)

    gan_inputs = GanMeasurementInputs(
        artifact_index=artifact_index,
        common_gan=common_gan,
        component_path=component_path,
        component_summary=component_summary,
        gan_calibration=gan_calibration,
        gan_consistency=gan_consistency,
        gan_coverage=gan_coverage,
        gan_grounding=gan_grounding,
        gan_master_path=gan_master_path,
        gan_operations=gan_operations,
        gan_ops=gan_ops,
        gan_overread=gan_overread,
        gan_pragmatic=gan_pragmatic,
        gan_purist=gan_purist,
        gan_risk=gan_risk,
        gan_robustness=gan_robustness,
        gan_test=gan_test,
        gan_val=gan_val,
        hosted_path=hosted_path,
    )
    exect_inputs = ExectMeasurementInputs(
        artifact_index=artifact_index,
        calibration_paths=calibration_paths,
        calibration_summary=calibration_summary,
        common_exect=common_exect,
        component_path=component_path,
        component_summary=component_summary,
        confidence_path=confidence_path,
        confidence_summary=confidence_summary,
        dev_f1=dev_f1,
        exact_evidence=exact_evidence,
        exact_evidence_denominators=exact_evidence_denominators,
        exect_dev_paths=exect_dev_paths,
        exect_ops=exect_ops,
        exect_sources=exect_sources,
        family_f1=family_f1,
        hosted_path=hosted_path,
        regression_path=regression_path,
        regression_summary=regression_summary,
        review_paths=review_paths,
        review_substrate=REVIEW_SUBSTRATE,
        runtime_maps=runtime_maps,
        sf_path=sf_path,
        sf_summary=sf_summary,
        stage_f1=stage_f1,
        temperatures=temperatures,
        test_f1=test_f1,
        token_limits=token_limits,
    )
    measurements = build_gan2026_measurements(gan_inputs)
    measurements.extend(build_exectv2_measurements(exect_inputs))
    criterion_order = {item["id"]: index for index, item in enumerate(CRITERIA)}
    task_order = {"gan2026": 0, "exectv2": 1}
    measurements.sort(
        key=lambda item: (criterion_order[item["criterion_id"]], task_order[item["task"]])
    )

    task_cells = task_cells_for_measurements(measurements)
    criterion_lookup = {criterion["id"]: criterion for criterion in CRITERIA}
    cross_task_matrix = [
        {
            "criterion_id": criterion["id"],
            "criterion": criterion["name"],
            "comparability": "not_comparable"
            if criterion["id"] == "clinical_selection_unsupported_inference"
            else "construct_only",
            "numeric_delta": None,
            "reason": (
                "ExECT has no valid unknown-only denominator."
                if criterion["id"] == "clinical_selection_unsupported_inference"
                else (
                    "The tasks answer the same criterion with task-specific measurement "
                    "objects or units."
                )
            ),
        }
        for criterion in CRITERIA
    ]
    source_inventory = []
    for cell in task_cells:
        cell_measurements = [
            item for item in measurements if item["measurement_id"] in cell["measurement_ids"]
        ]
        source_inventory.append(
            {
                "task": cell["task"],
                "criterion_id": cell["criterion_id"],
                "result_state": cell["result_state"],
                "measurement_ids": cell["measurement_ids"],
                "source_artifacts": sorted(
                    {path for item in cell_measurements for path in item["source_artifacts"]}
                ),
                "gap_ids": cell["gap_ids"],
                "comparability": next(
                    item["comparability"]
                    for item in cross_task_matrix
                    if item["criterion_id"] == cell["criterion_id"]
                ),
            }
        )

    payload: dict[str, Any] = {
        "schema_version": "shared-reliability-scorecard-v1",
        "generated_date": "2026-07-18",
        "decision": "docs/decisions/0044-shared-reliability-criteria-use-task-specific-measures.md",
        "framework": "docs/design/reliability_evaluation_framework.md",
        "retained_evidence_manifest": MANIFEST_PATH.as_posix(),
        "assurance_gates": [
            "dataset_split_row_policy",
            "model_route_runtime_temperature_token_cache",
            "prompt_scorer_stage_repair",
            "source_hash_and_reproducibility",
            "split_barriers_canaries_failure_handling",
            "independent_clinical_review_status",
            "claim_boundary",
        ],
        "criteria": list(CRITERIA),
        "task_criteria": task_cells,
        "measurements": measurements,
        "cross_task_matrix": cross_task_matrix,
        "evidence_state_matrix": [
            {
                "criterion_id": criterion["id"],
                "gan2026": next(
                    cell
                    for cell in task_cells
                    if cell["task"] == "gan2026" and cell["criterion_id"] == criterion["id"]
                )["strongest_evidence_state"],
                "exectv2": next(
                    cell
                    for cell in task_cells
                    if cell["task"] == "exectv2" and cell["criterion_id"] == criterion["id"]
                )["strongest_evidence_state"],
                "comparability": next(
                    item["comparability"]
                    for item in cross_task_matrix
                    if item["criterion_id"] == criterion["id"]
                ),
            }
            for criterion in CRITERIA
        ],
        "source_inventory": source_inventory,
        "gaps": reliability_gaps(),
        "no_composite_rule": (
            "No overall reliability number, average criterion coverage, weighted index, "
            "or pooled cross-task model ranking is calculated."
        ),
        "claim_boundary": (
            "Shared questions with task-specific retained measures. The artifact does not "
            "establish a shared metric, cross-task transfer, demographic fairness, "
            "deployment reliability, or independent clinical validation."
        ),
    }
    validate_scorecard(payload, repo_root=repo_root)
    if set(criterion_lookup) != {criterion["id"] for criterion in payload["criteria"]}:
        raise AssertionError("criterion lookup drift")
    return payload


def _recursive_keys(value: Any) -> set[str]:
    if isinstance(value, Mapping):
        result = set(value)
        for child in value.values():
            result.update(_recursive_keys(child))
        return result
    if isinstance(value, list):
        result: set[str] = set()
        for child in value:
            result.update(_recursive_keys(child))
        return result
    return set()


def validate_scorecard(scorecard: Mapping[str, Any], *, repo_root: Path = ROOT) -> None:
    """Validate schema, split safety, source hashes, and comparison boundaries."""

    criterion_ids = [criterion["id"] for criterion in scorecard.get("criteria", [])]
    expected_ids = [criterion["id"] for criterion in CRITERIA]
    if criterion_ids != expected_ids:
        raise ValueError("scorecard must contain exactly the eight ordered criterion IDs")

    cells = list(scorecard.get("task_criteria", []))
    pairs = [(cell["task"], cell["criterion_id"]) for cell in cells]
    if len(cells) != 16 or len(set(pairs)) != 16:
        raise ValueError("both tasks require exactly one state for every criterion")

    manifest = _read_json(repo_root / MANIFEST_PATH)
    artifact_index = _artifact_index(manifest)
    measurement_ids: set[str] = set()
    for measurement in scorecard.get("measurements", []):
        missing = REQUIRED_MEASUREMENT_FIELDS - set(measurement)
        if missing:
            raise ValueError(
                f"measurement {measurement.get('measurement_id')} missing fields: {sorted(missing)}"
            )
        measurement_id = str(measurement["measurement_id"])
        if measurement_id in measurement_ids:
            raise ValueError(f"duplicate measurement ID: {measurement_id}")
        measurement_ids.add(measurement_id)

        denominator = measurement["denominator"]
        if isinstance(denominator, (int, float)) and denominator <= 0:
            if measurement["value"] is not None:
                raise ValueError(f"zero or invalid denominator emitted a rate: {measurement_id}")
        if measurement["row_scope"] == "aggregate_only_rows_sealed":
            if "rows" in measurement or "row_records" in measurement:
                raise ValueError(f"locked artifact emitted rows: {measurement_id}")
            if "aggregate" not in str(measurement["row_inspection_rule"]).lower():
                raise ValueError(f"sealed measurement lacks aggregate row rule: {measurement_id}")
        if measurement["comparability"] in {"construct_only", "not_comparable"}:
            if measurement.get("cross_task_numeric_delta") is not None:
                raise ValueError(
                    f"non-direct measurement emitted a cross-task delta: {measurement_id}"
                )

        for path in measurement["source_artifacts"]:
            if path not in artifact_index:
                raise ValueError(f"measurement source is not retained: {path}")
            expected = artifact_index[path]["sha256"]
            if measurement["source_hashes"].get(path) != expected:
                raise ValueError(f"measurement source hash metadata drift: {path}")
            actual, _ = _artifact_fingerprint(repo_root / path)
            if actual != expected:
                raise ValueError(f"measurement source hash drift: {path}")

    for cell in cells:
        if not cell["measurement_ids"]:
            raise ValueError(f"task-criterion cell has no explicit measurement state: {cell}")
        if not set(cell["measurement_ids"]) <= measurement_ids:
            raise ValueError("task-criterion cell references an unknown measurement")

    comparisons = list(scorecard.get("cross_task_matrix", []))
    if len(comparisons) != 8:
        raise ValueError("cross-task matrix must contain all eight criteria")
    for comparison in comparisons:
        if comparison["comparability"] != "direct" and comparison["numeric_delta"] is not None:
            raise ValueError("non-direct cross-task comparison emitted a numeric delta")

    gap_ids = set()
    for gap in scorecard.get("gaps", []):
        required = {"id", "class", "owner", "decision", "unblock_condition", "claim_effect"}
        if required - set(gap):
            raise ValueError(f"gap lacks decision metadata: {gap}")
        gap_ids.add(gap["id"])
    for cell in cells:
        if not set(cell["gap_ids"]) <= gap_ids:
            raise ValueError("task-criterion cell references an unknown gap")

    forbidden = {
        "composite_reliability",
        "composite_reliability_score",
        "overall_reliability_score",
        "weighted_reliability_index",
    }
    if forbidden & _recursive_keys(scorecard):
        raise ValueError("composite reliability fields are forbidden")

    zero = next(
        item
        for item in scorecard["measurements"]
        if item["measurement_id"] == "exectv2_sf_unknown_only_active_rate_overread_rate"
    )
    if zero["denominator"] != 0 or zero["value"] is not None:
        raise ValueError("ExECT zero denominator was not preserved")
    if zero.get("empty_gold_substitution_allowed") is not False:
        raise ValueError("ExECT empty-gold rows were relabelled as unknown")

    inventory = list(scorecard.get("source_inventory", []))
    if len(inventory) != 16:
        raise ValueError("source inventory must map all 16 task-by-criterion cells")


def _render_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--output-json", type=Path, default=OUTPUT_JSON)
    parser.add_argument("--output-report", type=Path, default=OUTPUT_REPORT)
    args = parser.parse_args()
    output_json = args.output_json if args.output_json.is_absolute() else ROOT / args.output_json
    output_report = (
        args.output_report if args.output_report.is_absolute() else ROOT / args.output_report
    )

    scorecard = build_scorecard(ROOT)
    rendered_json = _render_json(scorecard)
    rendered_report = render_report(scorecard)
    validate_report(scorecard, rendered_report)

    if args.check:
        stale = []
        if not output_json.is_file() or output_json.read_text(encoding="utf-8") != rendered_json:
            stale.append(str(output_json.relative_to(ROOT)))
        if (
            not output_report.is_file()
            or output_report.read_text(encoding="utf-8") != rendered_report
        ):
            stale.append(str(output_report.relative_to(ROOT)))
        if stale:
            raise SystemExit(f"shared reliability outputs are stale: {', '.join(stale)}")
        print("shared reliability scorecard and report are synchronized")
        return 0

    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_report.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(rendered_json, encoding="utf-8")
    output_report.write_text(rendered_report, encoding="utf-8")
    print(f"wrote {output_json.relative_to(ROOT)}")
    print(f"wrote {output_report.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
