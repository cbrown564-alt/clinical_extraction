#!/usr/bin/env python3
"""Audit and prototype an active-rate over-read guard for ExECTv2 SeizureFrequency.

Development-only, no-call replay over the six retained dev140 sidecars. See
docs/research/exectv2_sf_active_rate_overread_guard_protocol_2026-08-11.md.

The guard classifies the (already evidence-gated) ``evidence`` string of each
predicted SeizureFrequency mention whose state is ``active-rate`` into one of
four frozen, predeclared regex families: historical / hypothetical /
descriptive / current. Mentions classifying as non-current are dropped from a
*candidate* predicted-mentions list; the candidate list is then re-scored
against gold with the same clinical-headline SeizureFrequency scorer used
elsewhere in this study line, both per-model and pooled.

Zero model calls. No test59/test60 file is read.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    annotation_from_mapping,
    headline_keys,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.seizure_frequency import (
    _frequency_state,
    _frequency_type_key,
    score_frequency_state,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "docs/research/exectv2_sf_active_rate_overread_guard_protocol_2026-08-11.md"
DATE_STAMP = "20260811"
REPORT_DATE = "2026-08-11"

MODEL_SPECS = (
    ("gpt41mini", "GPT-4.1-mini"),
    ("gpt56luna", "GPT-5.6 Luna"),
    ("gpt56sol", "GPT-5.6 Sol"),
    ("deepseek_v4_flash", "DeepSeek V4 Flash"),
    ("qwen36_35b", "Qwen 3.6:35B"),
    ("gemma4_26b", "Gemma 4 26B"),
)

EXECT_JSONL = {
    "gpt41mini": REPO_ROOT
    / "experiments/exectv2_six_model_single_call_gpt41mini_dev140_20260715.jsonl",
    "gpt56luna": REPO_ROOT
    / "experiments/exectv2_six_model_single_call_gpt56luna_dev140_20260715.jsonl",
    "gpt56sol": REPO_ROOT
    / "experiments/exectv2_six_model_single_call_gpt56sol_dev140_20260715.jsonl",
    "deepseek_v4_flash": REPO_ROOT
    / "experiments/exectv2_deepseek_v4_flash_0731_update_dev140_20260731.jsonl",
    "qwen36_35b": REPO_ROOT
    / "experiments/exectv2_six_model_single_call_qwen36_35b_dev140_20260715.jsonl",
    "gemma4_26b": REPO_ROOT
    / "experiments/exectv2_six_model_single_call_gemma4_26b_dev140_20260715.jsonl",
}

_STATE_RE = re.compile(r"'(active-rate|seizure-free|unknown)'")

# --- Predeclared v1 evidence-classification pattern families -----------------
# Frozen before any of the 141 pooled extra active-rate cells' evidence text
# was inspected. Priority order: historical > hypothetical > descriptive >
# current (default).

_HISTORICAL_RE = re.compile(
    r"\b(previously|prior to|before (starting|commencing)|used to (have|get)|"
    r"history of|historically|in the past|at (diagnosis|presentation|onset)|"
    r"initial(ly)?|childhood|years? ago|months? ago|"
    r"last (year|clinic|letter|review)|old (letter|clinic letter|note)|"
    r"background history|past medical history)\b",
    re.IGNORECASE,
)

_HYPOTHETICAL_RE = re.compile(
    r"\b(if (seizures?|he|she|they) (increase|recur|return|worsen)|"
    r"should (seizures?|he|she|they)|in (the )?case of|as needed|"
    r"would (have|experience)|may (have|experience)|might (have|experience)|"
    r"risk of (seizures?|recurrence)|could (have|experience))\b",
    re.IGNORECASE,
)

_DESCRIPTIVE_RE = re.compile(
    r"\b(typically|usually|generally|tends? to (have|get)|"
    r"characteris(e|ation)d? by|pattern of|known to (have|get)|prone to)\b",
    re.IGNORECASE,
)


def classify_evidence(evidence: str, rationale: str) -> str:
    """Predeclared v1 classifier: historical / hypothetical / descriptive / current."""

    text = evidence.strip() or rationale.strip()
    if not text:
        return "current"
    if _HISTORICAL_RE.search(text):
        return "historical"
    if _HYPOTHETICAL_RE.search(text):
        return "hypothetical"
    if _DESCRIPTIVE_RE.search(text):
        return "descriptive"
    return "current"


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def _git_note() -> dict[str, Any]:
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT, text=True
        ).strip()
        dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=REPO_ROOT, text=True
            ).strip()
        )
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty_tree": None}
    return {"commit": commit, "dirty_tree": dirty}


def _sf_mentions(row: dict[str, Any], field: str) -> list[dict[str, Any]]:
    return [m for m in row.get(field, []) if str(m.get("entity", "")) == "SeizureFrequency"]


def _mention_key(mention: dict[str, Any]) -> tuple[Any, str]:
    annotation = annotation_from_mapping(mention)
    return (_frequency_type_key(annotation), _frequency_state(annotation.attributes))


def _dedup_keys(mentions: list[dict[str, Any]]) -> list[tuple[Any, str]]:
    return list(dict.fromkeys(_mention_key(m) for m in mentions))


def _apply_guard(mentions: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Return (candidate_sf_mentions, per-mention classification records)."""

    kept: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []
    for mention in mentions:
        annotation = annotation_from_mapping(mention)
        state = _frequency_state(annotation.attributes)
        if state != "active-rate":
            kept.append(mention)
            continue
        evidence = str(mention.get("evidence") or "")
        rationale = str(mention.get("rationale") or "")
        label = classify_evidence(evidence, rationale)
        record = {
            "text": mention.get("text"),
            "evidence": evidence,
            "classification": label,
            "dropped": label != "current",
        }
        records.append(record)
        if label == "current":
            kept.append(mention)
    return kept, records


