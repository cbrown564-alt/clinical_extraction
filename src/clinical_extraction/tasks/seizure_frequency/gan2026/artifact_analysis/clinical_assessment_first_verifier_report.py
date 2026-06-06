"""Materialize the first saved verifier comparison packet for Gan 2026 V6."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

DEFAULT_ROUTE_JSONL_PATH = Path(
    "experiments/gan2026_validation750_verification_route_gpt41mini_context_repair_v6_2026-06-06.jsonl"
)
DEFAULT_DECISION_JSONL_PATH = Path(
    "experiments/gan2026_validation750_verification_decision_gpt41mini_context_repair_v6_2026-06-06.jsonl"
)
DEFAULT_ASSESSMENT_JSONL_PATH = Path(
    "experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation750_gpt41mini_v3nested_v3_2026-06-06.jsonl"
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_validation750_first_verifier_saved_comparison_context_repair_v6_2026-06-06.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_validation750_first_verifier_saved_comparison_context_repair_v6_2026-06-06.json"
)
DEFAULT_REPORT_PATH = Path(
    "docs/research/gan2026_validation750_first_verifier_saved_comparison_context_repair_v6_2026-06-06.md"
)
DEFAULT_EXPERIMENT_INPUT_JSONL_PATH = Path(
    "experiments/gan2026_validation750_first_verifier_experiment_input_clean29_context_repair_v6_2026-06-06.jsonl"
)
DEFAULT_EXPERIMENT_INPUT_JSON_PATH = Path(
    "experiments/gan2026_validation750_first_verifier_experiment_input_clean29_context_repair_v6_2026-06-06.json"
)
DEFAULT_EXPERIMENT_INPUT_REPORT_PATH = Path(
    "docs/research/gan2026_validation750_first_verifier_experiment_input_clean29_context_repair_v6_2026-06-06.md"
)

CLAIM_BOUNDARY = (
    "saved validation-development verifier comparison packet only; no live verifier "
    "model call, no locked-test inspection, no benchmark-comparable claim, and no "
    "replacement scorer-facing label generation are authorized"
)
PROVENANCE_FAMILIES = {
    "selected_evidence_missing_exact_trace",
    "selected_source_id_invalid",
}
MAIN_AMBIGUITY_FAMILIES = {"mixed_window_or_vague_addition"}
ABSTAIN_EXEMPLAR_FAMILIES = {
    "relative_only_trend",
    "conditional_only_trigger",
    "seizure_free_proxy_evidence_overreach",
}
UPSTREAM_POLICY_FAMILIES = {
    "cluster_axis_ambiguity",
    "cyclic_window_without_event_count",
}
RENDERED_POLICY_FAMILIES = {
    "unresolved_cluster_cadence_with_per_cluster_burden",
    "rendered_label_supported_but_policy_sensitive",
}
ALLOWED_ACTIONS = ["affirm", "reject", "abstain", "human_review"]
VERIFIER_OUTPUT_SCHEMA = {
    "source_row_index": "Integer row id copied from the input case.",
    "component_owner": "Must be llm_verifier.",
    "schema_version": "Verifier output schema identifier.",
    "verifier_policy_id": "Named verifier policy or prompt identifier.",
    "baseline_action": ALLOWED_ACTIONS,
    "action": ALLOWED_ACTIONS,
    "action_basis": "Short action basis string.",
    "cited_candidate_ids": ["Candidate ids cited from the provided row-local evidence."],
    "cited_source_ids": ["Source ids or spans cited from the provided row-local evidence."],
    "issue_flags": ["Verifier issue flags grounded in the provided row-local evidence."],
    "rationale": "Brief evidence-grounded rationale.",
    "proposed_rendered_label": "Nullable copy of the proposed rendered label from input.",
    "final_rendered_label": (
        "Null for the first experiment unless a later policy explicitly authorizes it."
    ),
    "replacement_rendered_label": "Null for the first experiment.",
}
VERIFIER_SYSTEM_PROMPT = (
    "Review a routed seizure-frequency verification case using only the provided "
    "row-local evidence packet. Decide whether to affirm, reject, abstain, or send "
    "to human_review. Do not invent a new scorer-facing label, do not use gold or "
    "score outcomes, and cite only provided candidate ids and source ids."
)


def build_first_verifier_report_rows(
    route_rows: Sequence[Mapping[str, Any]],
    decision_rows: Sequence[Mapping[str, Any]],
    assessment_rows: Sequence[Mapping[str, Any]],
    *,
    route_artifact_path: str = str(DEFAULT_ROUTE_JSONL_PATH),
    decision_artifact_path: str = str(DEFAULT_DECISION_JSONL_PATH),
    assessment_artifact_path: str = str(DEFAULT_ASSESSMENT_JSONL_PATH),
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    decisions_by_row = _rows_by_source_index(decision_rows)
    assessments_by_row = _rows_by_source_index(assessment_rows)
    rows = []
    for route_row in route_rows:
        route = dict(route_row.get("verification_route") or {})
        if not route.get("routed"):
            continue
        source_row_index = int(route_row["source_row_index"])
        decision_row = decisions_by_row.get(source_row_index)
        if decision_row is None:
            raise ValueError(f"Missing verification decision row for {source_row_index}")
        assessment_row = assessments_by_row.get(source_row_index, {})
        rows.append(
            _build_first_verifier_row(
                route_row,
                decision_row,
                assessment_row,
            )
        )
    rows.sort(key=lambda row: int(row["source_row_index"]))
    return rows, summarize_first_verifier_report_rows(
        rows,
        route_artifact_path=route_artifact_path,
        decision_artifact_path=decision_artifact_path,
        assessment_artifact_path=assessment_artifact_path,
    )


def summarize_first_verifier_report_rows(
    rows: Sequence[Mapping[str, Any]],
    *,
    route_artifact_path: str,
    decision_artifact_path: str,
    assessment_artifact_path: str,
) -> dict[str, Any]:
    bucket_counts = Counter(str(row["route_bucket"]) for row in rows)
    section_counts = Counter(str(row["report_section"]) for row in rows)
    non_provenance_counts = Counter(
        str(row["non_provenance_route_family"])
        for row in rows
        if row.get("non_provenance_route_family")
    )
    clinical_policy_rows = [
        row for row in rows if row["route_bucket"] != "provenance_only_audit"
    ]
    rows_with_sidecar = [
        row for row in clinical_policy_rows if row["provenance_sidecar_present"]
    ]
    rows_without_sidecar = [
        row for row in clinical_policy_rows if not row["provenance_sidecar_present"]
    ]
    return {
        "artifact_kind": "gan2026_first_verifier_saved_comparison",
        "claim_boundary": CLAIM_BOUNDARY,
        "date": "2026-06-06",
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "route_artifact_path": route_artifact_path,
        "decision_artifact_path": decision_artifact_path,
        "assessment_artifact_path": assessment_artifact_path,
        "row_count": len(rows),
        "metrics": {
            "total_routed_rows": len(rows),
            "clinical_policy_rows": len(clinical_policy_rows),
            "clinical_policy_rows_with_provenance_sidecar": len(rows_with_sidecar),
            "clinical_policy_rows_without_provenance_sidecar": len(rows_without_sidecar),
            "main_ambiguity_rows": bucket_counts["verifier_eligible_ambiguity"],
            "abstain_exemplar_rows": bucket_counts["abstain_exemplar"],
            "upstream_policy_rows": bucket_counts["upstream_policy_appendix"],
            "rendered_policy_sensitive_rows": bucket_counts["rendered_policy_sensitive_appendix"],
            "provenance_only_rows": bucket_counts["provenance_only_audit"],
        },
        "bucket_counts": dict(sorted(bucket_counts.items())),
        "report_section_counts": dict(sorted(section_counts.items())),
        "non_provenance_route_family_counts": dict(sorted(non_provenance_counts.items())),
        "decision": (
            "first_verifier_saved_comparison_ready"
            if bucket_counts["verifier_eligible_ambiguity"] == 29
            and bucket_counts["abstain_exemplar"] == 4
            and bucket_counts["upstream_policy_appendix"] == 18
            and bucket_counts["rendered_policy_sensitive_appendix"] == 5
            and bucket_counts["provenance_only_audit"] == 220
            else "first_verifier_saved_comparison_shape_mismatch"
        ),
    }


def write_summary_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_report(
    rows: Sequence[Mapping[str, Any]],
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path = DEFAULT_JSONL_PATH,
    json_path: Path = DEFAULT_JSON_PATH,
) -> None:
    metrics = metadata["metrics"]
    lines = [
        "# Gan 2026 Validation750 First Verifier Saved Comparison V6",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Decision",
        "",
        (
            "Prepared the predeclared saved verifier comparison packet over the V6 "
            "routed surface. The first score table remains the 29-row ambiguity set, "
            "with abstain, upstream-policy, rendered-policy, and provenance-only rows "
            "kept in separate appendices."
        ),
        "",
        "## Artifacts",
        "",
        f"- Row JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        f"- Route source: `{metadata['route_artifact_path']}`",
        f"- Decision source: `{metadata['decision_artifact_path']}`",
        f"- Assessment source: `{metadata['assessment_artifact_path']}`",
        "",
        "## Bucket Counts",
        "",
        "| Bucket | Rows |",
        "| --- | ---: |",
        f"| Main ambiguity score table | {metrics['main_ambiguity_rows']} |",
        f"| Abstain appendix | {metrics['abstain_exemplar_rows']} |",
        f"| Upstream-policy appendix | {metrics['upstream_policy_rows']} |",
        f"| Rendered policy-sensitive appendix | {metrics['rendered_policy_sensitive_rows']} |",
        f"| Provenance-only audit appendix | {metrics['provenance_only_rows']} |",
        "",
        "## Provenance Sidecars",
        "",
        f"- Clinical/policy rows: {metrics['clinical_policy_rows']}",
        f"- With provenance sidecar: {metrics['clinical_policy_rows_with_provenance_sidecar']}",
        (
            "- Without provenance sidecar: "
            f"{metrics['clinical_policy_rows_without_provenance_sidecar']}"
        ),
        "",
        "## Main Score Table Rows",
        "",
        "| Row | Sidecar | Rendered label | Projection basis | Score status |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for row in rows:
        if row["route_bucket"] != "verifier_eligible_ambiguity":
            continue
        lines.append(
            f"| {row['source_row_index']} | "
            f"{'present' if row['provenance_sidecar_present'] else 'absent'} | "
            f"{row['rendered_label'] or 'null'} | "
            f"`{row['projection_basis']}` | "
            f"`{row['score_status']}` |"
        )
    lines.extend(
        [
            "",
            "## Packet Contract",
            "",
            "Each saved row packet includes:",
            "",
            "- deterministic `VerificationDecision` V0 baseline action and reasons",
            "- embedded `Verification Route` with route families, reasons, and route evidence",
            "- clinical-assessment state",
            "- projection/render state",
            "- row-local candidate evidence texts, candidate ids, and source ids",
            "- visible provenance sidecars when present on clinical/policy rows",
            "",
            "The model-visible packet excludes gold labels, correctness fields, and other "
            "score-derived hints.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_clean_first_verifier_experiment_input(
    rows: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Build the first verifier experiment surface without provenance-only rows."""

    included_rows = [
        {
            "artifact_kind": "gan2026_first_verifier_clean_experiment_input_row",
            "source_row_index": int(row["source_row_index"]),
            "split": row.get("split", "validation"),
            "split_manifest": row.get("split_manifest", "gan2026_split_v1"),
            "route_bucket": row["route_bucket"],
            "report_section": row["report_section"],
            "provenance_sidecar_present": row["provenance_sidecar_present"],
            "provenance_sidecar_families": list(
                row.get("provenance_sidecar_families") or []
            ),
            "verifier_model_input": row["verifier_model_input"],
            "appendix_policy": {
                "main_score_table": row["route_bucket"] == "verifier_eligible_ambiguity",
                "appendix_only": row["route_bucket"] != "verifier_eligible_ambiguity",
            },
        }
        for row in rows
        if row.get("route_bucket") != "provenance_only_audit"
    ]
    included_rows.sort(key=lambda row: int(row["source_row_index"]))
    bucket_counts = Counter(str(row["route_bucket"]) for row in included_rows)
    return included_rows, {
        "artifact_kind": "gan2026_first_verifier_clean_experiment_input",
        "claim_boundary": (
            "First verifier experiment input surface only: 29-row ambiguity core "
            "plus abstain/upstream-policy/rendered-policy appendices. Provenance-only "
            "audit rows, gold labels, correctness fields, and audit W->C/C->W counts "
            "are excluded from verifier-visible inputs."
        ),
        "date": "2026-06-06",
        "split": "validation",
        "split_manifest": "gan2026_split_v1",
        "row_count": len(included_rows),
        "metrics": {
            "main_ambiguity_rows": bucket_counts["verifier_eligible_ambiguity"],
            "abstain_appendix_rows": bucket_counts["abstain_exemplar"],
            "upstream_policy_appendix_rows": bucket_counts["upstream_policy_appendix"],
            "rendered_policy_sensitive_appendix_rows": bucket_counts[
                "rendered_policy_sensitive_appendix"
            ],
            "provenance_only_rows_excluded": sum(
                1 for row in rows if row.get("route_bucket") == "provenance_only_audit"
            ),
        },
        "decision": (
            "ready_for_first_verifier_run"
            if bucket_counts["verifier_eligible_ambiguity"] == 29
            and bucket_counts["abstain_exemplar"] == 4
            and bucket_counts["upstream_policy_appendix"] == 18
            and bucket_counts["rendered_policy_sensitive_appendix"] == 5
            else "shape_mismatch_do_not_run"
        ),
    }


