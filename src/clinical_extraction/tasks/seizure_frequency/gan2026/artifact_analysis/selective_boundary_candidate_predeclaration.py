"""Predeclare selective boundary-candidate proposer calls for Gan 2026."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.candidate_union import (
    DEFAULT_JSON_PATH as DEFAULT_CANDIDATE_UNION_JSON_PATH,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.candidate_union import (
    DEFAULT_JSONL_PATH as DEFAULT_CANDIDATE_UNION_JSONL_PATH,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.artifact_analysis.candidate_union import (
    DEFAULT_RICH_STATE_REPLAY_PATH,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_selective_boundary_candidate_predeclaration_2026-06-04.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_selective_boundary_candidate_predeclaration_2026-06-04.json"
)
DEFAULT_REPORT_PATH = Path(
    "docs/research/gan2026_selective_boundary_candidate_predeclaration_2026-06-04.md"
)
DEFAULT_PROTOCOL_PATH = Path("docs/research/gan2026_candidate_union_protocol_2026-06-04.md")

PROMPT_VERSION = "selective_boundary_candidate_proposer_v3"
MAX_PROPOSED_CANDIDATES = 4
ALLOWED_CANDIDATE_KINDS = [
    "frequency_rate",
    "cluster_frequency",
    "seizure_free",
    "unknown_frequency",
    "no_reference",
    "conditional_frequency",
]
ALLOWED_CURRENTNESS = ["current", "recent", "historical", "unclear"]
ALLOWED_ASSERTION_STATUS = ["asserted", "negated", "uncertain", "conditional"]
ELIGIBLE_HARD_FAMILIES = [
    "candidate_absent_or_weak",
    "cluster_burden",
    "cluster_or_diary",
    "competing_semiologies",
    "current_vs_historical",
    "deterministic_miss",
    "diary_or_log_aggregation",
    "rate_bucket_or_denominator",
    "seizure_free_duration",
    "seizure_free_overreach",
    "temporal_conflict",
    "uncertainty_or_ambiguity",
    "unknown_boundary",
    "unknown_no_reference_boundary",
]
STOP_GO_THRESHOLDS = {
    "exact_evidence_rate_min": 0.99,
    "valid_source_id_rate_min": 0.99,
    "deterministic_recall_lost_rows_max": 0,
    "p90_union_candidate_count_max": 4.0,
    "unsupported_candidate_rate_max": 0.05,
    "llm_recall_rescue_rows_min": 1,
}
BOUNDARY_PROPOSER_SYSTEM_PROMPT = (
    "Extract only seizure-frequency candidate facts that are easy to miss. "
    "Use exact words from the note for every evidence quote. Return candidates "
    "for uncertainty, no frequency reference, seizure-free claims with blockers, "
    "conditional-only events, competing seizure types, cluster patterns, diary "
    "or log summaries, and vague rates with a clear time basis. Do not choose a "
    "seizure-frequency answer. Do not rewrite ordinary rate facts unless they "
    "are needed to explain one of these hard cases. Use one string value, not a "
    "list, for each choice field such as candidate_kind, currentness, "
    "assertion_status, time_unit, and duration_unit. Use asserted, not "
    "no_reference, as assertion_status when candidate_kind is no_reference. For "
    "cluster statements, put the number of clusters and cluster timing in rate, "
    "and put seizures per cluster in cluster. Do not put seizures per cluster in "
    "rate count fields. If the note gives exact seizures per cluster, fill the "
    "numeric low/high fields and leave seizures_per_cluster_is_multiple false. "
    "If the note gives only seizures per cluster without timing, still return "
    "that cluster burden. For cluster timing, keep the stated unit: four to five "
    "weeks means time_count_low 4, time_count_high 5, and time_unit week. one to "
    "two times per month means count_low 1, count_high 2, time_count_low 1, and "
    "time_unit month. five days without seizures followed by a cluster means one "
    "cluster per five days, not one cluster per day."
)
BOUNDARY_PROPOSER_OUTPUT_SCHEMA = {
    "candidates": [
        {
            "candidate_kind": (
                "One string value: frequency_rate, cluster_frequency, seizure_free, "
                "unknown_frequency, no_reference, or conditional_frequency."
            ),
            "evidence_quote": "Exact substring copied from the note.",
            "currentness": "One string value: current, recent, historical, or unclear.",
            "assertion_status": (
                "One string value: asserted, negated, uncertain, or conditional. "
                "For candidate_kind no_reference, use asserted."
            ),
            "seizure_type": "Seizure type or null when the note does not say.",
            "rate": {
                "count_low": "Number or null.",
                "count_high": "Number or null.",
                "count_is_multiple": (
                    "true when the cluster count or ordinary event count says multiple, "
                    "many, several, or similar. For cluster_frequency, these count "
                    "fields describe clusters, not seizures per cluster."
                ),
                "time_count_low": "Number or null.",
                "time_count_high": "Number or null.",
                "time_unit": (
                    "One string value: day, week, month, year, or null. Keep the "
                    "note's stated time unit; do not collapse four to five weeks "
                    "into one month."
                ),
                "rate_text": "Exact phrase for the count and time basis, or null.",
            },
            "cluster": {
                "has_cluster_pattern": "Boolean.",
                "cluster_cadence_text": "Exact phrase for cluster timing, or null.",
                "seizures_per_cluster_low": "Number or null.",
                "seizures_per_cluster_high": "Number or null.",
                "seizures_per_cluster_is_multiple": (
                    "true only when the note says multiple, many, several, or similar "
                    "seizures per cluster and does not give exact low/high numbers."
                ),
                "cluster_uncertainty": "Short note or null.",
            },
            "seizure_free": {
                "has_no_event_claim": "Boolean.",
                "duration_count": "Number or null.",
                "duration_unit": "One string value: day, week, month, year, or null.",
                "applies_to_all_seizure_types": "true, false, or null.",
                "has_recent_events_or_conditions": "Boolean.",
                "boundary_note": "Short note or null.",
            },
            "conditionality_note": "Trigger or condition, or null.",
            "competing_state_summary": "Short summary of competing current facts, or null.",
            "ambiguity_flags": ["Short plain-language ambiguity flags."],
            "reason": "Brief reason this is a hard candidate.",
        }
    ]
}


def build_selective_boundary_candidate_predeclaration_rows(
    candidate_union_rows: Sequence[Mapping[str, Any]],
    candidate_union_metadata: Mapping[str, Any],
    *,
    rich_state_rows: Sequence[Mapping[str, Any]] = (),
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    stop_go = _stop_go_decision(candidate_union_metadata)
    if not stop_go["authorized"]:
        return [], summarize_selective_boundary_candidate_predeclaration(
            [],
            candidate_union_rows,
            candidate_union_metadata,
            stop_go=stop_go,
        )

    note_text_by_source = {
        int(row["source_row_index"]): str(row.get("typed_input", {}).get("note_text") or "")
        for row in rich_state_rows
    }
    rows = [
        _predeclaration_row(
            row,
            note_text=note_text_by_source.get(int(row["source_row_index"]), ""),
        )
        for row in candidate_union_rows
        if _is_hard_slice_eligible(row)
    ]
    rows.sort(key=lambda row: int(row["source_row_index"]))
    return rows, summarize_selective_boundary_candidate_predeclaration(
        rows,
        candidate_union_rows,
        candidate_union_metadata,
        stop_go=stop_go,
    )


def summarize_selective_boundary_candidate_predeclaration(
    rows: Sequence[Mapping[str, Any]],
    candidate_union_rows: Sequence[Mapping[str, Any]],
    candidate_union_metadata: Mapping[str, Any],
    *,
    stop_go: Mapping[str, Any],
) -> dict[str, Any]:
    family_counts = Counter(family for row in rows for family in row["hard_families"])
    kind_counts = Counter(
        proposal["candidate_kind"] for row in rows for proposal in row["saved_rescue_proposals"]
    )
    return {
        "artifact_kind": "gan2026_selective_boundary_candidate_predeclaration",
        "date": "2026-06-04",
        "split_manifest": "gan2026_split_v1",
        "split": "validation",
        "source_artifact": str(DEFAULT_CANDIDATE_UNION_JSONL_PATH),
        "source_metadata_artifact": str(DEFAULT_CANDIDATE_UNION_JSON_PATH),
        "rich_state_source_artifact": str(DEFAULT_RICH_STATE_REPLAY_PATH),
        "row_count": len(rows),
        "claim_language": (
            "Validation-development selective boundary-candidate proposer "
            "predeclaration only. No live model calls, locked-test inspection, "
            "whole-pipeline promotion, or benchmark-comparable claim are authorized."
        ),
        "prompt_version": PROMPT_VERSION,
        "max_proposed_candidates_per_row": MAX_PROPOSED_CANDIDATES,
        "eligible_hard_families": ELIGIBLE_HARD_FAMILIES,
        "stop_go_thresholds": STOP_GO_THRESHOLDS,
        "stop_go_decision": dict(stop_go),
        "boundary_proposer_output_schema": BOUNDARY_PROPOSER_OUTPUT_SCHEMA,
        "metrics": {
            "predeclared_rows": len(rows),
            "candidate_union_rows_reviewed": len(candidate_union_rows),
            "saved_recall_rescue_rows_available": int(
                candidate_union_metadata.get("metrics", {}).get("llm_recall_rescue_rows", 0)
            ),
            "rows_with_note_text": sum(bool(row["model_input"]["note_text"]) for row in rows),
            "saved_rescue_proposal_count": sum(len(row["saved_rescue_proposals"]) for row in rows),
        },
        "hard_family_counts": dict(sorted(family_counts.items())),
        "saved_rescue_candidate_kind_counts": dict(sorted(kind_counts.items())),
        "post_run_accounting_contract": {
            "gate_model_outputs_with_candidate_union_gates": True,
            "report_candidate_recall_rescue": True,
            "report_rejected_candidates": True,
            "block_final_label_use_before_selected_state_replay": True,
        },
    }


def write_selective_boundary_candidate_json(metadata: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_selective_boundary_candidate_report(
    metadata: Mapping[str, Any],
    path: Path,
    *,
    jsonl_path: Path = DEFAULT_JSONL_PATH,
    json_path: Path = DEFAULT_JSON_PATH,
    protocol_path: Path = DEFAULT_PROTOCOL_PATH,
) -> None:
    metrics = metadata["metrics"]
    stop_go = metadata["stop_go_decision"]
    lines = [
        "# Gan 2026 Selective Boundary-Candidate Predeclaration",
        "",
        "This is a pre-run validation-development contract for selective LLM "
        "boundary-candidate proposal. It fixes the exact hard slice, prompt, "
        "schema, gates, and post-run accounting before any new live model calls.",
        "",
        "## Decision",
        "",
        (
            "New selective boundary-candidate calls are authorized for the saved "
            f"hard-panel recall-rescue slice: {metrics['predeclared_rows']} validation "
            "rows where deterministic candidates did not cover the gold state but the "
            "saved LLM boundary proposal did."
        ),
        "",
        "## Stop/Go Evidence",
        "",
        f"Decision: `{stop_go['decision']}`.",
        "",
        "| Metric | Observed | Threshold |",
        "| --- | ---: | ---: |",
    ]
    for row in stop_go["checks"]:
        lines.append(
            f"| {row['metric'].replace('_', ' ')} | {_format_metric(row['observed'])} | "
            f"{_format_metric(row['threshold'])} |"
        )
    lines.extend(
        [
            "",
            "## Exact Hard Slice",
            "",
            "- Split: `validation` from `gan2026_split_v1`.",
            "- Include only saved hard-panel rows with deterministic candidate recall false, "
            "saved LLM boundary-proposal recall true, union recall true, exact retained "
            "LLM proposal evidence, and at least one eligible hard-family tag.",
            "- Exclude locked test rows, broad validation rows outside the saved hard panel, "
            "rows with non-exact saved proposal evidence, and rows where deterministic "
            "candidate recall already covers the gold state.",
            "",
            "## Prompt Contract",
            "",
            BOUNDARY_PROPOSER_SYSTEM_PROMPT,
            "",
            "The output must be JSON with one top-level `candidates` list. Each candidate "
            "must include `candidate_kind`, `evidence_quote`, `currentness`, "
            "`assertion_status`, `seizure_type`, `rate`, `cluster`, `seizure_free`, "
            "`conditionality_note`, `competing_state_summary`, `ambiguity_flags`, and "
            "`reason`.",
            "",
            "## Claim Boundary",
            "",
            str(metadata["claim_language"]),
            "",
            "## Artifacts",
            "",
            f"- Protocol: `{protocol_path}`",
            f"- Boundary-candidate input JSONL: `{jsonl_path}`",
            f"- Summary JSON: `{json_path}`",
            f"- Source candidate-union JSONL: `{metadata['source_artifact']}`",
            f"- Source rich-state replay: `{metadata['rich_state_source_artifact']}`",
            "",
            "## Metrics",
            "",
            "| Metric | Value |",
            "| --- | ---: |",
        ]
    )
    for key, value in metrics.items():
        lines.append(f"| {key.replace('_', ' ')} | {_format_metric(value)} |")
    lines.extend(["", "## Hard Families", "", "| Family | Rows |", "| --- | ---: |"])
    for key, value in metadata["hard_family_counts"].items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(
        [
            "",
            "## Post-Run Accounting",
            "",
            "After outputs are collected, apply the existing candidate-union gates before "
            "any selected-state replay. Report retained, merged, and rejected candidates; "
            "candidate-recall rescue; evidence exactness; source-id validity; burden; "
            "and metadata completeness. Do not use proposer outputs as final labels.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _predeclaration_row(row: Mapping[str, Any], *, note_text: str) -> dict[str, Any]:
    source_row_index = int(row["source_row_index"])
    proposals = _retained_llm_boundary_proposals(row)
    return {
        "artifact_kind": "gan2026_selective_boundary_candidate_predeclaration_row",
        "claim_boundary": "validation_development_predeclared_boundary_candidate_no_call",
        "source_row_index": source_row_index,
        "split": row.get("split", "validation"),
        "split_manifest": row.get("split_manifest", "gan2026_split_v1"),
        "hard_families": [
            family
            for family in row.get("hidden_families", [])
            if family in set(ELIGIBLE_HARD_FAMILIES)
        ],
        "eligibility_reason": (
            "deterministic_candidate_miss_saved_llm_boundary_rescue_exact_evidence"
        ),
        "model_input": {
            "system_prompt": BOUNDARY_PROPOSER_SYSTEM_PROMPT,
            "note_text": note_text,
            "allowed_candidate_kinds": ALLOWED_CANDIDATE_KINDS,
            "allowed_currentness": ALLOWED_CURRENTNESS,
            "allowed_assertion_status": ALLOWED_ASSERTION_STATUS,
            "max_candidates": MAX_PROPOSED_CANDIDATES,
            "output_schema": BOUNDARY_PROPOSER_OUTPUT_SCHEMA,
        },
        "saved_rescue_proposals": [
            {
                "candidate_kind": proposal.get("candidate_kind"),
                "evidence": proposal.get("evidence"),
                "currentness": proposal.get("currentness"),
                "assertion_status": proposal.get("assertion_status"),
                "semiology": proposal.get("semiology"),
                "metadata": proposal.get("metadata") or {},
            }
            for proposal in proposals
        ],
        "development_accounting": {
            "gold_label": row.get("gold_label"),
            "deterministic_top_label": row.get("deterministic_top_label"),
            "deterministic_candidates_recall": row["gold_state_recall_summary"][
                "deterministic_candidates_recall"
            ],
            "saved_llm_boundary_candidate_recall": row["gold_state_recall_summary"][
                "llm_boundary_candidate_recall"
            ],
            "saved_union_verified_candidate_recall": row["gold_state_recall_summary"][
                "union_verified_candidate_recall"
            ],
        },
        "post_run_accounting_contract": {
            "gold_label_excluded_from_model_input": True,
            "compare_new_outputs_to_saved_rescue_proposals": True,
            "apply_candidate_union_gates_before_selected_state_use": True,
        },
    }


def _stop_go_decision(metadata: Mapping[str, Any]) -> dict[str, Any]:
    metrics = metadata.get("metrics", {})
    checks = [
        _check_min(metrics, "exact_evidence_rate", STOP_GO_THRESHOLDS["exact_evidence_rate_min"]),
        _check_min(metrics, "valid_source_id_rate", STOP_GO_THRESHOLDS["valid_source_id_rate_min"]),
        _check_max(
            metrics,
            "deterministic_recall_lost_rows",
            STOP_GO_THRESHOLDS["deterministic_recall_lost_rows_max"],
        ),
        _check_max(
            metrics,
            "p90_union_candidate_count",
            STOP_GO_THRESHOLDS["p90_union_candidate_count_max"],
        ),
        _check_max(
            metrics,
            "unsupported_candidate_rate",
            STOP_GO_THRESHOLDS["unsupported_candidate_rate_max"],
        ),
        _check_min(
            metrics,
            "llm_recall_rescue_rows",
            STOP_GO_THRESHOLDS["llm_recall_rescue_rows_min"],
        ),
    ]
    authorized = all(check["passed"] for check in checks)
    return {
        "authorized": authorized,
        "decision": "go" if authorized else "stop",
        "checks": checks,
    }


def _check_min(metrics: Mapping[str, Any], metric: str, threshold: float | int) -> dict[str, Any]:
    observed = metrics.get(metric, 0)
    return {
        "metric": metric,
        "observed": observed,
        "threshold": threshold,
        "direction": "minimum",
        "passed": observed >= threshold,
    }


def _check_max(metrics: Mapping[str, Any], metric: str, threshold: float | int) -> dict[str, Any]:
    observed = metrics.get(metric, 0)
    return {
        "metric": metric,
        "observed": observed,
        "threshold": threshold,
        "direction": "maximum",
        "passed": observed <= threshold,
    }


def _is_hard_slice_eligible(row: Mapping[str, Any]) -> bool:
    recall = row.get("gold_state_recall_summary") or {}
    if recall.get("deterministic_candidates_recall"):
        return False
    if not recall.get("llm_boundary_candidate_recall"):
        return False
    if not recall.get("union_verified_candidate_recall"):
        return False
    if not set(row.get("hidden_families") or []) & set(ELIGIBLE_HARD_FAMILIES):
        return False
    return bool(_retained_llm_boundary_proposals(row))


def _retained_llm_boundary_proposals(row: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    retained = []
    for candidate in row.get("union_verified_candidates") or []:
        if "llm_boundary_proposal" not in set(candidate.get("provenance") or []):
            continue
        if candidate.get("gate_failures"):
            continue
        if not candidate.get("exact_evidence"):
            continue
        if candidate.get("source_id_status") != "valid":
            continue
        retained.append(candidate)
    return retained


def _format_metric(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--candidate-union-jsonl-path",
        type=Path,
        default=DEFAULT_CANDIDATE_UNION_JSONL_PATH,
    )
    parser.add_argument(
        "--candidate-union-json-path",
        type=Path,
        default=DEFAULT_CANDIDATE_UNION_JSON_PATH,
    )
    parser.add_argument(
        "--rich-state-replay-path",
        type=Path,
        default=DEFAULT_RICH_STATE_REPLAY_PATH,
    )
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    candidate_union_rows = load_jsonl_rows(args.candidate_union_jsonl_path)
    metadata = json.loads(args.candidate_union_json_path.read_text(encoding="utf-8"))
    rich_state_rows = (
        load_jsonl_rows(args.rich_state_replay_path) if args.rich_state_replay_path.exists() else []
    )
    rows, summary = build_selective_boundary_candidate_predeclaration_rows(
        candidate_union_rows,
        metadata,
        rich_state_rows=rich_state_rows,
    )
    summary = {
        **summary,
        "source_artifact": str(args.candidate_union_jsonl_path),
        "source_metadata_artifact": str(args.candidate_union_json_path),
        "rich_state_source_artifact": str(args.rich_state_replay_path),
    }
    write_jsonl_rows(rows, args.jsonl_path)
    write_selective_boundary_candidate_json(summary, args.json_path)
    write_selective_boundary_candidate_report(
        summary,
        args.report_path,
        jsonl_path=args.jsonl_path,
        json_path=args.json_path,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