def _mentions_with_field(letter_id: str, note_text: str, mentions: list[dict[str, Any]]) -> ExectLetter:
    return ExectLetter(
        letter_id=letter_id,
        note_text=note_text,
        annotations=tuple(annotation_from_mapping(m) for m in mentions),
    )


def _keys_for(row: dict[str, Any], field: str) -> list[str]:
    return headline_keys(row, "SeizureFrequency", field=field)


def _exact(gold: list[str], pred: list[str]) -> bool:
    return Counter(gold) == Counter(pred)


def _micro(pairs: list[tuple[list[str], list[str]]]) -> dict[str, float]:
    tp = fp = fn = 0
    for gold, pred in pairs:
        g, p = Counter(gold), Counter(pred)
        hit = sum((g & p).values())
        tp += hit
        fp += sum(p.values()) - hit
        fn += sum(g.values()) - hit
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "micro_f1": round(f1, 4),
        "tp": tp,
        "fp": fp,
        "fn": fn,
    }


def _clinical_f1(letters_pairs: list[tuple[ExectLetter, ExectLetter]]) -> float:
    gold_letters = [g for g, _p in letters_pairs]
    pred_letters = [p for _g, p in letters_pairs]
    return round(
        float(score_frequency_state(gold_letters, pred_letters).clinical_headline.f1), 4
    )


