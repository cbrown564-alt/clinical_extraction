"""Predeclare a Gan 2026 selective verifier input surface from saved routing rows."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.suspicious_selected_state_routing import (  # noqa: E501
    DEFAULT_JSONL_PATH as DEFAULT_ROUTING_JSONL_PATH,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_selective_verifier_predeclaration_2026-06-04.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_selective_verifier_predeclaration_2026-06-04.json"
)
DEFAULT_REPORT_PATH = Path(
    "docs/research/gan2026_selective_verifier_predeclaration_2026-06-04.md"
)
DEFAULT_PROTOCOL_PATH = Path(
    "docs/research/gan2026_ambiguity_ownership_protocol_2026-06-04.md"
)

ALLOWED_RECOMMENDATIONS = [
    "render_as_selected_state",
    "render_as_unknown",
    "abstain_review",
    "choose_listed_competing_hypothesis",
]
VERIFIER_OUTPUT_SCHEMA = {
    "recommendation": ALLOWED_RECOMMENDATIONS,
    "recommended_label": "Gan normalized label, unknown, or null for abstain_review.",
    "chosen_competing_hypothesis": "String copied from provided competing hypotheses or null.",
    "evidence_quotes": [
        "One or more exact substrings copied from selected_evidence or provided competing text."
    ],
    "reason": "Brief explanation grounded only in the provided state and evidence.",
    "confidence": "low, medium, or high.",
}
VERIFIER_SYSTEM_PROMPT = (
    "You are a selective verifier for Gan 2026 seizure-frequency selected states. "
    "Use only the provided selected state, selected evidence, suspicious flags, "
    "deterministic label, and explicitly listed competing hypotheses. Do not infer "
    "new candidates from outside the provided evidence. Choose one allowed "
    "recommendation and return JSON matching the schema."
)


def build_selective_verifier_predeclaration_rows(
    routing_rows: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = [_predeclaration_row(row) for row in routing_rows if _is_verifier_eligible(row)]
    rows.sort(key=lambda row: int(row["source_row_index"]))
    return rows, summarize_selective_verifier_predeclaration(rows, routing_rows)


def summarize_selective_verifier_predeclaration(
    rows: Sequence[Mapping[str, Any]],
    routing_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    action_counts = Counter(row["suspicious_state_action"] for row in rows)
    delta_counts = Counter(row["development_accounting"]["delta"] for row in rows)
    flag_counts = Counter(flag for row in rows for flag in row["suspicious_state_flags"])
    excluded = _excluded_rows(routing_rows)
    return {
        "artifact_kind": "gan2026_selective_verifier_predeclaration",
        "date": "2026-06-04",
        "split_manifest": "gan2026_split_v1",
        "split": "validation",
        "source_artifact": str(DEFAULT_ROUTING_JSONL_PATH),
        "row_count": len(rows),
        "claim_language": (
            "Validation-development verifier predeclaration only. No live model calls, "
            "locked-test inspection, whole-pipeline promotion, or benchmark-comparable "
            "claim are authorized."
        ),
        "eligibility_rule": (
            "Include saved suspicious selected-state rows routed to unknown or review "
            "only when selected evidence is an exact source substring. Exclude rows "
            "whose selected evidence is missing or non-exact from verifier calls."
        ),
        "allowed_recommendations": ALLOWED_RECOMMENDATIONS,
        "verifier_output_schema": VERIFIER_OUTPUT_SCHEMA,
        "metrics": {
            "eligible_verifier_rows": len(rows),
            "route_unknown_rows": action_counts["route_unknown"],
            "route_review_rows": action_counts["route_review"],
            "w_to_c_against_comparator_rows": delta_counts["W_to_C"],
            "c_to_w_against_comparator_rows": delta_counts["C_to_W"],
            "routed_to_review_rows": delta_counts["routed_to_review"],
            "exact_evidence_rate": _safe_rate(
                sum(row["evidence_contract"]["selected_evidence_exact"] for row in rows),
                len(rows),
            ),
            "excluded_non_exact_or_missing_evidence_rows": len(excluded),
        },
        "excluded_source_row_indices": excluded,
        "flag_counts": dict(sorted(flag_counts.items())),
        "by_hidden_family": _hidden_family_summary(rows),
        "decision_rule": (
            "The verifier can become prediction-bearing only if changed-decision "
            "precision is high and deterministic-correct regression count is zero "
            "or explicitly adjudicated before any further validation use."
        ),
    }


def write_selective_verifier_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_selective_verifier_report(
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path = DEFAULT_JSONL_PATH,
    json_path: Path = DEFAULT_JSON_PATH,
    protocol_path: Path = DEFAULT_PROTOCOL_PATH,
) -> None:
    metrics = metadata["metrics"]
    lines = [
        "# Gan 2026 Selective Verifier Predeclaration",
        "",
        "This is a pre-run validation-development contract for a selective LLM verifier. "
        "It materializes the stable suspicious slices from the saved selected-state "
        "routing artifact and does not make live model calls.",
        "",
        "## Decision",
        "",
        (
            "Run a verifier only on exact-evidence suspicious rows. The predeclared "
            f"surface contains {metrics['eligible_verifier_rows']} rows: "
            f"{metrics['route_unknown_rows']} route-unknown rows and "
            f"{metrics['route_review_rows']} route-review rows. The development-only "
            f"accounting set includes {metrics['w_to_c_against_comparator_rows']} W->C "
            f"and {metrics['c_to_w_against_comparator_rows']} C->W rows against the "
            "saved deterministic comparator."
        ),
        "",
        "## Claim Boundary",
        "",
        str(metadata["claim_language"]),
        "",
        "## Eligibility Rule",
        "",
        str(metadata["eligibility_rule"]),
        "",
        "## Allowed Recommendations",
        "",
    ]
    lines.extend(f"- `{item}`" for item in metadata["allowed_recommendations"])
    lines.extend(
        [
            "",
            "## Verifier Prompt Contract",
            "",
            VERIFIER_SYSTEM_PROMPT,
            "",
            "The verifier output must include `recommendation`, `recommended_label`, "
            "`chosen_competing_hypothesis`, `evidence_quotes`, `reason`, and "
            "`confidence`. Evidence quotes must be exact substrings from the provided "
            "selected evidence or competing-hypothesis text.",
            "",
            "## Artifacts",
            "",
            f"- Protocol: `{protocol_path}`",
            f"- Verifier input JSONL: `{jsonl_path}`",
            f"- Summary JSON: `{json_path}`",
            f"- Source routing: `{metadata['source_artifact']}`",
            "",
            "## Metrics",
            "",
            "| Metric | Value |",
            "| --- | ---: |",
        ]
    )
    for key, value in metrics.items():
        lines.append(f"| {key.replace('_', ' ')} | {_format_metric(value)} |")
    lines.extend(["", "## Suspicious Flags", "", "| Flag | Rows |", "| --- | ---: |"])
    for key, value in metadata["flag_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## Development Accounting Rule",
            "",
            str(metadata["decision_rule"]),
            "",
            "The model input rows omit gold labels and W->C/C->W fields. Those fields "
            "remain in `development_accounting` for offline analysis after outputs are "
            "collected.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _predeclaration_row(row: Mapping[str, Any]) -> dict[str, Any]:
    selected_state = dict(row.get("selected_state") or {})
    selected_evidence = str(selected_state.get("selected_evidence") or "")
    comparison = row.get("comparison") or {}
    final_policy = row.get("final_policy_under_test") or {}
    return {
        "artifact_kind": "gan2026_selective_verifier_predeclaration_row",
        "claim_boundary": "validation_development_predeclared_selective_verifier_no_call",
        "source_row_index": int(row["source_row_index"]),
        "split": row.get("split", "validation"),
        "split_manifest": row.get("split_manifest", "gan2026_split_v1"),
        "hidden_families": list(row.get("hidden_families") or []),
        "suspicious_state_action": row.get("suspicious_state_action"),
        "suspicious_state_flags": list(row.get("suspicious_state_flags") or []),
        "evidence_contract": {
            "selected_evidence": selected_evidence,
            "selected_evidence_exact": bool(
                (row.get("selected_evidence_status") or {}).get("exact_trace")
            ),
            "selected_evidence_present": bool(
                (row.get("selected_evidence_status") or {}).get(
                    "selected_evidence_present"
                )
            ),
        },
        "verifier_model_input": {
            "system_prompt": VERIFIER_SYSTEM_PROMPT,
            "selected_state": selected_state,
            "deterministic_policy_label": row.get("deterministic_policy_label"),
            "deterministic_policy_action": row.get("deterministic_policy_action"),
            "suspicious_state_action": row.get("suspicious_state_action"),
            "suspicious_state_flags": list(row.get("suspicious_state_flags") or []),
            "allowed_recommendations": ALLOWED_RECOMMENDATIONS,
            "provided_competing_hypotheses": _provided_competing_hypotheses(row),
            "output_schema": VERIFIER_OUTPUT_SCHEMA,
        },
        "development_accounting": {
            "comparator_label": row.get("deterministic_policy_label"),
            "routing_policy_label": final_policy.get("label"),
            "routing_policy_action": final_policy.get("action"),
            "gold_label": row.get("gold_label"),
            "delta": comparison.get("delta"),
            "comparator_correct": bool(comparison.get("comparator_correct")),
            "routing_policy_correct": comparison.get("final_policy_correct"),
        },
        "post_run_accounting_contract": {
            "score_changed_decisions_against_comparator": True,
            "report_w_to_c_and_c_to_w": True,
            "block_prediction_bearing_use_on_unadjudicated_c_to_w": True,
        },
    }


def _is_verifier_eligible(row: Mapping[str, Any]) -> bool:
    if row.get("suspicious_state_action") not in {"route_unknown", "route_review"}:
        return False
    return bool((row.get("selected_evidence_status") or {}).get("exact_trace"))


def _excluded_rows(routing_rows: Sequence[Mapping[str, Any]]) -> list[int]:
    rows = [
        int(row["source_row_index"])
        for row in routing_rows
        if row.get("suspicious_state_action") in {"route_unknown", "route_review"}
        and not bool((row.get("selected_evidence_status") or {}).get("exact_trace"))
    ]
    return sorted(rows)


def _provided_competing_hypotheses(row: Mapping[str, Any]) -> list[str]:
    embedded = row.get("embedded_ambiguity_fields") or {}
    summary = str(embedded.get("competing_state_summary") or "").strip()
    return [summary] if summary else []


def _hidden_family_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, int]]:
    by_family: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        families = row["hidden_families"] or ["unclassified"]
        for family in families:
            by_family[str(family)]["rows"] += 1
            if row["suspicious_state_action"] == "route_unknown":
                by_family[str(family)]["route_unknown_rows"] += 1
            if row["suspicious_state_action"] == "route_review":
                by_family[str(family)]["route_review_rows"] += 1
            if row["development_accounting"]["delta"] == "C_to_W":
                by_family[str(family)]["c_to_w_rows"] += 1
            if row["development_accounting"]["delta"] == "W_to_C":
                by_family[str(family)]["w_to_c_rows"] += 1
    return {family: dict(counts) for family, counts in sorted(by_family.items())}


def _safe_rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _format_metric(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--routing-jsonl-path", type=Path, default=DEFAULT_ROUTING_JSONL_PATH)
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    routing_rows = load_jsonl_rows(args.routing_jsonl_path)
    rows, metadata = build_selective_verifier_predeclaration_rows(routing_rows)
    metadata = {**metadata, "source_artifact": str(args.routing_jsonl_path)}
    write_jsonl_rows(rows, args.jsonl_path)
    write_selective_verifier_json(metadata, args.json_path)
    write_selective_verifier_report(
        metadata,
        args.report_path,
        jsonl_path=args.jsonl_path,
        json_path=args.json_path,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
