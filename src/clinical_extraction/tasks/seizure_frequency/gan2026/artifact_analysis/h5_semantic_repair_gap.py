"""Aggregate-safe H5 semantic-repair attribution test."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

DEFAULT_REPLACEMENT_JSON_PATH = Path(
    "experiments/gan2026_llm_replacement_postprocessing_ablation_validation250_v0_"
    "2026-06-02.json"
)
DEFAULT_FEWSHOT_VALIDATION_JSON_PATH = Path(
    "experiments/gan2026_fewshot_train_exemplar_full_validation750_gpt41_2026-06-05.json"
)
DEFAULT_FEWSHOT_TEST_JSON_PATH = Path(
    "experiments/gan2026_fewshot_train_exemplar_contract_test450_aggregate_audit_"
    "2026-06-05.json"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_h5_semantic_repair_gap_test_v0_2026-06-05.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_h5_semantic_repair_gap_test_v0_2026-06-05.md"
)


def build_h5_semantic_repair_gap(
    replacement_ablation: Mapping[str, Any],
    *,
    validation_summary: Mapping[str, Any],
    test_summary: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the H5 readout from validation ladders and aggregate test summaries."""

    conditions = {
        str(condition.get("condition")): condition
        for condition in replacement_ablation.get("conditions", [])
        if isinstance(condition, Mapping)
    }
    raw = _condition_summary(conditions.get("raw_model_selected_label"))
    format_only = _condition_summary(conditions.get("format_only_repair"))
    selected_evidence = _condition_summary(
        conditions.get("selected_evidence_arithmetic_only")
    )
    benchmark_aligned = _condition_summary(conditions.get("benchmark_aligned_adapter"))

    validation_metrics = _metrics(validation_summary)
    test_metrics = _metrics(test_summary)
    validation_raw = _number(validation_metrics.get("raw_proposed_purist_proxy"))
    validation_full = _number(validation_metrics.get("contract_projected_purist_proxy"))
    test_raw = _number(test_metrics.get("raw_base_purist_proxy"))
    test_full = _number(test_metrics.get("final_purist_proxy"))

    validation_gain = _difference(validation_full, validation_raw)
    test_gain = _difference(test_full, test_raw)
    raw_gap = _difference(validation_raw, test_raw)
    full_gap = _difference(validation_full, test_full)
    gain_gap = _difference(validation_gain, test_gain)

    outcome = _classify_outcome(
        validation_gain=validation_gain,
        test_gain=test_gain,
        raw_gap=raw_gap,
        full_gap=full_gap,
        benchmark_aligned_gain=_difference(
            benchmark_aligned["purist_accuracy"], raw["purist_accuracy"]
        ),
        selected_evidence_gain=_difference(
            selected_evidence["purist_accuracy"], raw["purist_accuracy"]
        ),
    )

    return {
        "artifact_kind": "gan2026_h5_semantic_repair_gap_test_v0",
        "date": "2026-06-05",
        "hypothesis_id": "H5",
        "hypothesis": "Deterministic semantic repair masks LLM weakness on validation.",
        "split_manifest": str(
            replacement_ablation.get("split_manifest") or "gan2026_split_v1"
        ),
        "inspection_policy": {
            "validation": "row_level_allowed",
            "locked_test": "aggregate_only",
        },
        "locked_test_row_level_artifacts_used": 0,
        "source_artifacts": {
            "same_output_ladder": str(DEFAULT_REPLACEMENT_JSON_PATH),
            "validation_summary": str(DEFAULT_FEWSHOT_VALIDATION_JSON_PATH),
            "locked_test_aggregate_summary": str(DEFAULT_FEWSHOT_TEST_JSON_PATH),
        },
        "same_output_ladder": {
            "row_count": _int(_metrics(replacement_ablation).get("row_count")),
            "raw_model_selected_label": raw,
            "format_only_repair": format_only,
            "selected_evidence_arithmetic_only": selected_evidence,
            "benchmark_aligned_adapter": benchmark_aligned,
            "format_only_gain_over_raw": _difference(
                format_only["purist_accuracy"], raw["purist_accuracy"]
            ),
            "selected_evidence_gain_over_raw": _difference(
                selected_evidence["purist_accuracy"], raw["purist_accuracy"]
            ),
            "benchmark_aligned_gain_over_raw": _difference(
                benchmark_aligned["purist_accuracy"], raw["purist_accuracy"]
            ),
        },
        "validation_test_repair_gain": {
            "validation_rows": _int(validation_metrics.get("row_count")),
            "test_rows": _int(test_metrics.get("test_rows")),
            "validation_raw_proxy": validation_raw,
            "validation_full_repair_proxy": validation_full,
            "validation_repair_gain": validation_gain,
            "test_raw_proxy": test_raw,
            "test_full_repair_proxy": test_full,
            "test_repair_gain": test_gain,
            "raw_validation_minus_test_gap": raw_gap,
            "full_repair_validation_minus_test_gap": full_gap,
            "repair_gain_validation_minus_test": gain_gap,
            "validation_contract_selected_rows": _int(
                validation_metrics.get("contract_selected_rows")
            ),
            "test_contract_selected_rows": _int(test_metrics.get("contract_selected_rows")),
            "validation_parse_ok_rate": _ratio(
                validation_metrics.get("parse_ok_rows"),
                validation_metrics.get("row_count"),
            ),
            "test_parse_ok_rate": _ratio(
                test_metrics.get("fewshot_parse_ok_rows"),
                test_metrics.get("test_rows"),
            ),
            "validation_exact_evidence_rate": _ratio(
                validation_metrics.get("exact_evidence_rows"),
                validation_metrics.get("row_count"),
            ),
            "test_exact_evidence_rate": _ratio(
                test_metrics.get("fewshot_exact_evidence_rows"),
                test_metrics.get("test_rows"),
            ),
        },
        "outcome": outcome,
        "interpretation": _interpretation(outcome),
    }