def build_artifact() -> dict[str, Any]:
    per_model: dict[str, Any] = {}
    pooled_pairs_baseline: list[tuple[list[str], list[str]]] = []
    pooled_pairs_guard: list[tuple[list[str], list[str]]] = []
    pooled_letters_baseline: list[tuple[ExectLetter, ExectLetter]] = []
    pooled_letters_guard: list[tuple[ExectLetter, ExectLetter]] = []
    pooled_extra_active_rate_keys = 0
    pooled_classification_counts: Counter[str] = Counter()
    pooled_rescue = pooled_harm = pooled_neutral = pooled_changed = 0
    pooled_cells: list[dict[str, Any]] = []
    pooled_missed_unknown_before = 0
    pooled_missed_unknown_after = 0
    pooled_missed_unknown_recovered = 0

    for slug, display in MODEL_SPECS:
        path = EXECT_JSONL[slug]
        rows = _read_jsonl(path)
        model_pairs_baseline: list[tuple[list[str], list[str]]] = []
        model_pairs_guard: list[tuple[list[str], list[str]]] = []
        model_letters_baseline: list[tuple[ExectLetter, ExectLetter]] = []
        model_letters_guard: list[tuple[ExectLetter, ExectLetter]] = []
        model_extra_active_rate_keys = 0
        model_classification_counts: Counter[str] = Counter()
        model_rescue = model_harm = model_neutral = model_changed = 0
        model_cells: list[dict[str, Any]] = []
        model_missed_unknown_before = 0
        model_missed_unknown_after = 0
        model_missed_unknown_recovered = 0

        for row in rows:
            letter_id = str(row["letter_id"])
            note_text = str(row.get("note_text") or "")
            gold_mentions = _sf_mentions(row, "gold_mentions")
            pred_mentions = _sf_mentions(row, "predicted_mentions")
            other_mentions = [
                m
                for m in row.get("predicted_mentions", [])
                if str(m.get("entity", "")) != "SeizureFrequency"
            ]

            gold_keys_full = _dedup_keys(gold_mentions)
            pred_keys_full = _dedup_keys(pred_mentions)
            gold_key_set = set(gold_keys_full)

            extra_active_rate_keys = [
                key for key in pred_keys_full if key not in gold_key_set and key[1] == "active-rate"
            ]
            model_extra_active_rate_keys += len(extra_active_rate_keys)
            pooled_extra_active_rate_keys += len(extra_active_rate_keys)

            candidate_sf, records = _apply_guard(pred_mentions)
            for record in records:
                model_classification_counts[record["classification"]] += 1
                pooled_classification_counts[record["classification"]] += 1

            baseline_row = {"gold_mentions": row["gold_mentions"], "predicted_mentions": row["predicted_mentions"]}
            candidate_row = {
                "gold_mentions": row["gold_mentions"],
                "predicted_mentions": other_mentions + candidate_sf,
            }

            gold_keys = _keys_for(baseline_row, "gold_mentions")
            baseline_keys = _keys_for(baseline_row, "predicted_mentions")
            guard_keys = _keys_for(candidate_row, "predicted_mentions")

            model_pairs_baseline.append((gold_keys, baseline_keys))
            model_pairs_guard.append((gold_keys, guard_keys))
            pooled_pairs_baseline.append((gold_keys, baseline_keys))
            pooled_pairs_guard.append((gold_keys, guard_keys))

            gold_letter = _mentions_with_field(letter_id, note_text, gold_mentions)
            baseline_letter = _mentions_with_field(letter_id, note_text, pred_mentions)
            guard_letter = _mentions_with_field(letter_id, note_text, candidate_sf)
            model_letters_baseline.append((gold_letter, baseline_letter))
            model_letters_guard.append((gold_letter, guard_letter))
            pooled_letters_baseline.append((gold_letter, baseline_letter))
            pooled_letters_guard.append((gold_letter, guard_letter))

            before_exact = _exact(gold_keys, baseline_keys)
            after_exact = _exact(gold_keys, guard_keys)
            if Counter(baseline_keys) != Counter(guard_keys):
                model_changed += 1
                pooled_changed += 1
                effect = "neutral_change"
                if after_exact and not before_exact:
                    model_rescue += 1
                    pooled_rescue += 1
                    effect = "rescue"
                elif before_exact and not after_exact:
                    model_harm += 1
                    pooled_harm += 1
                    effect = "harm"
                else:
                    model_neutral += 1
                    pooled_neutral += 1
                cell = {
                    "model_slug": slug,
                    "letter_id": letter_id,
                    "effect": effect,
                    "gold_keys": gold_keys,
                    "baseline_keys": baseline_keys,
                    "guard_keys": guard_keys,
                    "dropped_records": [r for r in records if r["dropped"]],
                }
                model_cells.append(cell)
                pooled_cells.append(cell)

            # Missed-unknown diagnostic arm.
            missing_unknown_keys = [
                key for key in gold_keys_full if key not in set(pred_keys_full) and key[1] == "unknown"
            ]
            if missing_unknown_keys:
                model_missed_unknown_before += len(missing_unknown_keys)
                pooled_missed_unknown_before += len(missing_unknown_keys)
                # Candidate: insert an unknown-state mention for each dropped
                # active-rate mention's type_key, if that recovers a missing
                # unknown key.
                inferred_type_keys = {
                    _frequency_type_key(annotation_from_mapping(m))
                    for m, rec in zip(
                        [mm for mm in pred_mentions if _frequency_state(annotation_from_mapping(mm).attributes) == "active-rate"],
                        records,
                        strict=False,
                    )
                    if rec["dropped"]
                }
                recovered = [
                    key for key in missing_unknown_keys if key[0] in inferred_type_keys
                ]
                model_missed_unknown_recovered += len(recovered)
                pooled_missed_unknown_recovered += len(recovered)
                still_missing = len(missing_unknown_keys) - len(recovered)
                model_missed_unknown_after += still_missing
                pooled_missed_unknown_after += still_missing

        baseline_micro = _micro(model_pairs_baseline)
        guard_micro = _micro(model_pairs_guard)
        baseline_exact = sum(_exact(g, p) for g, p in model_pairs_baseline)
        guard_exact = sum(_exact(g, p) for g, p in model_pairs_guard)
        n = len(model_pairs_baseline)
        per_model[slug] = {
            "display_name": display,
            "n_letters": n,
            "extra_active_rate_keys": model_extra_active_rate_keys,
            "active_rate_evidence_classification": dict(model_classification_counts),
            "cells_changed": model_changed,
            "rescue_cells": model_rescue,
            "harm_cells": model_harm,
            "neutral_changed_cells": model_neutral,
            "baseline_exact_rate": round(baseline_exact / n, 4) if n else None,
            "guard_exact_rate": round(guard_exact / n, 4) if n else None,
            "exactness_delta": round((guard_exact - baseline_exact) / n, 4) if n else None,
            "baseline_micro": baseline_micro,
            "guard_micro": guard_micro,
            "micro_f1_delta": round(guard_micro["micro_f1"] - baseline_micro["micro_f1"], 4),
            "baseline_clinical_f1": _clinical_f1(model_letters_baseline),
            "guard_clinical_f1": _clinical_f1(model_letters_guard),
            "missed_unknown_before": model_missed_unknown_before,
            "missed_unknown_after_inference": model_missed_unknown_after,
            "missed_unknown_recovered": model_missed_unknown_recovered,
        }

    pooled_baseline_micro = _micro(pooled_pairs_baseline)
    pooled_guard_micro = _micro(pooled_pairs_guard)
    pooled_baseline_exact = sum(_exact(g, p) for g, p in pooled_pairs_baseline)
    pooled_guard_exact = sum(_exact(g, p) for g, p in pooled_pairs_guard)
    pooled_n = len(pooled_pairs_baseline)

    sign_flip_models = [
        slug
        for slug, entry in per_model.items()
        if entry["micro_f1_delta"] < -0.005
    ]

    dev_selection = {
        "rule": (
            "pooled exactness delta >= 0, pooled micro-F1 delta >= +0.005, "
            "at most one model with micro-F1 sign flip below -0.005"
        ),
        "pooled_exactness_delta": round((pooled_guard_exact - pooled_baseline_exact) / pooled_n, 4)
        if pooled_n
        else None,
        "pooled_micro_f1_delta": round(
            pooled_guard_micro["micro_f1"] - pooled_baseline_micro["micro_f1"], 4
        ),
        "sign_flip_models": sign_flip_models,
        "n_sign_flip_models": len(sign_flip_models),
    }
    dev_selection["met"] = bool(
        dev_selection["pooled_exactness_delta"] is not None
        and dev_selection["pooled_exactness_delta"] >= 0
        and dev_selection["pooled_micro_f1_delta"] >= 0.005
        and dev_selection["n_sign_flip_models"] <= 1
    )

    return {
        "schema_version": "exectv2.sf_active_rate_overread_guard.v1",
        "date": REPORT_DATE,
        "protocol": PROTOCOL,
        "dataset": "ExECTv2",
        "split": "dev140",
        "surface": "llm_with_rules",
        "model_calls": 0,
        "replay": (
            "new deterministic evidence classification over already-persisted "
            "predicted_mentions/evidence text; zero model calls"
        ),
        "scorer": "SeizureFrequency clinical-headline unit-key exactness and micro P/R/F1",
        "classifier_version": "v1_predeclared",
        "pooled_extra_active_rate_keys": pooled_extra_active_rate_keys,
        "pooled_active_rate_evidence_classification": dict(pooled_classification_counts),
        "pooled_cells_changed": pooled_changed,
        "pooled_rescue_cells": pooled_rescue,
        "pooled_harm_cells": pooled_harm,
        "pooled_neutral_changed_cells": pooled_neutral,
        "pooled_baseline_exact_rate": round(pooled_baseline_exact / pooled_n, 4) if pooled_n else None,
        "pooled_guard_exact_rate": round(pooled_guard_exact / pooled_n, 4) if pooled_n else None,
        "pooled_baseline_micro": pooled_baseline_micro,
        "pooled_guard_micro": pooled_guard_micro,
        "pooled_baseline_clinical_f1": _clinical_f1(pooled_letters_baseline),
        "pooled_guard_clinical_f1": _clinical_f1(pooled_letters_guard),
        "pooled_missed_unknown_before": pooled_missed_unknown_before,
        "pooled_missed_unknown_after_inference": pooled_missed_unknown_after,
        "pooled_missed_unknown_recovered": pooled_missed_unknown_recovered,
        "models": per_model,
        "development_selection": dev_selection,
        "cells": pooled_cells,
        "claim_boundary": (
            "Development ExECTv2 no-call audit on dev140 across six retained "
            "structured sidecars. New deterministic classification over already-"
            "persisted evidence text, zero model calls. Not holdout evidence, not "
            "a production gate change, not clinical validation."
        ),
        "git": _git_note(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT
        / f"experiments/exectv2_sf_active_rate_overread_audit_dev140_{DATE_STAMP}.json",
    )
    args = parser.parse_args()
    artifact = build_artifact()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}")
    print(f"pooled_extra_active_rate_keys={artifact['pooled_extra_active_rate_keys']}")
    print(f"pooled_active_rate_evidence_classification={artifact['pooled_active_rate_evidence_classification']}")
    print(f"pooled_rescue={artifact['pooled_rescue_cells']} pooled_harm={artifact['pooled_harm_cells']}")
    print(f"pooled_exactness_delta={artifact['development_selection']['pooled_exactness_delta']}")
    print(f"pooled_micro_f1_delta={artifact['development_selection']['pooled_micro_f1_delta']}")
    print(f"development_selection_met={artifact['development_selection']['met']}")
    print(
        "missed_unknown before/after/recovered="
        f"{artifact['pooled_missed_unknown_before']}/"
        f"{artifact['pooled_missed_unknown_after_inference']}/"
        f"{artifact['pooled_missed_unknown_recovered']}"
    )


if __name__ == "__main__":
    main()
