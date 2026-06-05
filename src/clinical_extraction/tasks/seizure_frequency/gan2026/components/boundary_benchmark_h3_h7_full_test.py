"""Full H3/H7/H8 readout for boundary and benchmark convention mechanisms."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.components import (
    boundary_benchmark_candidate_assembly,
    boundary_benchmark_contract,
    boundary_benchmark_seed_panel,
    boundary_benchmark_validation_contract,
    boundary_benchmark_validation_panel,
    structured_candidate_contract,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.data import (
    GanRecord,
    load_records_for_split,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.pipeline_v1 import (
    Gan2026PipelineV1,
)

POLICY_NAME = "gan2026_h3_h7_full_boundary_benchmark_test_v0"
DEFAULT_OUTPUT_JSONL_PATH = Path(
    "experiments/gan2026_h3_h7_full_boundary_benchmark_test_v0_2026-06-05.jsonl"
)
DEFAULT_OUTPUT_JSON_PATH = Path(
    "experiments/gan2026_h3_h7_full_boundary_benchmark_test_v0_2026-06-05.json"
)
DEFAULT_OUTPUT_REPORT_PATH = Path(
    "experiments/gan2026_h3_h7_full_boundary_benchmark_test_v0_2026-06-05.md"
)


def build_synthetic_component_rows(
    panel_rows: Sequence[Mapping[str, Any]],
    contract_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Compare deterministic behavior with the typed H3/H7 contract on pairs."""

    contract_by_index = {
        int(row["source_row_index"]): row for row in contract_rows
    }
    pipeline = Gan2026PipelineV1()
    rows: list[dict[str, Any]] = []
    for panel_row in panel_rows:
        source_row_index = int(panel_row["source_row_index"])
        contract_row = contract_by_index[source_row_index]
        deterministic_label = _deterministic_label(panel_row, pipeline)
        typed_label = str(contract_row["gan_rendered_label"])
        gold_label = str(panel_row["expected_gan_rendered_label"])
        rows.append(
            {
                "artifact_kind": "gan2026_h3_h7_synthetic_component_row",
                "policy_name": POLICY_NAME,
                "source_row_index": source_row_index,
                "split": "synthetic_hard_control",
                "split_manifest": "gan2026_boundary_benchmark_seed_panel_v0",
                "hypothesis_ids": ["H3", "H7"],
                "pair_id": panel_row["pair_id"],
                "pair_variant": panel_row["pair_variant"],
                "panel_role": panel_row["panel_role"],
                "target_family": panel_row["target_family"],
                "target_mechanism": panel_row["target_mechanism"],
                "gold_label": gold_label,
                "typed_label": typed_label,
                "deterministic_label": deterministic_label,
                "typed_correct": _purist_correct(typed_label, gold_label),
                "deterministic_correct": _purist_correct(
                    deterministic_label,
                    gold_label,
                ),
                "typed_candidate_exposure": contract_row["candidate_exposure"],
                "typed_candidate_present": bool(contract_row["contract_matched"])
                and bool(contract_row["exact_evidence"]),
                "typed_exact_evidence": bool(contract_row["exact_evidence"]),
                "typed_contract_matched": bool(contract_row["contract_matched"]),
                "deterministic_component_owner": "deterministic_rule",
                "typed_component_owner": contract_row["component_owner"],
                "source_note_text": None,
                "claim_boundary": "synthetic_development_only_no_holdout_use",
            }
        )
    return rows