def write_clean_experiment_input_report(
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path = DEFAULT_EXPERIMENT_INPUT_JSONL_PATH,
    json_path: Path = DEFAULT_EXPERIMENT_INPUT_JSON_PATH,
) -> None:
    metrics = metadata["metrics"]
    lines = [
        "# Gan 2026 Validation750 First Verifier Experiment Input Clean29 V6",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Decision",
        "",
        f"`{metadata['decision']}`",
        "",
        "## Artifacts",
        "",
        f"- Row JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        "",
        "## Surface",
        "",
        "| Section | Rows |",
        "| --- | ---: |",
        f"| Main ambiguity core | {metrics['main_ambiguity_rows']} |",
        f"| Abstain appendix | {metrics['abstain_appendix_rows']} |",
        f"| Upstream-policy appendix | {metrics['upstream_policy_appendix_rows']} |",
        (
            "| Rendered policy-sensitive appendix | "
            f"{metrics['rendered_policy_sensitive_appendix_rows']} |"
        ),
        f"| Provenance-only audit rows excluded | {metrics['provenance_only_rows_excluded']} |",
        "",
        "## Input Hygiene",
        "",
        "Verifier-visible packets contain route, assessment, projection/render, "
        "candidate evidence, and provenance sidecars only. Gold labels, score "
        "correctness fields, and audit-only W->C/C->W counts are deliberately absent.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _build_first_verifier_row(
    route_row: Mapping[str, Any],
    decision_row: Mapping[str, Any],
    assessment_row: Mapping[str, Any],
) -> dict[str, Any]:
    route = dict(route_row.get("verification_route") or {})
    route_evidence = dict(route.get("route_evidence") or {})
    decision = dict(decision_row.get("verification_decision") or {})
    projection = dict(route_row.get("projection_decision") or {})
    rendered = dict(route_row.get("final_rendered_label") or {})
    clinical_assessment = dict(
        assessment_row.get("clinical_assessment") or route_row.get("clinical_assessment") or {}
    )
    route_families = [str(family) for family in route.get("route_families") or []]
    provenance_families = [f for f in route_families if f in PROVENANCE_FAMILIES]
    non_provenance_families = [f for f in route_families if f not in PROVENANCE_FAMILIES]
    route_bucket, report_section = _route_bucket(non_provenance_families)
    non_provenance_route_family = (
        non_provenance_families[0] if non_provenance_families else None
    )
    candidate_packets = _candidate_packets(assessment_row)
    verifier_model_input = _verifier_model_input(
        source_row_index=int(route_row["source_row_index"]),
        route=route,
        decision=decision,
        projection=projection,
        rendered=rendered,
        clinical_assessment=clinical_assessment,
        candidate_packets=candidate_packets,
        provenance_families=provenance_families,
    )
    score_context = dict(route.get("score_context") or {})
    return {
        "artifact_kind": "gan2026_first_verifier_saved_comparison_row",
        "claim_boundary": CLAIM_BOUNDARY,
        "source_row_index": int(route_row["source_row_index"]),
        "split": route_row.get("split", "validation"),
        "split_manifest": route_row.get("split_manifest", "gan2026_split_v1"),
        "route_bucket": route_bucket,
        "report_section": report_section,
        "non_provenance_route_family": non_provenance_route_family,
        "non_provenance_route_families": non_provenance_families,
        "provenance_sidecar_present": bool(provenance_families),
        "provenance_sidecar_families": provenance_families,
        "rendered_label": rendered.get("rendered_label"),
        "normalized_source_phrase": route_evidence.get("source_normalized_phrase"),
        "projection_basis": route_evidence.get("projection_basis"),
        "score_status": score_context.get("score_status"),
        "verification_decision_v0": {
            "action": decision.get("action"),
            "action_basis": decision.get("action_basis"),
            "action_reason": decision.get("action_reason"),
            "proposed_rendered_label": decision.get("proposed_rendered_label"),
        },
        "verifier_model_input": verifier_model_input,
        "post_run_accounting_contract": {
            "compare_actions_against_v0": True,
            "main_score_table_uses_only_verifier_eligible_ambiguity_bucket": True,
            "keep_provenance_only_rows_out_of_primary_score_table": True,
            "report_score_context_only_outside_model_input": True,
        },
        "development_accounting": {
            "gold_label": score_context.get("gold_label"),
            "purist_correct": score_context.get("purist_correct"),
            "pragmatic_correct": score_context.get("pragmatic_correct"),
            "exact_normalized_label_match": score_context.get("exact_normalized_label_match"),
            "score_status": score_context.get("score_status"),
        },
    }


