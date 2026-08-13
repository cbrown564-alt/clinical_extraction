#!/usr/bin/env python3
"""Audit every dev140 cell changed by Diagnosis residual additions.

This is a no-call, development-only mechanism audit.  It deliberately records
only the matched evidence fragment, not full note text, so the resulting ledger
is readable while remaining sufficient to identify the source-pattern rule.
"""

from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import load_letters_for_split
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.conventions import (
    diagnosis as diagnosis_dictionary,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    canonicalize_diagnosis_concept,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = (
    "docs/research/"
    "diagnosis_residual_additions_mechanism_audit_protocol_2026-08-10.md"
)
OUT = (
    REPO_ROOT
    / "experiments"
    / "exectv2_diagnosis_residual_additions_mechanism_audit_20260810.json"
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


def _effect(*, gold: list[str], baseline: list[str], candidate: list[str]) -> str:
    baseline_exact = Counter(gold) == Counter(baseline)
    candidate_exact = Counter(gold) == Counter(candidate)
    if baseline_exact and not candidate_exact:
        return "help"
    if not baseline_exact and candidate_exact:
        return "harm"
    return "neutral_change"


def _added_items(baseline: list[str], candidate: list[str]) -> list[str]:
    remaining = Counter(candidate)
    items: list[str] = []
    for key in baseline:
        if remaining[key]:
            remaining[key] -= 1
        else:
            items.append(key)
    return items


def _pattern_matches(note_text: str, added_text: str) -> list[dict[str, str]]:
    emitted = {
        (canonicalize_diagnosis_concept(text), evidence)
        for text, evidence in diagnosis_dictionary.diagnosis_residual_additions(note_text)
    }
    matches: list[dict[str, str]] = []
    patterns = diagnosis_dictionary.RESIDUAL_SOURCE_CONCEPT_PATTERNS
    for index, (pattern, target) in enumerate(patterns):
        if canonicalize_diagnosis_concept(target) != added_text:
            continue
        match = pattern.search(note_text)
        emitted_item = (canonicalize_diagnosis_concept(target), match.group(0)) if match else None
        if match is not None and emitted_item in emitted:
            matches.append(
                {
                    "pattern_id": f"residual_source_concept_{index:02d}",
                    "target_text": target,
                    "evidence": match.group(0),
                }
            )
            break
    return matches


def _family_label(match: dict[str, str]) -> str:
    target = match["target_text"]
    evidence = match["evidence"].lower()
    if "diagnosis:" in evidence:
        return "diagnosis-heading phrase"
    if "seizure type" in evidence:
        return "seizure-type heading phrase"
    if "drug refractory" in evidence or "intractable" in evidence:
        return "severity or treatment-resistance phrase"
    if "generalised" in evidence or "generalized" in evidence:
        return "generalised-seizure phrase"
    if "focal" in evidence or "partial" in evidence or "temporal" in evidence:
        return "focal-seizure phrase"
    if target in {"epilepsy", "generalised epilepsy", "juvenile myoclonic epilepsy"}:
        return "generic epilepsy assertion"
    return "other source-specific phrase"


def build_artifact() -> dict[str, Any]:
    cells: list[dict[str, Any]] = []
    pattern_stats: dict[str, Counter[str]] = defaultdict(Counter)
    by_letter: dict[str, Counter[str]] = defaultdict(Counter)
    replayable = 0
    unreplayable: Counter[str] = Counter()

    letters = {letter.letter_id: letter for letter in load_letters_for_split("dev")}
    for slug, _display in decomposition.stage.hs.MODEL_SPECS:
        main_path = decomposition.stage.hs.EXECT_JSONL[slug]
        main_rows = {
            str(row["letter_id"]): row for row in decomposition.stage.hs._read_jsonl(main_path)
        }
        structured_path = main_path.with_name(main_path.name.replace(".jsonl", "_structured.jsonl"))
        for structured_row in decomposition.stage.hs._read_jsonl(structured_path):
            letter_id = str(structured_row["letter_id"])
            letter = letters.get(letter_id)
            main_row = main_rows.get(letter_id)
            if letter is None or main_row is None:
                unreplayable["missing_letter_or_main_row"] += 1
                continue
            gold_mentions = list(main_row.get("gold_mentions") or [])
            with decomposition.disabled_rule(None):
                baseline = decomposition.stage.replay_letter(
                    copy.deepcopy(structured_row), letter, gold_mentions=gold_mentions
                )
            if not baseline.get("replayable"):
                unreplayable[str(baseline.get("reason", "unknown"))] += 1
                continue
            with decomposition.disabled_rule("diagnosis_residual_additions"):
                candidate = decomposition.stage.replay_letter(
                    copy.deepcopy(structured_row), letter, gold_mentions=gold_mentions
                )
            if not candidate.get("replayable"):
                unreplayable["candidate_unreplayable"] += 1
                continue
            replayable += 1
            gold_keys = decomposition._gold_keys(gold_mentions, "Diagnosis")
            baseline_keys = decomposition._family_keys(baseline, "Diagnosis")
            candidate_keys = decomposition._family_keys(candidate, "Diagnosis")
            if Counter(baseline_keys) == Counter(candidate_keys):
                continue
            added_keys = _added_items(baseline_keys, candidate_keys)
            effect = _effect(gold=gold_keys, baseline=baseline_keys, candidate=candidate_keys)
            additions: list[dict[str, Any]] = []
            for key in added_keys:
                text = key.removeprefix("('Diagnosis', '").removesuffix("')")
                matches = _pattern_matches(letter.note_text, text)
                if not matches:
                    matches = [{"pattern_id": "unresolved", "target_text": text, "evidence": ""}]
                for match in matches:
                    family = _family_label(match)
                    pattern_stats[match["pattern_id"]].update(
                        cells=1,
                        **{effect: 1},
                        gold_supported=int(key in gold_keys),
                    )
                    additions.append(
                        {**match, "pattern_family": family, "gold_supported": key in gold_keys}
                    )
            by_letter[letter_id].update(cells=1, **{effect: 1})
            cells.append(
                {
                    "model_slug": slug,
                    "letter_id": letter_id,
                    "effect": effect,
                    "gold_keys": gold_keys,
                    "with_additions_keys": baseline_keys,
                    "without_additions_keys": candidate_keys,
                    "added_keys": added_keys,
                    "additions": additions,
                }
            )

    effects = Counter(cell["effect"] for cell in cells)
    return {
        "schema_version": "exectv2.diagnosis_residual_additions_mechanism_audit.v1",
        "date": "2026-08-10",
        "protocol": PROTOCOL,
        "dataset": "ExECTv2",
        "split": "dev140",
        "row_policy": "permitted_development_cell_ledger",
        "surface": "llm_with_rules",
        "model_calls": 0,
        "replay": "ordered no-call replay of retained structured sidecars",
        "scorer": "clinical-headline Diagnosis unit-key exactness and micro-F1",
        "prompt_side_provider": "unchanged",
        "replayable_cells": replayable,
        "unreplayable": dict(unreplayable),
        "changed_cells": len(cells),
        "cell_effects": dict(effects),
        "pattern_summary": {
            key: dict(value) for key, value in sorted(pattern_stats.items())
        },
        "letter_effects": {key: dict(value) for key, value in sorted(by_letter.items())},
        "cells": cells,
        "claim_boundary": (
            "Development mechanism audit on permitted dev140 rows only. Pattern-level "
            "counts allocate a multi-addition cell to each matching addition and therefore "
            "do not establish individual causal credit. No holdout rows were inspected."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    artifact = build_artifact()
    args.out.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.out}")
    print(json.dumps(artifact["cell_effects"], sort_keys=True))


if __name__ == "__main__":
    main()