def build_validation_candidate_rows(
    contract_rows: Sequence[Mapping[str, Any]],
    current_candidate_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Build all-eligible validation transition rows for the H3 readout."""

    return boundary_benchmark_candidate_assembly.build_candidate_rows(
        contract_rows,
        current_candidate_rows,
    )


def summarize_full_test(
    *,
    synthetic_rows: Sequence[Mapping[str, Any]],
    validation_contract_rows: Sequence[Mapping[str, Any]],
    validation_candidate_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Summarize H3 candidate exposure, H7 pair consistency, and H8 conventions."""

    synthetic_pairs = _pair_groups(synthetic_rows)
    typed_consistent_pairs = sum(
        _pair_labels_consistent(pair, "typed_label") for pair in synthetic_pairs.values()
    )
    deterministic_consistent_pairs = sum(
        _pair_labels_consistent(pair, "deterministic_label")
        for pair in synthetic_pairs.values()
    )
    deterministic_flip_pairs = len(synthetic_pairs) - deterministic_consistent_pairs
    selected_validation = [
        row for row in validation_candidate_rows if row["selected_for_ablation"]
    ]
    h8_validation_rows = [
        row for row in validation_candidate_rows if _is_benchmark_convention_row(row)
    ]
    h8_selected_rows = [
        row for row in h8_validation_rows if row["selected_for_ablation"]
    ]
    h8_transitions = Counter(str(row["transition"]) for row in h8_selected_rows)
    h8_rule_counts = Counter(
        str(row["benchmark_format_rule_id"]) for row in h8_validation_rows
    )
    h8_clinical_rendering_separated_rows = sum(
        str(row.get("clinical_final_state", ""))
        and str(row.get("proposed_label", ""))
        and str(row.get("clinical_final_state")) != str(row.get("proposed_label"))
        for row in h8_validation_rows
    )
    transitions = Counter(str(row["transition"]) for row in selected_validation)
    candidate_exposure_counts = Counter(
        str(row["candidate_exposure"]) for row in validation_candidate_rows
    )
    validation_contract_matched = sum(
        bool(row["contract_matched"]) for row in validation_contract_rows
    )
    validation_exact_evidence = sum(
        bool(row["exact_evidence"]) for row in validation_contract_rows
    )
    validation_contract_count = len(validation_contract_rows)
    validation_candidate_present = sum(
        bool(row["contract_matched"]) and bool(row["exact_evidence"])
        for row in validation_contract_rows
    )
    unsupported_candidate_rows = sum(
        bool(row.get("contract_issues")) or not bool(row["exact_evidence"])
        for row in validation_contract_rows
    )
    metadata_complete_rows = sum(_metadata_complete(row) for row in validation_candidate_rows)
    selected_count = len(selected_validation)
    c_to_w_rate = _rate(transitions["C_to_W"], selected_count)
    h3_gate_failures = []
    if validation_candidate_present < 150:
        h3_gate_failures.append("validation_candidate_exposure_below_150")
    if transitions["W_to_C"] < structured_candidate_contract.MIN_W_TO_C:
        h3_gate_failures.append(
            f"validation_{structured_candidate_contract.W_TO_C_GATE_FAILURE}"
        )
    if c_to_w_rate > 0.05:
        h3_gate_failures.append("validation_c_to_w_above_5_percent")
    if unsupported_candidate_rows:
        h3_gate_failures.append("unsupported_or_inexact_candidate_rows")
    h7_gate_failures = []
    if typed_consistent_pairs != len(synthetic_pairs):
        h7_gate_failures.append("typed_pair_inconsistency")
    if deterministic_flip_pairs == 0:
        h7_gate_failures.append("no_deterministic_template_flips_observed")
    h8_gate_failures = []
    if not h8_validation_rows:
        h8_gate_failures.append("no_benchmark_convention_rows")
    if any(not bool(row["exact_evidence"]) for row in h8_validation_rows):
        h8_gate_failures.append("benchmark_convention_inexact_evidence")
    if any(bool(row.get("source_note_text_present")) for row in h8_validation_rows):
        h8_gate_failures.append("benchmark_convention_source_note_text_written")
    if h8_clinical_rendering_separated_rows != len(h8_validation_rows):
        h8_gate_failures.append("clinical_state_rendered_label_not_separated")

    return {
        "artifact_kind": "gan2026_h3_h7_full_boundary_benchmark_test_summary",
        "policy_name": POLICY_NAME,
        "hypotheses_tested": ["H3", "H7", "H8"],
        "split_manifest": "gan2026_split_v1",
        "inspection_policy": (
            "synthetic row review and validation row-level review only; no "
            "locked-test row-level artifacts used"
        ),
        "locked_test_row_level_artifacts_used": 0,
        "holdout_authorized": False,
        "h3_status": (
            "tested_rejected_for_current_typed_layer"
            if h3_gate_failures
            else "tested_supported_for_current_typed_layer"
        ),
        "h7_status": (
            "tested_supported_for_deterministic_template_brittleness"
            if not h7_gate_failures
            else "tested_not_supported_on_current_pair_panel"
        ),
        "h8_status": (
            "tested_partial_validation_support_for_benchmark_convention_subset"
            if not h8_gate_failures
            else "tested_not_supported_on_current_validation_panel"
        ),
        "synthetic_rows": len(synthetic_rows),
        "synthetic_pairs": len(synthetic_pairs),
        "typed_pair_consistent_pairs": typed_consistent_pairs,
        "deterministic_pair_consistent_pairs": deterministic_consistent_pairs,
        "deterministic_flip_pairs": deterministic_flip_pairs,
        "synthetic_typed_correct_rows": sum(
            bool(row["typed_correct"]) for row in synthetic_rows
        ),
        "synthetic_deterministic_correct_rows": sum(
            bool(row["deterministic_correct"]) for row in synthetic_rows
        ),
        "validation_contract_rows": validation_contract_count,
        "validation_candidate_present_rows": validation_candidate_present,
        "validation_contract_matched_rows": validation_contract_matched,
        "validation_exact_evidence_rows": validation_exact_evidence,
        "validation_unsupported_candidate_rows": unsupported_candidate_rows,
        "validation_metadata_complete_rows": metadata_complete_rows,
        "validation_selected_prediction_bearing_rows": selected_count,
        "validation_transition_counts": dict(sorted(transitions.items())),
        "validation_c_to_w_rate": c_to_w_rate,
        "h8_validation_rows": len(h8_validation_rows),
        "h8_selected_prediction_bearing_rows": len(h8_selected_rows),
        "h8_transition_counts": dict(sorted(h8_transitions.items())),
        "h8_benchmark_rule_counts": dict(sorted(h8_rule_counts.items())),
        "h8_clinical_rendering_separated_rows": h8_clinical_rendering_separated_rows,
        "candidate_exposure_counts": dict(sorted(candidate_exposure_counts.items())),
        "target_mechanism_counts": dict(
            sorted(
                Counter(
                    str(row["target_mechanism"]) for row in validation_candidate_rows
                ).items()
            )
        ),
        "slice_counts": dict(
            sorted(Counter(str(row["slice_id"]) for row in validation_candidate_rows).items())
        ),
        "h3_gate_failures": h3_gate_failures,
        "h7_gate_failures": h7_gate_failures,
        "h8_gate_failures": h8_gate_failures,
        "decision": _decision(h3_gate_failures, h7_gate_failures, h8_gate_failures),
        "claim_boundary": (
            "Development H3/H7/H8 readout over synthetic minimal pairs and all eligible "
            "validation boundary/benchmark rows. It tests candidate exposure, "
            "exact evidence, metadata completeness, transition safety, and pair "
            "consistency without using locked-test row-level artifacts."
        ),
        "interpretation": _interpretation(
            h3_gate_failures,
            h7_gate_failures,
            h8_gate_failures,
        ),
    }


def materialize_full_test(
    *,
    output_jsonl_path: Path = DEFAULT_OUTPUT_JSONL_PATH,
    output_json_path: Path = DEFAULT_OUTPUT_JSON_PATH,
    output_report_path: Path = DEFAULT_OUTPUT_REPORT_PATH,
    current_candidate_jsonl_path: Path = (
        boundary_benchmark_candidate_assembly.DEFAULT_CURRENT_CANDIDATE_JSONL_PATH
    ),
) -> dict[str, Any]:
    panel_rows = boundary_benchmark_seed_panel.build_seed_panel_rows()
    synthetic_contract_rows = boundary_benchmark_contract.build_contract_rows(panel_rows)
    validation_panel_rows = boundary_benchmark_validation_panel.build_validation_panel_rows(
        load_records_for_split("validation"),
        max_rows_per_slice=10_000,
    )
    validation_contract_rows = boundary_benchmark_validation_contract.build_contract_rows(
        validation_panel_rows
    )
    current_candidate_rows = load_jsonl_rows(current_candidate_jsonl_path)
    validation_candidate_rows = build_validation_candidate_rows(
        validation_contract_rows,
        current_candidate_rows,
    )
    synthetic_rows = build_synthetic_component_rows(panel_rows, synthetic_contract_rows)
    summary = summarize_full_test(
        synthetic_rows=synthetic_rows,
        validation_contract_rows=validation_contract_rows,
        validation_candidate_rows=validation_candidate_rows,
    )
    rows = [*synthetic_rows, *validation_candidate_rows]
    summary = {
        **summary,
        "jsonl_artifact": str(output_jsonl_path),
        "json_artifact": str(output_json_path),
        "report_artifact": str(output_report_path),
        "source_current_candidate_artifact": str(current_candidate_jsonl_path),
    }
    write_jsonl_rows(rows, output_jsonl_path)
    output_json_path.parent.mkdir(parents=True, exist_ok=True)
    output_json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(summary, output_report_path)
    return summary


def write_report(summary: Mapping[str, Any], path: Path) -> None:
    lines = [
        "# Gan 2026 H3/H7/H8 Full Boundary/Benchmark Test v0",
        "",
        str(summary["claim_boundary"]),
        "",
        "## Decision",
        "",
        str(summary["decision"]),
        "",
        "## Hypothesis Outcomes",
        "",
        "| Hypothesis | Status |",
        "| --- | --- |",
        f"| H3 candidate-generation recall | `{summary['h3_status']}` |",
        f"| H7 template brittleness | `{summary['h7_status']}` |",
        f"| H8 benchmark-format convention | `{summary['h8_status']}` |",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| synthetic rows | {summary['synthetic_rows']} |",
        f"| synthetic pairs | {summary['synthetic_pairs']} |",
        f"| typed pair-consistent pairs | {summary['typed_pair_consistent_pairs']} |",
        (
            "| deterministic pair-consistent pairs | "
            f"{summary['deterministic_pair_consistent_pairs']} |"
        ),
        f"| deterministic flip pairs | {summary['deterministic_flip_pairs']} |",
        f"| synthetic typed-correct rows | {summary['synthetic_typed_correct_rows']} |",
        (
            "| synthetic deterministic-correct rows | "
            f"{summary['synthetic_deterministic_correct_rows']} |"
        ),
        f"| validation contract rows | {summary['validation_contract_rows']} |",
        (
            "| validation candidate-present rows | "
            f"{summary['validation_candidate_present_rows']} |"
        ),
        f"| validation exact-evidence rows | {summary['validation_exact_evidence_rows']} |",
        (
            "| validation selected prediction-bearing rows | "
            f"{summary['validation_selected_prediction_bearing_rows']} |"
        ),
        f"| validation C->W rate | {summary['validation_c_to_w_rate']:.4f} |",
        f"| H8 validation rows | {summary['h8_validation_rows']} |",
        (
            "| H8 selected prediction-bearing rows | "
            f"{summary['h8_selected_prediction_bearing_rows']} |"
        ),
        (
            "| H8 clinical/rendering separated rows | "
            f"{summary['h8_clinical_rendering_separated_rows']} |"
        ),
        "",
        "## Validation Transitions",
        "",
        "| Transition | Rows |",
        "| --- | ---: |",
    ]
    for transition, count in summary["validation_transition_counts"].items():
        lines.append(f"| `{transition}` | {count} |")
    lines.extend(
        [
            "",
            "## H8 Benchmark Convention Transitions",
            "",
            "| Transition | Rows |",
            "| --- | ---: |",
        ]
    )
    for transition, count in summary["h8_transition_counts"].items():
        lines.append(f"| `{transition}` | {count} |")
    lines.extend(["", "## H8 Benchmark Rules", "", "| Rule | Rows |", "| --- | ---: |"])
    for rule, count in summary["h8_benchmark_rule_counts"].items():
        lines.append(f"| `{rule}` | {count} |")
    lines.extend(["", "## H3 Gate Failures", ""])
    lines.extend(
        f"- `{failure}`" for failure in summary["h3_gate_failures"]
    )
    if not summary["h3_gate_failures"]:
        lines.append("- none")
    lines.extend(["", "## H7 Gate Failures", ""])
    lines.extend(
        f"- `{failure}`" for failure in summary["h7_gate_failures"]
    )
    if not summary["h7_gate_failures"]:
        lines.append("- none")
    lines.extend(["", "## H8 Gate Failures", ""])
    lines.extend(
        f"- `{failure}`" for failure in summary["h8_gate_failures"]
    )
    if not summary["h8_gate_failures"]:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            str(summary["interpretation"]),
            "",
            "## Artifacts",
            "",
            f"- Rows JSONL: `{summary['jsonl_artifact']}`",
            f"- Summary JSON: `{summary['json_artifact']}`",
            f"- Source current candidate JSONL: `{summary['source_current_candidate_artifact']}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _deterministic_label(
    panel_row: Mapping[str, Any],
    pipeline: Gan2026PipelineV1,
) -> str:
    record = GanRecord(
        source_row_index=int(panel_row["source_row_index"]),
        note_text=str(panel_row["source_note_text"]),
        gold_label=str(panel_row["expected_gan_rendered_label"]),
        gold_reference=str(panel_row["expected_evidence_substring"]),
        labels_match_all_categories=True,
        quotes_ok_all_categories=True,
        row_ok=True,
        raw={},
    )
    return str(pipeline.run(record).output.final_value)


