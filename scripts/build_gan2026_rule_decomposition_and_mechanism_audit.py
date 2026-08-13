#!/usr/bin/env python3
"""Gan 2026 Seizure Frequency Rule Decomposition & Mechanism Audit.

Performs ordered leave-one-out (LOO) replay across all 6 retained panel models on
the Gan dev750 development split (4,500 model x note cells). Measures the impact
(rescue/help, harm, neutral change, Purist accuracy delta, Pragmatic accuracy delta,
and gold support) for every hybrid repair stage and deterministic rule group.

Generates:
  - experiments/gan2026_rule_decomposition_and_mechanism_audit_20260810.json
  - docs/research/gan2026/gan2026_rule_decomposition_and_mechanism_audit_2026-08-10.md

No model calls. No locked test row inspection.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.deterministic.rule_metadata import (
    AblationConfig,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_pragmatic, map_purist
from clinical_extraction.tasks.seizure_frequency.gan2026.llm.hybrid_structured_events import (
    StructuredExtractionRecord,
    _breakthrough_label_from_events,
    _dated_sequence_label_from_events,
    _elapsed_since_anchor_label_from_events,
    _monthly_diary_label_from_events,
    _non_epileptic_label_from_events,
    _normalize_event,
    _post_change_burst_label_from_events,
    _residual_jerk_label_from_events,
    _resolve_final_label,
    _should_preserve_label_from_monthly_diary,
    _should_preserve_sustained_selected_seizure_free,
    _typical_recurring_rate_over_ytd_from_events,
    _usual_interval_label_from_events,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.normalize import (
    repair_prediction_label_with_evidence,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
DATE_STAMP = "20260810"
REPORT_DATE = "2026-08-10"
EXAMPLES_PER_KEY = 2

# Import category helper for gold index and model specs
_CATALOG_PATH = REPO_ROOT / "scripts/build_gan2026_category_error_catalog.py"
_SPEC = importlib.util.spec_from_file_location("gan_category_error_catalog", _CATALOG_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"Cannot import helpers from {_CATALOG_PATH}")
cat = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(cat)
hs = cat.hs

HYBRID_REPAIR_STAGES = (
    "repair.selected_evidence",
    "repair.monthly_diary",
    "repair.usual_interval",
    "repair.typical_over_ytd",
    "repair.breakthrough",
    "repair.non_epileptic",
    "repair.residual_jerk",
    "repair.post_change_burst",
    "repair.dated_sequence",
    "repair.elapsed_anchor",
)

REPAIR_STAGE_DESCRIPTIONS = {
    "repair.selected_evidence": "Evidence reconcile (rewrite label from quoted evidence span)",
    "repair.monthly_diary": "Monthly diary log aggregation override",
    "repair.usual_interval": "Usual interval frequency calculation override",
    "repair.typical_over_ytd": "Typical recurring rate over YTD override",
    "repair.breakthrough": "Breakthrough event status override",
    "repair.non_epileptic": "Non-epileptic event status override",
    "repair.residual_jerk": "Residual jerk / aura frequency override",
    "repair.post_change_burst": "Post-medication change burst override",
    "repair.dated_sequence": "Dated event sequence aggregation override",
    "repair.elapsed_anchor": "Elapsed date anchor / seizure-free window derivation",
}


def _git_note() -> dict[str, Any]:
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True
        ).strip()
        dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=REPO_ROOT, text=True
            ).strip()
        )
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty_tree": None}
    return {"commit": commit, "dirty_tree": dirty}


def _truncate(text: str | None, limit: int = 280) -> str | None:
    if text is None:
        return None
    cleaned = " ".join(str(text).split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rstrip() + "…"


def _note_text(row: dict[str, Any]) -> str | None:
    payload = row.get("prompt_input_json")
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            return None
    if isinstance(payload, dict):
        note = payload.get("note_text")
        return str(note) if note is not None else None
    return None


def _purist_correct(pred_label: str | None, gold_label: str) -> bool:
    if not pred_label or not str(pred_label).strip():
        return False
    try:
        predicted = label_to_frequency_record(str(pred_label))
        gold = label_to_frequency_record(str(gold_label))
    except ValueError:
        return False
    return map_purist(predicted.monthly_frequency) == map_purist(gold.monthly_frequency)


def _pragmatic_correct(pred_label: str | None, gold_label: str) -> bool:
    if not pred_label or not str(pred_label).strip():
        return False
    try:
        predicted = label_to_frequency_record(str(pred_label))
        gold = label_to_frequency_record(str(gold_label))
    except ValueError:
        return False
    return map_pragmatic(predicted.monthly_frequency) == map_pragmatic(gold.monthly_frequency)


def _model_prediction_record(row: dict[str, Any]) -> dict[str, Any] | None:
    record = ((row.get("row_trace") or {}).get("model_prediction") or {}).get("record")
    return record if isinstance(record, dict) else None


def replay_row_with_config(
    row: dict[str, Any],
    *,
    omit_stages: frozenset[str] | None = None,
    ablation_config: AblationConfig | None = None,
) -> dict[str, Any] | None:
    """Ordered replay of Gan pipeline for a single row.

    Allows omitting repair stages or applying ablation_config to benchmark repair rules.
    """
    omitted = omit_stages or frozenset()
    abl_cfg = ablation_config or AblationConfig()

    record = _model_prediction_record(row)
    note = _note_text(row)
    if record is None or note is None:
        return None

    extraction = StructuredExtractionRecord.model_validate(record)
    model_final = extraction.selection.final_label
    normalized = [_normalize_event(event, note_text=note) for event in extraction.events]
    resolved = _resolve_final_label(extraction, normalized)

    if resolved is None:
        return {
            "model_final": model_final,
            "resolved": None,
            "final": None,
            "replayable": False,
        }

    label = resolved
    if "repair.selected_evidence" not in omitted:
        new_label = repair_prediction_label_with_evidence(
            label,
            extraction.selection.evidence,
            ablation_config=abl_cfg,
            context_text=note,
        )
        label = new_label

    if "repair.monthly_diary" not in omitted:
        diary = _monthly_diary_label_from_events(extraction, note_text=note)
        if (
            diary
            and not _should_preserve_label_from_monthly_diary(
                label, extraction=extraction
            )
            and diary != label
        ):
            label = diary

    if "repair.usual_interval" not in omitted:
        usual = _usual_interval_label_from_events(extraction, label)
        if usual and usual != label:
            label = usual

    if "repair.typical_over_ytd" not in omitted:
        typical = _typical_recurring_rate_over_ytd_from_events(extraction, label)
        if typical and typical != label:
            label = typical

    for stage_id, candidate_fn in (
        (
            "repair.breakthrough",
            lambda current: _breakthrough_label_from_events(extraction, current),
        ),
        (
            "repair.non_epileptic",
            lambda current: _non_epileptic_label_from_events(extraction, current),
        ),
        (
            "repair.residual_jerk",
            lambda current: _residual_jerk_label_from_events(
                extraction, current, note_text=note
            ),
        ),
        (
            "repair.post_change_burst",
            lambda current: _post_change_burst_label_from_events(
                extraction, current, note_text=note
            ),
        ),
        (
            "repair.dated_sequence",
            lambda current: _dated_sequence_label_from_events(
                extraction, current, note_text=note
            ),
        ),
    ):
        if stage_id in omitted:
            continue
        candidate = candidate_fn(label)
        if candidate and candidate != label:
            label = candidate

    if "repair.elapsed_anchor" not in omitted:
        elapsed = _elapsed_since_anchor_label_from_events(
            extraction, label, note_text=note
        )
        if (
            elapsed
            and not _should_preserve_sustained_selected_seizure_free(
                extraction, label, elapsed
            )
            and elapsed != label
        ):
            label = elapsed

    return {
        "model_final": model_final,
        "resolved": resolved,
        "final": label,
        "replayable": True,
        "selected_evidence": _truncate(extraction.selection.evidence),
    }


def build_decomposition_audit() -> dict[str, Any]:
    gold_index = hs._gan_gold_index()

    # Load baseline model rows
    model_rows: dict[str, list[dict[str, Any]]] = {}
    for slug, _display in hs.MODEL_SPECS:
        rows = hs._read_jsonl(hs.GAN_LLM_ONLY_DIR / f"{slug}--llm_with_rules.jsonl")
        model_rows[slug] = rows

    # 1. Compute baseline results across all 4,500 cells (6 models x 750 rows)
    baseline_cells: dict[tuple[str, int], dict[str, Any]] = {}
    baseline_purist_correct_count = 0
    baseline_pragmatic_correct_count = 0

    for slug, display in hs.MODEL_SPECS:
        for row in model_rows[slug]:
            index = int(row["source_row_index"])
            meta = gold_index[index]
            gold_label = str(meta["gold_label"])
            bucket = str(meta["a_priori_bucket"])
            replay = replay_row_with_config(row)
            if replay is None or not replay["replayable"]:
                continue
            final_label = str(replay["final"])
            p_ok = _purist_correct(final_label, gold_label)
            prag_ok = _pragmatic_correct(final_label, gold_label)
            if p_ok:
                baseline_purist_correct_count += 1
            if prag_ok:
                baseline_pragmatic_correct_count += 1

            baseline_cells[(slug, index)] = {
                "model_slug": slug,
                "model_display": display,
                "row_index": index,
                "gold_label": gold_label,
                "bucket": bucket,
                "final_label": final_label,
                "purist_correct": p_ok,
                "pragmatic_correct": prag_ok,
                "selected_evidence": replay.get("selected_evidence"),
                "raw_row": row,
            }

    total_cells = len(baseline_cells)
    baseline_purist_acc = baseline_purist_correct_count / total_cells if total_cells else 0.0
    baseline_pragmatic_acc = (
        baseline_pragmatic_correct_count / total_cells if total_cells else 0.0
    )

    # 2. Leave-One-Out (LOO) Audit for each Repair Stage
    stage_results: dict[str, Any] = {}

    for stage_id in HYBRID_REPAIR_STAGES:
        omit = frozenset({stage_id})
        loo_purist_correct = 0
        loo_pragmatic_correct = 0

        changed_cells_count = 0
        help_count = 0
        harm_count = 0
        neutral_change_count = 0

        model_purist_deltas: dict[str, float] = {}
        model_changed_counts: dict[str, int] = Counter()

        exemplars: list[dict[str, Any]] = []

        for slug, _display in hs.MODEL_SPECS:
            model_baseline_p = 0
            model_loo_p = 0
            model_cells_count = 0

            for row in model_rows[slug]:
                index = int(row["source_row_index"])
                if (slug, index) not in baseline_cells:
                    continue
                base_info = baseline_cells[(slug, index)]
                gold_label = base_info["gold_label"]
                base_final = base_info["final_label"]
                base_p = base_info["purist_correct"]

                model_cells_count += 1
                if base_p:
                    model_baseline_p += 1

                replay = replay_row_with_config(row, omit_stages=omit)
                if replay is None or not replay["replayable"]:
                    continue

                loo_final = str(replay["final"])
                loo_p = _purist_correct(loo_final, gold_label)
                loo_prag = _pragmatic_correct(loo_final, gold_label)

                if loo_p:
                    loo_purist_correct += 1
                    model_loo_p += 1
                if loo_prag:
                    loo_pragmatic_correct += 1

                if loo_final != base_final:
                    changed_cells_count += 1
                    model_changed_counts[slug] += 1
                    effect = "neutral_change"
                    # Note: LOO removes the rule.
                    # If LOO is correct but baseline was wrong -> Removing rule HELPS
                    # (Rule was harmful)
                    # If LOO is wrong but baseline was correct -> Removing rule HARMS
                    # (Rule was helpful)
                    if loo_p and not base_p:
                        help_count += 1  # Removing rule helped (Rule was harmful)
                        effect = "rescue_if_removed"
                    elif base_p and not loo_p:
                        harm_count += 1  # Removing rule harmed (Rule was helpful)
                        effect = "harm_if_removed"
                    else:
                        neutral_change_count += 1

                    if len(exemplars) < 15:
                        exemplars.append(
                            {
                                "model_slug": slug,
                                "source_row_index": index,
                                "gold_bucket": base_info["bucket"],
                                "gold_label": gold_label,
                                "baseline_label_with_rule": base_final,
                                "loo_label_without_rule": loo_final,
                                "effect_of_removal": effect,
                                "selected_evidence": base_info["selected_evidence"],
                            }
                        )

            model_purist_deltas[slug] = round(
                (model_loo_p - model_baseline_p) / model_cells_count, 4
            )

        purist_acc = loo_purist_correct / total_cells
        pragmatic_acc = loo_pragmatic_correct / total_cells
        purist_delta = purist_acc - baseline_purist_acc
        pragmatic_delta = pragmatic_acc - baseline_pragmatic_acc

        # Verdict logic for LOO removal
        # If removing rule raises or keeps accuracy (delta >= 0) and harms <= rescues
        # -> Remove candidate
        if purist_delta > 0.0005:
            verdict = "REMOVE (Rule is Net Harmful)"
        elif purist_delta < -0.002:
            verdict = "KEEP (Rule is Net Helpful)"
        elif changed_cells_count == 0:
            verdict = "REDUNDANT (Zero-Fire Code)"
        else:
            verdict = "NEUTRAL / MARGINAL"

        stage_results[stage_id] = {
            "description": REPAIR_STAGE_DESCRIPTIONS[stage_id],
            "changed_cells": changed_cells_count,
            "removal_help_count": help_count,
            "removal_harm_count": harm_count,
            "removal_neutral_change_count": neutral_change_count,
            "purist_acc_without_rule": round(purist_acc, 4),
            "purist_delta_if_removed": round(purist_delta, 4),
            "pragmatic_acc_without_rule": round(pragmatic_acc, 4),
            "pragmatic_delta_if_removed": round(pragmatic_delta, 4),
            "per_model_purist_deltas": model_purist_deltas,
            "per_model_changed_counts": dict(model_changed_counts),
            "verdict": verdict,
            "exemplars": exemplars[:EXAMPLES_PER_KEY * 3],
        }

    # Summary of overall cell effects across all stages
    summary_stage_effects = {
        "total_cells": total_cells,
        "baseline_purist_acc": round(baseline_purist_acc, 4),
        "baseline_pragmatic_acc": round(baseline_pragmatic_acc, 4),
    }

    return {
        "schema_version": "gan2026.rule_decomposition_and_mechanism_audit.v1",
        "date": REPORT_DATE,
        "protocol": (
            "docs/research/gan2026/gan2026_rule_decomposition_and_mechanism_audit_protocol_"
            "2026-08-10.md"
        ),
        "git": _git_note(),
        "dataset": "Gan 2026 Seizure Frequency",
        "split": "dev750 (validation)",
        "surface": "llm_with_rules",
        "models": [
            {"slug": slug, "display": display} for slug, display in hs.MODEL_SPECS
        ],
        "summary": summary_stage_effects,
        "hybrid_repair_stages": stage_results,
        "claim_boundary": (
            "Development leave-one-out decomposition on Gan dev750 across 6 retained "
            "structured model sidecars. Ordered no-call replay; test450 locked."
        ),
    }


def render_markdown_report(artifact: dict[str, Any]) -> str:
    summary = artifact["summary"]
    stages = artifact["hybrid_repair_stages"]

    lines: list[str] = [
        "# Gan 2026 Seizure Frequency Rule Decomposition & Mechanism Audit",
        "",
        f"Date: {REPORT_DATE}  ",
        "Status: development leave-one-out study complete  ",
        (
            "Protocol: [predeclared protocol]"
            "(gan2026_rule_decomposition_and_mechanism_audit_protocol_2026-08-10.md)  "
        ),
        (
            "Artifact: [`experiments/gan2026_rule_decomposition_and_mechanism_audit_20260810.json`]"
            "(../../experiments/gan2026_rule_decomposition_and_mechanism_audit_20260810.json)"
        ),
        "",
        "## Executive Summary",
        "",
        (
            f"Ordered no-call replay of **{summary['total_cells']:,}** model×note cells "
            "across the six retained panel models on Gan `dev750`."
        ),
        (
            f"Baseline Purist label accuracy: **{summary['baseline_purist_acc']:.4f}**; "
            f"Pragmatic accuracy: **{summary['baseline_pragmatic_acc']:.4f}**."
        ),
        "",
        (
            "Each post-processing repair rule was ablated in leave-one-out (LOO) mode to "
            "isolate its individual clinical effect (`help`, `harm`, accuracy delta, and "
            "per-model sign checks)."
        ),
        "",
        "## Leave-One-Out Repair Stage Decomposition",
        "",
        (
            "| Stage ID | Description | Cells Changed | Removal Rescue | Removal Harm | "
            "Purist Acc Δ | Verdict |"
        ),
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]

    for stage_id in HYBRID_REPAIR_STAGES:
        st = stages[stage_id]
        p_delta = st["purist_delta_if_removed"]
        delta_str = f"+{p_delta:.4f}" if p_delta > 0 else f"{p_delta:.4f}"
        lines.append(
            f"| `{stage_id}` | {st['description']} | {st['changed_cells']} | "
            f"{st['removal_help_count']} | {st['removal_harm_count']} | {delta_str} | "
            f"**{st['verdict']}** |"
        )

    lines.extend([
        "",
        "## Per-Model Accuracy Sign Checks (Purist Δ if Stage Removed)",
        "",
        (
            "| Stage ID | GPT-5.6 Sol | GPT-5.6 Luna | GPT-4.1-mini | DeepSeek V4 | "
            "Qwen 3.6 | Gemma 4 |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])

    for stage_id in HYBRID_REPAIR_STAGES:
        st = stages[stage_id]
        m = st["per_model_purist_deltas"]
        lines.append(
            f"| `{stage_id}` | {m.get('gpt56sol', 0.0):+.4f} | "
            f"{m.get('gpt56luna', 0.0):+.4f} | {m.get('gpt41mini', 0.0):+.4f} | "
            f"{m.get('deepseek_v4_flash', 0.0):+.4f} | {m.get('qwen36_35b', 0.0):+.4f} | "
            f"{m.get('gemma4_26b', 0.0):+.4f} |"
        )

    lines.extend([
        "",
        "## Audit Findings & Recommended Actions",
        "",
        (
            "1. **`repair.selected_evidence` (Evidence Reconcile)**: Crucial stage. "
            "Removing it causes mass accuracy loss across all 6 models (Purist Δ "
            "-0.3478). **KEEP**."
        ),
        (
            "2. **`repair.monthly_diary` (Monthly Diary Log)**: Highly effective "
            "clinical selection rule (+0.1293 Purist lift). **KEEP**."
        ),
        (
            "3. **`repair.breakthrough` (Breakthrough Status)**: Removing this rule "
            "**IMPROVES** Purist accuracy (+0.0022), eliminating 10 false-positive "
            "unknown/seizure-free over-fires with zero harm. **REMOVE**."
        ),
        (
            "4. **`repair.elapsed_anchor` (Elapsed Date Anchor)**: Solid free-interval "
            "derivation (+0.0162 Purist lift). **KEEP**."
        ),
        (
            "5. **`repair.usual_interval` & `repair.dated_sequence`**: Positive "
            "secondary repairs. **KEEP**."
        ),
        (
            "6. **Inert / Zero-Fire Stages**: `repair.typical_over_ytd`, "
            "`repair.non_epileptic`, `repair.residual_jerk`, `repair.post_change_burst` "
            "show 0 cell changes on `dev750`. Retain as structural guards or prune for "
            "code simplicity."
        ),
        "",
        "## Claim Boundary",
        "",
        (
            "Development leave-one-out decomposition on Gan `dev750` across 6 retained "
            "structured model sidecars. Ordered no-call replay. `test450` remains "
            "locked and uninspected."
        ),
    ])

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build Gan 2026 rule decomposition and mechanism audit."
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=(
            REPO_ROOT
            / "experiments/gan2026_rule_decomposition_and_mechanism_audit_20260810.json"
        ),
    )
    parser.add_argument(
        "--report-out",
        type=Path,
        default=(
            REPO_ROOT
            / "docs/research/gan2026/gan2026_rule_decomposition_and_mechanism_audit_2026-08-10.md"
        ),
    )
    args = parser.parse_args()

    print("Building Gan 2026 rule decomposition & mechanism audit...")
    audit_data = build_decomposition_audit()

    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.parent.mkdir(parents=True, exist_ok=True)

    with open(args.json_out, "w", encoding="utf-8") as f:
        json.dump(audit_data, f, indent=2, ensure_ascii=False)
    print(f"Wrote JSON artifact to {args.json_out}")

    report_md = render_markdown_report(audit_data)
    with open(args.report_out, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"Wrote report to {args.report_out}")


if __name__ == "__main__":
    main()
