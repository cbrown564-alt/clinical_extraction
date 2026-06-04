"""Predeclare Gan 2026 RQ9 abstention and human-review routing from RQ10 classes."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.rq10_gold_scorer_ambiguity_audit import (  # noqa: E501
    DEFAULT_JSON_PATH as DEFAULT_RQ10_JSON_PATH,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.rq10_gold_scorer_ambiguity_audit import (  # noqa: E501
    DEFAULT_JSONL_PATH as DEFAULT_RQ10_JSONL_PATH,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_rq9_abstention_review_predeclaration_2026-06-04.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_rq9_abstention_review_predeclaration_2026-06-04.json"
)
DEFAULT_REPORT_PATH = Path(
    "docs/research/gan2026_rq9_abstention_review_predeclaration_2026-06-04.md"
)
DEFAULT_RQ10_REPORT_PATH = Path(
    "docs/research/gan2026_rq10_gold_scorer_ambiguity_audit_answer_2026-06-04.md"
)

ROUTING_POLICY_VERSION = "gan2026_rq9_abstention_review_policy_v0"
ACTION_BY_BUCKET = {
    "possible_gold_weakness": "human_review_gold_reference",
    "clinically_defensible_alternative": "human_review_clinical_convention",
    "benchmark_convention_dominated": "human_review_benchmark_convention",
    "underdetermined_note": "abstain_or_route_unknown",
    "true_extraction_failure": "extraction_error_analysis",
}
PREDICTION_BLOCKING_ACTIONS = {
    "human_review_gold_reference",
    "human_review_clinical_convention",
    "human_review_benchmark_convention",
    "abstain_or_route_unknown",
}


def build_rq9_predeclaration_rows(
    rq10_rows: Sequence[Mapping[str, Any]],
    *,
    rq10_summary: Mapping[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = [_predeclaration_row(row) for row in rq10_rows]
    rows.sort(key=lambda row: int(row["source_row_index"]))
    return rows, summarize_rq9_predeclaration(rows, rq10_rows, rq10_summary=rq10_summary)


def summarize_rq9_predeclaration(
    rows: Sequence[Mapping[str, Any]],
    rq10_rows: Sequence[Mapping[str, Any]],
    *,
    rq10_summary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    action_counts = Counter(row["routing_action"] for row in rows)
    bucket_counts = Counter(row["review_bucket"] for row in rows)
    primary_class_counts = Counter(row["rq10_primary_class"] for row in rows)
    return {
        "artifact_kind": "gan2026_rq9_abstention_review_predeclaration",
        "date": "2026-06-04",
        "split_manifest": "gan2026_split_v1",
        "split": "validation",
        "source_artifact": str(DEFAULT_RQ10_JSONL_PATH),
        "source_summary": str(DEFAULT_RQ10_JSON_PATH),
        "routing_policy_version": ROUTING_POLICY_VERSION,
        "row_count": len(rows),
        "claim_language": (
            "Validation-development RQ9 predeclaration only. The policy defines "
            "abstention and human-review routing from saved RQ10 audit classes; it "
            "does not change scorer policy, gold labels, prompts, deterministic rules, "
            "projection policy, locked-test behavior, or benchmark-comparable claims."
        ),
        "routing_priority": [
            "possible_gold_weakness",
            "clinically_defensible_alternative",
            "benchmark_convention_dominated",
            "underdetermined_note",
            "true_extraction_failure",
        ],
        "routing_actions": ACTION_BY_BUCKET,
        "metrics": {
            "predeclared_rows": len(rows),
            "prediction_blocked_rows": sum(
                row["prediction_blocked_pending_review_or_abstention"] for row in rows
            ),
            "extraction_error_analysis_rows": action_counts["extraction_error_analysis"],
            "abstain_or_route_unknown_rows": action_counts["abstain_or_route_unknown"],
            "human_review_clinical_convention_rows": action_counts[
                "human_review_clinical_convention"
            ],
            "human_review_benchmark_convention_rows": action_counts[
                "human_review_benchmark_convention"
            ],
            "human_review_gold_reference_rows": action_counts["human_review_gold_reference"],
            "exact_evidence_rate": _safe_rate(
                sum(row["evidence_contract"]["selected_evidence_exact"] for row in rows),
                len(rows),
            ),
            "rq10_hard_row_ambiguity_rate": _rq10_metric(
                rq10_summary, "hard_row_ambiguity_rate"
            ),
        },
        "review_bucket_counts": dict(sorted(bucket_counts.items())),
        "primary_class_counts": dict(sorted(primary_class_counts.items())),
        "by_hidden_family": _hidden_family_summary(rows),
        "decision_rule": (
            "Use RQ9 as a selective-action evaluation: rows routed to review or "
            "abstention are success cases only when they block an unsafe final label "
            "without hiding true extraction failures. Promote no automatic label "
            "changes from this predeclaration."
        ),
    }


def write_rq9_predeclaration_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_rq9_predeclaration_report(
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path = DEFAULT_JSONL_PATH,
    json_path: Path = DEFAULT_JSON_PATH,
    rq10_report_path: Path = DEFAULT_RQ10_REPORT_PATH,
) -> None:
    metrics = metadata["metrics"]
    lines = [
        "# Gan 2026 RQ9 Abstention And Human-Review Predeclaration",
        "",
        "This is a pre-run validation-development contract for abstention and "
        "human-review routing using the saved RQ10 residual-miss classes.",
        "",
        "## Decision",
        "",
        (
            "Predeclare a selective-action policy over the 53 saved RQ10 residual "
            f"Purist misses. The policy blocks prediction-bearing use for "
            f"{metrics['prediction_blocked_rows']} rows through abstention or human "
            f"review, and keeps {metrics['extraction_error_analysis_rows']} rows as "
            "true extraction failures for component debugging."
        ),
        "",
        "## Claim Boundary",
        "",
        str(metadata["claim_language"]),
        "",
        "## Routing Policy",
        "",
        "| Review bucket | Action |",
        "| --- | --- |",
    ]
    for bucket in metadata["routing_priority"]:
        action = metadata["routing_actions"][bucket]
        lines.append(f"| `{bucket}` | `{action}` |")
    lines.extend(
        [
            "",
            "Priority order matters: possible gold/reference weakness and clinically "
            "defensible alternatives are routed before benchmark-convention and "
            "underdetermined-note classes, so RQ9 can separate manual review targets "
            "from ordinary extraction failures.",
            "",
            "## Artifacts",
            "",
            f"- RQ10 answer: `{rq10_report_path}`",
            f"- RQ9 JSONL: `{jsonl_path}`",
            f"- RQ9 summary JSON: `{json_path}`",
            f"- RQ10 source audit: `{metadata['source_artifact']}`",
            "",
            "## Metrics",
            "",
            "| Metric | Value |",
            "| --- | ---: |",
        ]
    )
    for key, value in metrics.items():
        lines.append(f"| {key.replace('_', ' ')} | {_format_metric(value)} |")
    lines.extend(["", "## Review Buckets", "", "| Bucket | Rows |", "| --- | ---: |"])
    for key, value in metadata["review_bucket_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(["", "## RQ10 Primary Classes", "", "| RQ10 class | Rows |", "| --- | ---: |"])
    for key, value in metadata["primary_class_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## Evaluation Contract",
            "",
            str(metadata["decision_rule"]),
            "",
            "Human-review packets omit gold labels, scorer categories, and W/C-style "
            "development accounting. Those fields remain only in "
            "`development_accounting` for post-routing analysis.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _predeclaration_row(row: Mapping[str, Any]) -> dict[str, Any]:
    bucket = _review_bucket(row)
    action = ACTION_BY_BUCKET[bucket]
    predicted_label = row.get("primary_predicted_label")
    return {
        "artifact_kind": "gan2026_rq9_abstention_review_predeclaration_row",
        "claim_boundary": "validation_development_predeclared_rq9_no_policy_change",
        "source_row_index": int(row["source_row_index"]),
        "split": row.get("split", "validation"),
        "split_manifest": row.get("split_manifest", "gan2026_split_v1"),
        "routing_policy_version": ROUTING_POLICY_VERSION,
        "rq10_primary_class": row.get("rq10_primary_class"),
        "review_bucket": bucket,
        "routing_action": action,
        "prediction_blocked_pending_review_or_abstention": action
        in PREDICTION_BLOCKING_ACTIONS,
        "hidden_families": list(row.get("hidden_families") or []),
        "evidence_contract": {
            "selected_evidence": row.get("selected_evidence"),
            "selected_evidence_exact": bool(row.get("selected_evidence_exact")),
            "selected_source_ids_valid": bool(row.get("selected_source_ids_valid")),
        },
        "review_packet": {
            "selected_evidence": row.get("selected_evidence"),
            "system_prediction": predicted_label,
            "routing_action": action,
            "review_bucket": bucket,
            "hidden_families": list(row.get("hidden_families") or []),
            "first_failure_owner": row.get("first_failure_owner"),
            "first_failure_reason": row.get("first_failure_reason"),
            "adjudication_rationale": row.get("adjudication_rationale"),
        },
        "development_accounting": {
            "gold_label": row.get("gold_label"),
            "gold_reference": row.get("gold_reference"),
            "primary_predicted_label": predicted_label,
            "primary_purist_correct": bool(row.get("primary_purist_correct")),
            "primary_pragmatic_correct": bool(row.get("primary_pragmatic_correct")),
            "clinically_defensible_alternative": bool(
                row.get("clinically_defensible_alternative")
            ),
            "benchmark_convention_flag": bool(row.get("benchmark_convention_flag")),
            "possible_gold_weakness": bool(row.get("possible_gold_weakness")),
            "likely_gold_defect": bool(row.get("likely_gold_defect")),
        },
    }


def _review_bucket(row: Mapping[str, Any]) -> str:
    if row.get("likely_gold_defect") or row.get("possible_gold_weakness"):
        return "possible_gold_weakness"
    if row.get("clinically_defensible_alternative"):
        return "clinically_defensible_alternative"
    primary_class = str(row.get("rq10_primary_class") or "")
    if primary_class in ACTION_BY_BUCKET:
        return primary_class
    return "true_extraction_failure"


def _hidden_family_summary(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, int]]:
    by_family: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        families = row["hidden_families"] or ["unclassified"]
        for family in families:
            by_family[str(family)]["rows"] += 1
            by_family[str(family)][row["review_bucket"]] += 1
    return {family: dict(counts) for family, counts in sorted(by_family.items())}


def _rq10_metric(rq10_summary: Mapping[str, Any] | None, key: str) -> Any:
    if not rq10_summary:
        return None
    return (rq10_summary.get("metrics") or {}).get(key)


def _safe_rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _format_metric(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rq10-jsonl-path", type=Path, default=DEFAULT_RQ10_JSONL_PATH)
    parser.add_argument("--rq10-json-path", type=Path, default=DEFAULT_RQ10_JSON_PATH)
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    rq10_rows = load_jsonl_rows(args.rq10_jsonl_path)
    rq10_summary = _load_json(args.rq10_json_path) if args.rq10_json_path.exists() else None
    rows, metadata = build_rq9_predeclaration_rows(rq10_rows, rq10_summary=rq10_summary)
    metadata = {
        **metadata,
        "source_artifact": str(args.rq10_jsonl_path),
        "source_summary": str(args.rq10_json_path),
    }
    write_jsonl_rows(rows, args.jsonl_path)
    write_rq9_predeclaration_json(metadata, args.json_path)
    write_rq9_predeclaration_report(metadata, args.report_path, jsonl_path=args.jsonl_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