def _pair_groups(rows: Sequence[Mapping[str, Any]]) -> dict[str, list[Mapping[str, Any]]]:
    pairs: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for row in rows:
        pairs[str(row["pair_id"])].append(row)
    return pairs


def _pair_labels_consistent(rows: Sequence[Mapping[str, Any]], field: str) -> bool:
    labels = {str(row[field]) for row in rows}
    return len(labels) == 1


def _metadata_complete(row: Mapping[str, Any]) -> bool:
    required = (
        "candidate_exposure",
        "event_kind",
        "event_target",
        "temporality",
        "assertion_status",
        "benchmark_policy_id",
        "benchmark_format_rule_id",
        "component_owner",
    )
    return all(str(row.get(field, "")) != "" for field in required)


def _is_benchmark_convention_row(row: Mapping[str, Any]) -> bool:
    return (
        str(row.get("target_mechanism", "")) == "benchmark_convention_renderer_v0"
        or str(row.get("benchmark_format_rule_id", "")) not in {"", "none_boundary_state_only"}
    )


def _purist_correct(prediction_label: str, gold_label: str) -> bool:
    try:
        parsed_prediction = label_to_frequency_record(prediction_label)
        parsed_gold = label_to_frequency_record(gold_label)
    except ValueError:
        return False
    if parsed_prediction is None or parsed_gold is None:
        return False
    return map_purist(parsed_prediction.monthly_frequency) == map_purist(
        parsed_gold.monthly_frequency
    )


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _decision(
    h3_gate_failures: Sequence[str],
    h7_gate_failures: Sequence[str],
    h8_gate_failures: Sequence[str],
) -> str:
    h8_suffix = "_h8_partial" if not h8_gate_failures else "_h8_not_supported"
    if h3_gate_failures and not h7_gate_failures:
        return f"h3_rejected_current_layer_h7_supported{h8_suffix}"
    if h3_gate_failures and h7_gate_failures:
        return f"h3_rejected_current_layer_h7_not_supported{h8_suffix}"
    if not h3_gate_failures and not h7_gate_failures:
        return f"h3_supported_current_layer_h7_supported{h8_suffix}"
    return f"h3_supported_current_layer_h7_not_supported{h8_suffix}"


