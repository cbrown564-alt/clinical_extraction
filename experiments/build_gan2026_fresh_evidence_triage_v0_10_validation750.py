"""Cycle C5 — confidence-gated triage scaffold in fresh-evidence reasoner (v0.10).

Predeclaration:
  experiments/gan2026_fresh_evidence_triage_v0_10_predeclaration_2026-06-16.md

Goal: fix the 11 no-correct-component validation rows by inserting a 4-step
triage scaffold (confound_check / window_check / cluster_check /
seizure_free_check) before label rendering, with a confidence gate that only
allows demotion to unknown on high-confidence triage reasons
(single_anchor_last_event or explicitly_provoked_or_transient).

Baseline: fresh-evidence v0.4 on validation750 = 682/750 Purist.

NEVER reads or runs test450.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from clinical_extraction.core.registry import (
    RunRegistryEntry,
    load_run_registry,
    validate_run_registry_artifacts,
    write_run_registry,
)
from clinical_extraction.core.run_resume import (
    merge_rows,
    pending_items,
    read_completed,
)
from clinical_extraction.tasks.seizure_frequency.gan2026 import data as gan_data
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    family_cv_promotion,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    fresh_evidence_reasoner as fer,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry_report import (
    write_run_registry_markdown,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import (
    BOUNDARY_BANDS,
    boundary_band,
)

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
REGISTRY_PATH = EXPERIMENTS / "registry.jsonl"
RUN_INDEX_PATH = EXPERIMENTS / "RUN_INDEX.md"

# v0.4 baseline (same source the v0.4 validation750 run used)
BASELINE_V04_JSONL = (
    EXPERIMENTS / "gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13.jsonl"
)

PREDECLARATION_PATH = (
    EXPERIMENTS / "gan2026_fresh_evidence_triage_v0_10_predeclaration_2026-06-16.md"
)

DATE = "2026-06-16"
MODEL = "openai/gpt-4.1"  # synonymous with gpt-4.1-mini per predeclaration
TEMPERATURE = 0.0
MAX_TOKENS = 3200  # increased vs 2800 for v0.4 to fit triage_result output
SPLIT = "validation"
SPLIT_MANIFEST = "gan2026_split_v1"

RUN_ID = "gan2026_fresh_evidence_triage_v0_10_validation750_live_gpt41_2026-06-16"
CHECKPOINT_JSONL = EXPERIMENTS / f"{RUN_ID}.jsonl"
JSON_PATH = EXPERIMENTS / f"{RUN_ID}.json"
MD_PATH = EXPERIMENTS / f"{RUN_ID}.md"

# The 11 no-correct rows from the predeclaration
NO_CORRECT_ROW_IDS = [5534, 6321, 6368, 6571, 9937, 9943, 11216, 11254, 11272, 13209, 14025]


def _load_baseline() -> dict[int, dict[str, Any]]:
    """Load v0.4 baseline rows indexed by source_row_index."""
    rows = load_jsonl_rows(BASELINE_V04_JSONL)
    return {int(row["source_row_index"]): row for row in rows if "source_row_index" in row}


def _score_indexed(rows: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    """Index rows by source_row_index with purist_correct + gold band."""
    out: dict[int, dict[str, Any]] = {}
    for row in rows:
        idx = int(row["source_row_index"])
        final_layer = (row.get("score_layers") or {}).get("final") or {}
        comparison = final_layer.get("comparison") or {}
        gold_month = (row.get("reference") or {}).get("gold_monthly_frequency")
        fresh_rec = row.get("fresh_evidence_decision_record") or {}
        triage = fresh_rec.get("triage_result") or {}
        out[idx] = {
            "purist_correct": bool(comparison.get("purist_correct")),
            "gold_band": boundary_band(gold_month),
            "final_label": final_layer.get("final_label"),
            "gold_label": (row.get("reference") or {}).get("gold_label"),
            "action": fresh_rec.get("action"),
            "triage_reason": triage.get("triage_reason"),
            "ambiguity_classification": fresh_rec.get("ambiguity_classification"),
        }
    return out


def _run_v0_10_live(records: list[gan_data.GanFrequencyRecord]) -> list[dict[str, Any]]:
    """Run v0.10 triage-scaffold fresh-evidence reasoner live, resumable."""

    # Set active prompt version BEFORE run_split so it threads through.
    fer.set_active_prompt_version(fer.PROMPT_VERSION_V0_10)

    # Load resume checkpoint if present.
    completed_rows, completed_keys = read_completed(
        CHECKPOINT_JSONL if CHECKPOINT_JSONL.exists() else None,
        key="source_row_index",
    )
    pending = pending_items(
        records,
        completed_keys,
        key_of=lambda r: str(r.source_row_index),
    )
    print(
        f"Resume: {len(completed_rows)} already done, {len(pending)} pending out of {len(records)}"
    )

    new_rows: list[dict[str, Any]] = []
    if pending:
        # run_split handles dspy.configure and model calls.
        new_rows, metadata = fer.run_split(
            pending,
            split=SPLIT,
            split_manifest=SPLIT_MANIFEST,
            model=MODEL,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            mode="live",
            dspy_cache=True,
            api_base=None,
            escalation_reason=(
                "Cycle C5 v0.10 confidence-gated triage scaffold fresh-evidence "
                "reasoner live on validation750, predeclared 2026-06-16."
            ),
            progress_every=50,
            checkpoint_jsonl_path=CHECKPOINT_JSONL,
            checkpoint_report_path=None,
        )
        del metadata  # final summary built after merge below

    all_rows = merge_rows(
        [*completed_rows, *new_rows],
        order=[str(r.source_row_index) for r in records],
        key="source_row_index",
    )
    # Write final checkpoint.
    _resilient_write(all_rows, CHECKPOINT_JSONL)
    return all_rows


def _resilient_write(rows: list[dict[str, Any]], path: Path) -> None:
    import time

    last_exc: Exception | None = None
    for _ in range(8):
        try:
            write_jsonl_rows(rows, path)
            return
        except OSError as exc:
            last_exc = exc
            time.sleep(0.5)
    if last_exc is not None:
        raise last_exc


def _transitions_by_family(
    baseline: dict[int, dict[str, Any]],
    candidate: dict[int, dict[str, Any]],
) -> dict[str, Any]:
    """Compute per-boundary-band transition counts."""
    families: dict[str, dict[str, int]] = {
        band: {"rows": 0, "changed_labels": 0, "wrong_to_correct": 0, "correct_to_wrong": 0}
        for band in BOUNDARY_BANDS
    }
    for idx, cand in candidate.items():
        base = baseline.get(idx)
        if base is None:
            continue
        band = cand["gold_band"]
        fam = families.setdefault(
            band,
            {"rows": 0, "changed_labels": 0, "wrong_to_correct": 0, "correct_to_wrong": 0},
        )
        fam["rows"] += 1
        if base.get("final_label") != cand["final_label"]:
            fam["changed_labels"] += 1
        if (not base["purist_correct"]) and cand["purist_correct"]:
            fam["wrong_to_correct"] += 1
        if base["purist_correct"] and (not cand["purist_correct"]):
            fam["correct_to_wrong"] += 1
    return {"families": families}


def _attribution_table(
    baseline: dict[int, dict[str, Any]],
    candidate: dict[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Row-level attribution for the 11 predeclared no-correct rows."""
    rows = []
    for idx in NO_CORRECT_ROW_IDS:
        cand = candidate.get(idx)
        base = baseline.get(idx)
        rows.append(
            {
                "source_row_index": idx,
                "gold_label": (cand or {}).get("gold_label"),
                "baseline_label_v04": (base or {}).get("final_label"),
                "new_fresh_label_v10": (cand or {}).get("final_label"),
                "now_purist_correct": (cand or {}).get("purist_correct", False),
                "triage_reason_emitted": (cand or {}).get("triage_reason"),
                "new_ambiguity_classification": (cand or {}).get("ambiguity_classification"),
                "action": (cand or {}).get("action"),
            }
        )
    return rows


