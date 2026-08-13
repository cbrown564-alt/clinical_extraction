#!/usr/bin/env python3
"""Dev140 Phase-1 check for the dead subsumption-guard fix.

Predeclared in docs/research/
diagnosis_residual_additions_subsumption_guard_fix_protocol_2026-08-11.md.

`is_redundant_diagnosis_residual_addition` compares
`canonicalize_diagnosis_concept(text) == "generalised tonic clonic seizures"`,
but that canonicalizer always strips "generalised", so the comparison can
never be true and the guard is dead. This patches only the string literal
(no other logic touched) and replays dev140 to check the fix suppresses the
one flagged pattern's harm without losing its help.

No model calls. No production code is changed by this script.
"""

from __future__ import annotations

import copy
import importlib.util
import json
from collections import Counter
from pathlib import Path
from typing import Any
from unittest.mock import patch

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import load_letters_for_split
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic import (
    standard_dictionary as sd,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.conventions import (
    diagnosis as diagnosis_dictionary,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    canonicalize_diagnosis_concept,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    "docs/research/"
    "diagnosis_residual_additions_subsumption_guard_fix_protocol_2026-08-11.md"
)
OUT = (
    REPO_ROOT
    / "experiments"
    / "exectv2_diagnosis_subsumption_guard_fix_dev140_20260811.json"
)
_DECOMPOSITION = REPO_ROOT / "scripts" / "build_exectv2_family_lens_rule_decomposition.py"


def _load_decomposition_module() -> Any:
    spec = importlib.util.spec_from_file_location("family_lens_decomposition", _DECOMPOSITION)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {_DECOMPOSITION}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


decomposition = _load_decomposition_module()


def _fixed_is_redundant(
    text: str,
    *,
    evidence: str,
    selected_texts: Any,
    include_resolution_candidate: bool = False,
    model_preserving_policy_candidate: bool = False,
) -> bool:
    """Same as the shipped function, with the one dead comparison corrected."""

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


def _effect(*, gold: list[str], baseline: list[str], candidate: list[str]) -> str:
    baseline_exact = Counter(gold) == Counter(baseline)
    candidate_exact = Counter(gold) == Counter(candidate)
    if baseline_exact and not candidate_exact:
        return "help_lost"
    if not baseline_exact and candidate_exact:
        return "rescue"
    return "neutral_change"


def build_artifact() -> dict[str, Any]:
    cells: list[dict[str, Any]] = []
    replayable = 0
    unreplayable: Counter[str] = Counter()
    per_model_baseline_exact: Counter[str] = Counter()
    per_model_candidate_exact: Counter[str] = Counter()
    per_model_n: Counter[str] = Counter()
    per_model_baseline_micro: dict[str, list[tuple[list[str], list[str]]]] = {}

    letters = {letter.letter_id: letter for letter in load_letters_for_split("dev")}
    for slug, _display in decomposition.stage.hs.MODEL_SPECS:
        main_path = decomposition.stage.hs.EXECT_JSONL[slug]
        main_rows = {
            str(row["letter_id"]): row for row in decomposition.stage.hs._read_jsonl(main_path)
        }
        structured_path = main_path.with_name(main_path.name.replace(".jsonl", "_structured.jsonl"))
        per_model_baseline_micro.setdefault(slug, [])
        for structured_row in decomposition.stage.hs._read_jsonl(structured_path):
            letter_id = str(structured_row["letter_id"])
            letter = letters.get(letter_id)
            main_row = main_rows.get(letter_id)
            if letter is None or main_row is None:
                unreplayable["missing_letter_or_main_row"] += 1
                continue
            gold_mentions = list(main_row.get("gold_mentions") or [])

            baseline = decomposition.stage.replay_letter(
                copy.deepcopy(structured_row), letter, gold_mentions=gold_mentions
            )
            with patch.object(sd, "is_redundant_diagnosis_residual_addition", _fixed_is_redundant):
                candidate = decomposition.stage.replay_letter(
                    copy.deepcopy(structured_row), letter, gold_mentions=gold_mentions
                )
            if not baseline.get("replayable") or not candidate.get("replayable"):
                unreplayable["candidate_unreplayable"] += 1
                continue

            replayable += 1
            gold_keys = decomposition._gold_keys(gold_mentions, "Diagnosis")
            baseline_keys = decomposition._family_keys(baseline, "Diagnosis")
            candidate_keys = decomposition._family_keys(candidate, "Diagnosis")

            per_model_n[slug] += 1
            per_model_baseline_exact[slug] += int(Counter(gold_keys) == Counter(baseline_keys))
            per_model_candidate_exact[slug] += int(Counter(gold_keys) == Counter(candidate_keys))
            per_model_baseline_micro[slug].append((gold_keys, baseline_keys))

            if Counter(baseline_keys) == Counter(candidate_keys):
                continue
            effect = _effect(gold=gold_keys, baseline=baseline_keys, candidate=candidate_keys)
            cells.append(
                {
                    "model_slug": slug,
                    "letter_id": letter_id,
                    "effect": effect,
                    "gold_keys": gold_keys,
                    "baseline_keys": baseline_keys,
                    "candidate_keys": candidate_keys,
                }
            )

    def micro(pairs: list[tuple[list[str], list[str]]], field: int) -> dict[str, float]:
        tp = fp = fn = 0
        for gold, keys_pair in pairs:
            pred = keys_pair
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

    by_model: dict[str, Any] = {}
    for slug in per_model_n:
        n = per_model_n[slug]
        baseline_micro = micro(per_model_baseline_micro[slug], 1)
        by_model[slug] = {
            "n": n,
            "baseline_exact_rate": round(per_model_baseline_exact[slug] / n, 4) if n else 0.0,
            "candidate_exact_rate": round(per_model_candidate_exact[slug] / n, 4) if n else 0.0,
            "exactness_delta": round(
                (per_model_candidate_exact[slug] - per_model_baseline_exact[slug]) / n, 4
            )
            if n
            else 0.0,
            "baseline_micro": baseline_micro,
        }

    effects = Counter(cell["effect"] for cell in cells)
    return {
        "schema_version": "exectv2.diagnosis_subsumption_guard_fix_dev140.v1",
        "date": "2026-08-11",
        "protocol": PROTOCOL,
        "dataset": "ExECTv2",
        "split": "dev140",
        "row_policy": "permitted_development_cell_ledger",
        "surface": "llm_with_rules",
        "model_calls": 0,
        "replay": "ordered no-call replay of retained structured sidecars",
        "scorer": "clinical-headline Diagnosis unit-key exactness",
        "replayable_cells": replayable,
        "unreplayable": dict(unreplayable),
        "changed_cells": len(cells),
        "cell_effects": dict(effects),
        "by_model_exactness": by_model,
        "cells": cells,
        "claim_boundary": (
            "Development mechanism/bugfix check on permitted dev140 rows only. "
            "No holdout rows inspected."
        ),
    }


def main() -> None:
    artifact = build_artifact()
    OUT.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")
    print("cell_effects:", json.dumps(artifact["cell_effects"]))
    print("changed_cells:", artifact["changed_cells"])
    for slug, v in artifact["by_model_exactness"].items():
        print(
            f"  {slug}: n={v['n']} exact_delta={v['exactness_delta']:+.4f} "
            f"baseline_exact={v['baseline_exact_rate']:.4f} "
            f"candidate_exact={v['candidate_exact_rate']:.4f}"
        )
    for cell in artifact["cells"]:
        print(
            f"  CHANGED {cell['model_slug']} {cell['letter_id']} {cell['effect']} "
            f"baseline={cell['baseline_keys']} candidate={cell['candidate_keys']} "
            f"gold={cell['gold_keys']}"
        )


if __name__ == "__main__":
    main()