def write_h5_outputs(
    artifact: Mapping[str, Any],
    *,
    json_path: Path,
    markdown_path: Path,
) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
    write_h5_report(artifact, markdown_path)


def write_h5_report(artifact: Mapping[str, Any], path: Path) -> None:
    ladder = artifact.get("same_output_ladder", {})
    gain = artifact.get("validation_test_repair_gain", {})
    lines = [
        "# Gan 2026 H5 Semantic Repair Gap Test",
        "",
        "Diagnostic attribution only. Locked-test readout is aggregate-only and does "
        "not inspect row-level failures.",
        "",
        f"- Hypothesis: `{artifact.get('hypothesis_id')}` {artifact.get('hypothesis')}",
        f"- Split manifest: `{artifact.get('split_manifest')}`",
        f"- Outcome: `{artifact.get('outcome')}`",
        "- Locked-test row-level artifacts used: "
        f"`{artifact.get('locked_test_row_level_artifacts_used')}`",
        "",
        "## Same-Output Validation Ladder",
        "",
        "| Layer | Purist proxy | Changed from raw | Raw W->C | Raw C->W | Owner |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for key in (
        "raw_model_selected_label",
        "format_only_repair",
        "selected_evidence_arithmetic_only",
        "benchmark_aligned_adapter",
    ):
        item = ladder.get(key, {})
        lines.append(
            "| {layer} | {acc} | {changed} | {wtc} | {ctw} | {owner} |".format(
                layer=_md(key),
                acc=_metric(item.get("purist_accuracy")),
                changed=_md(item.get("changed_from_raw")),
                wtc=_md(item.get("raw_wrong_to_condition_correct")),
                ctw=_md(item.get("raw_correct_to_condition_wrong")),
                owner=_md(item.get("prediction_owner")),
            )
        )
    lines.extend(
        [
            "",
            "## Validation-Test Repair Gain",
            "",
            "| Surface | Raw/base proxy | Full repair proxy | Repair gain | Rows |",
            "| --- | ---: | ---: | ---: | ---: |",
            "| Validation750 | {vr} | {vf} | {vg} | {vrows} |".format(
                vr=_metric(gain.get("validation_raw_proxy")),
                vf=_metric(gain.get("validation_full_repair_proxy")),
                vg=_metric(gain.get("validation_repair_gain")),
                vrows=_md(gain.get("validation_rows")),
            ),
            "| Locked test450 | {tr} | {tf} | {tg} | {trows} |".format(
                tr=_metric(gain.get("test_raw_proxy")),
                tf=_metric(gain.get("test_full_repair_proxy")),
                tg=_metric(gain.get("test_repair_gain")),
                trows=_md(gain.get("test_rows")),
            ),
            "",
            f"- Raw validation-test gap: `{_metric(gain.get('raw_validation_minus_test_gap'))}`",
            "- Full-repair validation-test gap: "
            f"`{_metric(gain.get('full_repair_validation_minus_test_gap'))}`",
            "- Repair-gain validation minus test: "
            f"`{_metric(gain.get('repair_gain_validation_minus_test'))}`",
            "",
            "## Interpretation",
            "",
            str(artifact.get("interpretation", "")),
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Build the aggregate-safe H5 readout.")
    parser.add_argument("--replacement-json", type=Path, default=DEFAULT_REPLACEMENT_JSON_PATH)
    parser.add_argument(
        "--validation-json", type=Path, default=DEFAULT_FEWSHOT_VALIDATION_JSON_PATH
    )
    parser.add_argument("--test-json", type=Path, default=DEFAULT_FEWSHOT_TEST_JSON_PATH)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    artifact = build_h5_semantic_repair_gap(
        json.loads(args.replacement_json.read_text(encoding="utf-8")),
        validation_summary=json.loads(args.validation_json.read_text(encoding="utf-8")),
        test_summary=json.loads(args.test_json.read_text(encoding="utf-8")),
    )
    write_h5_outputs(artifact, json_path=args.json, markdown_path=args.markdown)
    print(json.dumps({"json": str(args.json), "markdown": str(args.markdown)}, sort_keys=True))


def _condition_summary(condition: Mapping[str, Any] | None) -> dict[str, Any]:
    condition = condition or {}
    score = condition.get("score") if isinstance(condition.get("score"), Mapping) else {}
    repair = (
        condition.get("repair_attribution")
        if isinstance(condition.get("repair_attribution"), Mapping)
        else {}
    )
    return {
        "prediction_owner": str(condition.get("prediction_owner") or ""),
        "rows": _int(score.get("rows")),
        "purist_correct": _int(score.get("purist_correct")),
        "purist_accuracy": _number(score.get("purist_accuracy")),
        "changed_from_raw": _int(repair.get("changed_from_raw")),
        "raw_wrong_to_condition_correct": _int(
            repair.get("raw_wrong_to_condition_correct")
        ),
        "raw_correct_to_condition_wrong": _int(
            repair.get("raw_correct_to_condition_wrong")
        ),
    }


def _classify_outcome(
    *,
    validation_gain: float | None,
    test_gain: float | None,
    raw_gap: float | None,
    full_gap: float | None,
    benchmark_aligned_gain: float | None,
    selected_evidence_gain: float | None,
) -> str:
    if validation_gain is None or test_gain is None:
        return "inconclusive_instrumentation_gap"
    repair_masks_validation = validation_gain >= 0.10 and validation_gain > test_gain
    full_gap_exceeds_raw_gap = (
        raw_gap is not None and full_gap is not None and full_gap > raw_gap
    )
    ladder_has_semantic_gain = (
        (benchmark_aligned_gain is not None and benchmark_aligned_gain > 0.03)
        or (selected_evidence_gain is not None and selected_evidence_gain > 0.03)
    )
    if repair_masks_validation and full_gap_exceeds_raw_gap and ladder_has_semantic_gain:
        return "partially_supported_revise"
    if repair_masks_validation and ladder_has_semantic_gain:
        return "supported"
    return "not_supported"


def _interpretation(outcome: str) -> str:
    if outcome == "partially_supported_revise":
        return (
            "H5 is supported in the narrow sense that validation repair layers mask "
            "weak raw LLM behavior, but the original primary-signal wording should be "
            "revised. The raw/base layer does not show a larger validation-test gap "
            "than full repair; instead, validation receives a much larger repair gain "
            "than locked test. Treat this as deterministic semantic repair and "
            "contract coverage overfitting validation, not as an LLM-owned transfer "
            "success."
        )
    if outcome == "supported":
        return (
            "H5 is supported: same-output repair layers materially improve the "
            "validation score, and the validation repair gain is larger than the "
            "locked-test aggregate repair gain."
        )
    if outcome == "not_supported":
        return (
            "H5 is not supported by these aggregate-safe artifacts; repair layers do "
            "not materially explain the validation-test behavior."
        )
    return (
        "H5 remains inconclusive because required ladder or aggregate metrics were "
        "missing."
    )


def _metrics(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    value = payload.get("metrics")
    if isinstance(value, Mapping):
        return value
    value = payload.get("summary")
    if isinstance(value, Mapping):
        return value
    return {}


def _difference(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    return round(left - right, 4)


def _ratio(numerator: Any, denominator: Any) -> float | None:
    numerator = _number(numerator)
    denominator = _number(denominator)
    if numerator is None or denominator in (None, 0):
        return None
    return round(numerator / denominator, 4)


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return round(float(value), 4)
    return None


def _int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def _metric(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.4f}"
    return _md(value)


def _md(value: Any) -> str:
    return "" if value is None else str(value)


if __name__ == "__main__":
    main()
