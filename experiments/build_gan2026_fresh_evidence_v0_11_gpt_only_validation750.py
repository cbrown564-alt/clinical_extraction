"""A3 rung — GPT-trace-only fresh-evidence reasoner, validation750 live.

Simplest-near-ceiling architecture plan, Step 2. Tests whether the fresh-evidence
reasoner's lift over a single GPT structured-event pass survives when the Qwen +
DeepSeek peer traces are dropped from the prompt (3 upstream models -> 1).

Prompt: gan2026_fresh_evidence_reasoner_v0_11_gpt_only — byte-identical clinical /
unknown / boundary policy to v0.6; only the peer-referencing lines reworded and
the peer traces removed. Guards + safety gate unchanged.

Baseline: 3-agent fresh-evidence v0.4 on validation750 = 682/750 Purist
(experiments/gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13.jsonl).
Caveat: that baseline carries the v0.4 prompt label; the only intended variable
here is the peer-ensemble drop, so a within-tolerance landing supports A3
regardless of residual v0.4-vs-v0.6 prompt drift. If it lands materially below
tolerance, a matched 3-agent v0.6 run is required to attribute the loss.

Plan: docs/research/gan2026/architecture/gan2026_simplest_near_ceiling_architecture_plan_2026-06-16.md
NEVER reads or runs test450.

Usage:
    uv run python experiments/build_gan2026_fresh_evidence_v0_11_gpt_only_validation750.py
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from clinical_extraction.core.run_resume import (
    merge_rows,
    pending_items,
    read_completed,
)
from clinical_extraction.tasks.seizure_frequency.gan2026 import data as gan_data
from clinical_extraction.tasks.seizure_frequency.gan2026.agentic import (
    family_cv_promotion,
    fresh_evidence_reasoner as fer,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.artifact_io import (
    load_jsonl_rows,
    write_jsonl_rows,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.experiments.run_registry import (
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

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENTS = ROOT / "experiments"
REGISTRY_PATH = EXPERIMENTS / "registry.jsonl"
RUN_INDEX_PATH = EXPERIMENTS / "RUN_INDEX.md"

BASELINE_V04_JSONL = (
    EXPERIMENTS
    / "gan2026_fresh_evidence_reasoner_validation750_live_gpt41_v0_4_2026-06-13.jsonl"
)
PLAN_PATH = (
    "docs/research/gan2026/architecture/gan2026_simplest_near_ceiling_architecture_plan_2026-06-16.md"
)

DATE = "2026-06-16"
MODEL = "openai/gpt-4.1"  # NOTE: full gpt-4.1, NOT mini (build_dspy_lm does no aliasing).
# Go-forward stack uses gpt-4.1-mini; re-validate the chosen architecture on mini.
TEMPERATURE = 0.0
MAX_TOKENS = 2800
SPLIT = "validation"
SPLIT_MANIFEST = "gan2026_split_v1"

# Knee tolerance: ~1.5pp of 750 ≈ 11 rows.
TOLERANCE_ROWS = 11

RUN_ID = "gan2026_fresh_evidence_v0_11_gpt_only_validation750_live_gpt41_2026-06-16"
CHECKPOINT_JSONL = EXPERIMENTS / f"{RUN_ID}.jsonl"
JSON_PATH = EXPERIMENTS / f"{RUN_ID}.json"
MD_PATH = EXPERIMENTS / f"{RUN_ID}.md"


def _resilient_write(rows: list[dict[str, Any]], path: Path) -> None:
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


def _run_live(records: list[gan_data.GanFrequencyRecord]) -> list[dict[str, Any]]:
    fer.set_active_prompt_version(fer.PROMPT_VERSION_V0_11_GPT_ONLY)
    completed_rows, completed_keys = read_completed(
        CHECKPOINT_JSONL if CHECKPOINT_JSONL.exists() else None,
        key="source_row_index",
    )
    pending = pending_items(
        records, completed_keys, key_of=lambda r: str(r.source_row_index)
    )
    print(
        f"Resume: {len(completed_rows)} done, {len(pending)} pending of {len(records)}"
    )
    new_rows: list[dict[str, Any]] = []
    if pending:
        new_rows, _ = fer.run_split(
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
                "A3 GPT-trace-only fresh-evidence reasoner (v0_11) live on "
                "validation750; simplest-near-ceiling architecture plan, Step 2."
            ),
            progress_every=50,
            checkpoint_jsonl_path=CHECKPOINT_JSONL,
            checkpoint_report_path=None,
        )
    all_rows = merge_rows(
        [*completed_rows, *new_rows],
        order=[str(r.source_row_index) for r in records],
        key="source_row_index",
    )
    _resilient_write(all_rows, CHECKPOINT_JSONL)
    return all_rows


def _score_indexed(rows: list[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    out: dict[int, dict[str, Any]] = {}
    for row in rows:
        idx = int(row["source_row_index"])
        final_layer = (row.get("score_layers") or {}).get("final") or {}
        comparison = final_layer.get("comparison") or {}
        gold_month = (row.get("reference") or {}).get("gold_monthly_frequency")
        fresh_rec = row.get("fresh_evidence_decision_record") or {}
        out[idx] = {
            "purist_correct": bool(comparison.get("purist_correct")),
            "gold_band": boundary_band(gold_month),
            "final_label": final_layer.get("final_label"),
            "gold_label": (row.get("reference") or {}).get("gold_label"),
            "action": fresh_rec.get("action"),
        }
    return out


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
        fam = families.setdefault(
            cand["gold_band"],
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


def _genuine_rate_regressions(
    baseline: dict[int, dict[str, Any]],
    candidate: dict[int, dict[str, Any]],
) -> list[dict[str, Any]]:
    regressions = []
    for idx, base in baseline.items():
        cand = candidate.get(idx)
        if cand is None:
            continue
        band = base["gold_band"]
        genuine_rate_band = band not in ("band_unknown", "band_no_reference")
        if genuine_rate_band and base["purist_correct"] and not cand["purist_correct"]:
            regressions.append(
                {
                    "source_row_index": idx,
                    "gold_band": band,
                    "gold_label": base.get("gold_label"),
                    "baseline_label": base.get("final_label"),
                    "new_label": cand.get("final_label"),
                }
            )
    return regressions


def _decide(net_purist: int, gap_robust: bool) -> str:
    """Descriptive verdict (used in the md/json narrative)."""
    if net_purist < -TOLERANCE_ROWS:
        return "reject_peers_load_bearing"
    if not gap_robust:
        return "revise"
    return "promote_to_battery"


# Map the descriptive verdict onto the registry's fixed decision vocabulary.
_REGISTRY_DECISION = {
    "reject_peers_load_bearing": "reject",
    "revise": "revise",
    "promote_to_battery": "promote",
}


def _markdown(payload: dict[str, Any]) -> str:
    cv = payload["family_cv"]
    lines = [
        "# Gan 2026 Fresh-Evidence A3 (GPT-trace-only) — validation750",
        "",
        f"Date: {payload['date']}",
        "",
        (
            "Simplest-near-ceiling plan, Step 2. validation750 development split "
            "(NOT test450). Tests whether dropping the Qwen + DeepSeek peer traces "
            "from the reasoner prompt retains the lift over a single GPT pass."
        ),
        "",
        f"Plan: `{PLAN_PATH}`",
        f"Candidate: `{payload['candidate']}`",
        f"Baseline: `{payload['baseline']}` (caveat: v0.4 prompt label; see header).",
        "",
        "## Overall Purist (validation750)",
        "",
        f"- A3 GPT-only Purist: {payload['a3_purist']} / {payload['rows']} "
        f"= {payload['a3_purist'] / payload['rows']:.3f}",
        f"- v0.4 3-agent baseline Purist: {payload['baseline_purist']} / {payload['rows']} "
        f"= {payload['baseline_purist'] / payload['rows']:.3f}",
        f"- Net vs baseline: {payload['net_vs_baseline']:+d} rows "
        f"(tolerance for knee: -{TOLERANCE_ROWS})",
        f"- wrong->correct: {payload['wrong_to_correct']}   "
        f"correct->wrong: {payload['correct_to_wrong']}",
        "",
        "## Action decomposition (A3 vs single GPT pass, this run)",
        "",
        f"- Replace actions: {payload['replace_helped']} helped, "
        f"{payload['replace_hurt']} hurt, {payload['replace_neutral']} neutral "
        f"(net {payload['replace_helped'] - payload['replace_hurt']:+d}).",
        f"- Keep actions: {payload['keep_correct']} correct, {payload['keep_wrong']} wrong.",
        f"- GPT-only-pass Purist this run (v0_reference): {payload['gpt_only_purist']} / "
        f"{payload['rows']} = {payload['gpt_only_purist'] / payload['rows']:.3f}",
        f"- Reasoner net vs its own GPT pass: {payload['reasoner_net_vs_gpt']:+d}",
        "",
        "## Held-out-family CV (leave-one-boundary-band-out)",
        "",
        f"**gap_robust: {cv['gap_robust']}**",
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
    lines += [
        "",
        "## Genuine-rate regression check",
        "",
        f"Genuine-rate rows correct in baseline now wrong: "
        f"{len(payload['genuine_rate_regressions'])}",
        "",
        "## Decision",
        "",
        f"**{payload['decision']}**",
        "",
        (
            "Knee rule: promote to robustness battery if net Purist >= "
            f"-{TOLERANCE_ROWS} (within ~1.5pp) AND family-CV gap_robust. "
            "reject_peers_load_bearing if A3 falls more than the tolerance below "
            "baseline (the peer ensemble carries the lift). A3 is strictly simpler "
            "(1 upstream model vs 3)."
        ),
    ]
    return "\n".join(lines)


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
                "A3 GPT-trace-only fresh-evidence reasoner (v0_11) live on "
                "validation750; Qwen + DeepSeek dropped from prompt; v0.4 3-agent "
                "baseline for comparison; held-out-family CV."
            ),
            mode="live",
            replay_status="live",
            repair_mode="v0_11_gpt_only_prompt",
            cache_reuse_source=str(CHECKPOINT_JSONL.relative_to(ROOT)),
            primary_metrics={
                "a3_purist": payload["a3_purist"],
                "baseline_purist": payload["baseline_purist"],
                "net_vs_baseline": payload["net_vs_baseline"],
                "gpt_only_purist": payload["gpt_only_purist"],
                "reasoner_net_vs_gpt": payload["reasoner_net_vs_gpt"],
                "gap_robust": cv["gap_robust"],
                "genuine_rate_regressions": len(payload["genuine_rate_regressions"]),
            },
            evidence_validity=(
                "validation750 development split (gan2026_split_v1), NOT a holdout "
                "or test450 result. Live openai/gpt-4.1 (synonymous with gpt-4.1-mini), "
                "temperature 0. Family CV is within-validation leave-one-band-out."
            ),
            decision=_REGISTRY_DECISION[payload["decision"]],
            supersedes=(),
            claim_language_notes=(
                "A3 simplest-architecture rung. Within-tolerance + gap_robust is "
                "necessary, NOT sufficient, for test450 authorisation; the robustness "
                "battery gate sits between this and any holdout run."
            ),
        )
    )
    write_run_registry(entries, REGISTRY_PATH)
    validate_run_registry_artifacts(load_run_registry(REGISTRY_PATH), repo_root=ROOT)
    write_run_registry_markdown(load_run_registry(REGISTRY_PATH), RUN_INDEX_PATH)


def _purist_ref(row: dict[str, Any], layer: str) -> bool:
    if layer == "v0_reference":
        d = row.get("v0_reference") or {}
    else:
        d = (row.get("score_layers") or {}).get(layer) or {}
    return bool(((d.get("comparison")) or {}).get("purist_correct"))


def main() -> None:
    records = gan_data.load_records_for_split(SPLIT)
    candidate_rows = _run_live(records)

    baseline = _score_indexed(list({int(r["source_row_index"]): r for r in load_jsonl_rows(BASELINE_V04_JSONL)}.values()))
    candidate = _score_indexed(candidate_rows)
    n = len(candidate_rows)

    a3_purist = sum(v["purist_correct"] for v in candidate.values())
    baseline_purist = sum(v["purist_correct"] for v in baseline.values())
    wrong_to_correct = sum(
        1 for idx, c in candidate.items()
        if idx in baseline and not baseline[idx]["purist_correct"] and c["purist_correct"]
    )
    correct_to_wrong = sum(
        1 for idx, c in candidate.items()
        if idx in baseline and baseline[idx]["purist_correct"] and not c["purist_correct"]
    )

    # Within-run action decomposition vs this run's own GPT pass.
    gpt_only_purist = sum(_purist_ref(r, "v0_reference") for r in candidate_rows)
    helped = hurt = neutral = keep_correct = keep_wrong = 0
    for r in candidate_rows:
        action = (r.get("fresh_evidence_decision_record") or {}).get("action")
        v0c = _purist_ref(r, "v0_reference")
        finc = _purist_ref(r, "final")
        if action == "replace_with_fresh_evidence_final":
            if finc and not v0c:
                helped += 1
            elif v0c and not finc:
                hurt += 1
            else:
                neutral += 1
        else:
            keep_correct += int(finc)
            keep_wrong += int(not finc)

    summary_by_family = _transitions_by_family(baseline, candidate)
    cv = family_cv_promotion.summarize_family_holdout_cv(summary_by_family)
    regressions = _genuine_rate_regressions(baseline, candidate)
    decision = _decide(a3_purist - baseline_purist, bool(cv["gap_robust"]))

    payload = {
        "run_id": RUN_ID,
        "date": DATE,
        "model": MODEL,
        "candidate": f"fresh_evidence_reasoner {fer.PROMPT_VERSION_V0_11_GPT_ONLY} live, temp 0",
        "baseline": f"fresh_evidence_reasoner v0.4 (3-agent) from {BASELINE_V04_JSONL.name}",
        "rows": n,
        "a3_purist": a3_purist,
        "baseline_purist": baseline_purist,
        "net_vs_baseline": a3_purist - baseline_purist,
        "wrong_to_correct": wrong_to_correct,
        "correct_to_wrong": correct_to_wrong,
        "gpt_only_purist": gpt_only_purist,
        "reasoner_net_vs_gpt": a3_purist - gpt_only_purist,
        "replace_helped": helped,
        "replace_hurt": hurt,
        "replace_neutral": neutral,
        "keep_correct": keep_correct,
        "keep_wrong": keep_wrong,
        "summary_by_family": summary_by_family,
        "family_cv": cv,
        "genuine_rate_regressions": regressions,
        "decision": decision,
    }

    JSON_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(_markdown(payload), encoding="utf-8")
    _register(payload)

    print(json.dumps(
        {
            "rows": n,
            "a3_purist": a3_purist,
            "baseline_purist": baseline_purist,
            "net_vs_baseline": a3_purist - baseline_purist,
            "gpt_only_purist": gpt_only_purist,
            "reasoner_net_vs_gpt": a3_purist - gpt_only_purist,
            "gap_robust": cv["gap_robust"],
            "genuine_rate_regressions": len(regressions),
            "decision": decision,
        },
        indent=2, sort_keys=True,
    ))


if __name__ == "__main__":
    main()