def _genuine_rate_regressions(
    baseline: dict[int, dict[str, Any]],
    candidate: dict[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Count rows where a genuine-rate was correct in baseline but now wrong.

    Genuine-rate rows are those NOT in band_unknown and NOT in band_no_reference.
    This is the stop-rule check: coerce-to-unknown leakage.
    """
    regressions = []
    for idx, base in baseline.items():
        cand = candidate.get(idx)
        if cand is None:
            continue
        band = base["gold_band"]
        genuine_rate_band = band not in ("band_unknown", "band_no_reference")
        was_correct = base["purist_correct"]
        now_wrong = not cand["purist_correct"]
        if genuine_rate_band and was_correct and now_wrong:
            regressions.append(
                {
                    "source_row_index": idx,
                    "gold_band": band,
                    "gold_label": base.get("gold_label"),
                    "baseline_label": base.get("final_label"),
                    "new_label": cand.get("final_label"),
                    "triage_reason": cand.get("triage_reason"),
                }
            )
    return regressions


def _markdown(payload: dict[str, Any]) -> str:
    cv = payload["family_cv"]
    attr = payload["attribution_table"]
    regressions = payload["genuine_rate_regressions"]
    lines = [
        "# Gan 2026 Fresh-Evidence Triage v0.10 — Cycle C5 validation750",
        "",
        f"Date: {payload['date']}",
        "",
        (
            "Cycle C5 GATE step. validation750 development split (NOT test450). "
            f"Candidate: {payload['candidate']}. Baseline: {payload['baseline']}."
        ),
        "",
        f"Predeclaration: `{payload['predeclaration']}`",
        "",
        "## Overall Purist (validation750)",
        "",
        f"- v0.10 triage Purist: {payload['v010_purist']} / {payload['rows']}",
        f"- v0.4 baseline Purist: {payload['v04_baseline_purist']} / {payload['rows']}",
        f"- Net vs v0.4: {payload['net_purist_vs_v04']:+d}",
        f"- wrong->correct vs v0.4: {payload['wrong_to_correct_vs_v04']}",
        f"- correct->wrong vs v0.4: {payload['correct_to_wrong_vs_v04']}",
        "",
        "## Held-out-family CV (leave-one-boundary-band-out)",
        "",
        f"**gap_robust: {cv['gap_robust']}**",
        "",
        f"Reasons (empty = clean): {cv['reasons'] or 'none'}",
        f"Aggregate: {cv['aggregate']}",
        f"Worst held-out fold: {cv['worst_held_out_fold']}",
        "",
        "| Band (held out) | rows | changed | w->c | c->w | net | changed-label prec |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for fold in cv["folds"]:
        h = fold["held_out"]
        lines.append(
            f"| {fold['held_out_family']} | {h['rows']} | {h['changed_labels']} | "
            f"{h['wrong_to_correct']} | {h['correct_to_wrong']} | "
            f"{h['net_purist_gain']:+d} | {h['changed_label_precision']} |"
        )
    lines.extend(
        [
            "",
            "## Per-band transition summary (v0.10 vs v0.4 baseline)",
            "",
            "| Band | rows | changed | w->c | c->w |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for band, fam in payload["summary_by_family"]["families"].items():
        lines.append(
            f"| {band} | {fam['rows']} | {fam['changed_labels']} | "
            f"{fam['wrong_to_correct']} | {fam['correct_to_wrong']} |"
        )
    lines.extend(
        [
            "",
            "## 11-Row Attribution Table (predeclared no-correct rows)",
            "",
            (
                "| Row | Gold | Baseline (v0.4) | New (v0.10) | "
                "Now Correct? | Triage Reason | Ambiguity Class | Action |"
            ),
            ("| ---: | --- | --- | --- | --- | --- | --- | --- |"),
        ]
    )
    for row in attr:
        lines.append(
            f"| {row['source_row_index']} | `{row['gold_label']}` | "
            f"`{row['baseline_label_v04']}` | `{row['new_fresh_label_v10']}` | "
            f"{row['now_purist_correct']} | `{row['triage_reason_emitted']}` | "
            f"`{row['new_ambiguity_classification']}` | `{row['action']}` |"
        )
    lines.extend(
        [
            "",
            "## Genuine-Rate Regression Check (stop-rule)",
            "",
            f"Genuine-rate rows that regressed correct->wrong: {len(regressions)}",
            "",
        ]
    )
    if regressions:
        lines.extend(
            [
                "| Row | Band | Gold | Baseline | New | Triage Reason |",
                "| ---: | --- | --- | --- | --- | --- |",
            ]
        )
        for r in regressions:
            lines.append(
                f"| {r['source_row_index']} | {r['gold_band']} | `{r['gold_label']}` | "
                f"`{r['baseline_label']}` | `{r['new_label']}` | `{r['triage_reason']}` |"
            )
    else:
        lines.append("No genuine-rate regressions (stop rule CLEAR).")
    decision = payload["decision"]
    lines.extend(
        [
            "",
            "## Decision",
            "",
            f"**{decision}**",
            "",
            (
                "Stop rule: reject if net Purist < 0 OR family-CV not gap_robust "
                "OR any genuine-rate band regresses. Confidence gate is too loose "
                "if regressions > 0."
            ),
        ]
    )
    return "\n".join(lines)


def _decide(
    net_purist: int,
    gap_robust: bool,
    genuine_rate_regressions: int,
    cv: dict[str, Any],
) -> str:
    if net_purist < 0:
        return "reject"
    if not gap_robust:
        return "revise"
    if genuine_rate_regressions > 0:
        return "revise"
    return "promote"


def _register(payload: dict[str, Any]) -> None:
    cv = payload["family_cv"]
    entries = [e for e in load_run_registry(REGISTRY_PATH) if e.run_id != RUN_ID]
    entries.append(
        RunRegistryEntry(
            run_id=RUN_ID,
            artifact_paths=(
                f"experiments/{JSON_PATH.name}",
                f"experiments/{MD_PATH.name}",
                f"experiments/{CHECKPOINT_JSONL.name}",
            ),
            date=DATE,
            pipeline_family="fresh_evidence_reasoner",
            split="validation",
            row_count=payload["rows"],
            model=MODEL,
            model_role=(
                "Fresh-evidence reasoner v0.10 triage scaffold (Cycle C5) live on "
                "validation750; v0.4 baseline for comparison; held-out-family CV."
            ),
            mode="live",
            replay_status="live",
            repair_mode="v0_10_confidence_gated_triage_scaffold",
            cache_reuse_source=str(CHECKPOINT_JSONL.relative_to(ROOT)),
            primary_metrics={
                "v010_purist": payload["v010_purist"],
                "v04_baseline_purist": payload["v04_baseline_purist"],
                "net_purist_vs_v04": payload["net_purist_vs_v04"],
                "wrong_to_correct_vs_v04": payload["wrong_to_correct_vs_v04"],
                "correct_to_wrong_vs_v04": payload["correct_to_wrong_vs_v04"],
                "gap_robust": cv["gap_robust"],
                "aggregate_net_purist_gain": cv["aggregate"]["net_purist_gain"],
                "genuine_rate_regressions": len(payload["genuine_rate_regressions"]),
                "no_correct_rows_flipped_correct": sum(
                    1 for r in payload["attribution_table"] if r["now_purist_correct"]
                ),
            },
            evidence_validity=(
                "validation750 development split (gan2026_split_v1), NOT a holdout "
                "or test450 result. Live openai/gpt-4.1 (synonymous with gpt-4.1-mini "
                "per predeclaration), temperature 0. Family CV is within-validation "
                "leave-one-boundary-band-out; gap_robust is a promotion-stability "
                "estimate, not a test450 number."
            ),
            decision=payload["decision"],
            supersedes=(
                "gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13",
            ),
            claim_language_notes=(
                "Cycle C5 confidence-gated triage scaffold fresh-evidence reasoner v0.10. "
                "gap_robust + non-negative net is necessary, NOT sufficient, for "
                "test450 authorisation. Not a holdout result. "
                "Stop rule: reject if net < 0 or not gap_robust or genuine-rate regressions > 0."
            ),
        )
    )
    write_run_registry(entries, REGISTRY_PATH)
    validate_run_registry_artifacts(load_run_registry(REGISTRY_PATH), repo_root=ROOT)
    write_run_registry_markdown(load_run_registry(REGISTRY_PATH), RUN_INDEX_PATH)


def main() -> None:
    records = gan_data.load_records_for_split(SPLIT)
    candidate_rows = _run_v0_10_live(records)

    baseline_raw = _load_baseline()
    baseline = _score_indexed(list(baseline_raw.values()))
    candidate = _score_indexed(candidate_rows)

    v010_purist = sum(v["purist_correct"] for v in candidate.values())
    v04_purist = sum(v["purist_correct"] for v in baseline.values())
    n = len(candidate_rows)

    wrong_to_correct = sum(
        1
        for idx, c in candidate.items()
        if idx in baseline and not baseline[idx]["purist_correct"] and c["purist_correct"]
    )
    correct_to_wrong = sum(
        1
        for idx, c in candidate.items()
        if idx in baseline and baseline[idx]["purist_correct"] and not c["purist_correct"]
    )

    summary_by_family = _transitions_by_family(baseline, candidate)
    cv = family_cv_promotion.summarize_family_holdout_cv(summary_by_family)

    attribution = _attribution_table(baseline, candidate)
    regressions = _genuine_rate_regressions(baseline, candidate)
    decision = _decide(
        net_purist=v010_purist - v04_purist,
        gap_robust=bool(cv["gap_robust"]),
        genuine_rate_regressions=len(regressions),
        cv=cv,
    )

    payload = {
        "run_id": RUN_ID,
        "date": DATE,
        "model": MODEL,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
        "candidate": (
            f"fresh_evidence_reasoner {fer.PROMPT_VERSION_V0_10} "
            f"(Cycle C5 confidence-gated triage scaffold) live, temp 0"
        ),
        "baseline": (f"fresh_evidence_reasoner v0.4 from {BASELINE_V04_JSONL.name}"),
        "predeclaration": str(PREDECLARATION_PATH.relative_to(ROOT)),
        "evidence_validity": (
            "validation750 development split (gan2026_split_v1), NOT a holdout or test450 result."
        ),
        "rows": n,
        "v010_purist": v010_purist,
        "v04_baseline_purist": v04_purist,
        "net_purist_vs_v04": v010_purist - v04_purist,
        "wrong_to_correct_vs_v04": wrong_to_correct,
        "correct_to_wrong_vs_v04": correct_to_wrong,
        "summary_by_family": summary_by_family,
        "family_cv": cv,
        "attribution_table": attribution,
        "genuine_rate_regressions": regressions,
        "decision": decision,
    }

    JSON_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(_markdown(payload), encoding="utf-8")
    _register(payload)

    # Print key numbers
    flipped_correct = sum(1 for r in attribution if r["now_purist_correct"])
    print(
        json.dumps(
            {
                "rows": n,
                "v010_purist": v010_purist,
                "v04_baseline_purist": v04_purist,
                "net_purist_vs_v04": v010_purist - v04_purist,
                "wrong_to_correct_vs_v04": wrong_to_correct,
                "correct_to_wrong_vs_v04": correct_to_wrong,
                "gap_robust": cv["gap_robust"],
                "cv_reasons": cv["reasons"],
                "no_correct_rows_flipped": flipped_correct,
                "genuine_rate_regressions": len(regressions),
                "decision": decision,
            },
            indent=2,
            sort_keys=True,
        )
    )
    print("\n--- 11-Row Attribution ---")
    for row in attribution:
        print(
            f"  row {row['source_row_index']}: "
            f"gold={row['gold_label']!r} "
            f"v04={row['baseline_label_v04']!r} "
            f"v10={row['new_fresh_label_v10']!r} "
            f"correct={row['now_purist_correct']} "
            f"triage={row['triage_reason_emitted']!r}"
        )
    if regressions:
        print(f"\n--- STOP RULE VIOLATED: {len(regressions)} genuine-rate regressions ---")
        for r in regressions:
            print(
                f"  row {r['source_row_index']}: {r['gold_band']} "
                f"gold={r['gold_label']!r} base={r['baseline_label']!r} "
                f"new={r['new_label']!r} triage={r['triage_reason']!r}"
            )
    else:
        print("\nStop rule CLEAR: 0 genuine-rate regressions.")


if __name__ == "__main__":
    main()
