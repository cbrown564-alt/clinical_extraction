"""Build deterministic verification-route reports from projection score artifacts."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.verification_route import (
    ROUTE_POLICY_ID,
    SCHEMA_VERSION,
    VerificationRouteDecision,
    VerificationRouteFamily,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

DEFAULT_SCORE_JSONL_PATH = Path(
    "experiments/gan2026_clinical_assessment_projection_score_validation250_v0.jsonl"
)
DEFAULT_JSONL_PATH = Path("experiments/gan2026_validation250_verification_route_v0.jsonl")
DEFAULT_JSON_PATH = Path("experiments/gan2026_validation250_verification_route_v0.json")
DEFAULT_REPORT_PATH = Path("experiments/gan2026_validation250_verification_route_v0.md")


def build_verification_route_artifact(
    score_rows: Sequence[Mapping[str, Any]],
    *,
    score_artifact_path: str = str(DEFAULT_SCORE_JSONL_PATH),
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = [build_verification_route_row(row) for row in score_rows]
    return rows, summarize_rows(rows, score_artifact_path=score_artifact_path)


def build_verification_route_row(score_row: Mapping[str, Any]) -> dict[str, Any]:
    source_row_index = int(score_row["source_row_index"])
    projection = dict(score_row.get("projection_decision") or {})
    rendered = dict(score_row.get("final_rendered_label") or {})
    score = dict(score_row.get("score") or {})
    route = route_decision_for_row(
        source_row_index=source_row_index,
        projection_decision=projection,
        final_rendered_label=rendered,
        score=score,
    )
    return {
        "artifact_kind": "gan2026_verification_route_row",
        "source_row_index": source_row_index,
        "split": score_row.get("split", "validation"),
        "split_manifest": score_row.get("split_manifest", "gan2026_split_v1"),
        "schema_version": SCHEMA_VERSION,
        "route_policy_id": ROUTE_POLICY_ID,
        "claim_boundary": (
            "deterministic verification-route mechanics over saved validation250 "
            "score rows; no verifier model call, manual annotation, action decision, "
            "or benchmark-comparable claim"
        ),
        "source_artifacts": {
            "scoring_policy_id": score_row.get("scoring_policy_id"),
            "projection_policy_id": (score_row.get("source_artifacts") or {}).get(
                "projection_policy_id"
            ),
            "render_policy_id": (score_row.get("source_artifacts") or {}).get(
                "render_policy_id"
            ),
        },
        "projection_decision": projection or None,
        "final_rendered_label": rendered or None,
        "score_context": route.score_context,
        "verification_route": route.model_dump(),
    }


def route_decision_for_row(
    *,
    source_row_index: int,
    projection_decision: Mapping[str, Any],
    final_rendered_label: Mapping[str, Any],
    score: Mapping[str, Any],
) -> VerificationRouteDecision:
    projection_kind = str(projection_decision.get("projection_kind") or "")
    aggregation_policy = str(projection_decision.get("source_aggregation_policy") or "")
    projection_basis = str(projection_decision.get("projection_basis") or "")
    source_candidate_ids = list(projection_decision.get("source_candidate_ids") or [])
    projection_issues = [str(issue) for issue in projection_decision.get("projection_issues") or []]
    render_issues = [str(issue) for issue in final_rendered_label.get("render_issues") or []]
    rendered_label = final_rendered_label.get("rendered_label")
    issue_set = {*projection_issues, *render_issues}

    families: list[VerificationRouteFamily] = []
    reasons: list[str] = []

    if _has_seizure_free_conflict(issue_set):
        families.append("seizure_free_conflict")
        reasons.append("seizure_free conflict issue present")

    if "seizure_free_proxy_evidence_overreach" in issue_set:
        families.append("seizure_free_proxy_evidence_overreach")
        reasons.append(
            "seizure-free projection is based on proxy or conditional evidence"
        )

    if "medication_cadence_ambiguity" in issue_set:
        families.append("medication_cadence_ambiguity")
        reasons.append(
            "cadence evidence may describe medication or rescue use rather than events"
        )
    elif "cyclic_window_without_event_count" in issue_set:
        families.append("cyclic_window_without_event_count")
        reasons.append(
            "cyclic vulnerability window is present without event count or burden"
        )
    elif (
        projection_kind == "cluster_frequency"
        and rendered_label is None
        and projection_basis == "cluster_frequency"
        and (
        "cluster_frequency_operands_unparsed" in issue_set
        or "cluster_cadence_operands_incomplete" in issue_set
        )
    ):
        families.append("cluster_axis_ambiguity")
        reasons.append("cluster projection has unparsed or incomplete cluster-axis operands")

    if (
        rendered_label is None
        and aggregation_policy == "additive_same_window"
        and (
        "additive_frequency_period_mismatch" in issue_set
        or "vague_count" in issue_set
        or "frequency_rate_operands_incomplete" in issue_set
        )
    ):
        families.append("mixed_window_or_vague_addition")
        reasons.append("additive assessment includes mixed-window, vague, or incomplete operands")

    if (
        "seizure_free_proxy_evidence_overreach" not in issue_set
        and len(source_candidate_ids) > 1
        and aggregation_policy not in {
            "additive_same_window",
            "cluster_axis",
        }
    ):
        families.append("multiple_current_primary_facts")
        reasons.append(
            "multiple primary candidate ids are present outside an additive "
            "or cluster-axis policy"
        )

    if (
        projection_kind == "unknown_frequency"
        and aggregation_policy == "unknown_due_to_ambiguity"
        and rendered_label == "unknown"
    ):
        families.append("rendered_label_supported_but_policy_sensitive")
        reasons.append("unknown label rendered from explicit ambiguity rather than absence")

    if (
        rendered_label is not None
        and "prior_encounter_derived_seizure_free_duration" in issue_set
    ):
        families.append("rendered_label_supported_but_policy_sensitive")
        reasons.append(
            "seizure-free duration was derived from prior-encounter context"
        )

    families = _dedupe(families)
    reasons = _dedupe(reasons)
    return VerificationRouteDecision(
        source_row_index=source_row_index,
        component_owner="verification_route",
        routed=bool(families),
        route_families=families,
        route_reasons=reasons,
        route_evidence={
            "projection_kind": projection_kind or None,
            "source_aggregation_policy": aggregation_policy or None,
            "projection_basis": projection_basis or None,
            "source_candidate_ids": source_candidate_ids,
            "projection_issues": projection_issues,
            "render_issues": render_issues,
            "rendered_label_present": rendered_label is not None,
        },
        score_context={
            "score_status": score.get("score_status"),
            "purist_correct": score.get("purist_correct"),
            "pragmatic_correct": score.get("pragmatic_correct"),
            "exact_normalized_label_match": score.get("exact_normalized_label_match"),
            "rendered_label": score.get("rendered_label"),
            "gold_label": score.get("gold_label"),
            "predicted_purist_category": score.get("predicted_purist_category"),
            "gold_purist_category": score.get("gold_purist_category"),
        },
    )


def summarize_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    score_artifact_path: str = str(DEFAULT_SCORE_JSONL_PATH),
) -> dict[str, Any]:
    route_objects = [row["verification_route"] for row in rows]
    routed = [route for route in route_objects if route["routed"]]
    family_counts = Counter(
        family for route in route_objects for family in route.get("route_families") or []
    )
    status_counts = Counter(
        str((row.get("score_context") or {}).get("score_status"))
        for row in rows
        if row.get("score_context")
    )
    routed_status_counts = Counter(
        str((row.get("score_context") or {}).get("score_status"))
        for row in rows
        if (row.get("verification_route") or {}).get("routed")
    )
    surface_label = f"validation{len(rows)}"
    return {
        "artifact_kind": "gan2026_verification_route",
        "schema_version": SCHEMA_VERSION,
        "route_policy_id": ROUTE_POLICY_ID,
        "score_artifact_path": score_artifact_path,
        "row_count": len(rows),
        "claim_boundary": (
            f"Deterministic {surface_label} verification-route mechanics only. "
            "Routes use predeclared clinical/projection risk predicates over "
            "structured projection/render fields; score fields are audit context "
            "only and no verifier action is emitted."
        ),
        "summary": {
            "routed_rows": len(routed),
            "unrouted_rows": len(rows) - len(routed),
            "route_family_counts": dict(sorted(family_counts.items())),
            "score_status_counts": dict(sorted(status_counts.items())),
            "routed_score_status_counts": dict(sorted(routed_status_counts.items())),
            "routed_source_row_indices": [
                int(route["source_row_index"]) for route in routed
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
        "# Gan 2026 Verification Route Mechanics",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Artifacts",
        "",
        f"- Route JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        f"- Score source: `{metadata['score_artifact_path']}`",
        "",
        "## Summary",
        "",
        f"- Rows: {metadata['row_count']}",
        f"- Routed rows: {summary['routed_rows']}",
        f"- Unrouted rows: {summary['unrouted_rows']}",
        "",
        "## Route Families",
        "",
    ]
    if not summary["route_family_counts"]:
        lines.append("- None.")
    for family, count in summary["route_family_counts"].items():
        lines.append(f"- `{family}`: {count}")
    lines.extend(["", "## Routed Score Statuses", ""])
    if not summary["routed_score_status_counts"]:
        lines.append("- None.")
    for status, count in summary["routed_score_status_counts"].items():
        lines.append(f"- `{status}`: {count}")
    lines.extend(["", "## Routed Rows", ""])
    routed_rows = [
        row for row in rows if (row.get("verification_route") or {}).get("routed")
    ][:25]
    if not routed_rows:
        lines.append("- None.")
    for row in routed_rows:
        route = row["verification_route"]
        score = row.get("score_context") or {}
        lines.append(
            f"- {row['source_row_index']}: "
            f"{', '.join(route.get('route_families') or [])}; "
            f"score `{score.get('score_status')}`; "
            f"purist `{score.get('purist_correct')}`; "
            f"reasons: {'; '.join(route.get('route_reasons') or [])}"
        )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _has_seizure_free_conflict(issues: set[str]) -> bool:
    return any(
        token in issue
        for issue in issues
        for token in (
            "seizure_free_conflict",
            "active_event_conflict",
            "breakthrough_event",
            "event_scope_conflict",
        )
    )


def _dedupe(values: Sequence[Any]) -> list[Any]:
    seen: set[Any] = set()
    deduped: list[Any] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        deduped.append(value)
    return deduped


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--score-jsonl", type=Path, default=DEFAULT_SCORE_JSONL_PATH)
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    rows, metadata = build_verification_route_artifact(
        load_jsonl_rows(args.score_jsonl),
        score_artifact_path=str(args.score_jsonl),
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
