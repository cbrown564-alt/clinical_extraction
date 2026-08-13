#!/usr/bin/env python3
"""Aggregate-only test59 confirmation for the frozen family-lens dead-rule bundle."""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from collections.abc import Iterator
from contextlib import ExitStack, contextmanager
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    annotation_from_mapping,
    headline_keys,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    "docs/research/"
    "family_lens_rule_decomposition_test59_confirmation_protocol_2026-08-10.md"
)
OUT = REPO_ROOT / "experiments" / "exectv2_family_lens_rule_decomposition_test59_20260810.json"

HOLDOUT_ROOTS: dict[str, Path] = {
    "gpt41mini": REPO_ROOT / "scratch/holdout/exectv2_test60/gpt41mini",
    "gpt56luna": REPO_ROOT / "scratch/holdout/exectv2_test60/gpt56luna",
    "gpt56sol": REPO_ROOT / "scratch/holdout/exectv2_test60_sol_credit_v2/gpt56sol",
    "deepseek_v4_flash": REPO_ROOT / "scratch/holdout/exectv2_test60/deepseek_v4_flash",
    "qwen36_35b": REPO_ROOT / "scratch/local_queue/qwen36_35b_exect/test60/qwen36_35b",
    "gemma4_26b": REPO_ROOT / "scratch/local_queue/gemma4_26b_exect/test60/gemma4_26b",
}

CANDIDATE_RULES = (
    "diagnosis_heading_recovery",
    "diagnosis_attribute_repairs",
    "diagnosis_generic_epilepsy_companion",
    "investigation_attribute_repairs",
    "investigation_noise_drop",
    "investigation_residual_additions",
)
FAMILIES = ("Diagnosis", "Investigations")

_DEV_PATH = REPO_ROOT / "scripts/build_exectv2_family_lens_rule_decomposition.py"
_SPEC = importlib.util.spec_from_file_location("exect_family_decomposition", _DEV_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"cannot import replay helpers from {_DEV_PATH}")
decomposition = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(decomposition)


@contextmanager
def disabled_bundle() -> Iterator[None]:
    with ExitStack() as stack:
        for rule in CANDIDATE_RULES:
            stack.enter_context(decomposition.disabled_rule(rule))
        yield


def _micro(gold_by_cell: list[list[str]], pred_by_cell: list[list[str]]) -> dict[str, float]:
    tp = fp = fn = 0
    for gold, pred in zip(gold_by_cell, pred_by_cell, strict=True):
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
    }


def _exact(gold: list[str], predicted: list[str]) -> bool:
    return Counter(gold) == Counter(predicted)


def _clinical_f1(cells: list[dict[str, Any]], family: str, field: str) -> float:
    gold = [
        ExectLetter(
            letter_id=str(cell["ordinal"]),
            note_text="",
            annotations=tuple(annotation_from_mapping(m) for m in cell["gold_mentions"]),
        )
        for cell in cells
    ]
    predicted = [
        ExectLetter(
            letter_id=str(cell["ordinal"]),
            note_text="",
            annotations=tuple(annotation_from_mapping(m) for m in cell[field]),
        )
        for cell in cells
    ]
    from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
        clinical_headline_scores,
    )

    return round(float(clinical_headline_scores(gold, predicted)[family]["f1"]), 4)


def _family_summary(cells: list[dict[str, Any]], family: str) -> dict[str, Any]:
    base_exact = sum(_exact(c["gold_keys"], c["baseline_keys"]) for c in cells)
    candidate_exact = sum(_exact(c["gold_keys"], c["candidate_keys"]) for c in cells)
    changed = rescue = harm = 0
    for cell in cells:
        if Counter(cell["baseline_keys"]) == Counter(cell["candidate_keys"]):
            continue
        changed += 1
        base_ok = _exact(cell["gold_keys"], cell["baseline_keys"])
        candidate_ok = _exact(cell["gold_keys"], cell["candidate_keys"])
        rescue += int(candidate_ok and not base_ok)
        harm += int(base_ok and not candidate_ok)
    base_micro = _micro([c["gold_keys"] for c in cells], [c["baseline_keys"] for c in cells])
    candidate_micro = _micro([c["gold_keys"] for c in cells], [c["candidate_keys"] for c in cells])
    base_f1 = _clinical_f1(cells, family, "baseline_mentions")
    candidate_f1 = _clinical_f1(cells, family, "candidate_mentions")
    delta_exact = (candidate_exact - base_exact) / len(cells) if cells else 0.0
    delta_f1 = candidate_micro["micro_f1"] - base_micro["micro_f1"]
    return {
        "n_cells": len(cells),
        "cells_changed": changed,
        "rescue_cells": rescue,
        "harm_cells": harm,
        "baseline_exact_rate": round(base_exact / len(cells), 4) if cells else 0.0,
        "candidate_exact_rate": round(candidate_exact / len(cells), 4) if cells else 0.0,
        "exactness_delta": round(delta_exact, 4),
        "baseline_micro": base_micro,
        "candidate_micro": candidate_micro,
        "micro_f1_delta": round(delta_f1, 4),
        "baseline_clinical_f1": base_f1,
        "candidate_clinical_f1": candidate_f1,
        "clinical_f1_delta": round(candidate_f1 - base_f1, 4),
        "confirmed": delta_exact >= 0 and delta_f1 >= -0.005,
    }


