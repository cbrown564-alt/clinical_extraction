"""Validation ablations for selecting recalled assembly alternatives."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)

POLICY_NAME = "gan2026_exact_label_selector_ablation_v0"
ACTIONABLE_STATUSES = {"exact_label", "purist_category"}

FIELDNAMES = [
    "selector_name",
    "source_row_index",
    "base_transition",
    "base_final_action",
    "base_prediction_label",
    "base_purist_correct",
    "candidate_generator",
    "candidate_label",
    "candidate_kind",
    "candidate_evidence_status",
    "candidate_source_id_valid",
    "candidate_gold_match_status",
    "candidate_gold_match_basis",
    "candidate_non_gold_rank_key",
    "selected_transition",
]

SelectorPredicate = Callable[[Mapping[str, Any], Mapping[str, Any]], bool]


def build_selector_ablation_rows(
    matrix_rows: Sequence[Mapping[str, Any]],
    candidate_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Apply non-gold selector policies across all validation matrix rows."""

    candidates_by_source: dict[int, list[Mapping[str, Any]]] = defaultdict(list)
    for candidate in candidate_rows:
        candidates_by_source[int(candidate["source_row_index"])].append(candidate)

    rows = []
    for selector_name, predicate in _selector_predicates().items():
        for matrix in matrix_rows:
            source_row_index = int(matrix["source_row_index"])
            selected = _select_candidate(
                candidates_by_source.get(source_row_index, []),
                matrix,
                predicate,
            )
            if not selected:
                continue
            base_correct = _as_bool(matrix.get("final_purist_correct"))
            candidate_correct = selected.get("gold_match_status") in ACTIONABLE_STATUSES
            rows.append(
                {
                    "selector_name": selector_name,
                    "source_row_index": source_row_index,
                    "base_transition": matrix.get("comparator_transition"),
                    "base_final_action": matrix.get("final_action"),
                    "base_prediction_label": matrix.get("prediction_label") or "",
                    "base_purist_correct": base_correct,
                    "candidate_generator": selected.get("generator_name"),
                    "candidate_label": selected.get("candidate_label"),
                    "candidate_kind": selected.get("candidate_kind"),
                    "candidate_evidence_status": selected.get("evidence_status"),
                    "candidate_source_id_valid": selected.get("source_id_valid"),
                    "candidate_gold_match_status": selected.get("gold_match_status"),
                    "candidate_gold_match_basis": selected.get("gold_match_basis"),
                    "candidate_non_gold_rank_key": "|".join(
                        str(part) for part in _candidate_rank(selected)
                    ),
                    "selected_transition": _transition(
                        base_correct,
                        candidate_correct,
                    ),
                }
            )
    rows.sort(key=lambda row: (row["selector_name"], int(row["source_row_index"])))
    return rows


