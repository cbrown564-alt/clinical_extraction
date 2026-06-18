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
    ""
)
DEFAULT_PROTOCOL_PATH = Path(
    ""
)

ALLOWED_RECOMMENDATIONS = [
    "render_as_selected_state",
    "render_as_unknown",
    "abstain_review",
    "choose_listed_competing_hypothesis",
]
VERIFIER_OUTPUT_SCHEMA = {
    "recommendation": ALLOWED_RECOMMENDATIONS,
    "recommended_label": "Seizure-frequency answer, unknown, or null for abstain_review.",
    "chosen_competing_hypothesis": "String copied from provided competing hypotheses or null.",
    "evidence_quotes": [
        "One or more exact phrases copied from proposed_evidence or competing text."
    ],
    "reason": "Brief explanation using only the provided text.",
    "confidence": "low, medium, or high.",
}
VERIFIER_SYSTEM_PROMPT = (
    "Review a proposed seizure-frequency answer. Use only the proposed answer, "
    "the quoted supporting text, the review notes, and the listed competing "
    "possibilities. Do not add a new answer from other context. Choose one "
    "allowed recommendation and return only JSON matching the requested fields."
)
VETO_FIRST_SYSTEM_PROMPT = (
    "You are reviewing a proposed seizure-frequency answer. Use only the clinical "
    "text shown below. Decide whether the proposed answer is clearly supported. "
    "Mark the answer as unsafe if the text is vague, missing a clear count or "
    "timeframe, describes only one seizure type while another remains active, "
    "describes seizure freedom for only one seizure type, adds cluster details "
    "that are not clearly stated, or conflicts with another listed possibility. "
    "When in doubt, choose use_unknown or needs_review. Return only JSON matching "
    "the requested fields."
)
SUPPORT_PARTS_SYSTEM_PROMPT = (
    "Check whether the proposed seizure-frequency answer is fully supported by "
    "the clinical text. A complete answer needs a seizure or event type, a count, "
    "a timeframe, and enough context to show it applies to the current highest "
    "seizure frequency. Do not fill in missing parts from assumptions. Return "
    "only JSON matching the requested fields."
)
VETO_FIRST_OUTPUT_SCHEMA = {
    "decision": ["use_proposed_answer", "use_unknown", "needs_review"],
    "blocking_issue": [
        "none",
        "vague_count",
        "vague_timeframe",
        "competing_seizure_type",
        "partial_seizure_freedom",
        "cluster_not_supported",
        "historical_or_conditional",
        "other",
    ],
    "supporting_quotes": ["Exact copied phrases from clinical_text."],
    "reason": "Brief explanation using only the provided clinical text.",
    "confidence": "low, medium, or high.",
}
SUPPORT_PARTS_OUTPUT_SCHEMA = {
    "seizure_or_event_type_supported": "true or false.",
    "count_supported": "true or false.",
    "timeframe_supported": "true or false.",
    "current_highest_frequency_supported": "true or false.",
    "all_required_parts_supported": "true or false.",
    "recommended_action": ["use_proposed_answer", "use_unknown", "needs_review"],
    "missing_or_conflicting_parts": [
        "Short names of any unsupported or conflicting parts."
    ],
    "quotes": ["Exact copied phrases from clinical_text."],
    "reason": "Brief explanation using only the provided clinical text.",
}
PROMPT_DESIGN_ORDER = [
    "veto_first_safety_reviewer",
    "support_parts_fact_check",
]
FLAG_REVIEW_REASONS = {
    "denominator_window_mismatch": "The count and timeframe may not belong together.",
    "diary_log_date_list_without_defined_observation_window": (
        "The text lists dates or diary entries without a clear observation timeframe."
    ),
    "frequency_with_count_blocking_ambiguity": (
        "The text may not give enough information for both count and timeframe."
    ),
    "frequency_with_exclusive_conditionality": (
        "The frequency may apply only under a condition or trigger."
    ),
    "seizure_free_non_all_type_scope_with_current_events": (
        "The text may describe seizure freedom for one seizure type while another "
        "type remains active."
    ),
    "unresolved_cluster_cadence_with_per_cluster_burden": (
        "The text may describe seizures in groups without a clear group frequency."
    ),
    "vague_trend_without_absolute_current_frequency": (
        "The text describes a trend but may not give a current frequency."
    ),
}


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
        "prompt_design_candidates": PROMPT_DESIGN_ORDER,
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
            "## Prompt Design Candidates",
            "",
            "Two plain-language candidate designs are rendered into each row for "
            "offline inspection. They are not live-call results and are not "
            "prediction-bearing.",
            "",
            "### `veto_first_safety_reviewer`",
            "",
            VETO_FIRST_SYSTEM_PROMPT,
            "",
            "Output fields: `decision`, `blocking_issue`, `supporting_quotes`, "
            "`reason`, `confidence`.",
            "",
            "### `support_parts_fact_check`",
            "",
            SUPPORT_PARTS_SYSTEM_PROMPT,
            "",
            "Output fields: `seizure_or_event_type_supported`, `count_supported`, "
            "`timeframe_supported`, `current_highest_frequency_supported`, "
            "`all_required_parts_supported`, `recommended_action`, "
            "`missing_or_conflicting_parts`, `quotes`, `reason`.",
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
            "proposed_answer": row.get("deterministic_policy_label"),
            "proposed_evidence": selected_evidence,
            "review_notes": _review_reasons(row.get("suspicious_state_flags") or []),
            "allowed_recommendations": ALLOWED_RECOMMENDATIONS,
            "provided_competing_hypotheses": _provided_competing_hypotheses(row),
            "output_schema": VERIFIER_OUTPUT_SCHEMA,
        },
        "prompt_design_candidates": _prompt_design_candidates(row, selected_state),
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


def _prompt_design_candidates(
    row: Mapping[str, Any],
    selected_state: Mapping[str, Any],
) -> dict[str, dict[str, Any]]:
    proposed_answer = row.get("deterministic_policy_label")
    clinical_text = str(selected_state.get("selected_evidence") or "")
    competing = _provided_competing_hypotheses(row)
    review_reasons = _review_reasons(row.get("suspicious_state_flags") or [])
    common = {
        "clinical_text": clinical_text,
        "proposed_answer": proposed_answer,
        "competing_possibilities": competing,
        "review_reasons": review_reasons,
    }
    return {
        "veto_first_safety_reviewer": {
            "system_prompt": VETO_FIRST_SYSTEM_PROMPT,
            **common,
            "output_schema": VETO_FIRST_OUTPUT_SCHEMA,
        },
        "support_parts_fact_check": {
            "system_prompt": SUPPORT_PARTS_SYSTEM_PROMPT,
            **common,
            "output_schema": SUPPORT_PARTS_OUTPUT_SCHEMA,
        },
    }


def _review_reasons(flags: Sequence[Any]) -> list[str]:
    reasons = [
        FLAG_REVIEW_REASONS[str(flag)]
        for flag in flags
        if str(flag) in FLAG_REVIEW_REASONS
    ]
    return reasons or ["The proposed answer was routed for extra review."]


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
