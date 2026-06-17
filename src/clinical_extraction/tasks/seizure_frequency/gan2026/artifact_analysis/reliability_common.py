"""Shared primitives for the Gan 2026 reliability scorecard (Phase 0/1 drivers).

This module exists so every reliability driver reads the *same* canonical
subject layer and computes the *same* statistics. Per decision 0018, the
canonical scorecard subject is the frozen production single GPT structured-event
pass on ``gpt-4.1-mini``, read per row from the ``v0_reference`` layer of the V12
fresh-evidence-reasoner artifacts. Helpers here return that layer; comparator
layers (``score_layers.final`` = full-gpt-4.1 V12; rq9 router) must be requested
explicitly by the caller and tagged as comparators.

No model calls. Pure deterministic re-analysis over saved JSONL/JSON. Every
function is idempotent: re-running a driver re-derives identical output from the
frozen artifacts, which is the resumability contract for a no-call replay.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

# ── Canonical artifact registry (the only place paths are named) ────────────────

EXPERIMENTS = Path("experiments")

REASONER_TEST450 = (
    EXPERIMENTS
    / "gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_4_2026-06-13.jsonl"
)
REASONER_VALIDATION750 = (
    EXPERIMENTS
    / "gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13.jsonl"
)
CONSENSUS_VALIDATION750 = (
    EXPERIMENTS
    / "gan2026_agentic_structured_event_consensus_unanimous_exact_validation750_2026-06-13.jsonl"
)
CONSENSUS_TWO_AGENT_TEST450 = (
    EXPERIMENTS
    / "gan2026_agentic_structured_event_consensus_available_two_agent_exact_test450_2026-06-13.jsonl"
)
RQ9_ROUTER = EXPERIMENTS / "gan2026_rq9_selective_action_router_v3_2026-06-04.jsonl"
HARD50_SELF_CONSISTENCY = (
    EXPERIMENTS / "gan2026_agentic_hard50_tool_self_consistency_2026-06-12.jsonl"
)
SE_MINI_VALIDATION750 = (
    EXPERIMENTS
    / "gan2026_three_way_comparison_validation750_hybrid_structured_events_gpt41mini_2026-06-07.jsonl"
)
ROBUSTNESS_BATTERY = {
    "direct_labeler_v0_5": EXPERIMENTS
    / "gan2026_robustness_battery_v1_gpt41mini_2026-06-15.json",
    "evidence_v0_6": EXPERIMENTS
    / "gan2026_robustness_battery_v1_evidence_v0_6_gpt41mini_2026-06-15.json",
    "evidence_v0_7": EXPERIMENTS
    / "gan2026_robustness_battery_v1_evidence_v0_7_gpt41mini_2026-06-15.json",
}
ROBUSTNESS_CASES = EXPERIMENTS / "gan2026_robustness_battery_v1_cases.json"


# ── BOM-safe loaders ────────────────────────────────────────────────────────────

def load_jsonl(path: Path, *, skip_metadata: bool = True) -> list[dict[str, Any]]:
    """Load a JSONL artifact, tolerating a UTF-8 BOM and a leading
    ``{"_metadata": ...}`` header row (which the consensus artifacts carry)."""
    rows: list[dict[str, Any]] = []
    with open(path, encoding="utf-8-sig") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if skip_metadata and isinstance(obj, dict) and set(obj.keys()) == {"_metadata"}:
                continue
            rows.append(obj)
    return rows


def load_metadata(path: Path) -> dict[str, Any] | None:
    """Return the ``_metadata`` header of a JSONL artifact if present."""
    with open(path, encoding="utf-8-sig") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if isinstance(obj, dict) and "_metadata" in obj:
                return obj["_metadata"]
            return None
    return None


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


# ── Canonical subject accessors (decision 0018) ─────────────────────────────────

def subject_layer(row: Mapping[str, Any]) -> dict[str, Any]:
    """The canonical subject layer: single-SE-mini, byte-identical to the
    standalone mini run. Read every scorecard subject metric from here."""
    return row.get("v0_reference") or {}


def subject_purist_correct(row: Mapping[str, Any]) -> bool:
    return bool((subject_layer(row).get("comparison") or {}).get("purist_correct"))


def subject_pragmatic_correct(row: Mapping[str, Any]) -> bool:
    return bool((subject_layer(row).get("comparison") or {}).get("pragmatic_correct"))


def subject_evidence_valid(row: Mapping[str, Any]) -> bool:
    return bool(subject_layer(row).get("evidence_valid"))


def subject_predicted_purist(row: Mapping[str, Any]) -> str | None:
    return (subject_layer(row).get("comparison") or {}).get("predicted_purist_category")


def subject_gold_purist(row: Mapping[str, Any]) -> str | None:
    return (subject_layer(row).get("comparison") or {}).get("gold_purist_category")


def subject_final_label(row: Mapping[str, Any]) -> str | None:
    return subject_layer(row).get("final_label")


def subject_final_kind(row: Mapping[str, Any]) -> str | None:
    return subject_layer(row).get("final_kind")


def comparator_final_purist_correct(row: Mapping[str, Any]) -> bool:
    """``[comparator: V12-full-gpt4.1]`` final-layer Purist (the 0.842 ceiling)."""
    final = (row.get("score_layers") or {}).get("final") or {}
    return bool((final.get("comparison") or {}).get("purist_correct"))


def comparator_final_evidence_valid(row: Mapping[str, Any]) -> bool:
    """The full-gpt-4.1 V12 ``evidence_valid`` (703/750, 423/450 figures)."""
    return bool(row.get("evidence_valid"))


def gold_monthly(row: Mapping[str, Any]) -> float | None:
    ref = row.get("reference") or {}
    value = ref.get("gold_monthly_frequency")
    if value is None:
        value = (subject_layer(row).get("comparison") or {}).get("gold_monthly_frequency")
    return value


# ── Cross-model agreement (consensus votes) ─────────────────────────────────────

def agreement_count_by_source_index(consensus_rows: Sequence[Mapping[str, Any]]) -> dict[int, int]:
    """Map ``source_row_index`` -> size of the largest cluster of identical
    agent ``final_label`` votes (3 = unanimous, 2 = majority, 1 = all differ).

    This is the [[Cross-Model Agreement Count]] leg of the External Risk Score.
    """
    out: dict[int, int] = {}
    for row in consensus_rows:
        decision = row.get("consensus_decision") or {}
        votes = decision.get("votes") or []
        idx = row.get("source_row_index")
        if idx is None:
            idx = decision.get("source_row_index")
        if idx is None:
            continue
        labels = [str(v.get("final_label")) for v in votes if v.get("final_label") is not None]
        if not labels:
            out[int(idx)] = 0
            continue
        counts: dict[str, int] = {}
        for lab in labels:
            counts[lab] = counts.get(lab, 0) + 1
        out[int(idx)] = max(counts.values())
    return out


def rq9_boundary_features_by_source_index(rq9_rows: Sequence[Mapping[str, Any]]) -> dict[int, dict[str, Any]]:
    """Map ``source_row_index`` -> the router packet's boundary_features
    (``source_has_*`` flags, ``ambiguity_reasons``)."""
    out: dict[int, dict[str, Any]] = {}
    for row in rq9_rows:
        packet = row.get("router_packet") or {}
        idx = packet.get("source_row_index")
        if idx is None:
            idx = row.get("source_candidate", {}).get("source_row_index")
        if idx is None:
            continue
        out[int(idx)] = packet.get("boundary_features") or {}
    return out


# ── Statistics ──────────────────────────────────────────────────────────────────

def wilson_interval(successes: int, total: int, *, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion (95% default)."""
    if total == 0:
        return (0.0, 0.0)
    phat = successes / total
    denom = 1 + z * z / total
    centre = phat + z * z / (2 * total)
    margin = z * math.sqrt((phat * (1 - phat) + z * z / (4 * total)) / total)
    return ((centre - margin) / denom, (centre + margin) / denom)