def run() -> dict[str, Any]:
    missing = [slug for slug, root in HOLDOUT_ROOTS.items() if not root.is_dir()]
    if missing:
        raise FileNotFoundError(f"sealed holdout trees absent for: {missing}")
    letters = {letter.letter_id: letter for letter in load_letters_for_split("test")}
    cells_by_family: dict[str, list[dict[str, Any]]] = {family: [] for family in FAMILIES}
    fidelity: dict[str, int] = {family: 0 for family in FAMILIES}
    checked: dict[str, int] = {family: 0 for family in FAMILIES}
    unreplayable = 0

    for slug, root in HOLDOUT_ROOTS.items():
        structured_rows = decomposition.stage.hs._read_jsonl(root / f"{slug}_structured.jsonl")
        sealed_rows = {
            str(row["letter_id"]): row
            for row in decomposition.stage.hs._read_jsonl(root / f"{slug}_sealed_rows.jsonl")
        }
        for ordinal, structured_row in enumerate(structured_rows):
            letter_id = str(structured_row["letter_id"])
            letter = letters.get(letter_id)
            sealed = sealed_rows.get(letter_id)
            if letter is None or sealed is None:
                unreplayable += 1
                continue
            gold_mentions = list(sealed.get("gold_mentions") or [])
            baseline = decomposition.stage.replay_letter(
                structured_row, letter, gold_mentions=gold_mentions
            )
            with disabled_bundle():
                candidate = decomposition.stage.replay_letter(
                    structured_row, letter, gold_mentions=gold_mentions
                )
            if not baseline.get("replayable") or not candidate.get("replayable"):
                unreplayable += 1
                continue
            for family in FAMILIES:
                baseline_keys = decomposition._family_keys(baseline, family)
                candidate_keys = decomposition._family_keys(candidate, family)
                retained_keys = headline_keys(sealed, family, field="predicted_mentions")
                checked[family] += 1
                fidelity[family] += int(Counter(baseline_keys) == Counter(retained_keys))
                cells_by_family[family].append(
                    {
                        "ordinal": f"{slug}:{ordinal}",
                        "gold_mentions": gold_mentions,
                        "gold_keys": decomposition._gold_keys(gold_mentions, family),
                        "baseline_keys": baseline_keys,
                        "candidate_keys": candidate_keys,
                        "baseline_mentions": decomposition._family_mentions(baseline, family),
                        "candidate_mentions": decomposition._family_mentions(candidate, family),
                    }
                )

    by_family = {family: _family_summary(cells_by_family[family], family) for family in FAMILIES}
    overall_confirmed = all(payload["confirmed"] for payload in by_family.values())
    return {
        "schema_version": "exectv2.family_lens_rule_decomposition_test59.v1",
        "date": "2026-08-10",
        "protocol": PROTOCOL,
        "dataset": "ExECTv2",
        "split": "test59",
        "row_policy": "aggregate_only",
        "surface": "llm_with_rules",
        "model_calls": 0,
        "replay": "ordered no-call replay of retained sealed structured sidecars",
        "candidate_rules": list(CANDIDATE_RULES),
        "n_unreplayable": unreplayable,
        "fidelity": {
            family: {"matched": fidelity[family], "checked": checked[family]} for family in FAMILIES
        },
        "by_family": by_family,
        "kill_criterion": {
            "confirm_if": (
                "exactness delta >= 0 and micro-F1 delta >= -0.005 "
                "for every selected family"
            ),
            "verdict": "CONFIRMED" if overall_confirmed else "KILLED",
        },
        "claim_boundary": (
            "Single predeclared aggregate-only test59 confirmation of a dev140-selected "
            "assembly simplification. No holdout row inspection, no tuning, not clinical "
            "validation, and not the published ExECT benchmark."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=OUT)
    args = parser.parse_args()
    artifact = run()
    args.artifact.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(f"candidate_rules={len(CANDIDATE_RULES)}")
    for family, payload in artifact["by_family"].items():
        print(
            f"{family}: cells={payload['n_cells']} changed={payload['cells_changed']} "
            f"rescue={payload['rescue_cells']} harm={payload['harm_cells']} "
            f"exact_delta={payload['exactness_delta']:+.4f} "
            f"micro_f1_delta={payload['micro_f1_delta']:+.4f} "
            f"verdict={'CONFIRMED' if payload['confirmed'] else 'KILLED'}"
        )
    print(f"VERDICT: {artifact['kill_criterion']['verdict']}")
    print(f"wrote {args.artifact}")
    return 0 if artifact["kill_criterion"]["verdict"] == "CONFIRMED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