def _verifier_model_input(
    *,
    source_row_index: int,
    route: Mapping[str, Any],
    decision: Mapping[str, Any],
    projection: Mapping[str, Any],
    rendered: Mapping[str, Any],
    clinical_assessment: Mapping[str, Any],
    candidate_packets: Sequence[Mapping[str, Any]],
    provenance_families: Sequence[str],
) -> dict[str, Any]:
    route_evidence = dict(route.get("route_evidence") or {})
    return {
        "system_prompt": VERIFIER_SYSTEM_PROMPT,
        "verification_case": {
            "source_row_index": source_row_index,
            "baseline_verification_decision_v0": {
                "action": decision.get("action"),
                "action_basis": decision.get("action_basis"),
                "action_reason": decision.get("action_reason"),
                "proposed_rendered_label": decision.get("proposed_rendered_label"),
            },
            "verification_route": {
                "route_families": list(route.get("route_families") or []),
                "route_reasons": list(route.get("route_reasons") or []),
                "route_evidence": {
                    "projection_basis": route_evidence.get("projection_basis"),
                    "projection_kind": route_evidence.get("projection_kind"),
                    "projection_issues": list(route_evidence.get("projection_issues") or []),
                    "rendered_label_present": route_evidence.get("rendered_label_present"),
                    "render_issues": list(route_evidence.get("render_issues") or []),
                    "source_candidate_ids": list(
                        route_evidence.get("source_candidate_ids") or []
                    ),
                    "source_aggregation_policy": route_evidence.get(
                        "source_aggregation_policy"
                    ),
                    "source_normalized_phrase": route_evidence.get(
                        "source_normalized_phrase"
                    ),
                },
            },
            "clinical_assessment": {
                "assessment_kind": clinical_assessment.get("assessment_kind"),
                "aggregation_policy": clinical_assessment.get("aggregation_policy"),
                "assessment_summary": clinical_assessment.get("assessment_summary"),
                "normalized_burden": clinical_assessment.get("normalized_burden"),
                "normalization_issues": list(
                    clinical_assessment.get("normalization_issues") or []
                ),
                "primary_candidate_ids": list(
                    clinical_assessment.get("primary_candidate_ids") or []
                ),
                "supporting_candidate_ids": list(
                    clinical_assessment.get("supporting_candidate_ids") or []
                ),
                "rejected_candidate_ids": list(
                    clinical_assessment.get("rejected_candidate_ids") or []
                ),
            },
            "projection_render_state": {
                "projection_decision": {
                    "projection_kind": projection.get("projection_kind"),
                    "projection_basis": projection.get("projection_basis"),
                    "projected_label_semantics": projection.get(
                        "projected_label_semantics"
                    ),
                    "projection_issues": list(projection.get("projection_issues") or []),
                    "projection_owner": projection.get("projection_owner"),
                    "projection_rule_id": projection.get("projection_rule_id"),
                },
                "final_rendered_label": {
                    "rendered_label": rendered.get("rendered_label"),
                    "render_basis": rendered.get("render_basis"),
                    "render_issues": list(rendered.get("render_issues") or []),
                    "projection_owner": rendered.get("projection_owner"),
                    "projection_rule_id": rendered.get("projection_rule_id"),
                },
            },
            "candidate_evidence_packets": list(candidate_packets),
            "provenance_sidecar": {
                "present": bool(provenance_families),
                "families": list(provenance_families),
                "selected_evidence_status": route_evidence.get("selected_evidence_status"),
            },
        },
        "allowed_actions": ALLOWED_ACTIONS,
        "output_schema": VERIFIER_OUTPUT_SCHEMA,
    }


