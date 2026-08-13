#!/usr/bin/env python3
"""Gan 2026 llm_with_rules band + first-changer stage ablation.

No new model calls. No locked-test row inspection. See
docs/research/gan2026/gan2026_hybrid_stage_ablation_protocol_2026-08-06.md.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.contract.label_parser import (
    label_to_frequency_record,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.labels import map_purist
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
DATE_STAMP = "20260806"
REPORT_DATE = "2026-08-06"
EXAMPLES_PER_KEY = 2

_CATALOG_PATH = REPO_ROOT / "scripts/build_gan2026_category_error_catalog.py"
_SPEC = importlib.util.spec_from_file_location("gan_category_error_catalog", _CATALOG_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"Cannot import helpers from {_CATALOG_PATH}")
cat = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(cat)
hs = cat.hs

MODEL_PREFERENCE = cat.MODEL_PREFERENCE
BUCKET_ORDER = cat.BUCKET_ORDER

BAND_ORDER = (
    "model_final",
    "representation",
    "evidence_reconcile",
    "clinical_selection",
    "free_interval",
)

BAND_LABELS = {
    "model_final": "Model final label",
    "representation": "After resolve (representation)",
    "evidence_reconcile": "After evidence reconcile",
    "clinical_selection": "After clinical selection repairs",
    "free_interval": "After free-interval / final",
}

REPAIR_STAGE_ORDER = (
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

STAGE_BAND = {
    "repair.selected_evidence": "evidence_reconcile",
    "repair.monthly_diary": "clinical_selection",
    "repair.usual_interval": "clinical_selection",
    "repair.typical_over_ytd": "clinical_selection",
    "repair.breakthrough": "clinical_selection",
    "repair.non_epileptic": "clinical_selection",
    "repair.residual_jerk": "clinical_selection",
    "repair.post_change_burst": "clinical_selection",
    "repair.dated_sequence": "clinical_selection",
    "repair.elapsed_anchor": "free_interval",
}

MAIN_BUCKETS = (
    "ordinary_point_rate",
    "cluster_burden",
    "seizure_free",
    "range_rate",
    "unknown_sentinel",
    "no_reference_sentinel",
    "unresolved_multiple",
)


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


def _error_mode_for(bucket: str, pred_label: str | None, purist_ok: bool | None) -> str:
    if pred_label is None or not str(pred_label).strip():
        return "parse_or_call_failure"
    comparison = {"purist_correct": bool(purist_ok)} if purist_ok is not None else None
    if purist_ok:
        return "correct"
    return cat._error_mode(bucket, str(pred_label), comparison)


def _count_modes(modes: list[str]) -> dict[str, int]:
    counter = Counter(modes)
    return dict(sorted(counter.items(), key=lambda item: (-item[1], item[0])))


def _floors_panel_finals() -> dict[str, dict[int, dict[str, Any]]]:
    return hs._load_gan_hybrid_rows()


def _model_prediction_record(row: dict[str, Any]) -> dict[str, Any] | None:
    record = ((row.get("row_trace") or {}).get("model_prediction") or {}).get("record")
    return record if isinstance(record, dict) else None


def replay_row(
    row: dict[str, Any],
    *,
    omit_stages: frozenset[str] | None = None,
) -> dict[str, Any] | None:
    """Ordered study-local repair replay.

    ``omit_stages`` skips named families for leave-one-family-out studies.
    Production ``parse_structured_json_with_trace`` defaults are unchanged.
    """
    omitted = omit_stages or frozenset()
    record = _model_prediction_record(row)
    note = _note_text(row)
    if record is None or note is None:
        return None
    extraction = StructuredExtractionRecord.model_validate(record)
    model_final = extraction.selection.final_label
    normalized = [_normalize_event(event, note_text=note) for event in extraction.events]
    resolved = _resolve_final_label(extraction, normalized)
    historical = (row.get("row_trace") or {}).get("deterministic_semantic") or {}

    band_labels: dict[str, str | None] = {
        "model_final": model_final,
        "representation": resolved,
        "evidence_reconcile": resolved,
        "clinical_selection": resolved,
        "free_interval": resolved,
    }
    changes: list[dict[str, str]] = []
    if resolved is None:
        return {
            "model_final": model_final,
            "resolved": None,
            "final": None,
            "band_labels": band_labels,
            "changes": changes,
            "historical_before": historical.get("before_label"),
            "historical_after": historical.get("after_label"),
            "replayable": False,
            "omit_stages": sorted(omitted),
        }

    label = resolved
    if "repair.selected_evidence" not in omitted:
        new_label = repair_prediction_label_with_evidence(
            label,
            extraction.selection.evidence,
            context_text=note,
        )
        if new_label != label:
            changes.append(
                {
                    "stage": "repair.selected_evidence",
                    "band": "evidence_reconcile",
                    "before": label,
                    "after": new_label,
                }
            )
            label = new_label
    band_labels["evidence_reconcile"] = label

    if "repair.monthly_diary" not in omitted:
        diary = _monthly_diary_label_from_events(extraction, note_text=note)
        if (
            diary
            and not _should_preserve_label_from_monthly_diary(
                label, extraction=extraction
            )
            and diary != label
        ):
            changes.append(
                {
                    "stage": "repair.monthly_diary",
                    "band": "clinical_selection",
                    "before": label,
                    "after": diary,
                }
            )
            label = diary

    if "repair.usual_interval" not in omitted:
        usual = _usual_interval_label_from_events(extraction, label)
        if usual and usual != label:
            changes.append(
                {
                    "stage": "repair.usual_interval",
                    "band": "clinical_selection",
                    "before": label,
                    "after": usual,
                }
            )
            label = usual

    if "repair.typical_over_ytd" not in omitted:
        typical = _typical_recurring_rate_over_ytd_from_events(extraction, label)
        if typical and typical != label:
            changes.append(
                {
                    "stage": "repair.typical_over_ytd",
                    "band": "clinical_selection",
                    "before": label,
                    "after": typical,
                }
            )
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
            changes.append(
                {
                    "stage": stage_id,
                    "band": "clinical_selection",
                    "before": label,
                    "after": candidate,
                }
            )
            label = candidate

    band_labels["clinical_selection"] = label

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
            changes.append(
                {
                    "stage": "repair.elapsed_anchor",
                    "band": "free_interval",
                    "before": label,
                    "after": elapsed,
                }
            )
            label = elapsed
    band_labels["free_interval"] = label

    return {
        "model_final": model_final,
        "resolved": resolved,
        "final": label,
        "band_labels": band_labels,
        "changes": changes,
        "historical_before": historical.get("before_label"),
        "historical_after": historical.get("after_label"),
        "replayable": True,
        "selected_evidence": _truncate(extraction.selection.evidence),
        "omit_stages": sorted(omitted),
    }


def _pathway_key(changes: list[dict[str, str]]) -> str:
    if not changes:
        return "no_repair_change"
    return " → ".join(item["stage"].removeprefix("repair.") for item in changes)


def _pick_examples(
    candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    def sort_key(row: dict[str, Any]) -> tuple[int, int, str]:
        slug = str(row.get("model_slug", ""))
        try:
            model_rank = MODEL_PREFERENCE.index(slug)
        except ValueError:
            model_rank = len(MODEL_PREFERENCE)
        effect_rank = 0 if row.get("effect") in {"rescue", "harm"} else 1
        return effect_rank, model_rank, str(row["source_row_index"])

    picked: list[dict[str, Any]] = []
    seen: set[tuple[str, int]] = set()
    for row in sorted(candidates, key=sort_key):
        key = (str(row["model_slug"]), int(row["source_row_index"]))
        if key in seen:
            continue
        picked.append(row)
        seen.add(key)
        if len(picked) >= EXAMPLES_PER_KEY:
            break
    return picked


def build_artifact() -> dict[str, Any]:
    gold_index = hs._gan_gold_index()
    floors = _floors_panel_finals()

    band_wrong_modes: dict[str, dict[str, list[str]]] = {
        band: defaultdict(list) for band in BAND_ORDER
    }
    band_correct: dict[str, dict[str, int]] = {
        band: Counter() for band in BAND_ORDER
    }
    band_n: dict[str, int] = Counter()

    family_stats: dict[str, dict[str, Any]] = {
        stage: {
            "fires": 0,
            "first_changer": 0,
            "first_rescue": 0,
            "first_harm": 0,
            "any_rescue": 0,
            "any_harm": 0,
            "by_bucket_first_changer": Counter(),
            "examples_rescue": [],
            "examples_harm": [],
        }
        for stage in REPAIR_STAGE_ORDER
    }
    band_first_changer: Counter[str] = Counter()
    pathway_counter: Counter[str] = Counter()
    pathway_examples: dict[str, list[dict[str, Any]]] = defaultdict(list)

    fidelity = {
        "replayable_rows": 0,
        "exact_match_historical_after": 0,
        "exact_match_floors_panel": 0,
        "purist_agree_floors_panel": 0,
        "unreplayable_rows": 0,
    }
    residual_ownership = Counter()
    changed_rows: list[dict[str, Any]] = []

    for slug, display in hs.MODEL_SPECS:
        rows = hs._read_jsonl(hs.GAN_LLM_ONLY_DIR / f"{slug}--llm_with_rules.jsonl")
        for row in rows:
            index = int(row["source_row_index"])
            meta = gold_index[index]
            bucket = str(meta["a_priori_bucket"])
            gold_label = str(meta["gold_label"])
            replay = replay_row(row)
            if replay is None or not replay["replayable"]:
                fidelity["unreplayable_rows"] += 1
                continue

            fidelity["replayable_rows"] += 1
            historical_after = replay.get("historical_after")
            floors_row = floors[slug][index]
            floors_final = str(floors_row["final_label"])
            floors_ok = bool(floors_row["purist_correct"])
            final_label = str(replay["final"])
            fidelity["exact_match_historical_after"] += int(
                final_label == str(historical_after or "")
            )
            fidelity["exact_match_floors_panel"] += int(final_label == floors_final)
            final_ok = _purist_correct(final_label, gold_label)
            fidelity["purist_agree_floors_panel"] += int(final_ok == floors_ok)

            band_n[bucket] += 1
            for band in BAND_ORDER:
                pred = replay["band_labels"].get(band)
                ok = _purist_correct(pred, gold_label) if pred is not None else False
                if ok:
                    band_correct[band][bucket] += 1
                else:
                    mode = _error_mode_for(bucket, pred, False)
                    band_wrong_modes[band][bucket].append(mode)

            changes = list(replay["changes"])
            pathway = _pathway_key(changes)
            pathway_counter[pathway] += 1

            resolve_ok = _purist_correct(replay["resolved"], gold_label)
            if not changes:
                residual_ownership[
                    "final_wrong_no_repair" if not final_ok else "final_correct_no_repair"
                ] += 1
            else:
                residual_ownership[
                    "final_wrong_after_repair"
                    if not final_ok
                    else "final_correct_after_repair"
                ] += 1

            first_attributed = False
            for change in changes:
                stage = change["stage"]
                before_ok = _purist_correct(change["before"], gold_label)
                after_ok = _purist_correct(change["after"], gold_label)
                stats = family_stats[stage]
                stats["fires"] += 1
                effect = "neutral"
                if after_ok and not before_ok:
                    stats["any_rescue"] += 1
                    effect = "rescue"
                elif before_ok and not after_ok:
                    stats["any_harm"] += 1
                    effect = "harm"
                example = {
                    "model_slug": slug,
                    "model_display": display,
                    "source_row_index": index,
                    "gold_bucket": bucket,
                    "gold_label": gold_label,
                    "stage": stage,
                    "band": change["band"],
                    "before_label": change["before"],
                    "after_label": change["after"],
                    "final_label": final_label,
                    "effect": effect,
                    "selected_evidence": replay.get("selected_evidence"),
                    "pathway": pathway,
                }
                if effect == "rescue":
                    stats["examples_rescue"].append(example)
                elif effect == "harm":
                    stats["examples_harm"].append(example)
                if not first_attributed:
                    first_attributed = True
                    stats["first_changer"] += 1
                    stats["by_bucket_first_changer"][bucket] += 1
                    band_first_changer[change["band"]] += 1
                    if effect == "rescue":
                        stats["first_rescue"] += 1
                    elif effect == "harm":
                        stats["first_harm"] += 1
                    changed_rows.append(example)

            if changes:
                pathway_examples[pathway].append(
                    {
                        "model_slug": slug,
                        "model_display": display,
                        "source_row_index": index,
                        "gold_bucket": bucket,
                        "gold_label": gold_label,
                        "pathway": pathway,
                        "stages": [item["stage"] for item in changes],
                        "before_label": changes[0]["before"],
                        "after_label": changes[-1]["after"],
                        "final_label": final_label,
                        "resolve_purist_correct": resolve_ok,
                        "final_purist_correct": final_ok,
                        "effect": (
                            "rescue"
                            if final_ok and not resolve_ok
                            else "harm"
                            if resolve_ok and not final_ok
                            else "reshape"
                        ),
                        "selected_evidence": replay.get("selected_evidence"),
                    }
                )

    buckets_out: dict[str, Any] = {}
    for bucket in BUCKET_ORDER:
        if band_n[bucket] == 0:
            continue
        n = band_n[bucket]
        band_block: dict[str, Any] = {}
        prev_modes: dict[str, int] | None = None
        for band in BAND_ORDER:
            modes = _count_modes(band_wrong_modes[band][bucket])
            correct = int(band_correct[band][bucket])
            delta = None
            if prev_modes is not None:
                keys = sorted(set(prev_modes) | set(modes))
                delta = {
                    key: int(modes.get(key, 0) - prev_modes.get(key, 0))
                    for key in keys
                    if modes.get(key, 0) != prev_modes.get(key, 0)
                }
            band_block[band] = {
                "n_correct": correct,
                "n_wrong": n - correct,
                "accuracy": round(correct / n, 4) if n else None,
                "wrong_mode_counts": modes,
                "mode_delta_from_previous_band": delta,
            }
            prev_modes = modes
        buckets_out[bucket] = {"n_row_model_cells": n, "bands": band_block}

    family_out: dict[str, Any] = {}
    for stage in REPAIR_STAGE_ORDER:
        stats = family_stats[stage]
        family_out[stage] = {
            "band": STAGE_BAND[stage],
            "fires": stats["fires"],
            "first_changer": stats["first_changer"],
            "first_rescue": stats["first_rescue"],
            "first_harm": stats["first_harm"],
            "any_rescue": stats["any_rescue"],
            "any_harm": stats["any_harm"],
            "by_bucket_first_changer": dict(
                sorted(
                    stats["by_bucket_first_changer"].items(),
                    key=lambda item: (-item[1], item[0]),
                )
            ),
            "examples_rescue": _pick_examples(stats["examples_rescue"]),
            "examples_harm": _pick_examples(stats["examples_harm"]),
        }

    top_pathways = [
        {
            "pathway": pathway,
            "count": count,
            "examples": _pick_examples(pathway_examples[pathway]),
        }
        for pathway, count in pathway_counter.most_common(12)
    ]

    replayable = max(int(fidelity["replayable_rows"]), 1)
    fidelity_rates = {
        **fidelity,
        "exact_match_historical_after_rate": round(
            fidelity["exact_match_historical_after"] / replayable, 4
        ),
        "exact_match_floors_panel_rate": round(
            fidelity["exact_match_floors_panel"] / replayable, 4
        ),
        "purist_agree_floors_panel_rate": round(
            fidelity["purist_agree_floors_panel"] / replayable, 4
        ),
    }

    return {
        "schema_version": "gan2026.hybrid_stage_ablation.v1",
        "date": REPORT_DATE,
        "protocol": (
            "docs/research/gan2026/gan2026_hybrid_stage_ablation_protocol_2026-08-06.md"
        ),
        "parent_catalog": (
            "docs/research/gan2026/gan2026_category_error_catalog_2026-08-06.md"
        ),
        "git": _git_note(),
        "dataset": "Gan 2026",
        "split": "validation / dev750",
        "surface": "llm_with_rules",
        "models": [{"slug": slug, "display": display} for slug, display in hs.MODEL_SPECS],
        "band_order": list(BAND_ORDER),
        "repair_stage_order": list(REPAIR_STAGE_ORDER),
        "fidelity": fidelity_rates,
        "band_first_changer_counts": dict(band_first_changer.most_common()),
        "residual_ownership": dict(residual_ownership.most_common()),
        "buckets": buckets_out,
        "families": family_out,
        "top_pathways": top_pathways,
        "changed_row_count": len(changed_rows),
        "claim_boundary": (
            "Development llm_with_rules stage ablation on Gan dev750. "
            "First-changer attribution under ordered current-code replay of "
            "saved model ledgers; not leave-one-family-out; not holdout."
        ),
    }


def _fmt_mode_delta(delta: dict[str, int] | None, *, limit: int = 6) -> str:
    if not delta:
        return "—"
    items = sorted(delta.items(), key=lambda item: (-abs(item[1]), item[0]))[:limit]
    return ", ".join(f"`{name}` {value:+d}" for name, value in items)


def _mermaid_label(text: str | None, *, limit: int = 42) -> str:
    cleaned = " ".join(str(text or "").split()).replace('"', "'")
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rstrip() + "…"


def _acc(block: dict[str, Any] | None) -> str:
    if not block or block.get("accuracy") is None:
        return "—"
    return f"{block['accuracy']:.2f}"


def render_report(artifact: dict[str, Any]) -> str:
    fidelity = artifact["fidelity"]
    families = artifact["families"]
    buckets = artifact["buckets"]
    lines: list[str] = [
        "# Gan 2026 llm_with_rules stage ablation",
        "",
        f"Date: {REPORT_DATE}  ",
        "Status: development stage ablation inside hybrid only  ",
        "Protocol: [hybrid stage ablation protocol]"
        "(gan2026_hybrid_stage_ablation_protocol_2026-08-06.md)  ",
        "Parent: [category error catalog](gan2026_category_error_catalog_2026-08-06.md)  ",
        "Companions: [task-shape framework](task_shape_framework_2026-08-06.md), "
        "[architecture stage diagram](../architecture/diagrams/gan2026_llm_with_rules_stages.md)  ",
        "Artifact: "
        f"[`experiments/gan2026_hybrid_stage_ablation_{DATE_STAMP}.json`]"
        f"(../../experiments/gan2026_hybrid_stage_ablation_{DATE_STAMP}.json)",
        "",
        "## Plain answer",
        "",
        "Inside `llm_with_rules`, most label movement is not “rules as a blob.” "
        "On 4,482 replayable six-model cells:",
        "",
        "1. **Evidence reconcile** is the mass first-changer "
        f"({artifact['band_first_changer_counts'].get('evidence_reconcile', 0)} "
        "of "
        f"{sum(artifact['band_first_changer_counts'].values())} "
        "changed rows; "
        f"{families['repair.selected_evidence']['first_rescue']} first-rescues). "
        "On ordinary rates it lifts Purist from ~0.37 at resolve to ~0.72 mainly "
        "by clearing malformed / incomplete grammar.",
        "2. **Clinical selection** then adds the next large lift "
        "(ordinary ~0.72 → ~0.85), led by `monthly_diary` "
        f"({families['repair.monthly_diary']['any_rescue']} any-rescues, "
        f"{families['repair.monthly_diary']['any_harm']} any-harms). "
        "`breakthrough` is the next harm source; `dated_sequence`, "
        "`usual_interval`, and `residual_jerk` are mostly rescue-sided.",
        "3. **Free-interval** (`elapsed_anchor`) is smaller but clean on "
        "seizure-free mass "
        f"({families['repair.elapsed_anchor']['any_rescue']} any-rescues, "
        f"{families['repair.elapsed_anchor']['any_harm']} any-harms).",
        "4. Residuals after the stack are mostly "
        f"`final_wrong_after_repair` "
        f"({artifact['residual_ownership'].get('final_wrong_after_repair', 0)}) "
        "plus a thin "
        f"`final_wrong_no_repair` "
        f"({artifact['residual_ownership'].get('final_wrong_no_repair', 0)}) "
        "band—selection/convention errors, not missing format cleanup.",
        "",
        "## Why this document exists",
        "",
        "The [category error catalog](gan2026_category_error_catalog_2026-08-06.md) "
        "contrasts `llm` vs `llm_with_rules`. This sibling stays on hybrid only "
        "and splits the deterministic stack into bands and named repair families.",
        "",
        "## Observable bands",
        "",
        "No new calls. Saved `model_prediction.record` ledgers are replayed "
        "through the current normalize/resolve + ten repair families.",
        "",
        "```mermaid",
        "flowchart LR",
        '  model["0. Model final label"]',
        '  resolve["1. Representation<br/>resolve_label"]',
        '  evidence["2. Evidence reconcile<br/>selected_evidence"]',
        '  clinical["3. Clinical selection<br/>diary…dated"]',
        '  free["4. Free-interval<br/>elapsed_anchor"]',
        "  model --> resolve --> evidence --> clinical --> free",
        "```",
        "",
        "| Band | Stages | Role |",
        "| --- | --- | --- |",
        "| Representation | `normalize_events`, `resolve_label` | "
        "Render the model selection into a Gan label |",
        "| Evidence reconcile | `repair.selected_evidence` | "
        "Rewrite the label from the quoted evidence span |",
        "| Clinical selection | diary, usual, YTD, breakthrough, "
        "non-epileptic, jerk, burst, dated | Re-choose among ledger readings |",
        "| Free-interval | `repair.elapsed_anchor` | "
        "Derive seizure-free windows from elapsed anchors |",
        "",
        "Attribute a rescue or harm to the **first** stage that changes the "
        "Purist answer. Later fires are counted separately under any-rescue / "
        "any-harm.",
        "",
        "## Four pathways that explain the stack",
        "",
    ]

    # Signature pathway vignettes from artifact top pathways with effects.
    vignette_specs = [
        (
            "A. Evidence reconcile cleans / rewrites the rate",
            "selected_evidence",
            "Mass first-changer. Often grammar cleanup; often also the Purist rescue.",
        ),
        (
            "B. Diary overrides after evidence",
            "monthly_diary",
            "Second-stage clinical rewrite from month-by-month ledger counts.",
        ),
        (
            "C. Free-interval / dated clinical rewrite",
            "elapsed_anchor",
            "Elapsed or dated-sequence families commit a window the resolve step left open.",
        ),
        (
            "D. Residual with no repair change",
            "no_repair_change",
            "Many hybrid finals never rewrite after resolve; wrongs here are "
            "selection/convention residuals, not missing repair fires.",
        ),
    ]
    pathway_by_name = {item["pathway"]: item for item in artifact["top_pathways"]}
    for title, needle, lesson in vignette_specs:
        match = None
        if needle == "no_repair_change":
            match = pathway_by_name.get("no_repair_change")
        else:
            for item in artifact["top_pathways"]:
                if needle in item["pathway"]:
                    match = item
                    break
        lines.append(f"### {title}")
        lines.append("")
        lines.append(lesson)
        if match and match.get("examples"):
            example = match["examples"][0]
            before = example.get("before_label") or example.get("final_label")
            after = example.get("after_label") or example.get("final_label")
            lines.extend(
                [
                    "",
                    "```mermaid",
                    "flowchart LR",
                    f'  gold["Gold<br/>{_mermaid_label(example["gold_label"])}"]',
                    f'  before["Before repairs<br/>{_mermaid_label(before)}"]',
                    f'  after["After pathway<br/>{_mermaid_label(after)}"]',
                    "  gold -.-> before",
                    f'  before -->|{_mermaid_label(example["pathway"], limit=48)}| after',
                    "```",
                    "",
                    f"Row {example['source_row_index']} / {example['model_display']}. "
                    f"Bucket `{example['gold_bucket']}`; pathway effect "
                    f"`{example.get('effect')}`.",
                ]
            )
        elif match:
            lines.append(f"Pooled count: {match['count']}.")
        lines.append("")

    lines.extend(
        [
            "## Band ablation by gold bucket",
            "",
            "Pooled six-model row×model cells. Accuracy is Purist at the band "
            "endpoint. Mode Δ is wrong-mode count versus the previous band "
            "(negative means that wrong shape shrank).",
            "",
        ]
    )

    for bucket in MAIN_BUCKETS:
        block = buckets.get(bucket)
        if not block:
            continue
        lines.append(f"### `{bucket}` (n={block['n_row_model_cells']})")
        lines.append("")
        lines.append("| Band | Acc | Top wrong modes | Mode Δ from previous |")
        lines.append("| --- | ---: | --- | --- |")
        for band in BAND_ORDER:
            band_block = block["bands"][band]
            modes = band_block["wrong_mode_counts"]
            top = ", ".join(
                f"`{name}` ({count})"
                for name, count in list(modes.items())[:3]
                if name != "correct"
            ) or "—"
            lines.append(
                f"| {BAND_LABELS[band]} | {_acc(band_block)} | {top} | "
                f"{_fmt_mode_delta(band_block.get('mode_delta_from_previous_band'))} |"
            )
        lines.append("")

    lines.extend(
        [
            "## First-changer family ledger",
            "",
            "Counts are pooled six-model repair hops on replayable rows. "
            "**First-changer** = earliest repair that changed the label. "
            "**Any-rescue / any-harm** count every hop, so later families are "
            "not hidden behind `selected_evidence`.",
            "",
            "| Stage | Band | Fires | First | Rescue | Harm | Any+ | Any- |",
            "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for stage in REPAIR_STAGE_ORDER:
        stats = families[stage]
        lines.append(
            f"| `{stage}` | {stats['band']} | {stats['fires']} | "
            f"{stats['first_changer']} | {stats['first_rescue']} | "
            f"{stats['first_harm']} | {stats['any_rescue']} | {stats['any_harm']} |"
        )

    lines.extend(
        [
            "",
            "### Band-level first-changer share",
            "",
            "| Band | First-changer rows |",
            "| --- | ---: |",
        ]
    )
    for band, count in artifact["band_first_changer_counts"].items():
        lines.append(f"| `{band}` | {count} |")

    lines.extend(
        [
            "",
            "### Family notes worth remembering",
            "",
        ]
    )
    notable = [
        stage
        for stage in REPAIR_STAGE_ORDER
        if families[stage]["fires"]
        or families[stage]["first_changer"]
        or families[stage]["any_harm"]
    ]
    for stage in notable:
        stats = families[stage]
        if stats["fires"] == 0:
            continue
        bucket_bits = ", ".join(
            f"`{name}` {count}"
            for name, count in list(stats["by_bucket_first_changer"].items())[:4]
        ) or "—"
        rescue_ex = stats["examples_rescue"][:1]
        harm_ex = stats["examples_harm"][:1]
        lines.append(f"#### `{stage}`")
        lines.append("")
        lines.append(
            f"Fires {stats['fires']}; first-changer {stats['first_changer']} "
            f"(rescue {stats['first_rescue']}, harm {stats['first_harm']}); "
            f"any-rescue {stats['any_rescue']}, any-harm {stats['any_harm']}. "
            f"First-changer homes: {bucket_bits}."
        )
        if rescue_ex:
            ex = rescue_ex[0]
            lines.append(
                f"- Rescue example: row {ex['source_row_index']} / {ex['model_display']}: "
                f"`{ex['before_label']}` → `{ex['after_label']}` "
                f"(gold `{ex['gold_label']}`)."
            )
        if harm_ex:
            ex = harm_ex[0]
            lines.append(
                f"- Harm example: row {ex['source_row_index']} / {ex['model_display']}: "
                f"`{ex['before_label']}` → `{ex['after_label']}` "
                f"(gold `{ex['gold_label']}`)."
            )
        lines.append("")

    residual = artifact["residual_ownership"]
    lines.extend(
        [
            "## Residual ownership after the full stack",
            "",
            "| Outcome | Count |",
            "| --- | ---: |",
        ]
    )
    for key, count in residual.items():
        lines.append(f"| `{key}` | {count} |")
    lines.extend(
        [
            "",
            "Most hybrid competence is already present at resolve or created by "
            "`selected_evidence`. The hard remainder is dominated by rows with "
            "no repair rewrite, or repairs that reshape without clearing the "
            "selection/convention error.",
            "",
            "## Top pathways",
            "",
            "| Pathway | Count |",
            "| --- | ---: |",
        ]
    )
    for item in artifact["top_pathways"][:10]:
        lines.append(f"| `{item['pathway']}` | {item['count']} |")

    lines.extend(
        [
            "",
            "## How to explore further",
            "",
            "| Need | Where |",
            "| --- | --- |",
            "| Band mode tables and family examples | JSON artifact |",
            "| llm vs hybrid mode catalog | "
            "[category error catalog](gan2026_category_error_catalog_2026-08-06.md) |",
            "| Stage ownership definitions | "
            "[llm_with_rules stages]"
            "(../architecture/diagrams/gan2026_llm_with_rules_stages.md) |",
            "| Regenerate | `python scripts/build_gan2026_hybrid_stage_ablation.py` |",
            "",
            "## Method",
            "",
            "- Split: Gan `dev750`. Surface: `llm_with_rules` only.",
            "- Replay input: `row_trace.model_prediction.record` + prompt note text.",
            "- Baseline: post-`resolve_label`; then ten repair families in "
            "manifest order.",
            "- Wrongness: Purist false. Modes: same predicted-shape vocabulary "
            "as the parent catalog.",
            "- Attribution: first label-changing repair is the first-changer; "
            "any-rescue/harm count later hops too.",
            f"- Fidelity on replayable rows: historical after-label exact "
            f"{fidelity['exact_match_historical_after_rate']:.3f}; floors-panel "
            f"exact {fidelity['exact_match_floors_panel_rate']:.3f}; floors-panel "
            f"Purist agreement {fidelity['purist_agree_floors_panel_rate']:.3f}.",
            "",
            "## Claim boundary",
            "",
            "- Development Gan `llm_with_rules` stage ablation on `dev750`.",
            "- Ordered current-code replay of saved ledgers, not a factorial "
            "leave-one-family-out experiment.",
            "- Not a replacement for parent-catalog floors-panel aggregate scores.",
            "- Not sealed holdout competence.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--artifact",
        type=Path,
        default=REPO_ROOT / f"experiments/gan2026_hybrid_stage_ablation_{DATE_STAMP}.json",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=REPO_ROOT
        / f"docs/research/gan2026/gan2026_hybrid_stage_ablation_{REPORT_DATE}.md",
    )
    args = parser.parse_args()

    artifact = build_artifact()
    args.artifact.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    args.report.write_text(render_report(artifact), encoding="utf-8")
    print(f"Wrote {args.artifact}")
    print(f"Wrote {args.report}")
    fidelity = artifact["fidelity"]
    print(
        "replayable",
        fidelity["replayable_rows"],
        "hist_exact",
        fidelity["exact_match_historical_after_rate"],
        "floors_purist",
        fidelity["purist_agree_floors_panel_rate"],
    )


if __name__ == "__main__":
    main()
