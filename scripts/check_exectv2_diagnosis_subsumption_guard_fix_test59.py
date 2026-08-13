#!/usr/bin/env python3
"""Aggregate-only test59 informational check for the subsumption guard fix.

Predeclared Phase 1 (dev140) REFUTED this fix per the strict "zero help
lost" kill criterion -- see docs/research/
diagnosis_residual_additions_subsumption_guard_fix_2026-08-11.md.
This script is run for disclosure only, ahead of a user decision to land the
fix despite that result: it measures how the fix behaves on held-out notes
before shipping. It does not re-run or override the predeclared Phase 1
verdict.

No model calls. No production code changed by this script.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any
from unittest.mock import patch

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    standard_dictionary as sd,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.conventions import (
    diagnosis as diagnosis_dictionary,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    canonicalize_diagnosis_concept,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    annotation_from_mapping,
    clinical_headline_scores,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    "docs/research/"
    "diagnosis_residual_additions_subsumption_guard_fix_protocol_2026-08-11.md"
)
OUT = (
    REPO_ROOT
    / "experiments"
    / "exectv2_diagnosis_subsumption_guard_fix_test59_20260811.json"
)

HOLDOUT_ROOTS: dict[str, Path] = {
    "gpt41mini": REPO_ROOT / "scratch/holdout/exectv2_test60/gpt41mini",
    "gpt56luna": REPO_ROOT / "scratch/holdout/exectv2_test60/gpt56luna",
    "gpt56sol": REPO_ROOT / "scratch/holdout/exectv2_test60_sol_credit_v2/gpt56sol",
    "deepseek_v4_flash": REPO_ROOT / "scratch/holdout/exectv2_test60/deepseek_v4_flash",
    "qwen36_35b": REPO_ROOT / "scratch/local_queue/qwen36_35b_exect/test60/qwen36_35b",
    "gemma4_26b": REPO_ROOT / "scratch/local_queue/gemma4_26b_exect/test60/gemma4_26b",
}

_DEV_PATH = REPO_ROOT / "scripts/build_exectv2_family_lens_rule_decomposition.py"
_SPEC = importlib.util.spec_from_file_location("exect_family_decomposition", _DEV_PATH)
if _SPEC is None or _SPEC.loader is None:
    raise RuntimeError(f"cannot import replay helpers from {_DEV_PATH}")
decomposition = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(decomposition)


def _fixed_is_redundant(
    text: str,
    *,
    evidence: str,
    selected_texts: Any,
    include_resolution_candidate: bool = False,
    model_preserving_policy_candidate: bool = False,
) -> bool:
    concept = canonicalize_diagnosis_concept(text)
    if (
        concept == "tonic clonic seizures"
        and diagnosis_dictionary._SECONDARY_GENERALISED_EVIDENCE.search(evidence)
    ):
        return True
    selected = {canonicalize_diagnosis_concept(item) for item in selected_texts}
    if model_preserving_policy_candidate and diagnosis_dictionary._seizure_concept_is_subsumed(
        concept, selected
    ):
        return True
    if include_resolution_candidate and concept == "generalised epilepsy":
        return any(
            item != concept and item.endswith("generalised epilepsy") for item in selected
        )
    if concept == "focal":
        return concept in selected
    if concept == "generalised":
        return concept in selected
    if concept == "secondary":
        return concept in selected
    if concept == "focal seizures with altered awareness" and "dyscognitive seizures" in selected:
        return True
    return False


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
    return {"precision": round(precision, 4), "recall": round(recall, 4), "micro_f1": round(f1, 4)}


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
    }


def run() -> dict[str, Any]:
    missing = [slug for slug, root in HOLDOUT_ROOTS.items() if not root.is_dir()]
    if missing:
        raise FileNotFoundError(f"sealed holdout trees absent for: {missing}")
    letters = {letter.letter_id: letter for letter in load_letters_for_split("test")}

    cells: list[dict[str, Any]] = []
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
            with patch.object(sd, "is_redundant_diagnosis_residual_addition", _fixed_is_redundant):
                candidate = decomposition.stage.replay_letter(
                    structured_row, letter, gold_mentions=gold_mentions
                )
            if not baseline.get("replayable") or not candidate.get("replayable"):
                unreplayable += 1
                continue

            baseline_keys = decomposition._family_keys(baseline, "Diagnosis")
            candidate_keys = decomposition._family_keys(candidate, "Diagnosis")

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

    return {
        "schema_version": "exectv2.diagnosis_subsumption_guard_fix_test59.v1",
        "date": "2026-08-11",
        "protocol": PROTOCOL,
        "dataset": "ExECTv2",
        "split": "test59",
        "row_policy": "aggregate_only",
        "surface": "llm_with_rules",
        "model_calls": 0,
        "replay": "ordered no-call replay of retained sealed structured sidecars",
        "candidate_change": "is_redundant_diagnosis_residual_addition string-comparison fix",
        "n_unreplayable": unreplayable,
        "overall": overall,
        "by_model": by_model,
        "note": (
            "Phase 1 (dev140) REFUTED this fix per the predeclared zero-help-lost "
            "criterion. This run is disclosure-only ahead of a deliberate user "
            "decision to land it anyway; it is not a Phase 2 confirmation of a "
            "study that already failed Phase 1."
        ),
        "claim_boundary": (
            "Aggregate-only informational test59 replay. No holdout row inspection, "
            "not clinical validation, not the published ExECT benchmark."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=OUT)
    args = parser.parse_args()
    artifact = run()
    args.artifact.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    overall = artifact["overall"]
    print(
        f"overall: cells={overall['n_cells']} changed={overall['cells_changed']} "
        f"rescue={overall['rescue_cells']} harm={overall['harm_cells']} "
        f"exact_delta={overall['exactness_delta']:+.4f} "
        f"micro_f1_delta={overall['micro_f1_delta']:+.4f}"
    )
    for slug, payload in artifact["by_model"].items():
        print(
            f"  {slug}: changed={payload['cells_changed']} rescue={payload['rescue_cells']} "
            f"harm={payload['harm_cells']} exact_delta={payload['exactness_delta']:+.4f} "
            f"micro_f1_delta={payload['micro_f1_delta']:+.4f}"
        )
    print(f"wrote {args.artifact}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
