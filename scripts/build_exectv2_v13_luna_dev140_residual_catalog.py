#!/usr/bin/env python3
"""Exhaustive v13 vs v0.9.24 residual catalog on Luna ExECT dev140.

No model calls. No test60 access. Reads the frozen v13 full-dev140 study
artifacts and gold development letters only.

Classifies every imperfect letter×family on the hybrid surface, measures
hybrid rescue versus harm on the same raws, and tags recurring constructions
for prompt-example versus rule work.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    load_letters_for_split,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
STUDY = REPO_ROOT / "experiments/exectv2_structured_prompt_v13_luna_dev140_20260815"
OUT_JSON = (
    REPO_ROOT
    / "experiments/exectv2_structured_prompt_v13_luna_dev140_residual_catalog_20260815.json"
)
PROTOCOL = (
    "docs/research/exectv2/structured_prompt_v13_luna_dev140_residual_catalog_"
    "protocol_2026-08-15.md"
)
REPORT = (
    "docs/research/exectv2/structured_prompt_v13_luna_dev140_residual_catalog_"
    "2026-08-15.md"
)
FAMILIES = ("Diagnosis", "SeizureFrequency", "Prescription", "Investigations")
SF_STATES = ("active-rate", "seizure-free", "unknown", "changed")
WORD_NUMBERS = {
    "several",
    "few",
    "couple",
    "a few",
    "a couple",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "none",
}
RX_PLAN_MARKERS = (
    "to start",
    "will start",
    "plan to",
    "planning to",
    "i suggest",
    "we will commence",
    "commence",
    "increasing to",
    "increase to",
    "if further",
    "if she",
    "if he",
    "target",
    "titrat",
    "week 1",
    "to be started",
)
RX_HISTORICAL_MARKERS = (
    "previously",
    "used to",
    "was on",
    "had been on",
    "stopped",
    "discontinued",
    "weaned",
    "in the past",
)
INV_PENDING_MARKERS = (
    "awaiting",
    "to arrange",
    "will arrange",
    "i will request",
    "we will request",
    "to be arranged",
    "pending",
    "booked",
    "refer for",
    "referral for",
)


def main() -> None:
    payload = build()
    OUT_JSON.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "status": "pass",
                "letters": payload["letter_count"],
                "imperfect_hybrid_cells": payload["summary"]["imperfect_hybrid_cells"],
                "output": OUT_JSON.as_posix(),
            },
            sort_keys=True,
        )
    )


def build() -> dict[str, Any]:
    gold_letters = {letter.letter_id: letter for letter in load_letters_for_split("dev")}
    if len(gold_letters) != 140:
        raise RuntimeError(f"expected 140 dev letters, found {len(gold_letters)}")

    families = {
        "v0924_head": _load_letter_family(STUDY / "v0924_head/letter_family.jsonl"),
        "v13_live": _load_letter_family(STUDY / "v13_live/letter_family.jsonl"),
    }
    metrics = {
        "v0924_head": _load_jsonl_by_id(STUDY / "v0924_head/letter_metrics.jsonl"),
        "v13_live": _load_jsonl_by_id(STUDY / "v13_live/letter_metrics.jsonl"),
    }
    structured = {
        "v0924_head": _load_jsonl_by_id(STUDY / "v0924_head/structured.jsonl"),
        "v13_live": _load_jsonl_by_id(STUDY / "v13_live/structured.jsonl"),
    }
    assemblies = {
        "v0924_head": _load_json_objects_by_id(STUDY / "v0924_head/assembly.jsonl"),
        "v13_live": _load_json_objects_by_id(STUDY / "v13_live/assembly.jsonl"),
    }
    projections = {
        "v0924_head": _load_jsonl_by_id(
            STUDY / "v0924_head/arm_sf_state_projection_combined.jsonl"
        ),
        "v13_live": _load_jsonl_by_id(
            STUDY / "v13_live/arm_sf_state_projection_combined.jsonl"
        ),
    }

    letter_ids = sorted(gold_letters)
    cells: list[dict[str, Any]] = []
    for letter_id in letter_ids:
        note = gold_letters[letter_id].note_text
        for family in FAMILIES:
            cells.append(
                _classify_cell(
                    letter_id=letter_id,
                    family=family,
                    note=note,
                    families=families,
                    metrics=metrics,
                    structured=structured,
                    assemblies=assemblies,
                    projections=projections,
                )
            )

    summary = _summarize(cells, metrics, projections)
    return {
        "schema_version": "exectv2.v13_luna_dev140_residual_catalog.v1",
        "date": date.today().isoformat(),
        "split": "dev140",
        "model": "openai/gpt-5.6-luna",
        "scorer": "four-family clinical_headline",
        "row_policy": "dev_rows_permitted",
        "holdout": "sealed",
        "model_calls": 0,
        "protocol": PROTOCOL,
        "report": REPORT,
        "parent_study": "experiments/exectv2_structured_prompt_v13_luna_dev140_20260815",
        "claim_boundary": (
            "Development residual catalog of v13+HEAD versus frozen Luna "
            "v0.9.24 through the same stack. Not holdout and not a fill."
        ),
        "letter_count": len(letter_ids),
        "cell_count": len(cells),
        "summary": summary,
        "modes": _mode_index(cells),
        "cells": cells,
    }


def _classify_cell(
    *,
    letter_id: str,
    family: str,
    note: str,
    families: dict[str, dict[str, dict[str, dict[str, Any]]]],
    metrics: dict[str, dict[str, dict[str, Any]]],
    structured: dict[str, dict[str, dict[str, Any]]],
    assemblies: dict[str, dict[str, dict[str, Any]]],
    projections: dict[str, dict[str, dict[str, Any]]],
) -> dict[str, Any]:
    v13 = families["v13_live"][letter_id][family]
    ctrl = families["v0924_head"][letter_id][family]
    gold = _expand_keys(v13["gold_keys"])
    v13_raw = _expand_keys(v13["raw_keys"])
    v13_hyb = _expand_keys(v13["hybrid_keys"])
    ctrl_raw = _expand_keys(ctrl["raw_keys"])
    ctrl_hyb = _expand_keys(ctrl["hybrid_keys"])

    v13_raw_shape = _shape(gold, v13_raw)
    v13_hyb_shape = _shape(gold, v13_hyb)
    ctrl_hyb_shape = _shape(gold, ctrl_hyb)

    v13_mentions = _family_mentions(
        structured["v13_live"][letter_id].get("predicted_mentions") or [],
        family,
    )
    ctrl_mentions = _family_mentions(
        structured["v0924_head"][letter_id].get("predicted_mentions") or [],
        family,
    )
    v13_hyb_mentions = _family_mentions(
        assemblies["v13_live"][letter_id].get("predicted_mentions") or [],
        family,
    )
    gold_mentions = _compact_gold(
        assemblies["v13_live"][letter_id].get("gold_mentions") or [],
        family,
    )

    mode, tags, construction = _primary_mode(
        family=family,
        gold=gold,
        pred=v13_hyb,
        raw=v13_raw,
        shape=v13_hyb_shape,
        raw_mentions=v13_mentions,
        hybrid_mentions=v13_hyb_mentions,
        gold_mentions=gold_mentions,
        note=note,
    )
    vs_ctrl = _vs_control(
        v13_exact=bool(v13["hybrid_letter_exact"]),
        ctrl_exact=bool(ctrl["hybrid_letter_exact"]),
    )
    hybrid_effect = _hybrid_effect(
        raw_exact=bool(v13["raw_letter_exact"]),
        hybrid_exact=bool(v13["hybrid_letter_exact"]),
        gold=gold,
        raw=v13_raw,
        hybrid=v13_hyb,
    )
    ctrl_hybrid_effect = _hybrid_effect(
        raw_exact=bool(ctrl["raw_letter_exact"]),
        hybrid_exact=bool(ctrl["hybrid_letter_exact"]),
        gold=gold,
        raw=ctrl_raw,
        hybrid=ctrl_hyb,
    )

    v13_metrics = metrics["v13_live"][letter_id]
    v13_proj = projections["v13_live"][letter_id]
    ctrl_proj = projections["v0924_head"][letter_id]
    lane = (assemblies["v13_live"][letter_id].get("lanes") or {}).get(family) or {}

    disposition = _disposition(mode, hybrid_effect, family)
    return {
        "letter_id": letter_id,
        "family": family,
        "gold_keys": _public_keys(gold),
        "v13_raw_keys": _public_keys(v13_raw),
        "v13_hybrid_keys": _public_keys(v13_hyb),
        "v0924_hybrid_keys": _public_keys(ctrl_hyb),
        "v13_raw_shape": v13_raw_shape,
        "v13_hybrid_shape": v13_hyb_shape,
        "v0924_hybrid_shape": ctrl_hyb_shape,
        "v13_raw_exact": bool(v13["raw_letter_exact"]),
        "v13_hybrid_exact": bool(v13["hybrid_letter_exact"]),
        "v0924_hybrid_exact": bool(ctrl["hybrid_letter_exact"]),
        "vs_v0924": vs_ctrl,
        "hybrid_effect": hybrid_effect,
        "v0924_hybrid_effect": ctrl_hybrid_effect,
        "mode": mode,
        "tags": tags,
        "construction": construction,
        "disposition": disposition,
        "empty_gold": not gold,
        "gold_mentions": gold_mentions,
        "v13_raw_mentions": v13_mentions,
        "v13_hybrid_mentions": v13_hyb_mentions,
        "v0924_raw_mentions": ctrl_mentions,
        "v13_projection_actions": _public_actions(v13_proj.get("projection_actions") or []),
        "v0924_projection_actions": _public_actions(ctrl_proj.get("projection_actions") or []),
        "v13_codebook_effect": v13_metrics.get("codebook_effect"),
        "v13_gate_events": list(v13_metrics.get("gate_events") or []),
        "v13_sf_encoding_rewrites": v13_metrics.get("sf_encoding_rewrites") or {},
        "v13_lens_diagnostics": _public_lens(lane.get("lens_diagnostics") or {}),
        "note_excerpt": _excerpt(note, 280),
    }


def _primary_mode(
    *,
    family: str,
    gold: Counter[tuple[Any, ...]],
    pred: Counter[tuple[Any, ...]],
    raw: Counter[tuple[Any, ...]],
    shape: str,
    raw_mentions: list[dict[str, Any]],
    hybrid_mentions: list[dict[str, Any]],
    gold_mentions: list[dict[str, Any]],
    note: str,
) -> tuple[str, list[str], str]:
    if shape.startswith("correct"):
        return "correct", [], "letter-exact on hybrid"
    extra = pred - gold
    miss = gold - pred
    raw_extra = raw - gold
    raw_miss = gold - raw
    hybrid_added = pred - raw
    hybrid_dropped = raw - pred
    dropped_wanted = Counter({k: n for k, n in hybrid_dropped.items() if k in gold})
    added_unwanted = Counter({k: n for k, n in hybrid_added.items() if k not in gold})

    tags: list[str] = []
    if dropped_wanted:
        tags.append("hybrid_dropped_wanted")
    if added_unwanted:
        tags.append("hybrid_added_unwanted")
    if hybrid_added and not added_unwanted:
        tags.append("hybrid_added_wanted")
    if hybrid_dropped and not dropped_wanted:
        tags.append("hybrid_dropped_unwanted")

    if family == "SeizureFrequency":
        return _sf_mode(
            shape=shape,
            extra=extra,
            miss=miss,
            dropped_wanted=dropped_wanted,
            added_unwanted=added_unwanted,
            tags=tags,
            raw_mentions=raw_mentions,
            gold_mentions=gold_mentions,
        )
    if family == "Diagnosis":
        return _dx_mode(
            shape=shape,
            extra=extra,
            miss=miss,
            dropped_wanted=dropped_wanted,
            added_unwanted=added_unwanted,
            tags=tags,
            raw_mentions=raw_mentions,
            gold_mentions=gold_mentions,
        )
    if family == "Prescription":
        return _rx_mode(
            shape=shape,
            extra=extra,
            miss=miss,
            dropped_wanted=dropped_wanted,
            added_unwanted=added_unwanted,
            tags=tags,
            raw_mentions=raw_mentions,
            hybrid_mentions=hybrid_mentions,
            gold_mentions=gold_mentions,
            note=note,
        )
    return _inv_mode(
        shape=shape,
        extra=extra,
        miss=miss,
        dropped_wanted=dropped_wanted,
        added_unwanted=added_unwanted,
        tags=tags,
        raw_mentions=raw_mentions,
        gold_mentions=gold_mentions,
        note=note,
        raw_extra=raw_extra,
        raw_miss=raw_miss,
    )


def _sf_mode(
    *,
    shape: str,
    extra: Counter[tuple[Any, ...]],
    miss: Counter[tuple[Any, ...]],
    dropped_wanted: Counter[tuple[Any, ...]],
    added_unwanted: Counter[tuple[Any, ...]],
    tags: list[str],
    raw_mentions: list[dict[str, Any]],
    gold_mentions: list[dict[str, Any]],
) -> tuple[str, list[str], str]:
    extra_states = _state_counts(extra)
    miss_states = _state_counts(miss)
    if dropped_wanted and _state_counts(dropped_wanted).get("active-rate"):
        return (
            "sf_hybrid_dropped_wanted_active_rate",
            tags,
            "HEAD dropped an active-rate key that gold still wants.",
        )
    if dropped_wanted and _state_counts(dropped_wanted).get("seizure-free"):
        return (
            "sf_hybrid_dropped_wanted_seizure_free",
            tags,
            "HEAD dropped a seizure-free key that gold still wants.",
        )
    if dropped_wanted and _state_counts(dropped_wanted).get("unknown"):
        return (
            "sf_hybrid_dropped_wanted_unknown",
            tags,
            "HEAD dropped an unknown-state key that gold still wants.",
        )
    if added_unwanted and _state_counts(added_unwanted).get("active-rate") and not miss:
        return (
            "sf_hybrid_added_unwanted_active_rate",
            tags,
            "HEAD added an extra active-rate that gold refuses.",
        )
    if shape == "empty_gold_spurious":
        dominant = _dominant_state(extra_states)
        return (
            f"sf_empty_gold_extra_{dominant.replace('-', '_')}",
            tags,
            f"Gold has no SF unit; v13 hybrid emitted extra {dominant}.",
        )
    if shape == "missed_all":
        dominant = _dominant_state(miss_states)
        return (
            f"sf_missed_all_{dominant.replace('-', '_')}",
            tags,
            f"v13 hybrid emitted no SF unit; gold wanted {dominant}.",
        )
    if shape == "extra_only":
        dominant = _dominant_state(extra_states)
        return (
            f"sf_extra_{dominant.replace('-', '_')}",
            tags,
            f"All gold units present; extra {dominant} remains.",
        )
    if shape == "missed_only":
        dominant = _dominant_state(miss_states)
        if dominant == "seizure-free" and _raw_has_last_event_without_zero(raw_mentions):
            tags.append("last_event_encoding_gap")
        if dominant == "active-rate" and _raw_has_word_number(raw_mentions):
            tags.append("word_number_present_in_raw")
        return (
            f"sf_missed_{dominant.replace('-', '_')}",
            tags,
            f"No extras; missing {dominant}.",
        )
    if _is_type_mismatch(extra, miss):
        return (
            "sf_type_cui_mismatch",
            tags,
            "State matches; named versus generic type does not.",
        )
    if _is_state_substitution(extra, miss):
        gold_state = _dominant_state(miss_states)
        pred_state = _dominant_state(extra_states)
        return (
            "sf_state_substitution",
            tags + [f"{gold_state}->{pred_state}"],
            f"Same type family, state {gold_state} became {pred_state}.",
        )
    if miss_states.get("seizure-free") and extra_states.get("active-rate"):
        return (
            "sf_last_event_as_active_rate",
            tags,
            "Gold seizure-free; hybrid still carries an active-rate.",
        )
    if miss_states.get("active-rate") and extra_states.get("unknown"):
        return (
            "sf_active_rate_as_unknown",
            tags,
            "Gold active-rate projected or emitted as unknown.",
        )
    if miss_states.get("seizure-free") and extra_states.get("unknown"):
        return (
            "sf_seizure_free_as_unknown",
            tags,
            "Gold seizure-free projected or emitted as unknown.",
        )
    return (
        "sf_mixed",
        tags,
        "Mixed extra and miss across SF states or types.",
    )


def _dx_mode(
    *,
    shape: str,
    extra: Counter[tuple[Any, ...]],
    miss: Counter[tuple[Any, ...]],
    dropped_wanted: Counter[tuple[Any, ...]],
    added_unwanted: Counter[tuple[Any, ...]],
    tags: list[str],
    raw_mentions: list[dict[str, Any]],
    gold_mentions: list[dict[str, Any]],
) -> tuple[str, list[str], str]:
    if added_unwanted and not miss:
        return (
            "dx_hybrid_added_unwanted",
            tags,
            "Diagnosis lens added a concept gold does not score.",
        )
    if dropped_wanted and not extra:
        return (
            "dx_hybrid_dropped_wanted",
            tags,
            "Diagnosis lens dropped a concept gold still wants.",
        )
    if shape == "empty_gold_spurious":
        return (
            "dx_empty_gold_extra",
            tags,
            "Gold has no Diagnosis unit; hybrid emitted extras.",
        )
    if shape == "missed_all":
        return (
            "dx_missed_all",
            tags,
            "Hybrid emitted no Diagnosis unit.",
        )
    if _looks_like_unsplit_heading(raw_mentions, gold_mentions, miss):
        return (
            "dx_heading_unsplit",
            tags,
            "Compound heading left as one concept; gold wants the split.",
        )
    if shape == "extra_only":
        return (
            "dx_extra_concept",
            tags,
            "All gold concepts present; extra diagnosis remains.",
        )
    if shape == "missed_only":
        return (
            "dx_missed_concept",
            tags,
            "No extras; missing a gold diagnosis concept.",
        )
    return (
        "dx_substituted",
        tags,
        "Wrong or partially overlapping diagnosis set.",
    )


def _rx_mode(
    *,
    shape: str,
    extra: Counter[tuple[Any, ...]],
    miss: Counter[tuple[Any, ...]],
    dropped_wanted: Counter[tuple[Any, ...]],
    added_unwanted: Counter[tuple[Any, ...]],
    tags: list[str],
    raw_mentions: list[dict[str, Any]],
    hybrid_mentions: list[dict[str, Any]],
    gold_mentions: list[dict[str, Any]],
    note: str,
) -> tuple[str, list[str], str]:
    if dropped_wanted and not extra:
        return (
            "rx_hybrid_dropped_wanted",
            tags,
            "Prescription lens dropped a complete regimen gold still wants.",
        )
    if added_unwanted and not miss:
        if _mentions_match_markers(hybrid_mentions, RX_PLAN_MARKERS, note):
            return (
                "rx_hybrid_kept_plan",
                tags,
                "Plan or titration regimen survived the lens.",
            )
        return (
            "rx_hybrid_added_unwanted",
            tags,
            "Lens or model left an extra complete regimen.",
        )
    if shape == "empty_gold_spurious":
        return (
            "rx_empty_gold_extra",
            tags,
            "Gold has no Prescription unit; hybrid emitted extras.",
        )
    if shape == "missed_all":
        return (
            "rx_missed_all",
            tags,
            "Hybrid emitted no complete regimen.",
        )
    if _same_name_dose_mismatch(extra, miss):
        return (
            "rx_dose_or_freq_mismatch",
            tags,
            "Same drug name; dose or frequency does not match gold.",
        )
    if shape == "extra_only":
        if _mentions_match_markers(hybrid_mentions, RX_PLAN_MARKERS, note):
            return (
                "rx_extra_plan_or_titration",
                tags,
                "Extra current-looking plan, start, or titration regimen.",
            )
        if _mentions_match_markers(hybrid_mentions, RX_HISTORICAL_MARKERS, note):
            return (
                "rx_extra_historical",
                tags,
                "Historical or stopped drug scored as current.",
            )
        return (
            "rx_extra_regimen",
            tags,
            "All gold regimens present; extra complete regimen remains.",
        )
    if shape == "missed_only":
        if any(
            str(m.get("text") or "").lower().find(str(_rx_name(k) or "")) >= 0
            for k in miss
            for m in raw_mentions
        ):
            tags.append("name_seen_in_raw")
        return (
            "rx_missed_current",
            tags,
            "No extras; missing a current complete regimen.",
        )
    if _same_name_dose_mismatch(extra, miss):
        return (
            "rx_dose_or_freq_mismatch",
            tags,
            "Same drug name; dose or frequency does not match gold.",
        )
    extra_names = {_rx_name(k) for k in extra}
    miss_names = {_rx_name(k) for k in miss}
    if extra_names and miss_names and extra_names == miss_names:
        return (
            "rx_dose_or_freq_mismatch",
            tags,
            "Same drug names; dose or frequency substituted.",
        )
    return (
        "rx_substituted",
        tags,
        "Mixed extra and missed prescription units.",
    )


def _inv_mode(
    *,
    shape: str,
    extra: Counter[tuple[Any, ...]],
    miss: Counter[tuple[Any, ...]],
    dropped_wanted: Counter[tuple[Any, ...]],
    added_unwanted: Counter[tuple[Any, ...]],
    tags: list[str],
    raw_mentions: list[dict[str, Any]],
    gold_mentions: list[dict[str, Any]],
    note: str,
    raw_extra: Counter[tuple[Any, ...]],
    raw_miss: Counter[tuple[Any, ...]],
) -> tuple[str, list[str], str]:
    if dropped_wanted and not extra:
        return (
            "inv_hybrid_dropped_wanted",
            tags,
            "Investigations lens dropped a completed test gold still wants.",
        )
    if added_unwanted and not miss:
        return (
            "inv_hybrid_added_unwanted",
            tags,
            "Investigations lens or model left an extra test.",
        )
    if shape == "empty_gold_spurious":
        return (
            "inv_empty_gold_extra",
            tags,
            "Gold has no Investigations unit; hybrid emitted extras.",
        )
    if shape == "missed_all":
        return (
            "inv_missed_all",
            tags,
            "Hybrid emitted no completed test.",
        )
    if _inv_result_mismatch(extra, miss):
        return (
            "inv_result_mismatch",
            tags,
            "Same modality; performed or result value differs.",
        )
    if shape == "extra_only":
        if _mentions_match_markers(raw_mentions, INV_PENDING_MARKERS, note):
            return (
                "inv_extra_pending",
                tags,
                "Pending or planned test scored as completed.",
            )
        return (
            "inv_extra_completed",
            tags,
            "Extra completed test remains.",
        )
    if shape == "missed_only":
        return (
            "inv_missed_completed",
            tags,
            "No extras; missing a completed test.",
        )
    return (
        "inv_substituted",
        tags,
        "Mixed extra and missed investigation units.",
    )


def _disposition(mode: str, hybrid_effect: str, family: str) -> str:
    if mode == "correct":
        return "hold"
    if hybrid_effect == "harm" or mode.startswith(
        ("sf_hybrid_dropped", "sf_hybrid_added_unwanted", "dx_hybrid_", "rx_hybrid_", "inv_hybrid_")
    ):
        return "rule_harm_or_revisit"
    if mode in {
        "sf_type_cui_mismatch",
        "sf_state_substitution",
        "sf_last_event_as_active_rate",
        "sf_seizure_free_as_unknown",
        "sf_active_rate_as_unknown",
        "sf_missed_seizure_free",
        "sf_missed_all_seizure_free",
        "sf_missed_active_rate",
        "sf_missed_all_active_rate",
        "dx_heading_unsplit",
        "dx_missed_concept",
        "dx_missed_all",
        "rx_missed_current",
        "rx_missed_all",
        "rx_dose_or_freq_mismatch",
        "inv_missed_completed",
        "inv_missed_all",
        "inv_result_mismatch",
    }:
        return "prompt_example_or_instruction"
    if mode.startswith(("sf_extra", "dx_extra", "rx_extra", "inv_extra")):
        return "scope_rule_or_prompt_negative"
    if mode.endswith("_mixed") or mode.endswith("substituted"):
        return "inspect_then_split"
    return "inspect"


def _summarize(
    cells: list[dict[str, Any]],
    metrics: dict[str, dict[str, dict[str, Any]]],
    projections: dict[str, dict[str, dict[str, Any]]],
) -> dict[str, Any]:
    imperfect = [c for c in cells if c["mode"] != "correct"]
    by_family: dict[str, dict[str, Any]] = {}
    for family in FAMILIES:
        fam = [c for c in cells if c["family"] == family]
        by_family[family] = {
            "n": len(fam),
            "v13_hybrid_exact": sum(1 for c in fam if c["v13_hybrid_exact"]),
            "v0924_hybrid_exact": sum(1 for c in fam if c["v0924_hybrid_exact"]),
            "losses": sum(1 for c in fam if c["vs_v0924"] == "loss"),
            "wins": sum(1 for c in fam if c["vs_v0924"] == "win"),
            "shared_miss": sum(1 for c in fam if c["vs_v0924"] == "shared_miss"),
            "hybrid_rescue": sum(1 for c in fam if c["hybrid_effect"] == "rescue"),
            "hybrid_harm": sum(1 for c in fam if c["hybrid_effect"] == "harm"),
            "hybrid_neutral_imperfect": sum(
                1 for c in fam if c["hybrid_effect"] == "neutral_imperfect"
            ),
            "modes": dict(Counter(c["mode"] for c in fam if c["mode"] != "correct")),
            "loss_modes": dict(
                Counter(c["mode"] for c in fam if c["vs_v0924"] == "loss")
            ),
            "harm_modes": dict(
                Counter(c["mode"] for c in fam if c["hybrid_effect"] == "harm")
            ),
            "dispositions": dict(Counter(c["disposition"] for c in fam if c["mode"] != "correct")),
        }

    v13_actions = Counter()
    ctrl_actions = Counter()
    action_help = Counter()
    action_harm = Counter()
    for letter_id, row in projections["v13_live"].items():
        sf_cell = next(
            c
            for c in cells
            if c["letter_id"] == letter_id and c["family"] == "SeizureFrequency"
        )
        for action in row.get("projection_actions") or []:
            rule = str(action.get("rule_id") or "")
            kind = str(action.get("action") or "")
            key = f"{kind}:{rule}"
            v13_actions[key] += 1
            if sf_cell["hybrid_effect"] == "rescue":
                action_help[key] += 1
            elif sf_cell["hybrid_effect"] == "harm":
                action_harm[key] += 1
    for row in projections["v0924_head"].values():
        for action in row.get("projection_actions") or []:
            ctrl_actions[f"{action.get('action')}:{action.get('rule_id')}"] += 1

    four_family: dict[str, dict[str, bool]] = {}
    for cell in cells:
        flags = four_family.setdefault(
            cell["letter_id"], {"v13": True, "v0924": True}
        )
        if not cell["v13_hybrid_exact"]:
            flags["v13"] = False
        if not cell["v0924_hybrid_exact"]:
            flags["v0924"] = False
    four_family_wins = [
        letter_id
        for letter_id, flags in four_family.items()
        if flags["v13"] and not flags["v0924"]
    ]
    four_family_losses = [
        letter_id
        for letter_id, flags in four_family.items()
        if flags["v0924"] and not flags["v13"]
    ]

    return {
        "imperfect_hybrid_cells": len(imperfect),
        "imperfect_letters": len({c["letter_id"] for c in imperfect}),
        "four_family_exact": {
            "v13": sum(1 for flags in four_family.values() if flags["v13"]),
            "v0924": sum(1 for flags in four_family.values() if flags["v0924"]),
            "wins": four_family_wins,
            "losses": four_family_losses,
            "net": len(four_family_wins) - len(four_family_losses),
        },
        "vs_v0924": dict(Counter(c["vs_v0924"] for c in cells)),
        "hybrid_effect": dict(Counter(c["hybrid_effect"] for c in cells)),
        "by_family": by_family,
        "sf_projection_actions": {
            "v13": dict(v13_actions),
            "v0924": dict(ctrl_actions),
            "v13_on_rescue_letters": dict(action_help),
            "v13_on_harm_letters": dict(action_harm),
        },
        "v13_codebook_effect": dict(
            Counter(row.get("codebook_effect") for row in metrics["v13_live"].values())
        ),
        "v0924_codebook_effect": dict(
            Counter(row.get("codebook_effect") for row in metrics["v0924_head"].values())
        ),
    }


def _mode_index(cells: list[dict[str, Any]]) -> dict[str, Any]:
    index: dict[str, Any] = {}
    for cell in cells:
        if cell["mode"] == "correct":
            continue
        bucket = index.setdefault(
            cell["mode"],
            {
                "mode": cell["mode"],
                "family": cell["family"],
                "disposition": cell["disposition"],
                "construction": cell["construction"],
                "n": 0,
                "letters": [],
                "losses_vs_v0924": [],
                "hybrid_harm": [],
                "hybrid_rescue": [],
                "examples": [],
            },
        )
        bucket["n"] += 1
        bucket["letters"].append(cell["letter_id"])
        if cell["vs_v0924"] == "loss":
            bucket["losses_vs_v0924"].append(cell["letter_id"])
        if cell["hybrid_effect"] == "harm":
            bucket["hybrid_harm"].append(cell["letter_id"])
        if cell["hybrid_effect"] == "rescue":
            bucket["hybrid_rescue"].append(cell["letter_id"])
        if len(bucket["examples"]) < 4:
            bucket["examples"].append(
                {
                    "letter_id": cell["letter_id"],
                    "gold_keys": cell["gold_keys"],
                    "v13_hybrid_keys": cell["v13_hybrid_keys"],
                    "v0924_hybrid_keys": cell["v0924_hybrid_keys"],
                    "v13_raw_mentions": cell["v13_raw_mentions"][:4],
                    "v13_hybrid_mentions": cell["v13_hybrid_mentions"][:4],
                    "v0924_raw_mentions": cell["v0924_raw_mentions"][:4],
                    "note_excerpt": cell["note_excerpt"],
                    "vs_v0924": cell["vs_v0924"],
                    "hybrid_effect": cell["hybrid_effect"],
                    "tags": cell["tags"],
                }
            )
    for bucket in index.values():
        bucket["letters"] = sorted(set(bucket["letters"]))
        bucket["losses_vs_v0924"] = sorted(set(bucket["losses_vs_v0924"]))
        bucket["hybrid_harm"] = sorted(set(bucket["hybrid_harm"]))
        bucket["hybrid_rescue"] = sorted(set(bucket["hybrid_rescue"]))
        bucket["n"] = len(bucket["letters"])
        bucket["n_losses_vs_v0924"] = len(bucket["losses_vs_v0924"])
        bucket["n_hybrid_harm"] = len(bucket["hybrid_harm"])
    return dict(sorted(index.items(), key=lambda item: (-item[1]["n"], item[0])))


def _load_letter_family(path: Path) -> dict[str, dict[str, dict[str, Any]]]:
    out: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in _read_jsonl(path):
        out[str(row["letter_id"])][str(row["family"])] = row
    if len(out) != 140:
        raise RuntimeError(f"{path} has {len(out)} letters, expected 140")
    return out


def _load_jsonl_by_id(path: Path) -> dict[str, dict[str, Any]]:
    rows = {str(row["letter_id"]): row for row in _read_jsonl(path)}
    if len(rows) != 140:
        raise RuntimeError(f"{path} has {len(rows)} letters, expected 140")
    return rows


def _load_json_objects_by_id(path: Path) -> dict[str, dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    decoder = json.JSONDecoder()
    rows: dict[str, dict[str, Any]] = {}
    index = 0
    while index < len(text):
        while index < len(text) and text[index].isspace():
            index += 1
        if index >= len(text):
            break
        obj, index = decoder.raw_decode(text, index)
        rows[str(obj["letter_id"])] = obj
    if len(rows) != 140:
        raise RuntimeError(f"{path} has {len(rows)} letters, expected 140")
    return rows


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _expand_keys(items: list[dict[str, Any]] | None) -> Counter[tuple[Any, ...]]:
    counts: Counter[tuple[Any, ...]] = Counter()
    for item in items or []:
        key = _freeze(item.get("key"))
        counts[key] += int(item.get("count") or 1)
    return counts


def _freeze(value: Any) -> tuple[Any, ...]:
    if isinstance(value, list):
        return tuple(_freeze(item) if isinstance(item, list) else item for item in value)
    return (value,)


def _public_keys(counter: Counter[tuple[Any, ...]]) -> list[dict[str, Any]]:
    return [
        {"count": count, "key": _unfreeze(key)}
        for key, count in sorted(counter.items(), key=lambda item: repr(item[0]))
    ]


def _unfreeze(value: tuple[Any, ...]) -> Any:
    out = [
        list(item) if isinstance(item, tuple) else item
        for item in value
    ]
    return out[0] if len(out) == 1 and not isinstance(value[0], tuple) else out


def _shape(gold: Counter[tuple[Any, ...]], pred: Counter[tuple[Any, ...]]) -> str:
    extra = sum((pred - gold).values())
    miss = sum((gold - pred).values())
    if extra == 0 and miss == 0:
        return "correct_empty" if not gold else "correct_nonempty"
    if not gold and pred:
        return "empty_gold_spurious"
    if gold and not pred:
        return "missed_all"
    if extra > 0 and miss == 0:
        return "extra_only"
    if miss > 0 and extra == 0:
        return "missed_only"
    return "substituted_or_mixed"


def _vs_control(*, v13_exact: bool, ctrl_exact: bool) -> str:
    if v13_exact and ctrl_exact:
        return "shared_exact"
    if v13_exact and not ctrl_exact:
        return "win"
    if ctrl_exact and not v13_exact:
        return "loss"
    return "shared_miss"


def _hybrid_effect(
    *,
    raw_exact: bool,
    hybrid_exact: bool,
    gold: Counter[tuple[Any, ...]],
    raw: Counter[tuple[Any, ...]],
    hybrid: Counter[tuple[Any, ...]],
) -> str:
    if raw_exact and hybrid_exact:
        return "hold_exact"
    if (not raw_exact) and hybrid_exact:
        return "rescue"
    if raw_exact and not hybrid_exact:
        return "harm"
    raw_err = sum((raw - gold).values()) + sum((gold - raw).values())
    hyb_err = sum((hybrid - gold).values()) + sum((gold - hybrid).values())
    if hyb_err < raw_err:
        return "partial_rescue"
    if hyb_err > raw_err:
        return "harm"
    return "neutral_imperfect"


def _family_mentions(mentions: list[dict[str, Any]], family: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for mention in mentions:
        if str(mention.get("entity") or "") != family:
            continue
        attrs = {
            str(key): str(value)
            for key, value in (mention.get("attributes") or {}).items()
            if value not in (None, "")
        }
        out.append(
            {
                "text": mention.get("text"),
                "attributes": attrs,
                "evidence": str(mention.get("evidence") or "")[:220],
            }
        )
    return out


def _compact_gold(mentions: list[dict[str, Any]], family: str) -> list[dict[str, Any]]:
    return _family_mentions(mentions, family)


def _public_actions(actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "action": action.get("action"),
            "rule_id": action.get("rule_id"),
            "text": action.get("text"),
        }
        for action in actions
    ]


def _public_lens(diagnostics: dict[str, Any]) -> dict[str, Any]:
    keep = (
        "added_dictionary_findings",
        "dropped_dictionary_findings",
        "rewritten_dictionary_findings",
        "selected_findings",
        "dropped_non_antiepileptic_findings",
        "normalized_dictionary_findings",
        "split_regimen_dictionary_findings",
        "pending_investigations_dropped",
        "cross_modality_not_performed_stripped",
        "lens_id",
        "producer_id",
    )
    return {key: diagnostics[key] for key in keep if key in diagnostics}


def _state_counts(counter: Counter[tuple[Any, ...]]) -> Counter[str]:
    states: Counter[str] = Counter()
    for key, count in counter.items():
        states[_sf_state(key)] += count
    return states


def _sf_state(key: tuple[Any, ...]) -> str:
    if len(key) >= 2 and key[1] in SF_STATES:
        return str(key[1])
    return "other"


def _dominant_state(states: Counter[str]) -> str:
    if not states:
        return "other"
    return states.most_common(1)[0][0]


def _is_type_mismatch(
    extra: Counter[tuple[Any, ...]],
    miss: Counter[tuple[Any, ...]],
) -> bool:
    extra_states = {_sf_state(key) for key in extra}
    miss_states = {_sf_state(key) for key in miss}
    return bool(extra) and extra_states == miss_states and extra_states <= set(SF_STATES)


def _is_state_substitution(
    extra: Counter[tuple[Any, ...]],
    miss: Counter[tuple[Any, ...]],
) -> bool:
    extra_types = {_sf_type(key) for key in extra}
    miss_types = {_sf_type(key) for key in miss}
    extra_states = {_sf_state(key) for key in extra}
    miss_states = {_sf_state(key) for key in miss}
    return bool(extra_types & miss_types) and extra_states != miss_states


def _sf_type(key: tuple[Any, ...]) -> Any:
    return key[0] if key else None


def _raw_has_word_number(mentions: list[dict[str, Any]]) -> bool:
    for mention in mentions:
        value = str((mention.get("attributes") or {}).get("NumberOfSeizures") or "").lower()
        if value in WORD_NUMBERS:
            return True
        text = " ".join(
            [
                str(mention.get("text") or ""),
                str(mention.get("evidence") or ""),
            ]
        ).lower()
        if any(token in text for token in ("several", "a few", "few ", "couple")):
            return True
    return False


def _raw_has_last_event_without_zero(mentions: list[dict[str, Any]]) -> bool:
    for mention in mentions:
        blob = " ".join(
            [
                str(mention.get("text") or ""),
                str(mention.get("evidence") or ""),
                " ".join((mention.get("attributes") or {}).values()),
            ]
        ).lower()
        count = str((mention.get("attributes") or {}).get("NumberOfSeizures") or "")
        last_event_markers = (
            "last event",
            "last seizure",
            "none since",
            "no further",
            "seizure free",
            "seizure-free",
        )
        if any(token in blob for token in last_event_markers):
            if count not in {"0", "zero"}:
                return True
    return False


def _looks_like_unsplit_heading(
    raw_mentions: list[dict[str, Any]],
    gold_mentions: list[dict[str, Any]],
    miss: Counter[tuple[Any, ...]],
) -> bool:
    if not miss:
        return False
    raw_text = " | ".join(str(m.get("text") or "") for m in raw_mentions).lower()
    markers = ("probable", "possible", "unclassified", " - ", " – ", "focal onset", "temporal")
    return any(marker in raw_text for marker in markers) and len(gold_mentions) > len(raw_mentions)


def _same_name_dose_mismatch(
    extra: Counter[tuple[Any, ...]],
    miss: Counter[tuple[Any, ...]],
) -> bool:
    extra_names = {_rx_name(key) for key in extra}
    miss_names = {_rx_name(key) for key in miss}
    return bool(extra_names and extra_names == miss_names)


def _rx_name(key: tuple[Any, ...]) -> str | None:
    if len(key) >= 2 and key[0] in {"ordinary", "rescue"}:
        return str(key[1])
    return None


def _inv_result_mismatch(
    extra: Counter[tuple[Any, ...]],
    miss: Counter[tuple[Any, ...]],
) -> bool:
    extra_mod = {_inv_modality(key) for key in extra}
    miss_mod = {_inv_modality(key) for key in miss}
    return bool(extra_mod and extra_mod == miss_mod)


def _inv_modality(key: tuple[Any, ...]) -> str | None:
    if key:
        return str(key[0])
    return None


def _mentions_match_markers(
    mentions: list[dict[str, Any]],
    markers: tuple[str, ...],
    note: str,
) -> bool:
    blobs = [
        " ".join(
            [
                str(mention.get("text") or ""),
                str(mention.get("evidence") or ""),
            ]
        ).lower()
        for mention in mentions
    ]
    blobs.append(note.lower())
    joined = " \n ".join(blobs)
    return any(marker in joined for marker in markers)


def _excerpt(note: str, limit: int) -> str:
    compact = " ".join(note.split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 1] + "…"


if __name__ == "__main__":
    main()
