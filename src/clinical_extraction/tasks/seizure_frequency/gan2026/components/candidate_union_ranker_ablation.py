"""Candidate-union ranker ablations for Gan 2026 hard panels."""

from __future__ import annotations

import csv
import json
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_purist

POLICY_NAME = "gan2026_candidate_union_ranker_ablation_v0"

FIELDNAMES = [
    "ranker_name",
    "source_row_index",
    "gold_label",
    "comparator_label",
    "comparator_correct",
    "selected_candidate_id",
    "selected_candidate_label",
    "selected_candidate_kind",
    "selected_candidate_rule_id",
    "selected_candidate_provenance",
    "selected_candidate_evidence",
    "selected_candidate_correct",
    "selected_transition",
]

Ranker = Callable[[Mapping[str, Any]], Mapping[str, Any] | None]


def build_ranker_ablation_rows(
    selected_state_union_rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Apply non-gold rankers to selected-state union rows."""

    rows: list[dict[str, Any]] = []
    for ranker_name, ranker in _rankers().items():
        for source_row in selected_state_union_rows:
            candidate = ranker(source_row)
            if not candidate:
                continue
            comparator_correct = bool(source_row["comparison"]["comparator_correct"])
            gold_label = str(source_row.get("gold_label") or "")
            selected_label = str(candidate.get("normalized_label") or "")
            candidate_correct = _purist_correct(selected_label, gold_label)
            rows.append(
                {
                    "ranker_name": ranker_name,
                    "source_row_index": int(source_row["source_row_index"]),
                    "gold_label": gold_label,
                    "comparator_label": (
                        source_row.get("comparator_selected_state_replay") or {}
                    ).get("label"),
                    "comparator_correct": comparator_correct,
                    "selected_candidate_id": candidate.get("candidate_id"),
                    "selected_candidate_label": selected_label,
                    "selected_candidate_kind": candidate.get("candidate_kind"),
                    "selected_candidate_rule_id": _rule_id(candidate),
                    "selected_candidate_provenance": "|".join(
                        str(item) for item in candidate.get("provenance") or []
                    ),
                    "selected_candidate_evidence": candidate.get("evidence"),
                    "selected_candidate_correct": candidate_correct,
                    "selected_transition": _transition(
                        comparator_correct,
                        candidate_correct,
                    ),
                }
            )
    rows.sort(key=lambda row: (row["ranker_name"], int(row["source_row_index"])))
    return rows


def summarize_ranker_ablation_rows(
    rows: Sequence[Mapping[str, Any]],
    selected_state_union_rows: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Summarize hard-panel ranker transitions."""

    base_correct_rows = sum(
        bool(row["comparison"]["comparator_correct"])
        for row in selected_state_union_rows
    )
    total_rows = len(selected_state_union_rows)
    oracle_rows = _oracle_recoverable_rows(selected_state_union_rows)
    ranker_summaries = {}
    for ranker_name in _rankers():
        selected = [row for row in rows if row["ranker_name"] == ranker_name]
        transitions = Counter(str(row["selected_transition"]) for row in selected)
        kinds = Counter(str(row["selected_candidate_kind"]) for row in selected)
        rules = Counter(str(row["selected_candidate_rule_id"]) for row in selected)
        w_to_c = transitions["W_to_C"]
        c_to_w = transitions["C_to_W"]
        projected_correct_rows = base_correct_rows + w_to_c - c_to_w
        ranker_summaries[ranker_name] = {
            "selected_rows": len(selected),
            "selected_transition_counts": dict(sorted(transitions.items())),
            "selected_candidate_kind_counts": dict(sorted(kinds.items())),
            "selected_candidate_rule_counts": dict(sorted(rules.items())),
            "base_correct_rows": base_correct_rows,
            "projected_correct_rows": projected_correct_rows,
            "projected_purist_proxy": _rate(projected_correct_rows, total_rows),
            "changed_label_precision": _rate(w_to_c, w_to_c + c_to_w),
            "decision": _decision(w_to_c, c_to_w),
        }
    best_ranker = max(
        ranker_summaries,
        key=lambda name: ranker_summaries[name]["projected_correct_rows"],
    )
    return {
        "component_name": "candidate_union_ranker_ablation",
        "policy_name": POLICY_NAME,
        "row_count": len(rows),
        "hard_panel_rows": total_rows,
        "base_correct_rows": base_correct_rows,
        "base_purist_proxy": _rate(base_correct_rows, total_rows),
        "oracle_recoverable_miss_rows": len(oracle_rows),
        "oracle_upper_bound_correct_rows": base_correct_rows + len(oracle_rows),
        "oracle_upper_bound_purist_proxy": _rate(
            base_correct_rows + len(oracle_rows),
            total_rows,
        ),
        "rankers": ranker_summaries,
        "best_ranker_by_projected_correct": best_ranker,
        "claim_language": (
            "Validation hard-panel ranker ablation over selected-state union "
            "candidates. Ranker selection uses non-gold candidate features; gold "
            "labels are used only after selection for W->C/C->W accounting. This "
            "does not change production predictions, scorer policy, split policy, "
            "or locked-test behavior."
        ),
        "recommended_next_step": _recommended_next_step(ranker_summaries),
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
        "# Gan 2026 Candidate-Union Ranker Ablation",
        "",
        str(summary["claim_language"]),
        "",
        "## Summary",
        "",
        f"Base hard-panel Purist proxy: {_format_rate(summary['base_purist_proxy'])} "
        f"({summary['base_correct_rows']} / {summary['hard_panel_rows']}).",
        (
            "Oracle recoverable miss rows: "
            f"{summary['oracle_recoverable_miss_rows']}; oracle upper bound "
            f"{_format_rate(summary['oracle_upper_bound_purist_proxy'])}."
        ),
        "",
        "| Ranker | Selected | W->C | C->W | Projected proxy | Decision |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for ranker_name, ranker in summary["rankers"].items():
        transitions = ranker["selected_transition_counts"]
        lines.append(
            f"| `{ranker_name}` | {ranker['selected_rows']} | "
            f"{transitions.get('W_to_C', 0)} | {transitions.get('C_to_W', 0)} | "
            f"{_format_rate(ranker['projected_purist_proxy'])} | "
            f"`{ranker['decision']}` |"
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
            f"- Ranker CSV: `{csv_path}`",
            f"- Ranker JSON: `{json_path}`",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _rankers() -> dict[str, Ranker]:
    return {
        "diary_log_only_v0": _diary_log_only,
        "comparator_absent_quality_rank_v0": _comparator_absent_quality_rank,
        "comparator_absent_structural_guard_rank_v0": (
            _comparator_absent_structural_guard_rank
        ),
        "unknown_or_cluster_frequency_rank_v0": _unknown_or_cluster_frequency_rank,
    }


def _diary_log_only(row: Mapping[str, Any]) -> Mapping[str, Any] | None:
    return _first_ranked_candidate(
        row,
        lambda candidate: _rule_id(candidate).startswith("diary.")
        and _label_differs(candidate, row),
    )


def _comparator_absent_quality_rank(row: Mapping[str, Any]) -> Mapping[str, Any] | None:
    if not _comparator_absent_from_union(row):
        return None
    return _first_ranked_candidate(row, lambda candidate: _label_differs(candidate, row))


def _comparator_absent_structural_guard_rank(
    row: Mapping[str, Any],
) -> Mapping[str, Any] | None:
    if not _comparator_absent_from_union(row):
        return None
    comparator_label = _comparator_label(row)
    return _first_ranked_candidate(
        row,
        lambda candidate: _label_differs(candidate, row)
        and not _is_live_boundary_cluster(candidate)
        and candidate.get("candidate_kind") != "seizure_free"
        and _preserves_cluster_structure(candidate, comparator_label),
    )


def _unknown_or_cluster_frequency_rank(
    row: Mapping[str, Any],
) -> Mapping[str, Any] | None:
    comparator_label = _comparator_label(row)
    if "unknown" not in comparator_label and "cluster" not in comparator_label:
        return None
    return _first_ranked_candidate(
        row,
        lambda candidate: candidate.get("candidate_kind") == "frequency_rate"
        and _label_differs(candidate, row),
    )


def _first_ranked_candidate(
    row: Mapping[str, Any],
    predicate: Callable[[Mapping[str, Any]], bool],
) -> Mapping[str, Any] | None:
    candidates = [
        candidate
        for candidate in row.get("union_verified_candidates") or []
        if predicate(candidate)
    ]
    if not candidates:
        return None
    return sorted(candidates, key=_rank_key)[0]


def _rank_key(candidate: Mapping[str, Any]) -> tuple[int, str, str]:
    rule_id = _rule_id(candidate)
    kind = str(candidate.get("candidate_kind") or "")
    priority = 50
    if rule_id.startswith("diary."):
        priority = 0
    elif rule_id in {"rate.yesterday_or_today_count", "cluster.vague_days_over_period"}:
        priority = 1
    elif rule_id.startswith(("rate.occurring_adjective", "rate.seizure_adjective")):
        priority = 2
    elif rule_id.startswith("rate.direct_count_per_period"):
        priority = 3
    elif kind == "cluster_frequency":
        priority = 4
    elif kind == "frequency_rate":
        priority = 5
    elif kind == "unknown_frequency":
        priority = 6
    elif kind == "no_reference":
        priority = 9
    elif kind == "seizure_free":
        priority = 10
    return (
        priority,
        str(candidate.get("normalized_label") or ""),
        str(candidate.get("candidate_id") or ""),
    )


def _label_differs(candidate: Mapping[str, Any], row: Mapping[str, Any]) -> bool:
    return str(candidate.get("normalized_label") or "") != _comparator_label(row)


def _comparator_absent_from_union(row: Mapping[str, Any]) -> bool:
    comparator_label = _comparator_label(row)
    union_labels = {
        str(candidate.get("normalized_label") or "")
        for candidate in row.get("union_verified_candidates") or []
    }
    return comparator_label not in union_labels


def _comparator_label(row: Mapping[str, Any]) -> str:
    return str((row.get("comparator_selected_state_replay") or {}).get("label") or "")


def _is_live_boundary_cluster(candidate: Mapping[str, Any]) -> bool:
    return candidate.get("candidate_kind") == "cluster_frequency" and (
        "live_llm_boundary_proposal_v3" in set(candidate.get("provenance") or [])
    )


def _preserves_cluster_structure(
    candidate: Mapping[str, Any],
    comparator_label: str,
) -> bool:
    if "cluster" not in comparator_label:
        return True
    return "cluster" in str(candidate.get("normalized_label") or "") or _rule_id(
        candidate
    ).startswith("diary.")


def _oracle_recoverable_rows(rows: Sequence[Mapping[str, Any]]) -> list[int]:
    source_rows = []
    for row in rows:
        if bool(row["comparison"]["comparator_correct"]):
            continue
        gold_label = str(row.get("gold_label") or "")
        if any(
            _purist_correct(str(candidate.get("normalized_label") or ""), gold_label)
            for candidate in row.get("union_verified_candidates") or []
        ):
            source_rows.append(int(row["source_row_index"]))
    return source_rows


def _purist_correct(label: str, gold_label: str) -> bool:
    if label == gold_label:
        return True
    predicted = _purist_category(label)
    gold = _purist_category(gold_label)
    return bool(predicted and gold and predicted == gold)


def _purist_category(label: str) -> str | None:
    try:
        record = label_to_frequency_record(label)
    except ValueError:
        return None
    return str(map_purist(record.monthly_frequency))


def _rule_id(candidate: Mapping[str, Any]) -> str:
    return str((candidate.get("metadata") or {}).get("rule_id") or "")


def _transition(base_correct: bool, candidate_correct: bool) -> str:
    if base_correct and candidate_correct:
        return "C_to_C"
    if base_correct and not candidate_correct:
        return "C_to_W"
    if not base_correct and candidate_correct:
        return "W_to_C"
    return "W_to_W"


def _decision(w_to_c: int, c_to_w: int) -> str:
    if w_to_c > 0 and c_to_w == 0:
        return "promote_candidate"
    if w_to_c > c_to_w:
        return "diagnostic_positive_but_not_promotable"
    return "reject"


def _recommended_next_step(ranker_summaries: Mapping[str, Mapping[str, Any]]) -> str:
    clean = [
        (name, summary)
        for name, summary in ranker_summaries.items()
        if summary["selected_transition_counts"].get("W_to_C", 0) > 0
        and summary["selected_transition_counts"].get("C_to_W", 0) == 0
    ]
    if clean:
        best_name, best_summary = max(
            clean,
            key=lambda item: item[1]["projected_correct_rows"],
        )
        return (
            f"`{best_name}` is a clean validation hard-panel signal with "
            f"{best_summary['selected_transition_counts'].get('W_to_C', 0)} W->C "
            "and 0 C->W. Expand this family with negative tests before any "
            "full-validation or holdout use."
        )
    return (
        "No ranker is safe enough to promote. Use the oracle recoverability rows "
        "to design a stronger verifier or candidate-ranker prompt over the same "
        "small union surface."
    )


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _format_rate(value: float) -> str:
    return f"{value:.4f}"