def _candidate_packets(assessment_row: Mapping[str, Any]) -> list[dict[str, Any]]:
    typed_input = dict(assessment_row.get("typed_input") or {})
    candidate_set = dict(typed_input.get("candidate_set") or {})
    packets = []
    for candidate in candidate_set.get("candidates") or []:
        packets.append(
            {
                "candidate_id": candidate.get("candidate_id"),
                "candidate_kind": candidate.get("candidate_kind"),
                "event_type": candidate.get("event_type"),
                "temporality": candidate.get("temporality"),
                "certainty": candidate.get("certainty"),
                "assertion_status": candidate.get("assertion_status"),
                "source_phrase": candidate.get("source_phrase"),
                "evidence_text": candidate.get("evidence_text"),
                "source_ids": list(candidate.get("source_ids") or []),
            }
        )
    return packets


def _route_bucket(non_provenance_families: Sequence[str]) -> tuple[str, str]:
    family_set = set(non_provenance_families)
    if not non_provenance_families:
        return "provenance_only_audit", "provenance_only_audit_appendix"
    if family_set & MAIN_AMBIGUITY_FAMILIES:
        return "verifier_eligible_ambiguity", "main_ambiguity_score_table"
    if family_set & ABSTAIN_EXEMPLAR_FAMILIES:
        return "abstain_exemplar", "abstain_exemplar_appendix"
    if family_set & UPSTREAM_POLICY_FAMILIES:
        return "upstream_policy_appendix", "upstream_policy_appendix"
    if family_set & RENDERED_POLICY_FAMILIES:
        return "rendered_policy_sensitive_appendix", "rendered_policy_sensitive_appendix"
    raise ValueError(f"Unclassified non-provenance route families: {non_provenance_families}")


