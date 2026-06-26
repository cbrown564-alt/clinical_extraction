"""Gan 2026 v0.7 label-binding — authorised validation750 live pass + family CV.

Cycle-3 GATE step (Part 4). Runs ONLY after the v0.7 robustness battery cleared
Panel A AND Panel B AND kept Panel C >= 80% (it did:
`experiments/gan2026_robustness_battery_v1_evidence_v0_7_gpt41mini_2026-06-15.*`,
verdict `transfers`).

This driver:
  1. Runs the v0.7 candidate (sharpened scaffold + answer_kind/rationale label
     binding) live on the 750 validation rows, resumable via its own JSONL
     checkpoint (so a re-run never re-pays for completed rows).
  2. Re-scores the established v0.5 champion baseline by re-parsing its saved
     validation750 raw outputs under v0.5 parsing (no new calls). v0.5 is the
     current best holdout family per the protocol.
  3. Computes overall validation750 Purist for both, the wrong->correct vs
     correct->wrong flip counts (the regression the coerce-to-unknown rule could
     cause), and held-out-family CV via
     `agentic.family_cv_promotion.summarize_family_holdout_cv` over the gold
     boundary bands (`labels.boundary_band`).

Live gpt-4.1-mini, temperature 0. NEVER reads or runs test450.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026 import data as gan_data
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic.family_cv_promotion import (
    summarize_family_holdout_cv,
)
from clinical_extraction.core.registry import (
    RunRegistryEntry,
    load_run_registry,
    validate_run_registry_artifacts,
    write_run_registry,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry_report import (
    write_run_registry_markdown,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import (
    BOUNDARY_BANDS,
    boundary_band,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    llm_only_direct_labeler as labeler,
)

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
REGISTRY_PATH = EXPERIMENTS / "registry.jsonl"
RUN_INDEX_PATH = EXPERIMENTS / "RUN_INDEX.md"

BASELINE_V05_JSONL = (
    EXPERIMENTS
    / "gan2026_llm_only_direct_labeler_v05_validation750_gpt41mini_2026-06-09.jsonl"
)
PREDECLARATION_PATH = (
    EXPERIMENTS / "gan2026_label_binding_v0_7_predeclaration_2026-06-15.md"
)

RUN_ID = "gan2026_llm_only_direct_labeler_v07_validation750_gpt41mini_2026-06-15"
JSON_PATH = EXPERIMENTS / f"{RUN_ID}.json"
MD_PATH = EXPERIMENTS / f"{RUN_ID}.md"
CHECKPOINT_JSONL = EXPERIMENTS / f"{RUN_ID}.jsonl"
CHECKPOINT_MD = EXPERIMENTS / f"{RUN_ID}_checkpoint.md"

DATE = "2026-06-15"
MODEL = "openai/gpt-4.1-mini"
TEMPERATURE = 0.0
MAX_TOKENS = 900


def _score_rows(rows: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    """Index rows by source_row_index with purist_correct and gold band."""

    out: dict[int, dict[str, Any]] = {}
    for row in rows:
        comparison = row.get("comparison") or {}
        gold_month = row["reference"]["gold_monthly_frequency"]
        out[row["source_row_index"]] = {
            "purist_correct": bool(comparison.get("purist_correct")),
            "gold_band": boundary_band(gold_month),
            "final_label": (row.get("decision_record") or {}).get("final_label"),
            "answer_kind": (row.get("decision_record") or {}).get("answer_kind"),
        }
    return out


def _reparse_baseline_v05() -> dict[int, dict[str, Any]]:
    """Re-score the v0.5 baseline from its saved raw outputs under v0.5 parsing."""

    labeler.set_active_prompt_version(labeler.PROMPT_VERSION_V0_5)
    baseline_rows = [
        json.loads(line)
        for line in BASELINE_V05_JSONL.read_text(encoding="utf-8").splitlines()
    ]
    rescored: dict[int, dict[str, Any]] = {}
    records = {
        rec.source_row_index: rec
        for rec in gan_data.load_records_for_split("validation")
    }
    for row in baseline_rows:
        idx = row["source_row_index"]
        rec = records[idx]
        decision, _errs = labeler.parse_decision_json(row.get("raw_output") or "")
        comparison = labeler._compare_to_gold(rec, decision) if decision else None
        rescored[idx] = {
            "purist_correct": bool((comparison or {}).get("purist_correct")),
            "gold_band": boundary_band(rec.gold_monthly_frequency),
            "final_label": decision.final_label if decision else None,
            "answer_kind": decision.answer_kind if decision else None,
        }
    return rescored


def _run_v07_live() -> list[dict[str, Any]]:
    labeler.set_active_prompt_version(labeler.PROMPT_VERSION_V0_7)
    records = gan_data.load_records_for_split("validation")
    reuse: dict[int, str] = {}
    if CHECKPOINT_JSONL.exists():
        reuse = labeler.load_reusable_raw_outputs(CHECKPOINT_JSONL)
    rows, _meta = labeler.run_split(
        records,
        split="validation",
        split_manifest="gan2026_split_v1",
        model=MODEL,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        mode="live",
        dspy_cache=True,
        api_base=None,
        reuse_raw_outputs=reuse or None,
        reuse_source=str(CHECKPOINT_JSONL) if reuse else None,
        escalation_reason=(
            "Cycle-3 v0.7 label-binding authorised validation750 live pass after "
            "the v0.7 robustness battery cleared Panels A/B/C (verdict transfers)."
        ),
        # Mid-run checkpoint writes hit a transient Windows OSError (Errno 22) at
        # the frequent cadence; write only at the very end (rows are resumable
        # from any prior partial checkpoint regardless).
        progress_every=200,
        checkpoint_jsonl_path=CHECKPOINT_JSONL,
        checkpoint_report_path=CHECKPOINT_MD,
    )
    _resilient_write_jsonl(rows, CHECKPOINT_JSONL)
    return rows


def _resilient_write_jsonl(rows: list[dict[str, Any]], path: Path) -> None:
    """Write the checkpoint, retrying through transient Windows OSErrors."""

    import time

    last_exc: Exception | None = None
    for _ in range(8):
        try:
            labeler.write_jsonl(rows, path)
            return
        except OSError as exc:  # transient Errno 22 on rapid reopen
            last_exc = exc
            time.sleep(0.5)
    if last_exc is not None:
        raise last_exc


def _transitions_by_family(
    baseline: dict[int, dict[str, Any]],
    candidate: dict[int, dict[str, Any]],
) -> dict[str, Any]:
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
        if base["final_label"] != cand["final_label"]:
            fam["changed_labels"] += 1
        if (not base["purist_correct"]) and cand["purist_correct"]:
            fam["wrong_to_correct"] += 1
        if base["purist_correct"] and (not cand["purist_correct"]):
            fam["correct_to_wrong"] += 1
    return {"families": families}


def main() -> None:
    candidate_rows = _run_v07_live()
    candidate = _score_rows(candidate_rows)
    baseline = _reparse_baseline_v05()

    cand_purist = sum(v["purist_correct"] for v in candidate.values())
    base_purist = sum(v["purist_correct"] for v in baseline.values())
    n = len(candidate)

    wrong_to_correct = sum(
        1
        for idx, c in candidate.items()
        if idx in baseline
        and not baseline[idx]["purist_correct"]
        and c["purist_correct"]
    )
    correct_to_wrong = sum(
        1
        for idx, c in candidate.items()
        if idx in baseline
        and baseline[idx]["purist_correct"]
        and not c["purist_correct"]
    )

    summary_by_family = _transitions_by_family(baseline, candidate)
    cv = summarize_family_holdout_cv(summary_by_family)

    payload = {
        "run_id": RUN_ID,
        "date": DATE,
        "model": MODEL,
        "temperature": TEMPERATURE,
        "candidate": "llm_only_direct_labeler prompt v0.7 (label binding) live, temp 0",
        "baseline": (
            "llm_only_direct_labeler prompt v0.5 re-parsed from "
            f"{BASELINE_V05_JSONL.name} (no new calls)"
        ),
        "predeclaration": str(PREDECLARATION_PATH.relative_to(ROOT)),
        "evidence_validity": (
            "validation750 development split (gan2026_split_v1), NOT a holdout or "
            "test450 result. Live gpt-4.1-mini, temperature 0. Family CV is "
            "within-validation leave-one-boundary-band-out; gap_robust is a "
            "promotion-stability estimate, not a test450 number."
        ),
        "rows": n,
        "v07_purist": cand_purist,
        "v05_baseline_purist": base_purist,
        "net_purist_vs_v05": cand_purist - base_purist,
        "wrong_to_correct_vs_v05": wrong_to_correct,
        "correct_to_wrong_vs_v05": correct_to_wrong,
        "summary_by_family": summary_by_family,
        "family_cv": cv,
    }
    JSON_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    MD_PATH.write_text(_markdown(payload), encoding="utf-8")
    _register(payload)
    print(json.dumps(
        {k: payload[k] for k in (
            "rows", "v07_purist", "v05_baseline_purist", "net_purist_vs_v05",
            "wrong_to_correct_vs_v05", "correct_to_wrong_vs_v05",
        )} | {"gap_robust": cv["gap_robust"], "cv_reasons": cv["reasons"]},
        indent=2, sort_keys=True,
    ))


def _markdown(p: dict[str, Any]) -> str:
    cv = p["family_cv"]
    lines = [
        "# Gan 2026 v0.7 Label-Binding — validation750 + family CV",
        "",
        f"Date: {p['date']}",
        "",
        "Cycle-3 GATE step. validation750 development split (NOT test450). "
        f"Candidate: {p['candidate']}. Baseline: {p['baseline']}.",
        "",
        f"Predeclaration: `{p['predeclaration']}`",
        "",
        "## Overall Purist (validation750)",
        "",
        f"- v0.7 Purist: {p['v07_purist']} / {p['rows']}",
        f"- v0.5 baseline Purist: {p['v05_baseline_purist']} / {p['rows']}",
        f"- Net vs v0.5: {p['net_purist_vs_v05']:+d}",
        f"- wrong->correct vs v0.5: {p['wrong_to_correct_vs_v05']}",
        f"- correct->wrong vs v0.5: {p['correct_to_wrong_vs_v05']}",
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
    lines.extend(["", "## Per-band transition summary (candidate vs baseline)", "",
                  "| Band | rows | changed | w->c | c->w |", "| --- | ---: | ---: | ---: | ---: |"])
    for band, fam in p["summary_by_family"]["families"].items():
        lines.append(
            f"| {band} | {fam['rows']} | {fam['changed_labels']} | "
            f"{fam['wrong_to_correct']} | {fam['correct_to_wrong']} |"
        )
    lines.extend(["", "## Interpretation", "",
                  "A gap_robust verdict means no held-out boundary band silently "
                  "regresses and every changed band clears the changed-label "
                  "precision bar. This is within-validation stability, necessary "
                  "but NOT sufficient for test450: it is not a holdout result.", ""])
    return "\n".join(lines)


def _register(p: dict[str, Any]) -> None:
    cv = p["family_cv"]
    decision = "promote" if cv["gap_robust"] and p["net_purist_vs_v05"] > 0 else "revise"
    entries = [
        e for e in load_run_registry(REGISTRY_PATH) if e.run_id != RUN_ID
    ]
    entries.append(
        RunRegistryEntry(
            run_id=RUN_ID,
            artifact_paths=(
                f"experiments/{JSON_PATH.name}",
                f"experiments/{MD_PATH.name}",
                f"experiments/{CHECKPOINT_JSONL.name}",
            ),
            date=DATE,
            pipeline_family="llm_only_direct_labeler",
            split="validation",
            row_count=p["rows"],
            model=MODEL,
            model_role=(
                "LLM-only direct labeler prompt v0.7 (label binding) live on "
                "validation750; v0.5 re-parsed baseline; held-out-family CV."
            ),
            mode="live",
            replay_status="live",
            repair_mode="v0_7_label_binding",
            cache_reuse_source=str(CHECKPOINT_JSONL.relative_to(ROOT)),
            primary_metrics={
                "v07_purist": p["v07_purist"],
                "v05_baseline_purist": p["v05_baseline_purist"],
                "net_purist_vs_v05": p["net_purist_vs_v05"],
                "wrong_to_correct_vs_v05": p["wrong_to_correct_vs_v05"],
                "correct_to_wrong_vs_v05": p["correct_to_wrong_vs_v05"],
                "gap_robust": cv["gap_robust"],
                "aggregate_net_purist_gain": cv["aggregate"]["net_purist_gain"],
            },
            evidence_validity=p["evidence_validity"],
            decision=decision,
            claim_language_notes=(
                "Cycle-3 validation750 + family-CV gate for v0.7 label binding. "
                "gap_robust + positive net is necessary, NOT sufficient, for "
                "test450 authorisation. Not a holdout result."
            ),
        )
    )
    write_run_registry(entries, REGISTRY_PATH)
    validate_run_registry_artifacts(load_run_registry(REGISTRY_PATH), repo_root=ROOT)
    write_run_registry_markdown(load_run_registry(REGISTRY_PATH), RUN_INDEX_PATH)


if __name__ == "__main__":
    main()
