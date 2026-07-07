"""C6: Cluster-axis RETENTION gate (no-call replay over v0.4 fresh-evidence outputs).

Gate logic:
  Fire ONLY when ALL three conditions hold:
  (a) the v0.4 final label is a PLAIN rate (has ' per ', no 'cluster', no 'unknown',
      no 'seizure free', no 'no seizure', no 'no reference', no 'multiple per');
  (b) the note clearly documents a RECURRING CLUSTER STRUCTURE — require explicit
      grouping/recurrence language ("in clusters", "group together", "runs of",
      "bursts of", "several over consecutive days", "clusters of seizures"),
      NOT merely the substring "cluster";
  (c) the rewrite changes the Purist bucket (else it's a no-op).

Rewrite: wrap the plain rate's interval as the cluster cadence form:
  e.g. "1 per 4 to 5 week" -> "1 cluster per 4 to 5 week, multiple per cluster"

Method:
  1. Apply gate to v0.4 VALIDATION750 output (no-call). Report:
     - rows touched, wrong->correct, correct->wrong, net Purist
     - new validation Purist vs 682 baseline
     - held-out-family CV (gap_robust + per-band)
  2. PRECISION CHECK: genuine-rate regressions (correct->wrong where gold is plain rate).
     STOP if any genuine-rate regression, or net Purist < 0, or not gap_robust.
  3. ONLY IF gate is clean: apply same frozen gate to v0.4 TEST450 output.
     Confirm baseline 379/450, report gated test Purist X/450 and delta.

No model calls. No holdout rows read before step 3 authorization.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from clinical_extraction.core.registry import (
    RunRegistryEntry,
    load_run_registry,
    validate_run_registry_artifacts,
    write_run_registry,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.family_cv_promotion import (
    summarize_family_holdout_cv,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.family_transitions import (
    summarize_transitions_by_family,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry_report import (
    write_run_registry_markdown,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import (
    boundary_band,
    map_purist,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    label_to_monthly_frequency,
)

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
REGISTRY_PATH = EXPERIMENTS / "registry.jsonl"
RUN_INDEX_PATH = EXPERIMENTS / "RUN_INDEX.md"

VAL_SOURCE_JSONL = (
    EXPERIMENTS / "gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13.jsonl"
)
TEST_SOURCE_JSONL = (
    EXPERIMENTS / "gan2026_fresh_evidence_reasoner_test450_live_gpt41_v0_4_2026-06-13.jsonl"
)

RUN_ID = "gan2026_cluster_axis_gate_v1_tightened_2026-06-16"
JSON_PATH = EXPERIMENTS / f"{RUN_ID}.json"
MD_PATH = EXPERIMENTS / f"{RUN_ID}.md"

# ---------------------------------------------------------------------------
# Gate pattern v1 (original, too loose): fired on 7 rows, 6 genuine-rate
# regressions, net=-5. Root cause: "run(s) of", "bursts of", "in clusters" in
# incidental/plan context all fire falsely when gold is a plain rate.
#
# Gate pattern v1-tightened (this version): two triggers only—
#   (A) "group together" / "groups together" / "grouped together" / "grouping together"
#       — highly specific cadence-defining language (only found in notes where
#       the grouping IS the primary frequency cadence)
#   (B) "in clusters" immediately followed (within same sentence, no period)
#       by an explicit cadence interval: "every N" (e.g. "in clusters every 4 days")
#       — captures cadence-explicit cluster notes; the "every \d" sub-clause
#       prevents the pattern from firing on incidental mentions like
#       "occur in clusters on stressful days" or plan notes
#       ("sooner if events occur in clusters").
#
# Validation result: 1 row fires (idx=9943), W->C=1, C->W=0, net=+1,
# genuine_rate_regressions=0.
# ---------------------------------------------------------------------------
CLUSTER_RECURRING_RE = re.compile(
    r"group(?:s|ed|ing)? together"
    r"|\bin clusters?\b[^.]*every\s+\d",
    re.IGNORECASE,
)


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]


def _get_note_text(row: dict[str, Any]) -> str:
    """Extract raw note text from prompt_input_json."""
    pij = row.get("prompt_input_json", "")
    if isinstance(pij, str) and pij:
        try:
            parsed = json.loads(pij)
            return str(parsed.get("raw_note_excerpt", ""))
        except (ValueError, TypeError):
            return ""
    if isinstance(pij, dict):
        return str(pij.get("raw_note_excerpt", ""))
    return ""


def _get_v04_final_label(row: dict[str, Any]) -> str | None:
    """Get the v0.4 final label from decision_record."""
    dr = row.get("decision_record")
    if dr is None:
        return None
    return dr.get("final_label")


def _is_plain_rate(label: str | None) -> bool:
    """True iff the label is a numeric plain rate (not cluster, unknown, seizure-free, etc.)."""
    if not label:
        return False
    ll = label.lower()
    return (
        " per " in ll
        and "cluster" not in ll
        and "unknown" not in ll
        and "seizure free" not in ll
        and "no seizure" not in ll
        and "no reference" not in ll
        and "multiple per" not in ll
    )


def _rewrite_plain_rate_to_cluster(plain_rate: str) -> str:
    """Rewrite 'N per X' -> 'N cluster per X, multiple per cluster'.

    Handles both simple ('1 per week') and range rates ('1 per 4 to 5 week').
    The interval portion after 'per' becomes the cluster cadence denominator.
    """
    # Find first ' per ' and split
    idx = plain_rate.lower().find(" per ")
    if idx < 0:
        return plain_rate  # fallback: no change
    count_part = plain_rate[:idx]
    interval_part = plain_rate[idx + 5 :]  # everything after ' per '
    return f"{count_part} cluster per {interval_part}, multiple per cluster"


def _gate_fires(
    plain_label: str,
    note_text: str,
    cluster_label: str,
) -> bool:
    """Return True iff all three gate conditions hold.

    (a) plain_label is a plain rate - already pre-checked by caller
    (b) note has recurring cluster language
    (c) rewriting changes the Purist bucket
    """
    if not CLUSTER_RECURRING_RE.search(note_text):
        return False
    # Condition (c): bucket must change
    try:
        plain_freq = label_to_monthly_frequency(plain_label)
        cluster_freq = label_to_monthly_frequency(cluster_label)
    except Exception:
        return False
    if plain_freq is None or cluster_freq is None:
        return False
    plain_bucket = map_purist(plain_freq)
    cluster_bucket = map_purist(cluster_freq)
    return plain_bucket != cluster_bucket


def _apply_gate_to_rows(
    rows: list[dict[str, Any]],
    *,
    split_name: str,
) -> dict[str, Any]:
    """Apply the cluster-axis gate to a list of v0.4 output rows.

    Returns a summary dict with per-row records and aggregate metrics.
    """
    touched: list[dict[str, Any]] = []
    total_purist_base = 0
    total_purist_gated = 0
    wrong_to_correct = 0
    correct_to_wrong = 0

    for row in rows:
        idx = row.get("source_row_index")
        gold_label = row.get("reference", {}).get("gold_label", "")
        gold_monthly = row.get("reference", {}).get("gold_monthly_frequency")
        comparison = row.get("score_layers", {}).get("final", {}).get("comparison", {})
        base_purist = comparison.get("purist_correct", False)
        comparison.get("final_label", "")

        v04_label = _get_v04_final_label(row)
        note = _get_note_text(row)

        # Baseline tally
        if base_purist:
            total_purist_base += 1

        # Gate: condition (a) - is plain rate?
        if not _is_plain_rate(v04_label):
            total_purist_gated += int(base_purist)
            continue

        # Build cluster rewrite
        cluster_label = _rewrite_plain_rate_to_cluster(v04_label)

        # Gate: conditions (b) and (c)
        if not _gate_fires(v04_label, note, cluster_label):
            total_purist_gated += int(base_purist)
            continue

        # Gate fires: compute gated correctness
        try:
            cluster_freq = label_to_monthly_frequency(cluster_label)
            gated_purist_cat = map_purist(cluster_freq) if cluster_freq is not None else None
        except Exception:
            cluster_freq = None
            gated_purist_cat = None

        gold_purist_cat = comparison.get("gold_purist_category", "")
        gated_correct = (gated_purist_cat == gold_purist_cat) if gated_purist_cat else False

        total_purist_gated += int(gated_correct)

        transition = None
        if not base_purist and gated_correct:
            transition = "wrong_to_correct"
            wrong_to_correct += 1
        elif base_purist and not gated_correct:
            transition = "correct_to_wrong"
            correct_to_wrong += 1

        # Is gold a plain rate? (for precision check)
        gold_is_plain_rate = _is_plain_rate(gold_label)

        touched.append(
            {
                "source_row_index": idx,
                "gold_label": gold_label,
                "gold_monthly_frequency": gold_monthly,
                "gold_purist_category": gold_purist_cat,
                "gold_is_plain_rate": gold_is_plain_rate,
                "v04_label": v04_label,
                "cluster_rewrite": cluster_label,
                "cluster_monthly_frequency": cluster_freq,
                "gated_purist_category": gated_purist_cat,
                "base_purist_correct": base_purist,
                "gated_purist_correct": gated_correct,
                "transition": transition,
            }
        )

    genuine_rate_regressions = [
        r for r in touched if r["transition"] == "correct_to_wrong" and r["gold_is_plain_rate"]
    ]
    net_purist = wrong_to_correct - correct_to_wrong

    return {
        "split": split_name,
        "total_rows": len(rows),
        "baseline_purist_correct": total_purist_base,
        "gated_purist_correct": total_purist_gated,
        "touched_rows": len(touched),
        "wrong_to_correct": wrong_to_correct,
        "correct_to_wrong": correct_to_wrong,
        "net_purist": net_purist,
        "genuine_rate_regressions": len(genuine_rate_regressions),
        "genuine_rate_regression_rows": [r["source_row_index"] for r in genuine_rate_regressions],
        "touched_records": touched,
    }


def _build_transition_rows_for_cv(
    rows: list[dict[str, Any]],
    gate_summary: dict[str, Any],
) -> list[dict[str, Any]]:
    """Build annotated rows suitable for family_transitions.summarize_transitions_by_family.

    Each row gets:
    - hidden_families (from boundary_band on gold_monthly_frequency)
    - transition_vs_gate.purist_transition
    - transition_vs_gate.label_changed
    - v04_reference.comparison.purist_correct (baseline)
    - gated_score.purist_correct (candidate)
    """
    # Build index of gate-touched rows
    touched_by_idx: dict[int, dict[str, Any]] = {
        r["source_row_index"]: r for r in gate_summary["touched_records"]
    }

    annotated: list[dict[str, Any]] = []
    for row in rows:
        idx = row.get("source_row_index")
        gold_monthly = row.get("reference", {}).get("gold_monthly_frequency")
        comparison = row.get("score_layers", {}).get("final", {}).get("comparison", {})
        base_purist = comparison.get("purist_correct", False)
        _get_note_text(row)

        families = (boundary_band(gold_monthly),)

        if idx in touched_by_idx:
            t = touched_by_idx[idx]
            gated_correct = t["gated_purist_correct"]
            label_changed = True
            if not base_purist and gated_correct:
                transition = "wrong_to_correct"
            elif base_purist and not gated_correct:
                transition = "correct_to_wrong"
            else:
                transition = "unchanged"
        else:
            gated_correct = base_purist
            label_changed = False
            transition = "unchanged"

        annotated.append(
            {
                "source_row_index": idx,
                "hidden_families": families,
                "transition_vs_gate": {
                    "purist_transition": transition,
                    "label_changed": label_changed,
                },
                "v04_reference": {
                    "comparison": {"purist_correct": base_purist},
                },
                "gated_score": {"purist_correct": gated_correct},
            }
        )
    return annotated


def _run_family_cv(
    rows: list[dict[str, Any]],
    gate_summary: dict[str, Any],
) -> dict[str, Any]:
    """Run held-out-family CV on the gated validation rows."""
    annotated = _build_transition_rows_for_cv(rows, gate_summary)
    transitions = summarize_transitions_by_family(
        annotated,
        transition_path=("transition_vs_gate", "purist_transition"),
        label_changed_path=("transition_vs_gate", "label_changed"),
        baseline_correct_path=("v04_reference", "comparison", "purist_correct"),
        candidate_correct_path=("gated_score", "purist_correct"),
        families_path=("hidden_families",),
    )
    cv_result = summarize_family_holdout_cv(transitions)
    return {
        "transitions_by_family": transitions,
        "cv_result": cv_result,
    }


def _markdown(payload: dict[str, Any]) -> str:
    val = payload["validation"]
    cv = payload["family_cv"]
    cv_result = cv["cv_result"]
    test = payload.get("test")

    lines = [
        "# Gan 2026 C6: Cluster-Axis RETENTION Gate v1 (No-Call Replay)",
        "",
        "Date: 2026-06-16",
        "",
        "No-call post-hoc replay over v0.4 fresh-evidence outputs. No model calls. "
        "No test450 rows were read until step 3 authorization was confirmed.",
        "",
        "## Gate Definition (v1-tightened)",
        "",
        "Original v1 pattern fired too broadly (7 rows, 6 genuine-rate regressions, net=-5). "
        "Tightened to two high-precision triggers only.",
        "",
        "Fires when ALL hold:",
        "- (a) v0.4 final label is a PLAIN rate (numeric, no cluster/unknown/seizure-free/no-reference/multiple-per)",
        "- (b) note contains TIGHT recurring-cluster language: "
        '"group(s/ed/ing) together" (cadence-defining grouping) OR "in clusters...every N" (cadence-explicit interval)',
        "  - Excluded from original v1: 'runs of', 'bursts of', 'in clusters' in isolation (too many false positives)",
        "- (c) the rewrite changes the Purist bucket",
        "",
        "Rewrite: 'N per X' -> 'N cluster per X, multiple per cluster'",
        "",
        "## Validation750 Results",
        "",
        f"- Baseline Purist: {val['baseline_purist_correct']}/{val['total_rows']}",
        f"- Gated Purist: {val['gated_purist_correct']}/{val['total_rows']}",
        f"- Rows touched by gate: {val['touched_rows']}",
        f"- Wrong->Correct (W->C): {val['wrong_to_correct']}",
        f"- Correct->Wrong (C->W): {val['correct_to_wrong']}",
        f"- Net Purist: {val['net_purist']:+d}",
        "",
        "### Touched Rows",
        "",
        "| idx | gold | v0.4 pred | cluster rewrite | gold_purist | gated_purist | transition |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for r in val["touched_records"]:
        lines.append(
            f"| {r['source_row_index']} "
            f"| `{r['gold_label']}` "
            f"| `{r['v04_label']}` "
            f"| `{r['cluster_rewrite']}` "
            f"| `{r['gold_purist_category']}` "
            f"| `{r['gated_purist_category']}` "
            f"| {r['transition'] or 'unchanged'} |"
        )

    lines.extend(
        [
            "",
            "## Precision Check (Genuine-Rate Regressions)",
            "",
            f"- Genuine-rate regressions (C->W where gold is plain rate): "
            f"{val['genuine_rate_regressions']}",
        ]
    )
    if val["genuine_rate_regression_rows"]:
        lines.append(f"- Row indices: {val['genuine_rate_regression_rows']}")
    if val["genuine_rate_regressions"] == 0:
        lines.append("- PASS: zero genuine-rate regressions (gate is precision-safe)")
    else:
        lines.append("- FAIL: genuine-rate regressions detected; gate is too leaky")
    lines.append("")

    lines.extend(
        [
            "## Held-Out-Family CV",
            "",
            f"- gap_robust: **{cv_result['gap_robust']}**",
            f"- Aggregate net Purist gain: {cv_result['aggregate']['net_purist_gain']}",
            f"- Worst held-out fold: {cv_result['worst_held_out_fold']}",
            f"- Regressing held-out families: {cv_result['regressing_held_out_families']}",
            f"- Low-precision held-out families: {cv_result['low_precision_held_out_families']}",
            f"- Reasons for non-robust: {cv_result['reasons']}",
            "",
            "### Per-Band Transition Summary",
            "",
            "| Band | rows | W->C | C->W | net | precision |",
            "| --- | ---: | ---: | ---: | ---: | --- |",
        ]
    )
    families = cv["transitions_by_family"].get("families", {})
    for band in [
        "band_zero",
        "band_unknown",
        "band_submonthly",
        "band_monthly",
        "band_weekly",
        "band_daily",
    ]:
        f = families.get(band, {})
        if f:
            prec = f.get("changed_label_precision")
            lines.append(
                f"| {band} | {f['rows']} | {f['wrong_to_correct']} "
                f"| {f['correct_to_wrong']} | {f['net_purist_gain']:+d} "
                f"| {prec if prec is not None else 'n/a'} |"
            )
    lines.append("")

    if test is not None:
        lines.extend(
            [
                "## Test450 Results (Authorised Gate Applied)",
                "",
                f"- Baseline Purist (v0.4): {test['baseline_purist_correct']}/{test['total_rows']}",
                f"- Gated Purist: {test['gated_purist_correct']}/{test['total_rows']}",
                f"- Rows touched by gate: {test['touched_rows']}",
                f"- Wrong->Correct (W->C): {test['wrong_to_correct']}",
                f"- Correct->Wrong (C->W): {test['correct_to_wrong']}",
                f"- Net Purist: {test['net_purist']:+d}",
                f"- Delta vs 379 baseline: {test['gated_purist_correct'] - 379:+d}",
                "",
                "### Test Touched Rows",
                "",
                "| idx | gold | v0.4 pred | cluster rewrite | gold_purist | gated_purist | transition |",
                "| --- | --- | --- | --- | --- | --- | --- |",
            ]
        )
        for r in test["touched_records"]:
            lines.append(
                f"| {r['source_row_index']} "
                f"| `{r['gold_label']}` "
                f"| `{r['v04_label']}` "
                f"| `{r['cluster_rewrite']}` "
                f"| `{r['gold_purist_category']}` "
                f"| `{r['gated_purist_category']}` "
                f"| {r['transition'] or 'unchanged'} |"
            )
        lines.append("")
    else:
        lines.extend(
            [
                "## Test450 Results",
                "",
                "GATE DID NOT REACH TEST: See stop-rule evaluation in summary.",
                "",
            ]
        )

    lines.extend(
        [
            "## Decision",
            "",
            payload.get("decision_note", ""),
            "",
        ]
    )
    return "\n".join(lines)


def _register(payload: dict[str, Any]) -> None:
    val = payload["validation"]
    test = payload.get("test")
    decision = payload["decision"]

    metrics: dict[str, Any] = {
        "validation_baseline_purist": val["baseline_purist_correct"],
        "validation_gated_purist": val["gated_purist_correct"],
        "validation_total_rows": val["total_rows"],
        "validation_touched": val["touched_rows"],
        "validation_wrong_to_correct": val["wrong_to_correct"],
        "validation_correct_to_wrong": val["correct_to_wrong"],
        "validation_net_purist": val["net_purist"],
        "genuine_rate_regressions": val["genuine_rate_regressions"],
        "gap_robust": payload["family_cv"]["cv_result"]["gap_robust"],
    }
    if test is not None:
        metrics.update(
            {
                "test_baseline_purist": test["baseline_purist_correct"],
                "test_gated_purist": test["gated_purist_correct"],
                "test_total_rows": test["total_rows"],
                "test_touched": test["touched_rows"],
                "test_wrong_to_correct": test["wrong_to_correct"],
                "test_correct_to_wrong": test["correct_to_wrong"],
                "test_net_purist": test["net_purist"],
                "test_delta_vs_379_baseline": test["gated_purist_correct"] - 379,
            }
        )

    split_label = "validation+test" if test is not None else "validation"

    entries = [entry for entry in load_run_registry(REGISTRY_PATH) if entry.run_id != RUN_ID]
    entries.append(
        RunRegistryEntry(
            run_id=RUN_ID,
            artifact_paths=(
                f"experiments/{JSON_PATH.name}",
                f"experiments/{MD_PATH.name}",
            ),
            date="2026-06-16",
            pipeline_family="cluster_axis_gate_no_call_replay",
            split=split_label,
            row_count=val["total_rows"] + (test["total_rows"] if test else 0),
            model="none",
            model_role=(
                "No-call post-hoc replay over v0.4 fresh-evidence outputs. "
                "No model calls made. Test450 rows read only after gate cleared "
                "precision check and gap_robust on validation750."
            ),
            mode="analysis/no-call",
            replay_status="saved_output_replay",
            repair_mode="cluster_axis_retention_gate_v1",
            cache_reuse_source=str(VAL_SOURCE_JSONL),
            primary_metrics=metrics,
            evidence_validity=(
                "Validation-only replay for gate development (step 1-2). "
                "Test450 applied only after validation gate cleared: "
                "zero genuine-rate regressions + gap_robust. "
                "Test450 result reported verbatim, no tuning on test."
            ),
            decision=decision,
            claim_language_notes=(
                "C6 cluster-axis RETENTION gate: fires only on plain-rate v0.4 "
                "predictions where the note has explicit recurring-cluster language "
                "AND the rewrite changes the Purist bucket. "
                "Zero unknown-coercion; additive cluster-axis only. "
                "Genuine-rate regression count must be 0 to clear precision gate."
            ),
        )
    )
    write_run_registry(entries, REGISTRY_PATH)
    validate_run_registry_artifacts(load_run_registry(REGISTRY_PATH), repo_root=ROOT)
    write_run_registry_markdown(load_run_registry(REGISTRY_PATH), RUN_INDEX_PATH)


def main() -> None:
    # -------------------------------------------------------------------------
    # Step 1: Apply gate to VALIDATION750
    # -------------------------------------------------------------------------
    print("Loading validation750 rows...")
    val_rows = _load_jsonl(VAL_SOURCE_JSONL)
    print(f"  Loaded {len(val_rows)} rows")

    val_summary = _apply_gate_to_rows(val_rows, split_name="validation750")
    print(
        f"  Baseline Purist: {val_summary['baseline_purist_correct']}/{val_summary['total_rows']}"
    )
    print(f"  Gated Purist:    {val_summary['gated_purist_correct']}/{val_summary['total_rows']}")
    print(f"  Touched: {val_summary['touched_rows']} rows")
    print(
        f"  W->C: {val_summary['wrong_to_correct']}, C->W: {val_summary['correct_to_wrong']}, "
        f"Net: {val_summary['net_purist']:+d}"
    )
    print(f"  Genuine-rate regressions: {val_summary['genuine_rate_regressions']}")

    # -------------------------------------------------------------------------
    # Family CV
    # -------------------------------------------------------------------------
    print("\nRunning held-out-family CV on validation...")
    family_cv = _run_family_cv(val_rows, val_summary)
    cv_result = family_cv["cv_result"]
    print(f"  gap_robust: {cv_result['gap_robust']}")
    print(f"  Aggregate net Purist: {cv_result['aggregate']['net_purist_gain']}")
    print(f"  Worst fold: {cv_result['worst_held_out_fold']}")
    print(f"  Regressing bands: {cv_result['regressing_held_out_families']}")
    print(f"  Reasons: {cv_result['reasons']}")

    # -------------------------------------------------------------------------
    # Step 2: PRECISION CHECK + STOP RULE
    # -------------------------------------------------------------------------
    genuine_regressions = val_summary["genuine_rate_regressions"]
    net_purist = val_summary["net_purist"]
    gap_robust = cv_result["gap_robust"]

    proceed_to_test = genuine_regressions == 0 and net_purist >= 0 and gap_robust

    print("\nStop-rule evaluation:")
    print(f"  genuine_rate_regressions == 0: {genuine_regressions == 0}")
    print(f"  net_purist >= 0: {net_purist >= 0} ({net_purist})")
    print(f"  gap_robust: {gap_robust}")
    print(f"  => proceed_to_test: {proceed_to_test}")

    test_summary: dict[str, Any] | None = None
    if proceed_to_test:
        # ---------------------------------------------------------------------
        # Step 3: Apply SAME FROZEN gate to TEST450
        # ---------------------------------------------------------------------
        print("\nLoading test450 rows...")
        test_rows = _load_jsonl(TEST_SOURCE_JSONL)
        print(f"  Loaded {len(test_rows)} rows")

        test_summary = _apply_gate_to_rows(test_rows, split_name="test450")
        print(
            f"  Test baseline Purist: {test_summary['baseline_purist_correct']}/{test_summary['total_rows']}"
        )
        print(
            f"  Test gated Purist:    {test_summary['gated_purist_correct']}/{test_summary['total_rows']}"
        )
        print(f"  Test touched: {test_summary['touched_rows']} rows")
        print(
            f"  Test W->C: {test_summary['wrong_to_correct']}, C->W: {test_summary['correct_to_wrong']}, "
            f"Net: {test_summary['net_purist']:+d}"
        )
        print(f"  Delta vs 379: {test_summary['gated_purist_correct'] - 379:+d}")

        # Confirm baseline
        if test_summary["baseline_purist_correct"] != 379:
            print(
                f"  WARNING: Expected test baseline 379, got {test_summary['baseline_purist_correct']}"
            )

    # -------------------------------------------------------------------------
    # Build decision note
    # -------------------------------------------------------------------------
    if test_summary is not None:
        delta = test_summary["gated_purist_correct"] - 379
        if delta > 0 and gap_robust:
            decision = "revise"  # positive signal, recommend integrating into hybrid
            decision_note = (
                f"Gate cleared precision check (0 genuine-rate regressions, "
                f"gap_robust=True). Test450 gated Purist: "
                f"{test_summary['gated_purist_correct']}/450 "
                f"(delta {delta:+d} vs 379 baseline). "
                f"Cluster-axis RETENTION gate is a safe, additive improvement. "
                f"Recommend integrating into the v0.4 hybrid pipeline as a frozen gate."
            )
        else:
            decision = "revise"
            decision_note = (
                f"Gate cleared precision check but test delta is {delta:+d}. "
                f"Cluster-axis gate is precision-safe but the lift is limited."
            )
    else:
        if not proceed_to_test:
            reasons = []
            if genuine_regressions > 0:
                reasons.append(f"{genuine_regressions} genuine-rate regressions")
            if net_purist < 0:
                reasons.append(f"net Purist {net_purist} < 0")
            if not gap_robust:
                reasons.append(f"gap_robust=False ({cv_result['reasons']})")
            decision = "revise"
            decision_note = (
                "STOP RULE triggered: gate did not reach test. Reasons: "
                + "; ".join(reasons)
                + ". Gate needs tightening before test application."
            )
        else:
            decision = "revise"
            decision_note = "Gate passed but test was not applied (unexpected)."

    # -------------------------------------------------------------------------
    # Write artifacts
    # -------------------------------------------------------------------------
    payload: dict[str, Any] = {
        "run_id": RUN_ID,
        "date": "2026-06-16",
        "gate_pattern": CLUSTER_RECURRING_RE.pattern,
        "gate_version": "v1-tightened",
        "gate_conditions": [
            "(a) v0.4 final label is a PLAIN rate (numeric, no cluster/unknown/seizure-free/no-reference/multiple-per)",
            "(b) note contains TIGHT recurring-cluster language: 'group(s/ed/ing) together' OR 'in clusters...every N'",
            "(c) rewrite changes the Purist bucket",
        ],
        "rewrite_rule": "N per X -> N cluster per X, multiple per cluster",
        "validation": val_summary,
        "family_cv": family_cv,
        "proceed_to_test": proceed_to_test,
        "decision": decision,
        "decision_note": decision_note,
    }
    if test_summary is not None:
        payload["test"] = test_summary

    # Remove large touched_records for JSON size sanity (keep essential fields)
    payload_for_json = {
        **payload,
        "validation": {k: v for k, v in val_summary.items() if k != "touched_records"},
        "validation_touched_records": val_summary["touched_records"],
    }
    if test_summary is not None:
        payload_for_json["test"] = {k: v for k, v in test_summary.items() if k != "touched_records"}
        payload_for_json["test_touched_records"] = test_summary["touched_records"]

    JSON_PATH.write_text(
        json.dumps(payload_for_json, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"\nWrote {JSON_PATH}")

    MD_PATH.write_text(_markdown(payload), encoding="utf-8")
    print(f"Wrote {MD_PATH}")

    _register(payload)
    print("Registry updated.")


if __name__ == "__main__":
    main()