def expected_calibration_error(
    pairs: Sequence[tuple[float, bool]], *, n_bins: int = 10
) -> tuple[float, list[dict[str, Any]]]:
    """ECE over (score, outcome) pairs where score is a P(correct) in [0,1].

    Returns (ece, bins) with one dict per occupied bin for a reliability diagram.
    """
    bins: list[list[tuple[float, bool]]] = [[] for _ in range(n_bins)]
    for score, outcome in pairs:
        s = min(max(float(score), 0.0), 1.0)
        b = min(int(s * n_bins), n_bins - 1)
        bins[b].append((s, outcome))
    total = len(pairs)
    ece = 0.0
    table: list[dict[str, Any]] = []
    for i, bucket in enumerate(bins):
        if not bucket:
            continue
        conf = sum(s for s, _ in bucket) / len(bucket)
        acc = sum(1 for _, o in bucket if o) / len(bucket)
        ece += (len(bucket) / total) * abs(acc - conf)
        table.append(
            {
                "bin": f"[{i / n_bins:.1f},{(i + 1) / n_bins:.1f})",
                "n": len(bucket),
                "mean_score": conf,
                "empirical_accuracy": acc,
                "gap": acc - conf,
            }
        )
    return ece, table


def brier_score(pairs: Sequence[tuple[float, bool]]) -> float:
    if not pairs:
        return float("nan")
    return sum((float(s) - (1.0 if o else 0.0)) ** 2 for s, o in pairs) / len(pairs)


def auroc(scores: Sequence[float], labels: Sequence[bool]) -> float:
    """AUROC via the Mann-Whitney U statistic, with tie handling.

    ``labels`` True = positive class (here: the event we want the score to
    predict, e.g. *failure*). Returns 0.5 for degenerate single-class input.
    """
    pos = [s for s, y in zip(scores, labels) if y]
    neg = [s for s, y in zip(scores, labels) if not y]
    if not pos or not neg:
        return float("nan")
    ranked = sorted(zip(scores, labels), key=lambda t: t[0])
    # average ranks for ties
    ranks: list[float] = [0.0] * len(ranked)
    i = 0
    while i < len(ranked):
        j = i
        while j + 1 < len(ranked) and ranked[j + 1][0] == ranked[i][0]:
            j += 1
        avg_rank = (i + j) / 2 + 1  # 1-based average rank
        for k in range(i, j + 1):
            ranks[k] = avg_rank
        i = j + 1
    sum_ranks_pos = sum(r for r, (_, y) in zip(ranks, ranked) if y)
    n_pos, n_neg = len(pos), len(neg)
    u = sum_ranks_pos - n_pos * (n_pos + 1) / 2
    return u / (n_pos * n_neg)


def fmt_pct(n: int, d: int) -> str:
    return f"{n / d:.1%}" if d else "—"


def provenance_block(*, subject: str, sources: Iterable[Path]) -> dict[str, Any]:
    """Standard provenance stamp embedded in every reliability artifact."""
    return {
        "canonical_subject": subject,
        "decision": "0018-reliability-scorecard-canonical-subject-is-v0reference-single-se-mini",
        "model_calls": 0,
        "replay": "deterministic_no_call",
        "sources": [str(p) for p in sources],
    }
