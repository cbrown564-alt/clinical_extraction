"""Build deterministic verification-action reports from route artifacts."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.verification_decision import (
    SCHEMA_VERSION,
    VERIFICATION_POLICY_ID,
    VerificationDecision,
    VerifierAction,
    VerifierActionBasis,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

DEFAULT_ROUTE_JSONL_PATH = Path("experiments/gan2026_validation250_verification_route_v6.jsonl")
DEFAULT_JSONL_PATH = Path("experiments/gan2026_validation250_verification_decision_v0.jsonl")
DEFAULT_JSON_PATH = Path("experiments/gan2026_validation250_verification_decision_v0.json")
DEFAULT_REPORT_PATH = Path("experiments/gan2026_validation250_verification_decision_v0.md")

CLAIM_BOUNDARY = (
    "deterministic verification-action baseline over routed rows; no verifier "
    "model call, no manual annotation, no replacement label invention, and score "
    "context is audit-only"
)


def build_verification_decision_artifact(
    route_rows: Sequence[Mapping[str, Any]],
    *,
    route_artifact_path: str = str(DEFAULT_ROUTE_JSONL_PATH),
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = [
        build_verification_decision_row(row)
        for row in route_rows
        if (row.get("verification_route") or {}).get("routed")
    ]
    return rows, summarize_rows(
        rows,
        route_rows=route_rows,
        route_artifact_path=route_artifact_path,
    )


def build_verification_decision_row(route_row: Mapping[str, Any]) -> dict[str, Any]:
    route = dict(route_row["verification_route"])
    rendered = dict(route_row.get("final_rendered_label") or {})
    score_context = dict(route_row.get("score_context") or route.get("score_context") or {})
    proposed_rendered_label = rendered.get("rendered_label")
    decision = decision_for_route(
        source_row_index=int(route["source_row_index"]),
        route_families=[str(family) for family in route.get("route_families") or []],
        route_reasons=[str(reason) for reason in route.get("route_reasons") or []],
        source_route_policy_id=str(route.get("route_policy_id") or ""),
        proposed_rendered_label=(
            str(proposed_rendered_label) if proposed_rendered_label is not None else None
        ),
        score_context=score_context,
    )
    return {
        "artifact_kind": "gan2026_verification_decision_row",
        "source_row_index": int(route_row["source_row_index"]),
        "split": route_row.get("split", "validation"),
        "split_manifest": route_row.get("split_manifest", "gan2026_split_v1"),
        "schema_version": SCHEMA_VERSION,
        "verification_policy_id": VERIFICATION_POLICY_ID,
        "claim_boundary": CLAIM_BOUNDARY,
        "source_artifacts": {
            "route_policy_id": route.get("route_policy_id"),
            "route_schema_version": route.get("schema_version"),
            **dict(route_row.get("source_artifacts") or {}),
        },
        "verification_route": route,
        "verification_decision": decision.model_dump(),
    }


def decision_for_route(
    *,
    source_row_index: int,
    route_families: Sequence[str],
    route_reasons: Sequence[str],
    source_route_policy_id: str,
    proposed_rendered_label: str | None,
    score_context: Mapping[str, Any] | None = None,
) -> VerificationDecision:
    action, basis, reason = _action_for_route_families(
        route_families,
        proposed_rendered_label=proposed_rendered_label,
    )
    final_rendered_label = proposed_rendered_label if action == "affirm" else None
    return VerificationDecision(
        source_row_index=source_row_index,
        component_owner="verification_decision",
        source_route_policy_id=source_route_policy_id,
        route_families=list(route_families),
        route_reasons=list(route_reasons),
        action=action,
        action_reason=reason,
        action_basis=basis,
        proposed_rendered_label=proposed_rendered_label,
        final_rendered_label=final_rendered_label,
        score_context=dict(score_context or {}),
        claim_boundary=CLAIM_BOUNDARY,
    )


def _action_for_route_families(
    route_families: Sequence[str],
    *,
    proposed_rendered_label: str | None,
) -> tuple[VerifierAction, VerifierActionBasis, str]:
    family_set = set(route_families)
    if "seizure_free_proxy_evidence_overreach" in family_set and proposed_rendered_label:
        return (
            "reject",
            "proposed_outcome_block",
            "block proposed seizure-free rendering based on proxy or conditional evidence",
        )
    if "medication_cadence_ambiguity" in family_set:
        return (
            "human_review",
            "manual_review_required",
            "cadence may describe medication or rescue use rather than event occurrence",
        )
    if "cyclic_window_without_event_count" in family_set:
        return (
            "abstain",
            "route_family_policy",
            "cyclic vulnerability window lacks event count or burden for automated projection",
        )
    if "seizure_free_proxy_evidence_overreach" in family_set:
        return (
            "abstain",
            "route_family_policy",
            "proxy-only seizure-free evidence has no safe automated replacement label",
        )
    return (
        "abstain",
        "route_family_policy",
        "routed risk family has no deterministic V0 action beyond abstention",
    )


def summarize_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    route_rows: Sequence[Mapping[str, Any]],
    route_artifact_path: str = str(DEFAULT_ROUTE_JSONL_PATH),
) -> dict[str, Any]:
    decisions = [row["verification_decision"] for row in rows]
    action_counts = Counter(decision["action"] for decision in decisions)
    family_counts = Counter(
        family for decision in decisions for family in decision.get("route_families") or []
    )
    basis_counts = Counter(decision["action_basis"] for decision in decisions)
    routed_count = sum(
        1 for row in route_rows if (row.get("verification_route") or {}).get("routed")
    )
    return {
        "artifact_kind": "gan2026_verification_decision",
        "schema_version": SCHEMA_VERSION,
        "verification_policy_id": VERIFICATION_POLICY_ID,
        "route_artifact_path": route_artifact_path,
        "row_count": len(rows),
        "claim_boundary": CLAIM_BOUNDARY,
        "summary": {
            "input_route_rows": len(route_rows),
            "input_routed_rows": routed_count,
            "decision_rows": len(rows),
            "action_counts": dict(sorted(action_counts.items())),
            "action_basis_counts": dict(sorted(basis_counts.items())),
            "route_family_counts": dict(sorted(family_counts.items())),
            "decision_source_row_indices": [
                int(row["source_row_index"]) for row in rows
            ][:50],
        },
    }


def write_summary_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_report(
    metadata: Mapping[str, Any],
    rows: Sequence[Mapping[str, Any]],
    path: Path,
    *,
    jsonl_path: Path = DEFAULT_JSONL_PATH,
    json_path: Path = DEFAULT_JSON_PATH,
) -> None:
    summary = metadata["summary"]
    lines = [
        "# Gan 2026 VerificationDecision V0 Baseline",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Artifacts",
        "",
        f"- Decision JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        f"- Route source: `{metadata['route_artifact_path']}`",
        "",
        "## Summary",
        "",
        f"- Input route rows: {summary['input_route_rows']}",
        f"- Input routed rows: {summary['input_routed_rows']}",
        f"- Decision rows: {summary['decision_rows']}",
        "",
        "## Actions",
        "",
    ]
    if not summary["action_counts"]:
        lines.append("- None.")
    for action, count in summary["action_counts"].items():
        lines.append(f"- `{action}`: {count}")
    lines.extend(["", "## Route Families", ""])
    if not summary["route_family_counts"]:
        lines.append("- None.")
    for family, count in summary["route_family_counts"].items():
        lines.append(f"- `{family}`: {count}")
    lines.extend(["", "## Decision Rows", ""])
    if not rows:
        lines.append("- None.")
    for row in rows[:25]:
        decision = row["verification_decision"]
        lines.append(
            f"- {row['source_row_index']}: `{decision['action']}`; "
            f"basis `{decision['action_basis']}`; "
            f"families: {', '.join(decision.get('route_families') or [])}; "
            f"reason: {decision['action_reason']}"
        )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--route-jsonl", type=Path, default=DEFAULT_ROUTE_JSONL_PATH)
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    rows, metadata = build_verification_decision_artifact(
        load_jsonl_rows(args.route_jsonl),
        route_artifact_path=str(args.route_jsonl),
    )
    write_jsonl_rows(rows, args.jsonl_path)
    write_summary_json(metadata, args.json_path)
    write_report(
        metadata,
        rows,
        args.report_path,
        jsonl_path=args.jsonl_path,
        json_path=args.json_path,
    )
    print(json.dumps(metadata["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