def _rows_by_source_index(
    rows: Sequence[Mapping[str, Any]],
) -> dict[int, Mapping[str, Any]]:
    return {int(row["source_row_index"]): row for row in rows if "source_row_index" in row}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--route-jsonl-path", type=Path, default=DEFAULT_ROUTE_JSONL_PATH)
    parser.add_argument(
        "--decision-jsonl-path", type=Path, default=DEFAULT_DECISION_JSONL_PATH
    )
    parser.add_argument(
        "--assessment-jsonl-path", type=Path, default=DEFAULT_ASSESSMENT_JSONL_PATH
    )
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument(
        "--clean-experiment-input-jsonl-path",
        type=Path,
        default=DEFAULT_EXPERIMENT_INPUT_JSONL_PATH,
    )
    parser.add_argument(
        "--clean-experiment-input-json-path",
        type=Path,
        default=DEFAULT_EXPERIMENT_INPUT_JSON_PATH,
    )
    parser.add_argument(
        "--clean-experiment-input-report-path",
        type=Path,
        default=DEFAULT_EXPERIMENT_INPUT_REPORT_PATH,
    )
    args = parser.parse_args(argv)

    rows, metadata = build_first_verifier_report_rows(
        load_jsonl_rows(args.route_jsonl_path),
        load_jsonl_rows(args.decision_jsonl_path),
        load_jsonl_rows(args.assessment_jsonl_path),
        route_artifact_path=str(args.route_jsonl_path),
        decision_artifact_path=str(args.decision_jsonl_path),
        assessment_artifact_path=str(args.assessment_jsonl_path),
    )
    write_jsonl_rows(rows, args.jsonl_path)
    write_summary_json(metadata, args.json_path)
    write_report(
        rows,
        metadata,
        args.report_path,
        jsonl_path=args.jsonl_path,
        json_path=args.json_path,
    )
    clean_rows, clean_metadata = build_clean_first_verifier_experiment_input(rows)
    write_jsonl_rows(clean_rows, args.clean_experiment_input_jsonl_path)
    write_summary_json(clean_metadata, args.clean_experiment_input_json_path)
    write_clean_experiment_input_report(
        clean_metadata,
        args.clean_experiment_input_report_path,
        jsonl_path=args.clean_experiment_input_jsonl_path,
        json_path=args.clean_experiment_input_json_path,
    )
    print(json.dumps(metadata["metrics"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