def summarize_selector_ablation_rows(
    rows: Sequence[Mapping[str, Any]],
    matrix_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Summarize selector damage and recoveries against the base matrix."""

    base_correct_rows = sum(_as_bool(row.get("final_purist_correct")) for row in matrix_rows)
    total_rows = len(matrix_rows)
    selector_summaries = {}
    for selector_name in _selector_predicates():
        selected = [row for row in rows if row["selector_name"] == selector_name]
        transition_counts = Counter(str(row["selected_transition"]) for row in selected)
        status_counts = Counter(str(row["candidate_gold_match_status"]) for row in selected)
        generator_counts = Counter(str(row["candidate_generator"]) for row in selected)
        w_to_c = transition_counts.get("W_to_C", 0)
        c_to_w = transition_counts.get("C_to_W", 0)
        projected_correct = base_correct_rows + w_to_c - c_to_w
        selector_summaries[selector_name] = {
            "selected_rows": len(selected),
            "candidate_gold_match_status_counts": dict(sorted(status_counts.items())),
            "selected_transition_counts": dict(sorted(transition_counts.items())),
            "candidate_generator_counts": dict(sorted(generator_counts.items())),
            "base_correct_rows": base_correct_rows,
            "projected_correct_rows": projected_correct,
            "projected_full_row_purist_proxy": _rate(projected_correct, total_rows),
            "changed_label_precision": _rate(w_to_c, w_to_c + c_to_w),
            "decision": _selector_decision(w_to_c, c_to_w),
        }
    best_selector = max(
        selector_summaries,
        key=lambda name: selector_summaries[name]["projected_correct_rows"],
    )
    return {
        "component_name": "exact_label_selector_ablation",
        "policy_name": POLICY_NAME,
        "row_count": len(rows),
        "base_total_rows": total_rows,
        "base_correct_rows": base_correct_rows,
        "base_full_row_purist_proxy": _rate(base_correct_rows, total_rows),
        "selectors": selector_summaries,
        "best_selector_by_projected_correct": best_selector,
        "claim_language": (
            "Validation-development selector ablation. Candidate selection uses "
            "only non-gold candidate features; gold_match_status is used only "
            "after selection to score W->C and C->W. This artifact does not "
            "change predictions, inspect locked-test row-level failures, or "
            "make a benchmark-comparable claim."
        ),
        "recommended_next_step": _recommended_next_step(selector_summaries),
    }


def write_csv_rows(rows: Sequence[Mapping[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in FIELDNAMES})


def write_summary_json(summary: Mapping[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n")


def write_report(
    summary: Mapping[str, Any],
    path: Path,
    *,
    csv_path: Path,
    json_path: Path,
) -> None:
    lines = [
        "# Gan 2026 Exact-Label Selector Ablation",
        "",
        str(summary["claim_language"]),
        "",
        "## Summary",
        "",
        f"Base full-row Purist proxy: {_format_rate(summary['base_full_row_purist_proxy'])} "
        f"({summary['base_correct_rows']} / {summary['base_total_rows']}).",
        "",
        "| Selector | Selected | W->C | C->W | Projected proxy | Decision |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for selector_name, selector in summary["selectors"].items():
        transitions = selector["selected_transition_counts"]
        lines.append(
            f"| `{selector_name}` | {selector['selected_rows']} | "
            f"{transitions.get('W_to_C', 0)} | {transitions.get('C_to_W', 0)} | "
            f"{_format_rate(selector['projected_full_row_purist_proxy'])} | "
            f"`{selector['decision']}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            str(summary["recommended_next_step"]),
            "",
            "## Artifacts",
            "",
            f"- Ablation CSV: `{csv_path}`",
            f"- Ablation JSON: `{json_path}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _selector_predicates() -> dict[str, SelectorPredicate]:
    return {
        "deterministic_window_parseable_v0": _is_deterministic_window_parseable,
        "deterministic_non_seizure_free_parseable_v0": (
            _is_deterministic_non_seizure_free_parseable
        ),
        "llm_unknown_current_v0": _is_llm_unknown_current,
        "llm_unknown_any_v0": _is_llm_unknown_any,
        "nonprediction_llm_unknown_current_v0": (
            _is_nonprediction_llm_unknown_current
        ),
        "nonprediction_llm_unknown_any_v0": _is_nonprediction_llm_unknown_any,
    }


def _select_candidate(
    candidates: Sequence[Mapping[str, Any]],
    matrix: Mapping[str, Any],
    predicate: SelectorPredicate,
) -> Mapping[str, Any] | None:
    eligible = [candidate for candidate in candidates if predicate(candidate, matrix)]
    if not eligible:
        return None
    return sorted(eligible, key=_candidate_rank)[0]


def _common_eligible(candidate: Mapping[str, Any], matrix: Mapping[str, Any]) -> bool:
    label = str(candidate.get("candidate_label") or "")
    if not label or label == "frequency":
        return False
    if label == str(matrix.get("prediction_label") or ""):
        return False
    if candidate.get("evidence_status") != "exact":
        return False
    if candidate.get("source_id_valid") is not True:
        return False
    return _parseable_label(label)


def _is_deterministic_window_parseable(
    candidate: Mapping[str, Any],
    matrix: Mapping[str, Any],
) -> bool:
    return (
        _common_eligible(candidate, matrix)
        and candidate.get("generator_name") == "deterministic_candidates_all"
        and candidate.get("candidate_kind") in {"frequency_rate", "cluster_frequency"}
        and bool(candidate.get("denominator_or_window"))
    )


def _is_deterministic_non_seizure_free_parseable(
    candidate: Mapping[str, Any],
    matrix: Mapping[str, Any],
) -> bool:
    return (
        _common_eligible(candidate, matrix)
        and candidate.get("generator_name") == "deterministic_candidates_all"
        and candidate.get("candidate_kind")
        in {"frequency_rate", "cluster_frequency", "unknown_frequency"}
    )


def _is_llm_unknown_current(
    candidate: Mapping[str, Any],
    matrix: Mapping[str, Any],
) -> bool:
    return (
        _is_llm_unknown_any(candidate, matrix)
        and str(candidate.get("temporality") or "") == "current"
    )


def _is_llm_unknown_any(
    candidate: Mapping[str, Any],
    matrix: Mapping[str, Any],
) -> bool:
    return (
        _common_eligible(candidate, matrix)
        and candidate.get("generator_name") == "llm_candidate_selector_raw"
        and candidate.get("candidate_label") == "unknown"
    )


def _is_nonprediction_llm_unknown_current(
    candidate: Mapping[str, Any],
    matrix: Mapping[str, Any],
) -> bool:
    return _is_nonprediction(matrix) and _is_llm_unknown_current(candidate, matrix)


def _is_nonprediction_llm_unknown_any(
    candidate: Mapping[str, Any],
    matrix: Mapping[str, Any],
) -> bool:
    return _is_nonprediction(matrix) and _is_llm_unknown_any(candidate, matrix)


def _is_nonprediction(matrix: Mapping[str, Any]) -> bool:
    return str(matrix.get("final_action") or "") != "predict"


def _candidate_rank(candidate: Mapping[str, Any]) -> tuple[int, int, str, str]:
    missing = candidate.get("metadata_missing_fields") or []
    kind_rank = {
        "frequency_rate": 0,
        "cluster_frequency": 1,
        "unknown_frequency": 2,
    }.get(str(candidate.get("candidate_kind") or ""), 9)
    return (
        len(missing),
        kind_rank,
        str(candidate.get("candidate_label") or ""),
        str(candidate.get("candidate_id") or ""),
    )


def _transition(base_correct: bool, candidate_correct: bool) -> str:
    if base_correct and candidate_correct:
        return "C_to_C"
    if base_correct and not candidate_correct:
        return "C_to_W"
    if not base_correct and candidate_correct:
        return "W_to_C"
    return "W_to_W"


def _parseable_label(label: str) -> bool:
    try:
        label_to_frequency_record(label)
    except ValueError:
        return False
    return True


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).lower() == "true"


def _selector_decision(w_to_c: int, c_to_w: int) -> str:
    if w_to_c > 0 and c_to_w == 0:
        return "promote_candidate"
    if w_to_c > c_to_w:
        return "diagnostic_positive_but_not_promotable"
    return "reject"


def _recommended_next_step(selector_summaries: Mapping[str, Mapping[str, Any]]) -> str:
    useful = [
        (name, summary)
        for name, summary in selector_summaries.items()
        if summary["selected_transition_counts"].get("W_to_C", 0)
        > summary["selected_transition_counts"].get("C_to_W", 0)
    ]
    if not useful:
        return (
            "Reject these broad selectors. They select many already-correct rows "
            "without enough recoveries, so the next iteration needs a narrower "
            "mechanism or a verifier targeted to the recoverable failure families."
        )
    best_name, best_summary = max(
        useful,
        key=lambda item: item[1]["projected_correct_rows"],
    )
    return (
        f"`{best_name}` is the least-bad diagnostic selector with projected "
        f"{best_summary['projected_correct_rows']} correct rows, but promotion "
        "still depends on proving low C->W risk on a predeclared validation or "
        "synthetic hard-slice gate."
    )


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _format_rate(value: float) -> str:
    return f"{value:.4f}"
