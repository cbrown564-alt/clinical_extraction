"""Exploratory analysis: do uncertainty/confidence signals correlate with accuracy?

Covers:
  - llm_only_direct_labeler: confidence (low/medium/high) x purist_correct
  - llm_only_canonical_pipeline: confidence x purist_correct
  - llm_only_direct_labeler + canonical: answer_kind x accuracy
  - hybrid_structured_events: answer_kind (predicted_purist_category) x accuracy
  - hybrid: assessment_kind / aggregation_policy / uncertainty_flags distributions
    (no per-row accuracy without deep-replay; shown as distributions only)

Run from repo root:
    uv run python experiments/explore_uncertainty_signals.py
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

# ── file registry ──────────────────────────────────────────────────────────────

FILES = {
    "direct_labeler_gpt41mini": Path(
        "experiments/gan2026_three_way_comparison_validation750"
        "_llm_only_direct_labeler_gpt41mini_2026-06-07.jsonl"
    ),
    "direct_labeler_qwen": Path(
        "experiments/gan2026_three_way_comparison_validation750"
        "_llm_only_direct_labeler_qwen3635b_2026-06-08.jsonl"
    ),
    "direct_labeler_deepseek": Path(
        "experiments/gan2026_three_way_comparison_validation750"
        "_llm_only_direct_labeler_deepseek_2026-06-08.jsonl"
    ),
    "canonical_gpt41mini": Path(
        "experiments/gan2026_three_way_comparison_validation750"
        "_llm_only_canonical_pipeline_gpt41mini_2026-06-07.jsonl"
    ),
    "canonical_qwen": Path(
        "experiments/gan2026_three_way_comparison_validation750"
        "_llm_only_canonical_pipeline_qwen3635b_2026-06-08.jsonl"
    ),
    "canonical_deepseek": Path(
        "experiments/gan2026_three_way_comparison_validation750"
        "_llm_only_canonical_pipeline_deepseek_2026-06-08.jsonl"
    ),
    "structured_events_gpt41mini": Path(
        "experiments/gan2026_three_way_comparison_validation750"
        "_hybrid_structured_events_gpt41mini_2026-06-07.jsonl"
    ),
    "structured_events_qwen": Path(
        "experiments/gan2026_three_way_comparison_validation750"
        "_hybrid_structured_events_qwen3635b_2026-06-08.jsonl"
    ),
    "structured_events_deepseek": Path(
        "experiments/gan2026_three_way_comparison_validation750"
        "_hybrid_structured_events_deepseek_2026-06-08.jsonl"
    ),
    "hybrid_gpt41mini": Path(
        "experiments/gan2026_three_way_comparison_validation750"
        "_hybrid_live_candidate_sets_gpt41mini_2026-06-08.jsonl"
    ),
    "hybrid_deepseek": Path(
        "experiments/gan2026_three_way_comparison_validation750_hybrid_deepseek_2026-06-08.jsonl"
    ),
    "hybrid_qwen": Path(
        "experiments/gan2026_three_way_comparison_validation750_hybrid_qwen3635b_2026-06-08.jsonl"
    ),
}


def load(key: str) -> list[dict]:
    path = FILES[key]
    if not path.exists():
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


# ── helpers ────────────────────────────────────────────────────────────────────


def pct(n: int, d: int) -> str:
    return f"{n / d:.1%}" if d else "—"


def accuracy_by_group(
    rows: list[dict],
    group_fn,
    *,
    correct_fn=None,
) -> dict[str, tuple[int, int]]:
    """Return {group: (correct, total)} sorted by total desc."""
    correct_fn = correct_fn or (lambda r: bool((r.get("comparison") or {}).get("purist_correct")))
    buckets: dict[str, list[bool]] = defaultdict(list)
    for row in rows:
        g = group_fn(row)
        buckets[g].append(correct_fn(row))
    return {g: (sum(v), len(v)) for g, v in sorted(buckets.items(), key=lambda kv: -len(kv[1]))}


def print_table(title: str, data: dict[str, tuple[int, int]], note: str = "") -> None:
    print(f"\n### {title}")
    if note:
        print(f"    ({note})")
    print(f"  {'Group':<35} {'Correct':>8} {'Total':>7} {'Accuracy':>9}")
    print(f"  {'-' * 35} {'-' * 8} {'-' * 7} {'-' * 9}")
    for group, (correct, total) in data.items():
        print(f"  {group:<35} {correct:>8} {total:>7} {pct(correct, total):>9}")


def print_dist(title: str, counter: Counter, total: int, note: str = "") -> None:
    print(f"\n### {title}")
    if note:
        print(f"    ({note})")
    print(f"  {'Value':<40} {'Count':>7} {'Share':>8}")
    print(f"  {'-' * 40} {'-' * 7} {'-' * 8}")
    for val, count in counter.most_common():
        print(f"  {str(val):<40} {count:>7} {pct(count, total):>8}")


# ── Section 1: confidence x accuracy (direct_labeler, canonical) ───────────────

CONF_ARCHITECTURES = {
    "direct_labeler_gpt41mini": "llm_only_direct_labeler / gpt-4.1-mini",
    "direct_labeler_qwen": "llm_only_direct_labeler / qwen3.6-35b",
    "direct_labeler_deepseek": "llm_only_direct_labeler / deepseek-v4-flash",
    "canonical_gpt41mini": "llm_only_canonical_pipeline / gpt-4.1-mini",
    "canonical_qwen": "llm_only_canonical_pipeline / qwen3.6-35b",
    "canonical_deepseek": "llm_only_canonical_pipeline / deepseek-v4-flash",
}

print("\n" + "=" * 70)
print("SECTION 1: confidence (low/medium/high) × purist accuracy")
print("  Fields: decision_record.confidence, comparison.purist_correct")
print("=" * 70)

conf_summary: dict[str, dict[str, tuple[int, int]]] = {}
for key, label in CONF_ARCHITECTURES.items():
    rows = load(key)
    if not rows:
        print(f"\n  [{label}] — file not found, skipping")
        continue
    data = accuracy_by_group(
        rows,
        group_fn=lambda r: (r.get("decision_record") or {}).get("confidence") or "missing",
    )
    conf_summary[label] = data
    print_table(label, data)

# Cross-model view: aggregate confidence accuracy across all models per confidence level
print("\n### Cross-architecture confidence accuracy (raw counts)")
print("  Aggregated across both direct_labeler and canonical_pipeline, all models")
agg: dict[str, list[bool]] = defaultdict(list)
for key in CONF_ARCHITECTURES:
    rows = load(key)
    for row in rows:
        conf = (row.get("decision_record") or {}).get("confidence") or "missing"
        correct = bool((row.get("comparison") or {}).get("purist_correct"))
        agg[conf].append(correct)
agg_data = {g: (sum(v), len(v)) for g, v in sorted(agg.items(), key=lambda kv: -len(kv[1]))}
print_table("All confidence-bearing architectures combined", agg_data)


# ── Section 2: answer_kind × accuracy ──────────────────────────────────────────

AK_ARCHITECTURES = {
    "direct_labeler_gpt41mini": ("llm_only_direct_labeler / gpt-4.1-mini", "decision_record"),
    "direct_labeler_qwen": ("llm_only_direct_labeler / qwen3.6-35b", "decision_record"),
    "direct_labeler_deepseek": ("llm_only_direct_labeler / deepseek", "decision_record"),
    "canonical_gpt41mini": ("llm_only_canonical_pipeline / gpt-4.1-mini", "decision_record"),
    "canonical_qwen": ("llm_only_canonical_pipeline / qwen3.6-35b", "decision_record"),
    "canonical_deepseek": ("llm_only_canonical_pipeline / deepseek", "decision_record"),
}

print("\n" + "=" * 70)
print("SECTION 2: answer_kind × purist accuracy")
print("  (answer_kind encodes the model's own classification of the outcome)")
print("=" * 70)

for key, (label, record_key) in AK_ARCHITECTURES.items():
    rows = load(key)
    if not rows:
        continue
    data = accuracy_by_group(
        rows,
        group_fn=lambda r, rk=record_key: (r.get(rk) or {}).get("answer_kind") or "missing",
    )
    print_table(label, data)

# structured_events: uses predicted_purist_category as its "kind" proxy
print("\n### hybrid_structured_events — predicted_purist_category × accuracy")
print("    (no confidence or answer_kind field; scoring category is the closest proxy)")
for key in ("structured_events_gpt41mini", "structured_events_qwen", "structured_events_deepseek"):
    rows = load(key)
    if not rows:
        continue
    label = key.replace("structured_events_", "structured_events / ").replace("_", " ")
    data = accuracy_by_group(
        rows,
        group_fn=lambda r: str(
            (r.get("comparison") or {}).get("predicted_purist_category") or "missing"
        ),
    )
    print_table(label, data)


# ── Section 3: confidence × answer_kind joint distribution ────────────────────

print("\n" + "=" * 70)
print("SECTION 3: confidence × answer_kind joint distribution")
print("  Do low-confidence rows cluster on particular answer_kinds?")
print("=" * 70)

for key in ("direct_labeler_gpt41mini", "canonical_gpt41mini"):
    rows = load(key)
    if not rows:
        continue
    label = (
        "direct_labeler / gpt-4.1-mini" if "direct" in key else "canonical_pipeline / gpt-4.1-mini"
    )
    joint: Counter = Counter()
    for row in rows:
        dr = row.get("decision_record") or {}
        conf = dr.get("confidence") or "missing"
        ak = dr.get("answer_kind") or "missing"
        joint[(conf, ak)] += 1
    total = sum(joint.values())
    print(f"\n### {label} (n={total})")
    print(f"  {'confidence × answer_kind':<45} {'Count':>7} {'Share':>8} {'Purist%':>8}")
    print(f"  {'-' * 45} {'-' * 7} {'-' * 8} {'-' * 8}")
    # compute per-cell accuracy
    cell_acc: dict[tuple, list[bool]] = defaultdict(list)
    for row in rows:
        dr = row.get("decision_record") or {}
        conf = dr.get("confidence") or "missing"
        ak = dr.get("answer_kind") or "missing"
        correct = bool((row.get("comparison") or {}).get("purist_correct"))
        cell_acc[(conf, ak)].append(correct)
    for cell, count in joint.most_common(20):
        acc_list = cell_acc[cell]
        acc_str = pct(sum(acc_list), len(acc_list))
        print(f"  {str(cell):<45} {count:>7} {pct(count, total):>8} {acc_str:>8}")


# ── Section 4: hybrid uncertainty signals (distributions only) ─────────────────

print("\n" + "=" * 70)
print("SECTION 4: hybrid uncertainty signal distributions")
print("  Per-row accuracy unavailable without deep-replay. Distributions only.")
print("=" * 70)

HYBRID_KEYS = {
    "hybrid_gpt41mini": "hybrid / gpt-4.1-mini",
    "hybrid_deepseek": "hybrid / deepseek-v4-flash",
    "hybrid_qwen": "hybrid / qwen3.6-35b",
}

for key, label in HYBRID_KEYS.items():
    rows = load(key)
    if not rows:
        print(f"\n  [{label}] — file not found, skipping")
        continue

    # filter to real assessment rows (exclude candidate_set_missing)
    assessment_rows = [r for r in rows if r.get("clinical_assessment")]
    placeholder_count = len(rows) - len(assessment_rows)
    print(
        f"\n### {label}: {len(assessment_rows)} real assessment rows"
        f"{f', {placeholder_count} candidate_set_missing' if placeholder_count else ''}"
    )

    # assessment_kind
    ak_counter: Counter = Counter(
        (r.get("clinical_assessment") or {}).get("assessment_kind") or "missing"
        for r in assessment_rows
    )
    print_dist("  assessment_kind distribution", ak_counter, len(assessment_rows))

    # aggregation_policy
    ap_counter: Counter = Counter(
        (r.get("clinical_assessment") or {}).get("aggregation_policy") or "missing"
        for r in assessment_rows
    )
    print_dist("  aggregation_policy distribution", ap_counter, len(assessment_rows))

    # uncertainty_flags: flatten all flags across rows
    flag_counter: Counter = Counter()
    rows_with_flags = 0
    rows_no_flags = 0
    for r in assessment_rows:
        flags = (r.get("clinical_assessment") or {}).get("uncertainty_flags") or []
        if flags:
            rows_with_flags += 1
            for f in flags:
                flag_counter[f] += 1
        else:
            rows_no_flags += 1
    print(
        f"\n  uncertainty_flags: rows_with_flags={rows_with_flags} "
        f"({pct(rows_with_flags, len(assessment_rows))}), "
        f"rows_no_flags={rows_no_flags} ({pct(rows_no_flags, len(assessment_rows))})"
    )
    if flag_counter:
        print_dist("  uncertainty_flags (by flag value)", flag_counter, rows_with_flags)
    else:
        print("    (no uncertainty_flags observed)")

    # normalization_issues: rows with any issues
    issues_rows = sum(
        1
        for r in assessment_rows
        if (r.get("clinical_assessment") or {}).get("normalization_issues")
    )
    print(
        f"\n  normalization_issues: rows_with_issues={issues_rows} "
        f"({pct(issues_rows, len(assessment_rows))})"
    )


# ── Section 5: confidence calibration summary ──────────────────────────────────

print("\n" + "=" * 70)
print("SECTION 5: calibration summary — expected vs observed accuracy by confidence")
print("=" * 70)

CONF_ORDER = ["high", "medium", "low"]
print(f"\n  {'Architecture':<45} {'conf':>6} {'correct':>8} {'total':>7} {'accuracy':>9}")
print(f"  {'-' * 45} {'-' * 6} {'-' * 8} {'-' * 7} {'-' * 9}")

for key, label in CONF_ARCHITECTURES.items():
    rows = load(key)
    if not rows:
        continue
    buckets: dict[str, list[bool]] = defaultdict(list)
    for row in rows:
        conf = (row.get("decision_record") or {}).get("confidence") or "missing"
        correct = bool((row.get("comparison") or {}).get("purist_correct"))
        buckets[conf].append(correct)
    for conf in CONF_ORDER:
        v = buckets.get(conf, [])
        correct_n = sum(v)
        total_n = len(v)
        print(f"  {label:<45} {conf:>6} {correct_n:>8} {total_n:>7} {pct(correct_n, total_n):>9}")
    print()
