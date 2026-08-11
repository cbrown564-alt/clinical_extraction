#!/usr/bin/env python3
"""Aggregate-only test59 study for `diagnosis_residual_additions`.

Predeclared in docs/research/
exectv2_diagnosis_residual_additions_compensation_removal_protocol_2026-08-11.md.

Two measurements, both no-call, aggregate-only:

1. Firing-rate transfer check (primary): does the rule's pattern table match
   any held-out note text at all, per model? A near-zero holdout firing rate
   relative to dev140's ~25.7% of cells (213/830) would independently confirm
   the rule is dev140-literal memorization regardless of the accuracy delta.
2. Removal-arm accuracy delta (secondary): standard exactness/F1 kill
   criterion against the current shipped rule, for the whole panel and
   per-model.

No letter text, letter ID, or prediction leaves this process's aggregate
counters; only counts and deltas are written to the output artifact.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.conventions import (
    diagnosis as diagnosis_dictionary,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    annotation_from_mapping,
    clinical_headline_scores,
    headline_keys,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    "docs/research/"
    "exectv2_diagnosis_residual_additions_compensation_removal_protocol_2026-08-11.md"
)
OUT = (
    REPO_ROOT
    / "experiments"
    / "exectv2_diagnosis_residual_additions_test59_20260811.json"
)

HOLDOUT_ROOTS: dict[str, Path] = {
    "gpt41mini": REPO_ROOT / "scratch/holdout/exectv2_test60/gpt41mini",
    "gpt56luna": REPO_ROOT / "scratch/holdout/exectv2_test60/gpt56luna",
    "gpt56sol": REPO_ROOT / "scratch/holdout/exectv2_test60_sol_credit_v2/gpt56sol",
    "deepseek_v4_flash": REPO_ROOT / "scratch/holdout/exectv2_test60/deepseek_v4_flash",
    "qwen36_35b": REPO_ROOT / "scratch/local_queue/qwen36_35b_exect/test60/qwen36_35b",
    "gemma4_26b": REPO_ROOT / "scratch/local_queue/gemma4_26b_exect/test60/gemma4_26b",
}

def _dev140_reference_firing_rate() -> float:
    """Raw per-letter firing rate on dev140, computed the same way as test59.

    Not the 213/830 "changed cells" figure from the 2026-08-10 decomposition
    — that counts only matches that survived de-duplication and changed the
    assembled Diagnosis set, which undercounts raw pattern firing. This is
    the apples-to-apples comparator for the test59 firing-rate check below.
    """

    letters = list(load_letters_for_split("dev"))
    fires = sum(
        1
        for letter in letters
        if diagnosis_dictionary.diagnosis_residual_additions(letter.note_text)
    )
    return fires / len(letters) if letters else 0.0

_DEV_PATH = REPO_ROOT / "scripts/build_exectv2_family_lens_rule_decomposition.py"
_SPEC = importlib.util.spec_from_file_location("exect_family_decomposition", _DEV_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"cannot import replay helpers from {_DEV_PATH}")
decomposition = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(decomposition)


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


def _clinical_f1(cells: list[dict[str, Any]], field: str) -> float:
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
    return round(float(clinical_headline_scores(gold, predicted)["Diagnosis"]["f1"]), 4)


def _family_summary(cells: list[dict[str, Any]]) -> dict[str, Any]:
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
    base_f1 = _clinical_f1(cells, "baseline_mentions")
    candidate_f1 = _clinical_f1(cells, "candidate_mentions")
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

    cells: list[dict[str, Any]] = []
    unreplayable = 0
    fidelity_matched = 0
    fidelity_checked = 0

    firing_cells_by_model: dict[str, int] = defaultdict(int)
    total_cells_by_model: dict[str, int] = defaultdict(int)
    firing_letters: set[str] = set()
    total_letters: set[str] = set()

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

            total_cells_by_model[slug] += 1
            total_letters.add(letter_id)
            fires = bool(diagnosis_dictionary.diagnosis_residual_additions(letter.note_text))
            if fires:
                firing_cells_by_model[slug] += 1
                firing_letters.add(letter_id)

            baseline = decomposition.stage.replay_letter(
                structured_row, letter, gold_mentions=gold_mentions
            )
            with decomposition.disabled_rule("diagnosis_residual_additions"):
                candidate = decomposition.stage.replay_letter(
                    structured_row, letter, gold_mentions=gold_mentions
                )
            if not baseline.get("replayable") or not candidate.get("replayable"):
                unreplayable += 1
                continue

            baseline_keys = decomposition._family_keys(baseline, "Diagnosis")
            candidate_keys = decomposition._family_keys(candidate, "Diagnosis")
            retained_keys = headline_keys(sealed, "Diagnosis", field="predicted_mentions")
            fidelity_checked += 1
            fidelity_matched += int(Counter(baseline_keys) == Counter(retained_keys))

            cells.append(
                {
                    "ordinal": f"{slug}:{ordinal}",
                    "model_slug": slug,
                    "gold_mentions": gold_mentions,
                    "gold_keys": decomposition._gold_keys(gold_mentions, "Diagnosis"),
                    "baseline_keys": baseline_keys,
                    "candidate_keys": candidate_keys,
                    "baseline_mentions": decomposition._family_mentions(baseline, "Diagnosis"),
                    "candidate_mentions": decomposition._family_mentions(candidate, "Diagnosis"),
                }
            )

    overall = _family_summary(cells)
    by_model = {
        slug: _family_summary([c for c in cells if c["model_slug"] == slug])
        for slug in HOLDOUT_ROOTS
    }

    total_cells = sum(total_cells_by_model.values())
    total_firing = sum(firing_cells_by_model.values())
    firing_rate_overall = total_firing / total_cells if total_cells else 0.0
    per_model_firing_rate = {
        slug: round(firing_cells_by_model[slug] / total_cells_by_model[slug], 4)
        if total_cells_by_model[slug]
        else 0.0
        for slug in HOLDOUT_ROOTS
    }
    letter_firing_rate = len(firing_letters) / len(total_letters) if total_letters else 0.0
    dev140_reference_rate = _dev140_reference_firing_rate()

    transfer_verdict = (
        "MEMORIZATION_CONFIRMED"
        if letter_firing_rate < 0.5 * dev140_reference_rate
        else "TRANSFERS"
    )

    return {
        "schema_version": "exectv2.diagnosis_residual_additions_test59.v1",
        "date": "2026-08-11",
        "protocol": PROTOCOL,
        "dataset": "ExECTv2",
        "split": "test59",
        "row_policy": "aggregate_only",
        "surface": "llm_with_rules",
        "model_calls": 0,
        "replay": "ordered no-call replay of retained sealed structured sidecars",
        "candidate_rule": "diagnosis_residual_additions",
        "n_unreplayable": unreplayable,
        "fidelity": {"matched": fidelity_matched, "checked": fidelity_checked},
        "firing_rate": {
            "dev140_reference_letter_rate": round(dev140_reference_rate, 4),
            "dev140_reference_rate_definition": (
                "raw per-letter firing rate (any pattern matches note text), "
                "NOT the 213/830 post-dedup 'changed cells' figure from the "
                "2026-08-10 decomposition"
            ),
            "test59_cell_rate_overall": round(firing_rate_overall, 4),
            "test59_letter_rate_overall": round(letter_firing_rate, 4),
            "test59_cell_rate_by_model": per_model_firing_rate,
            "n_firing_cells": total_firing,
            "n_total_cells": total_cells,
            "n_firing_letters": len(firing_letters),
            "n_total_letters": len(total_letters),
            "transfer_verdict": transfer_verdict,
        },
        "overall": overall,
        "by_model": by_model,
        "kill_criterion": {
            "confirm_if": (
                "exactness delta >= 0 and micro-F1 delta >= -0.005 for the whole panel "
                "and no individual model regresses beyond that tolerance"
            ),
            "verdict": "CONFIRMED"
            if overall["confirmed"] and all(v["confirmed"] for v in by_model.values())
            else "KILLED",
        },
        "claim_boundary": (
            "Single predeclared aggregate-only test59 study of one flagged Diagnosis "
            "rule from the model-compensating rule audit. No holdout row inspection, "
            "no tuning, not clinical validation, not the published ExECT benchmark."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=OUT)
    args = parser.parse_args()
    artifact = run()
    args.artifact.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")

    fr = artifact["firing_rate"]
    print(
        f"firing_rate: dev140_ref_letters={fr['dev140_reference_letter_rate']:.4f} "
        f"test59_letters={fr['test59_letter_rate_overall']:.4f} "
        f"({fr['n_firing_letters']}/{fr['n_total_letters']} letters, "
        f"{fr['n_firing_cells']}/{fr['n_total_cells']} cells) "
        f"verdict={fr['transfer_verdict']}"
    )
    print("per-model firing rate:", json.dumps(fr["test59_cell_rate_by_model"]))
    overall = artifact["overall"]
    print(
        f"overall: cells={overall['n_cells']} changed={overall['cells_changed']} "
        f"rescue={overall['rescue_cells']} harm={overall['harm_cells']} "
        f"exact_delta={overall['exactness_delta']:+.4f} "
        f"micro_f1_delta={overall['micro_f1_delta']:+.4f}"
    )
    for slug, payload in artifact["by_model"].items():
        print(
            f"  {slug}: changed={payload['cells_changed']} "
            f"exact_delta={payload['exactness_delta']:+.4f} "
            f"micro_f1_delta={payload['micro_f1_delta']:+.4f} "
            f"confirmed={payload['confirmed']}"
        )
    print(f"VERDICT: {artifact['kill_criterion']['verdict']}")
    print(f"wrote {args.artifact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
