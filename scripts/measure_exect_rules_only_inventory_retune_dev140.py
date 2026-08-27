#!/usr/bin/env python3
"""Measure the rules-only inventory retune on development letters only."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    extract_deterministic_all9,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.rules import (
    apply_rules_only_later_stages,
    run_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    CLINICAL_HEADLINE_FAMILIES,
    aggregate_scores,
    exact_clinical_inventory_scores,
)

OUT = (
    Path(__file__).resolve().parents[1]
    / "experiments/exect_rules_only_inventory_retune_20260827/summary.json"
)
FAMILIES = CLINICAL_HEADLINE_FAMILIES


def _to_exect(letter_id: str, mentions: tuple[PredictedMention, ...]) -> ExectLetter:
    return ExectLetter(
        letter_id=letter_id,
        note_text="",
        annotations=tuple(
            ExectAnnotation(
                entity=mention.entity,
                text=mention.text,
                attributes=dict(mention.attributes),
            )
            for mention in mentions
            if mention.entity in FAMILIES
        ),
    )


def _score(gold: list[ExectLetter], preds: list[ExectLetter]) -> dict[str, object]:
    by_family = exact_clinical_inventory_scores(gold, preds)
    return {"overall": aggregate_scores(by_family.values()), "by_family": by_family}


def main() -> None:
    letters = sorted(load_letters_for_split("dev"), key=lambda item: item.letter_id)
    if len(letters) != 140:
        raise RuntimeError(f"expected 140 development letters, found {len(letters)}")
    gold = [
        ExectLetter(
            letter_id=letter.letter_id,
            note_text=letter.note_text,
            annotations=tuple(
                annotation
                for annotation in letter.annotations
                if annotation.entity in FAMILIES
            ),
        )
        for letter in letters
    ]
    extract_preds = []
    extract_plus_later = []
    run_letter_preds = []
    rateless_later = []
    for letter in letters:
        extracted = extract_deterministic_all9(letter)
        extract_preds.append(_to_exect(letter.letter_id, extracted.mentions))
        later = apply_rules_only_later_stages(letter, extracted)
        extract_plus_later.append(_to_exect(letter.letter_id, later.mentions))
        run_letter_preds.append(
            _to_exect(letter.letter_id, run_letter(letter).comparison_projection.mentions)
        )
        rateless = extract_deterministic_all9(letter, keep_unassociated_sf_anchors=True)
        rateless_later.append(
            _to_exect(
                letter.letter_id,
                apply_rules_only_later_stages(letter, rateless).mentions,
            )
        )
    summary = {
        "schema_version": "exect.rules_only.inventory_retune.dev140.v1",
        "date": date.today().isoformat(),
        "protocol": (
            "docs/research/exectv2/exect_rules_only_inventory_retune_protocol_2026-08-27.md"
        ),
        "split": "dev140",
        "holdout_loaded": False,
        "model_calls": 0,
        "scorer": "clinical_inventory_unit_keys",
        "comparator_pre_retune_inventory_f1": 0.8824,
        "arms": {
            "extract_recall_first": _score(gold, extract_preds),
            "extract_then_encode_select": _score(gold, extract_plus_later),
            "run_letter": _score(gold, run_letter_preds),
            "rateless_sf_then_encode_select": _score(gold, rateless_later),
        },
        "claim_boundary": (
            "Development mechanism only. Cited test60 rules cell is unchanged."
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(OUT)
    for name, arm in summary["arms"].items():
        overall = arm["overall"]
        print(name, overall["f1"], "P", overall["precision"], "R", overall["recall"])


if __name__ == "__main__":
    main()
