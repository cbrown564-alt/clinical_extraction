#!/usr/bin/env python3
"""Measure find/encode/select stops of the promoted rules program on dev140.

Protocol: docs/research/exectv2/exect_rules_only_stage_rungs_protocol_2026-08-27.md
Pure instrumentation of the frozen ACCEPTED_THREE_STAGE_CONFIG; the test
split is never loaded.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.rules import (
    ACCEPTED_THREE_STAGE_CONFIG,
    run_letter,
    three_stage_stop_mentions,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    CLINICAL_HEADLINE_FAMILIES,
    aggregate_scores,
    exact_clinical_inventory_scores,
)

OUT = (
    Path(__file__).resolve().parents[1]
    / "experiments/exect_rules_only_stage_rungs_20260827/dev140_summary.json"
)
FAMILIES = CLINICAL_HEADLINE_FAMILIES
STOPS = ("find", "encode", "select")
EXPECTED_SELECT_F1 = 0.9167


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

    stop_preds: dict[str, list[ExectLetter]] = {stop: [] for stop in STOPS}
    for letter in letters:
        stops = three_stage_stop_mentions(letter, ACCEPTED_THREE_STAGE_CONFIG)
        if stops.select != run_letter(letter).comparison_projection.mentions:
            raise RuntimeError(
                f"select stop diverges from run_letter on {letter.letter_id}"
            )
        find_non_diagnosis = tuple(
            m for m in stops.find if m.entity != DIAGNOSIS.name
        )
        encode_non_diagnosis = tuple(
            m for m in stops.encode if m.entity != DIAGNOSIS.name
        )
        if find_non_diagnosis != encode_non_diagnosis:
            raise RuntimeError(
                f"encode stop changed a non-Diagnosis family on {letter.letter_id}"
            )
        stop_preds["find"].append(_to_exect(letter.letter_id, stops.find))
        stop_preds["encode"].append(_to_exect(letter.letter_id, stops.encode))
        stop_preds["select"].append(_to_exect(letter.letter_id, stops.select))

    stage_rungs: dict[str, object] = {}
    for stop in STOPS:
        by_family = exact_clinical_inventory_scores(gold, stop_preds[stop])
        stage_rungs[stop] = {
            "overall": aggregate_scores(by_family.values()),
            "by_family": by_family,
        }

    select_f1 = stage_rungs["select"]["overall"]["f1"]
    if round(float(select_f1), 4) != EXPECTED_SELECT_F1:
        raise RuntimeError(
            f"select stop F1 {select_f1} does not reproduce promoted {EXPECTED_SELECT_F1}"
        )

    summary = {
        "schema_version": "exect.rules_only.stage_rungs.dev140.v1",
        "date": date.today().isoformat(),
        "protocol": (
            "docs/research/exectv2/exect_rules_only_stage_rungs_protocol_2026-08-27.md"
        ),
        "split": "dev140",
        "holdout_loaded": False,
        "model_calls": 0,
        "scorer": "clinical_inventory_unit_keys",
        "program": "run_letter_three_stage(ACCEPTED_THREE_STAGE_CONFIG)",
        "gates": {
            "select_stop_mention_identical_to_run_letter": True,
            "encode_stop_non_diagnosis_identical_to_find": True,
            "select_stop_reproduces_promoted_f1": EXPECTED_SELECT_F1,
        },
        "stage_rungs": stage_rungs,
        "claim_boundary": (
            "Stage-stop instrumentation of the frozen promoted rules program. "
            "Development evidence only; cited select-stop rows are unchanged."
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(OUT)
    for stop in STOPS:
        overall = stage_rungs[stop]["overall"]
        print(
            f"{stop}: F1 {overall['f1']:.4f} "
            f"P {overall['precision']:.4f} R {overall['recall']:.4f}"
        )


if __name__ == "__main__":
    main()
