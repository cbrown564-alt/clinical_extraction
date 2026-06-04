"""Materialize the Gan 2026 RQ9 selective-action router artifact."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.validation_gold_ambiguity_inventory import (  # noqa: E501
    DEFAULT_CSV_PATH as DEFAULT_INVENTORY_CSV_PATH,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

DEFAULT_SOURCE_JSONL_PATH = Path(
    "experiments/"
    "gan2026_hybrid_parallel_state_candidate_reasoner_validation750_gpt41mini_v0_"
    "deterministic_safety_floor_v2_replay_2026-06-03.jsonl"
)
DEFAULT_DECISIONS_PATH = Path("experiments/gold_audit_decisions.jsonl")
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_rq9_selective_action_router_2026-06-04.jsonl"
)
DEFAULT_JSON_PATH = Path("experiments/gan2026_rq9_selective_action_router_2026-06-04.json")
DEFAULT_REPORT_PATH = Path("experiments/gan2026_rq9_selective_action_router_2026-06-04.md")
DEFAULT_CONTRACT_PATH = Path(
    "docs/research/gan2026_rq9_selective_action_evaluation_contract_2026-06-04.md"
)
DEFAULT_BOUNDARY_POLICY_PATH = Path(
    "docs/research/gan2026_rq9_unknown_drop_attack_boundary_policy_2026-06-04.md"
)
DEFAULT_SOURCE_LAYER = "hybrid_adjudicator_with_adapters"
ROUTER_VERSION = "gan2026_rq9_selective_action_router_v0"

PREDICT = "predict"
ABSTAIN = "abstain"
HUMAN_REVIEW = "human_review"
EXTRACTION_ERROR_ANALYSIS = "extraction_error_analysis"


def load_inventory_rows(path: Path = DEFAULT_INVENTORY_CSV_PATH) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def load_human_decisions(path: Path = DEFAULT_DECISIONS_PATH) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return load_jsonl_rows(path)


def build_selective_action_router_rows(
    source_rows: Sequence[Mapping[str, Any]],
    inventory_rows: Sequence[Mapping[str, Any]],
    human_decisions: Sequence[Mapping[str, Any]] = (),
    *,
    source_layer: str = DEFAULT_SOURCE_LAYER,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    inventory_by_index = {int(row["source_row_index"]): row for row in inventory_rows}
    decisions_by_index = _latest_decision_by_index(human_decisions)
    rows = [
        _router_row(
            source_row,
            inventory_by_index.get(int(source_row["source_row_index"]), {}),
            decisions_by_index.get(int(source_row["source_row_index"])),
            source_layer=source_layer,
        )
        for source_row in source_rows
    ]
    rows.sort(key=lambda row: int(row["source_row_index"]))
    return rows, summarize_selective_action_router(rows, source_layer=source_layer)


def summarize_selective_action_router(
    rows: Sequence[Mapping[str, Any]],
    *,
    source_layer: str = DEFAULT_SOURCE_LAYER,
) -> dict[str, Any]:
    action_counts = Counter(str(row["selective_action"]) for row in rows)
    reason_counts = Counter(str(row["primary_reason"]) for row in rows)
    gold_kind_counts = Counter(
        str(row.get("development_accounting", {}).get("gold_label_kind") or "unknown")
        for row in rows
    )
    reviewed_rows = [
        row
        for row in rows
        if row.get("development_accounting", {}).get("human_simple_class") is not None
    ]
    nonprediction_rows = [
        row for row in rows if row["selective_action"] in {ABSTAIN, HUMAN_REVIEW}
    ]
    reviewed_nonprediction_rows = [
        row
        for row in nonprediction_rows
        if row.get("development_accounting", {}).get("human_simple_class") is not None
    ]
    predict_rows = [row for row in rows if row["selective_action"] == PREDICT]
    blocked_wrong_rows = [
        row
        for row in nonprediction_rows
        if row.get("source_candidate", {}).get("purist_correct") is False
    ]
    hidden_error_rows = [
        row
        for row in nonprediction_rows
        if _is_true_extraction_failure(row.get("development_accounting", {}))
    ]
    metrics = {
        "eligible_rows": len(rows),
        "covered_rows": action_counts[PREDICT],
        "abstained_rows": action_counts[ABSTAIN],
        "human_review_rows": action_counts[HUMAN_REVIEW],
        "extraction_error_analysis_rows": action_counts[EXTRACTION_ERROR_ANALYSIS],
        "coverage": _safe_rate(action_counts[PREDICT], len(rows)),
        "abstention_rate": _safe_rate(action_counts[ABSTAIN], len(rows)),
        "human_review_rate": _safe_rate(action_counts[HUMAN_REVIEW], len(rows)),
        "selective_accuracy": _safe_rate(
            sum(
                row.get("source_candidate", {}).get("purist_correct") is True
                for row in predict_rows
            ),
            len(predict_rows),
        ),
        "reviewed_rows": len(reviewed_rows),
        "reviewed_nonprediction_rows": len(reviewed_nonprediction_rows),
        "reviewed_human_correct_nonprediction_rows": sum(
            row.get("development_accounting", {}).get("human_simple_class") == "correct"
            for row in reviewed_nonprediction_rows
        ),
        "reviewed_human_noncorrect_nonprediction_rows": sum(
            row.get("development_accounting", {}).get("human_simple_class")
            in {"ambiguous", "wrong"}
            for row in reviewed_nonprediction_rows
        ),
        "over_abstention_rate_reviewed": _safe_rate(
            sum(
                row.get("selective_action") == ABSTAIN
                and row.get("development_accounting", {}).get("human_simple_class")
                == "correct"
                for row in reviewed_nonprediction_rows
            ),
            len(reviewed_nonprediction_rows),
        ),
        "over_review_rate_reviewed": _safe_rate(
            sum(
                row.get("selective_action") == HUMAN_REVIEW
                and row.get("development_accounting", {}).get("human_simple_class")
                == "correct"
                for row in reviewed_nonprediction_rows
            ),
            len(reviewed_nonprediction_rows),
        ),
        "rescue_value_rate": _safe_rate(len(blocked_wrong_rows), len(nonprediction_rows)),
        "hidden_error_rate": _safe_rate(len(hidden_error_rows), len(nonprediction_rows)),
    }
    return {
        "artifact_kind": "gan2026_rq9_selective_action_router",
        "date": "2026-06-04",
        "router_version": ROUTER_VERSION,
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "source_artifact": str(DEFAULT_SOURCE_JSONL_PATH),
        "source_layer": source_layer,
        "inventory_artifact": str(DEFAULT_INVENTORY_CSV_PATH),
        "human_decisions_artifact": str(DEFAULT_DECISIONS_PATH),
        "contract": str(DEFAULT_CONTRACT_PATH),
        "boundary_policy": str(DEFAULT_BOUNDARY_POLICY_PATH),
        "claim_language": (
            "Validation-development no-call selective-action router artifact. The "
            "router uses saved source predictions and predeclared boundary features; "
            "gold labels and human audit classes are development accounting only. It "
            "does not change scorer policy, prompts, deterministic rules, projection "
            "policy, locked-test behavior, or benchmark-comparable claims."
        ),
        "metrics": metrics,
        "action_counts": dict(sorted(action_counts.items())),
        "reason_counts": dict(sorted(reason_counts.items())),
        "gold_label_kind_counts": dict(sorted(gold_kind_counts.items())),
        "by_reason": _by_reason(rows),
        "by_gold_label_kind": _by_gold_label_kind(rows),
    }


def write_router_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_router_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path = DEFAULT_JSONL_PATH,
    json_path: Path = DEFAULT_JSON_PATH,
) -> None:
    metrics = metadata["metrics"]
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Gan 2026 RQ9 Selective-Action Router",
        "",
        "This is a no-call validation-development router artifact over a saved "
        "validation750 source candidate.",
        "",
        "## Decision",
        "",
        (
            f"Materialized `{metadata['router_version']}` over "
            f"{metrics['eligible_rows']} validation rows. It predicts on "
            f"{metrics['covered_rows']} rows, abstains on {metrics['abstained_rows']}, "
            f"routes {metrics['human_review_rows']} to human review, and keeps "
            f"{metrics['extraction_error_analysis_rows']} for extraction-error analysis."
        ),
        "",
        "## Claim Boundary",
        "",
        str(metadata["claim_language"]),
        "",
        "## Artifacts",
        "",
        f"- Router JSONL: `{jsonl_path}`",
        f"- Router summary JSON: `{json_path}`",
        f"- Source artifact: `{metadata['source_artifact']}`",
        f"- Source layer: `{metadata['source_layer']}`",
        f"- Inventory artifact: `{metadata['inventory_artifact']}`",
        f"- Human decisions: `{metadata['human_decisions_artifact']}`",
        f"- Contract: `{metadata['contract']}`",
        f"- Boundary policy: `{metadata['boundary_policy']}`",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in metrics.items():
        lines.append(f"| {key.replace('_', ' ')} | {_format_metric(value)} |")
    lines.extend(["", "## Reasons", "", "| Reason | Rows |", "| --- | ---: |"])
    for reason, count in metadata["reason_counts"].items():
        lines.append(f"| `{reason}` | {count} |")
    lines.extend(
        [
            "",
            "## Non-Prediction Rows",
            "",
            "| Row | Action | Reason | Source label | Human class |",
            "| ---: | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        if row["selective_action"] == PREDICT:
            continue
        accounting = row["development_accounting"]
        lines.append(
            f"| {row['source_row_index']} | `{row['selective_action']}` | "
            f"`{row['primary_reason']}` | "
            f"`{row['source_candidate'].get('final_label') or ''}` | "
            f"`{accounting.get('human_simple_class') or ''}` |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _router_row(
    source_row: Mapping[str, Any],
    inventory_row: Mapping[str, Any],
    human_decision: Mapping[str, Any] | None,
    *,
    source_layer: str,
) -> dict[str, Any]:
    source_index = int(source_row["source_row_index"])
    source_candidate = _source_candidate(source_row, source_layer=source_layer)
    boundary = _boundary_features(source_row, inventory_row, source_candidate)
    action, primary_reason, secondary_reasons = _route(boundary, source_candidate)
    final_label = source_candidate["final_label"] if action == PREDICT else None
    selected_evidence = source_candidate.get("selected_evidence") or ""
    router_packet = {
        "source_row_index": source_index,
        "split": source_row.get("split", "validation"),
        "split_manifest": source_row.get("split_manifest", "gan2026_split_v1"),
        "router_version": ROUTER_VERSION,
        "source_layer": source_layer,
        "selective_action": action,
        "primary_reason": primary_reason,
        "secondary_reasons": secondary_reasons,
        "final_label": final_label,
        "selected_evidence": selected_evidence or "no_exact_evidence",
        "selected_evidence_exact": bool(source_candidate.get("selected_evidence_exact")),
        "boundary_features": boundary,
    }
    return {
        "artifact_kind": "gan2026_rq9_selective_action_router_row",
        "claim_boundary": "validation_development_no_call_rq9_selective_action_router",
        "source_row_index": source_index,
        "split": source_row.get("split", "validation"),
        "split_manifest": source_row.get("split_manifest", "gan2026_split_v1"),
        "router_version": ROUTER_VERSION,
        "source_layer": source_layer,
        "selective_action": action,
        "primary_reason": primary_reason,
        "secondary_reasons": secondary_reasons,
        "final_label": final_label,
        "source_candidate": source_candidate,
        "router_packet": router_packet,
        "development_accounting": {
            "gold_label": _text(
                inventory_row.get("gold_label")
                or source_row.get("reference", {}).get("gold_normalized_label")
            ),
            "gold_label_kind": _text(
                inventory_row.get("gold_label_kind")
                or source_row.get("reference", {}).get("gold_label_kind")
            ),
            "gold_reference": _text(inventory_row.get("gold_reference")),
            "codex_initial_ambiguity_label": _text(
                inventory_row.get("codex_initial_ambiguity_label")
            ),
            "codex_ambiguity_reasons": boundary["ambiguity_reasons"],
            "human_simple_class": human_decision.get("simple_class") if human_decision else None,
            "human_rq10_class": human_decision.get("rq10_class") if human_decision else None,
            "human_all_system_fail": (
                bool(human_decision.get("all_system_fail")) if human_decision else False
            ),
        },
    }


def _source_candidate(row: Mapping[str, Any], *, source_layer: str) -> dict[str, Any]:
    layer = dict((row.get("score_layers") or {}).get(source_layer) or {})
    structured = dict(row.get("structured_adjudicator_record") or {})
    component_inputs = row.get("component_inputs") or {}
    deterministic_top = dict(component_inputs.get("deterministic_top") or {})
    selected_evidence = (
        structured.get("selected_evidence")
        or deterministic_top.get("evidence")
        or layer.get("selected_evidence")
        or ""
    )
    return {
        "final_label": _text(layer.get("final_label") or structured.get("final_label")),
        "final_kind": _text(structured.get("final_kind")),
        "purist_correct": layer.get("purist_correct"),
        "pragmatic_correct": layer.get("pragmatic_correct"),
        "scorable": bool(layer.get("scorable", bool(layer.get("final_label")))),
        "selected_evidence": _text(selected_evidence),
        "selected_evidence_exact": _selected_evidence_exact(row),
        "selected_source_ids": list(structured.get("selected_source_ids") or []),
        "rationale": _text(structured.get("rationale") or deterministic_top.get("rationale")),
    }


def _boundary_features(
    source_row: Mapping[str, Any],
    inventory_row: Mapping[str, Any],
    source_candidate: Mapping[str, Any],
) -> dict[str, Any]:
    reasons = _split_reasons(inventory_row.get("codex_ambiguity_reasons"))
    reference_text = _text(inventory_row.get("gold_reference")).lower()
    selected_evidence_text = _text(source_candidate.get("selected_evidence")).lower()
    trigger_text = " ".join((reference_text, selected_evidence_text))
    joined_text = " ".join(
        _text(value)
        for value in (
            inventory_row.get("gold_reference"),
            inventory_row.get("reference_context"),
            source_candidate.get("selected_evidence"),
        )
    ).lower()
    final_label = _text(source_candidate.get("final_label")).lower()
    return {
        "ambiguity_reasons": reasons,
        "final_label": final_label,
        "source_has_drop_attack_language": _has_any(
            joined_text, "drop attack", "drop attacks", "loss of tone", "collapse", "collapses"
        ),
        "source_has_unable_to_quantify": _has_any(
            joined_text, "unable to quantify", "cannot quantify", "not quantified"
        ),
        "source_has_since_anchor": " since " in f" {joined_text} ",
        "source_has_trigger_language": _has_any(
            trigger_text,
            "trigger",
            "triggers",
            "only with",
            "sleep deprivation",
            "missed meals",
            "skipping meals",
            "luteal",
            "menstrual",
            "perimenstrual",
        ),
        "source_has_last_event_language": _has_any(
            joined_text, "last seizure", "latest one", "none since"
        ),
        "gold_label_kind": _text(inventory_row.get("gold_label_kind")),
        "instrumented": bool(source_candidate.get("final_label")),
        "scorable": bool(source_candidate.get("scorable")),
        "selected_evidence_exact": bool(source_candidate.get("selected_evidence_exact")),
        "source_artifact_kind": _text(source_row.get("artifact_kind")),
    }


def _route(
    boundary: Mapping[str, Any], source_candidate: Mapping[str, Any]
) -> tuple[str, str, list[str]]:
    reasons = set(boundary["ambiguity_reasons"])
    label = _text(source_candidate.get("final_label")).lower()
    if not boundary["instrumented"] or not boundary["scorable"]:
        return EXTRACTION_ERROR_ANALYSIS, "true_extraction_failure", []
    if "conditional_or_trigger_bound" in reasons or boundary["source_has_trigger_language"]:
        return ABSTAIN, "trigger_conditioned_frequency", []
    if boundary["source_has_drop_attack_language"]:
        if boundary["source_has_unable_to_quantify"]:
            return ABSTAIN, "missing_denominator_anchor", ["drop_attack_boundary"]
        if (
            "calendar_or_diary_arithmetic" in reasons
            or "last_event_or_seizure_free_boundary" in reasons
        ) and label == "unknown":
            return HUMAN_REVIEW, "drop_attack_boundary", ["missing_denominator_anchor"]
        if label and label != "unknown":
            return PREDICT, _predict_reason(label), []
        return HUMAN_REVIEW, "drop_attack_boundary", []
    if "last_event_or_seizure_free_boundary" in reasons:
        return HUMAN_REVIEW, "last_event_boundary", []
    if "cluster_or_per_cluster_convention" in reasons:
        return HUMAN_REVIEW, "cluster_projection_boundary", []
    if _missing_denominator(boundary, reasons):
        return ABSTAIN, "missing_denominator_anchor", []
    if "no_reference_boundary" in reasons or "non_epileptic_or_seizure_like_boundary" in reasons:
        return HUMAN_REVIEW, "benchmark_convention_boundary", []
    if label == "unknown":
        return PREDICT, "unknown_frequency_unquantified", []
    return PREDICT, _predict_reason(label), []


def _predict_reason(label: str) -> str:
    if label == "no seizure frequency reference":
        return "plain_no_reference"
    if label.startswith("seizure free"):
        return "plain_predictable_seizure_free"
    return "plain_predictable_frequency"


def _missing_denominator(boundary: Mapping[str, Any], reasons: set[str]) -> bool:
    return bool(
        "vague_count_or_period" in reasons
        and (
            "calendar_or_diary_arithmetic" in reasons
            or boundary["source_has_since_anchor"]
            or "unknown_gold_boundary" in reasons
        )
        and boundary["final_label"] == "unknown"
    )


def _latest_decision_by_index(
    decisions: Sequence[Mapping[str, Any]],
) -> dict[int, Mapping[str, Any]]:
    latest: dict[int, Mapping[str, Any]] = {}
    for decision in decisions:
        if str(decision.get("split") or "validation") != "validation":
            continue
        latest[int(decision["source_row_index"])] = decision
    return latest


def _selected_evidence_exact(row: Mapping[str, Any]) -> bool:
    diagnostics = row.get("diagnostics") or {}
    if "selected_evidence_exact" in diagnostics:
        return bool(diagnostics["selected_evidence_exact"])
    status = row.get("component_status") or {}
    return status.get("selected_evidence_exactness") == "ok"


def _split_reasons(value: Any) -> list[str]:
    return [reason for reason in _text(value).split(";") if reason]


def _by_reason(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = defaultdict(lambda: defaultdict(int))
    for row in rows:
        summary = grouped[str(row["primary_reason"])]
        summary["rows"] += 1
        summary[f"{row['selective_action']}_rows"] += 1
    return {key: dict(value) for key, value in sorted(grouped.items())}


def _by_gold_label_kind(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = defaultdict(lambda: defaultdict(int))
    for row in rows:
        key = str(row.get("development_accounting", {}).get("gold_label_kind") or "unknown")
        summary = grouped[key]
        summary["rows"] += 1
        summary[f"{row['selective_action']}_rows"] += 1
    return {key: dict(value) for key, value in sorted(grouped.items())}


def _is_true_extraction_failure(accounting: Mapping[str, Any]) -> bool:
    return bool(accounting.get("human_all_system_fail")) or (
        accounting.get("human_rq10_class") == "true_extraction_failure"
    )


def _safe_rate(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return numerator / denominator


def _format_metric(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.4f}"
    return str(value)


def _has_any(text: str, *needles: str) -> bool:
    return any(needle in text for needle in needles)


def _text(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Materialize the Gan 2026 RQ9 selective-action router artifact."
    )
    parser.add_argument("--source-jsonl", type=Path, default=DEFAULT_SOURCE_JSONL_PATH)
    parser.add_argument("--inventory-csv", type=Path, default=DEFAULT_INVENTORY_CSV_PATH)
    parser.add_argument("--human-decisions", type=Path, default=DEFAULT_DECISIONS_PATH)
    parser.add_argument("--source-layer", default=DEFAULT_SOURCE_LAYER)
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args()

    rows, metadata = build_selective_action_router_rows(
        load_jsonl_rows(args.source_jsonl),
        load_inventory_rows(args.inventory_csv),
        load_human_decisions(args.human_decisions),
        source_layer=args.source_layer,
    )
    write_jsonl_rows(rows, args.jsonl_path)
    write_router_json(metadata, args.json_path)
    write_router_report(
        rows,
        metadata,
        args.report_path,
        jsonl_path=args.jsonl_path,
        json_path=args.json_path,
    )


if __name__ == "__main__":
    main()