def _interpretation(
    h3_gate_failures: Sequence[str],
    h7_gate_failures: Sequence[str],
    h8_gate_failures: Sequence[str],
) -> str:
    h3_text = (
        "H3 is rejected for the current shallow typed layer because all eligible "
        "validation rows have exact supported candidate exposure but the surface "
        "is too small and produces too few W->C transitions for promotion."
        if h3_gate_failures
        else "H3 is supported for the current shallow typed layer under the configured gates."
    )
    h7_text = (
        "H7 is supported on the synthetic pair panel: the typed mechanism is pair "
        "consistent while the deterministic comparator flips on superficial "
        "wording/order variants."
        if not h7_gate_failures
        else "H7 is not supported on the current pair panel under the configured gates."
    )
    h8_text = (
        "H8 has partial validation-development support: benchmark-convention rows "
        "are explicitly separated into clinical state and Gan-rendered label fields "
        "with exact evidence, but the readout is not a locked-test transfer audit."
        if not h8_gate_failures
        else "H8 is not supported on the current validation panel under the configured gates."
    )
    return f"{h3_text} {h7_text} {h8_text}"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-jsonl-path", type=Path, default=DEFAULT_OUTPUT_JSONL_PATH)
    parser.add_argument("--output-json-path", type=Path, default=DEFAULT_OUTPUT_JSON_PATH)
    parser.add_argument("--output-report-path", type=Path, default=DEFAULT_OUTPUT_REPORT_PATH)
    parser.add_argument(
        "--current-candidate-jsonl-path",
        type=Path,
        default=boundary_benchmark_candidate_assembly.DEFAULT_CURRENT_CANDIDATE_JSONL_PATH,
    )
    args = parser.parse_args(argv)
    summary = materialize_full_test(
        output_jsonl_path=args.output_jsonl_path,
        output_json_path=args.output_json_path,
        output_report_path=args.output_report_path,
        current_candidate_jsonl_path=args.current_candidate_jsonl_path,
    )
    print(json.dumps({"decision": summary["decision"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
