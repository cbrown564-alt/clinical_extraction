"""Diagnostics for SelectedCandidateDecision selector artifacts."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.selected_fact import (
    SelectedCandidateDecision,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)

DEFAULT_SELECTION_JSONL_PATH = Path(
    "experiments/gan2026_validation250_selected_candidate_decision_v2_v2_high_recall.jsonl"
)
DEFAULT_JSONL_PATH = Path(
    "experiments/gan2026_validation250_selected_candidate_decision_v2_diagnostics.jsonl"
)
DEFAULT_JSON_PATH = Path(
    "experiments/gan2026_validation250_selected_candidate_decision_v2_diagnostics.json"
)
DEFAULT_REPORT_PATH = Path(
    "experiments/gan2026_validation250_selected_candidate_decision_v2_diagnostics.md"
)
HIGH_BURDEN_THRESHOLD = 4
MAX_EXAMPLES_PER_SECTION = 12


def build_selected_candidate_decision_diagnostics(
    selection_rows: Sequence[Mapping[str, Any]],
    *,
    source_artifact: str = str(DEFAULT_SELECTION_JSONL_PATH),
    high_burden_threshold: int = HIGH_BURDEN_THRESHOLD,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    diagnostics = [
        _diagnostic_row(row, high_burden_threshold=high_burden_threshold)
        for row in selection_rows
    ]
    return diagnostics, summarize_diagnostics(
        diagnostics,
        source_artifact=source_artifact,
        high_burden_threshold=high_burden_threshold,
    )


def summarize_diagnostics(
    diagnostics: Sequence[Mapping[str, Any]],
    *,
    source_artifact: str = str(DEFAULT_SELECTION_JSONL_PATH),
    high_burden_threshold: int = HIGH_BURDEN_THRESHOLD,
) -> dict[str, Any]:
    mode_counts = Counter(str(row["selection_mode"]) for row in diagnostics)
    selected_kind_counts = Counter(
        kind
        for row in diagnostics
        for kind in row["selected_candidate_kinds"]
    )
    selected_source_type_counts = Counter(
        source_type
        for row in diagnostics
        for source_type in row["selected_source_types"]
    )
    source_composition_counts = Counter(
        str(row["selected_source_composition"]) for row in diagnostics
    )
    selected_count_counts = Counter(
        str(row["selected_candidate_count"]) for row in diagnostics
    )
    invalid_reference_rows = [
        row for row in diagnostics if row["unknown_selected_candidate_ids"]
    ]
    related_group_rows = [
        row for row in diagnostics if row["selection_mode"] == "related_candidate_group"
    ]
    high_burden_rows = [
        row for row in diagnostics if row["candidate_count"] >= high_burden_threshold
    ]
    group_issue_rows = [
        row
        for row in related_group_rows
        if row["related_group_coherence_flags"]
    ]
    return {
        "artifact_name": "gan2026_validation250_selected_candidate_decision_v2_diagnostics",
        "source_artifact": source_artifact,
        "row_count": len(diagnostics),
        "high_burden_threshold": high_burden_threshold,
        "claim_boundary": (
            "Validation250 selector-decision diagnostics only. This verifies "
            "candidate-id traceability and selection shape; it does not score, "
            "normalize, project, or render labels."
        ),
        "summary": {
            "selected_decision_rows": sum(
                row["decision_status"] == "present" for row in diagnostics
            ),
            "missing_decision_rows": sum(
                row["decision_status"] == "missing" for row in diagnostics
            ),
            "invalid_selected_reference_rows": len(invalid_reference_rows),
            "high_burden_rows": len(high_burden_rows),
            "high_burden_selected_rows": sum(
                bool(row["selected_candidate_ids"]) for row in high_burden_rows
            ),
            "selection_mode_counts": dict(sorted(mode_counts.items())),
            "selected_candidate_count_distribution": dict(sorted(selected_count_counts.items())),
            "selected_candidate_kind_counts": dict(sorted(selected_kind_counts.items())),
            "selected_source_type_counts": dict(sorted(selected_source_type_counts.items())),
            "selected_source_composition_counts": dict(sorted(source_composition_counts.items())),
            "related_group_rows": len(related_group_rows),
            "related_group_with_coherence_flags": len(group_issue_rows),
            "related_group_mixed_kind_rows": sum(
                "mixed_candidate_kind" in row["related_group_coherence_flags"]
                for row in related_group_rows
            ),
            "related_group_mixed_temporality_rows": sum(
                "mixed_temporality" in row["related_group_coherence_flags"]
                for row in related_group_rows
            ),
            "related_group_without_cluster_or_shared_kind_rows": sum(
                "no_cluster_or_shared_kind_signal" in row["related_group_coherence_flags"]
                for row in related_group_rows
            ),
            "invalid_reference_source_row_indices": [
                int(row["source_row_index"]) for row in invalid_reference_rows
            ],
            "related_group_source_row_indices": [
                int(row["source_row_index"]) for row in related_group_rows
            ],
            "high_burden_source_row_indices": [
                int(row["source_row_index"]) for row in high_burden_rows
            ],
        },
        "inspection_examples": {
            "invalid_reference_rows": _examples(invalid_reference_rows),
            "related_group_rows": _examples(related_group_rows),
            "related_group_coherence_flags": _examples(group_issue_rows),
            "high_burden_rows": _examples(high_burden_rows),
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
    path: Path,
    *,
    jsonl_path: Path = DEFAULT_JSONL_PATH,
    json_path: Path = DEFAULT_JSON_PATH,
) -> None:
    summary = metadata["summary"]
    lines = [
        "# Gan 2026 Selected Candidate Decision Diagnostics",
        "",
        str(metadata["claim_boundary"]),
        "",
        "## Artifacts",
        "",
        f"- Diagnostic JSONL: `{jsonl_path}`",
        f"- Summary JSON: `{json_path}`",
        f"- Selector source: `{metadata['source_artifact']}`",
        "",
        "## Summary",
        "",
        f"- Rows: {metadata['row_count']}",
        f"- Selected decision rows: {summary['selected_decision_rows']}",
        f"- Missing decision rows: {summary['missing_decision_rows']}",
        f"- Invalid selected-reference rows: {summary['invalid_selected_reference_rows']}",
        f"- High-burden rows: {summary['high_burden_rows']}",
        f"- Related-candidate-group rows: {summary['related_group_rows']}",
        (
            "- Related groups with coherence flags: "
            f"{summary['related_group_with_coherence_flags']}"
        ),
        "",
        "## Selection Modes",
        "",
    ]
    for mode, count in summary["selection_mode_counts"].items():
        lines.append(f"- `{mode}`: {count}")
    lines.extend(["", "## Selected Candidate Source Types", ""])
    for source_type, count in summary["selected_source_type_counts"].items():
        lines.append(f"- `{source_type}`: {count}")
    lines.extend(["", "## Selected Candidate Kinds", ""])
    for kind, count in summary["selected_candidate_kind_counts"].items():
        lines.append(f"- `{kind}`: {count}")
    lines.extend(["", "## Source Composition", ""])
    for composition, count in summary["selected_source_composition_counts"].items():
        lines.append(f"- `{composition}`: {count}")
    lines.extend(["", "## Inspection Examples", ""])
    for title, examples in metadata["inspection_examples"].items():
        lines.extend([f"### {title.replace('_', ' ').title()}", ""])
        if not examples:
            lines.append("- None.")
        for row in examples:
            lines.append(
                "- "
                f"{row['source_row_index']}: mode `{row['selection_mode']}`, "
                f"selected {row['selected_candidate_ids']}, kinds "
                f"{row['selected_candidate_kinds']}, source types "
                f"{row['selected_source_types']}, flags "
                f"{row['related_group_coherence_flags']}. "
                f"Rationale: {row['rationale']}"
            )
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _diagnostic_row(
    row: Mapping[str, Any],
    *,
    high_burden_threshold: int,
) -> dict[str, Any]:
    candidates = _candidate_payloads_from_row(row)
    decision = _decision_from_row(row)
    candidate_by_id = {
        str(candidate.get("candidate_id")): candidate for candidate in candidates
    }
    selected_ids = list(decision.selected_candidate_ids) if decision is not None else []
    selected_candidates = [
        candidate_by_id[candidate_id]
        for candidate_id in selected_ids
        if candidate_id in candidate_by_id
    ]
    unknown_selected_ids = [
        candidate_id for candidate_id in selected_ids if candidate_id not in candidate_by_id
    ]
    selected_kinds = [
        str(candidate.get("candidate_kind")) for candidate in selected_candidates
    ]
    selected_source_types = [
        str(candidate.get("source_type")) for candidate in selected_candidates
    ]
    temporality_values = [
        str(candidate.get("temporality")) for candidate in selected_candidates
    ]
    certainty_values = [
        str(candidate.get("certainty")) for candidate in selected_candidates
    ]
    selection_mode = decision.selection_mode if decision is not None else "missing"
    return {
        "source_row_index": int(row["source_row_index"]),
        "split": row.get("split", "validation"),
        "decision_status": "present" if decision is not None else "missing",
        "candidate_set_status": "present" if candidates else "missing_or_empty",
        "selection_mode": selection_mode,
        "selected_candidate_ids": selected_ids,
        "unknown_selected_candidate_ids": unknown_selected_ids,
        "selected_candidate_count": len(selected_ids),
        "candidate_count": len(candidates),
        "high_burden": len(candidates) >= high_burden_threshold,
        "selected_candidate_kinds": selected_kinds,
        "selected_source_types": selected_source_types,
        "selected_source_composition": _source_composition(selected_source_types),
        "selected_temporalities": temporality_values,
        "selected_certainties": certainty_values,
        "selected_evidence_texts": [
            _candidate_evidence_text(candidate) for candidate in selected_candidates
        ],
        "non_selected_candidate_ids": [
            str(candidate.get("candidate_id"))
            for candidate in candidates
            if str(candidate.get("candidate_id")) not in set(selected_ids)
        ],
        "related_group_coherence_flags": _related_group_coherence_flags(
            selection_mode=str(selection_mode),
            selected_kinds=selected_kinds,
            temporalities=temporality_values,
        ),
        "rationale": decision.rationale if decision is not None else "",
        "parse_errors": list(row.get("parse_errors") or []),
        "call_error": row.get("call_error"),
    }


def _candidate_payloads_from_row(row: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    typed_input = row.get("typed_input")
    if not isinstance(typed_input, Mapping):
        return []
    candidate_set_payload = typed_input.get("candidate_set")
    if not isinstance(candidate_set_payload, Mapping):
        return []
    candidates = candidate_set_payload.get("candidates")
    if not isinstance(candidates, list):
        return []
    return [candidate for candidate in candidates if isinstance(candidate, Mapping)]


def _candidate_evidence_text(candidate: Mapping[str, Any]) -> str:
    evidence = candidate.get("evidence_text")
    if isinstance(evidence, str):
        return evidence
    evidence_span = candidate.get("evidence_span")
    if isinstance(evidence_span, Mapping) and isinstance(evidence_span.get("text"), str):
        return str(evidence_span["text"])
    return ""


def _decision_from_row(row: Mapping[str, Any]) -> SelectedCandidateDecision | None:
    decision_payload = row.get("selected_candidate_decision")
    if not isinstance(decision_payload, Mapping):
        return None
    return SelectedCandidateDecision.model_validate(decision_payload)


def _source_composition(source_types: Sequence[str]) -> str:
    unique = set(source_types)
    if not unique:
        return "none"
    if unique == {"deterministic_candidate"}:
        return "deterministic_only"
    if unique == {"llm_candidate"}:
        return "llm_only"
    return "mixed"


def _related_group_coherence_flags(
    *,
    selection_mode: str,
    selected_kinds: Sequence[str],
    temporalities: Sequence[str],
) -> list[str]:
    if selection_mode != "related_candidate_group":
        return []
    flags = []
    unique_kinds = set(selected_kinds)
    unique_temporalities = set(temporalities)
    if len(unique_kinds) > 1:
        flags.append("mixed_candidate_kind")
    if len(unique_temporalities) > 1:
        flags.append("mixed_temporality")
    if "cluster_frequency" not in unique_kinds and len(unique_kinds) > 1:
        flags.append("no_cluster_or_shared_kind_signal")
    return flags


def _examples(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "source_row_index": int(row["source_row_index"]),
            "selection_mode": row["selection_mode"],
            "selected_candidate_ids": list(row["selected_candidate_ids"]),
            "selected_candidate_kinds": list(row["selected_candidate_kinds"]),
            "selected_source_types": list(row["selected_source_types"]),
            "related_group_coherence_flags": list(row["related_group_coherence_flags"]),
            "rationale": row["rationale"],
        }
        for row in rows[:MAX_EXAMPLES_PER_SECTION]
    ]


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection-jsonl", type=Path, default=DEFAULT_SELECTION_JSONL_PATH)
    parser.add_argument("--jsonl-path", type=Path, default=DEFAULT_JSONL_PATH)
    parser.add_argument("--json-path", type=Path, default=DEFAULT_JSON_PATH)
    parser.add_argument("--report-path", type=Path, default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    rows, metadata = build_selected_candidate_decision_diagnostics(
        load_jsonl_rows(args.selection_jsonl),
        source_artifact=str(args.selection_jsonl),
    )
    write_jsonl_rows(rows, args.jsonl_path)
    write_summary_json(metadata, args.json_path)
    write_report(metadata, args.report_path, jsonl_path=args.jsonl_path, json_path=args.json_path)
    print(json.dumps(metadata["summary"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
