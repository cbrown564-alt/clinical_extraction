#!/usr/bin/env python3
"""Measure the gated SF rewrite candidate against the three-stage baseline on dev140.

Protocol: docs/research/exectv2/exect_rules_only_sf_gated_rewrite_protocol_2026-08-27.md
Candidate: docs/research/exectv2/exect_rules_only_sf_gated_rewrite_candidate_2026-08-27.md
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.recognise_ledger import (
    SF_NAMED_TYPE,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.rules import (
    ACCEPTED_THREE_STAGE_CONFIG,
    ThreeStageConfig,
    run_letter_three_stage,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    CLINICAL_HEADLINE_FAMILIES,
    aggregate_scores,
    exact_clinical_inventory_scores,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match import (
    clinical_inventory_unit_keys,
)

OUT = (
    Path(__file__).resolve().parents[1]
    / "experiments/exect_rules_only_sf_gated_rewrite_20260827/summary.json"
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


@dataclass(frozen=True)
class PairScore:
    fn: int
    fp: int

    @property
    def exact(self) -> bool:
        return self.fn == 0 and self.fp == 0


def pair_scores(gold: ExectLetter, pred: ExectLetter, note_text: str) -> dict[str, PairScore]:
    scores: dict[str, PairScore] = {}
    for family in FAMILIES:
        gold_keys = Counter(
            clinical_inventory_unit_keys(
                family,
                [a for a in gold.annotations if a.entity == family],
                note_text,
            )
        )
        pred_keys = Counter(
            clinical_inventory_unit_keys(
                family,
                [a for a in pred.annotations if a.entity == family],
                note_text,
            )
        )
        scores[family] = PairScore(
            fn=sum((gold_keys - pred_keys).values()),
            fp=sum((pred_keys - gold_keys).values()),
        )
    return scores


def compare_pairs(
    comparator: dict[str, dict[str, PairScore]],
    arm: dict[str, dict[str, PairScore]],
) -> dict[str, object]:
    regressions: list[str] = []
    improved: list[str] = []
    worsened: list[str] = []
    family_error_delta: dict[str, int] = {family: 0 for family in FAMILIES}
    for letter_id, families in arm.items():
        for family, score in families.items():
            base = comparator[letter_id][family]
            if base.exact and not score.exact:
                regressions.append(f"{letter_id}/{family}")
            delta = (score.fn + score.fp) - (base.fn + base.fp)
            if delta:
                family_error_delta[family] += delta
                target = improved if delta < 0 else worsened
                target.append(f"{letter_id}/{family}")
    return {
        "comparator_exact_regressions": sorted(regressions),
        "improved_pairs": sorted(improved),
        "worsened_pairs": sorted(worsened),
        "family_error_delta": family_error_delta,
    }


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

    arms: dict[str, ThreeStageConfig] = {
        "comparator_accepted_three_stage": ACCEPTED_THREE_STAGE_CONFIG,
        "candidate_sf_named_type_ledger": ThreeStageConfig(
            deferred_classes=frozenset({SF_NAMED_TYPE}),
            recognise=ACCEPTED_THREE_STAGE_CONFIG.recognise,
            select_rule_ids=ACCEPTED_THREE_STAGE_CONFIG.select_rule_ids,
        ),
    }

    arm_preds: dict[str, list[ExectLetter]] = {name: [] for name in arms}
    arm_pairs: dict[str, dict[str, dict[str, PairScore]]] = {name: {} for name in arms}

    for letter in letters:
        for name, config in arms.items():
            result = run_letter_three_stage(letter, config)
            pred = _to_exect(letter.letter_id, result.comparison_projection.mentions)
            arm_preds[name].append(pred)
            arm_pairs[name][letter.letter_id] = pair_scores(
                next(g for g in gold if g.letter_id == letter.letter_id),
                pred,
                letter.note_text,
            )

    comparator_pairs = arm_pairs["comparator_accepted_three_stage"]
    summary_arms: dict[str, dict[str, Any]] = {}

    for name in arms:
        by_family = exact_clinical_inventory_scores(gold, arm_preds[name])
        entry: dict[str, Any] = {
            "overall": aggregate_scores(by_family.values()),
            "by_family": by_family,
        }
        if name != "comparator_accepted_three_stage":
            entry["vs_comparator"] = compare_pairs(comparator_pairs, arm_pairs[name])
        summary_arms[name] = entry

    summary = {
        "schema_version": "exect.rules_only.sf_gated_rewrite.dev140.v1",
        "date": date.today().isoformat(),
        "protocol": (
            "docs/research/exectv2/"
            "exect_rules_only_sf_gated_rewrite_protocol_2026-08-27.md"
        ),
        "split": "dev140",
        "holdout_loaded": False,
        "model_calls": 0,
        "scorer": "clinical_inventory_unit_keys",
        "comparator": "ACCEPTED_THREE_STAGE_CONFIG (dev140 F1 0.9167)",
        "arms": summary_arms,
        "claim_boundary": "Development mechanism evidence only. Test60 is sealed and unchanged.",
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n")
    print(f"Summary written to {OUT}")
    for name, entry in summary_arms.items():
        overall = entry["overall"]
        line = (
            f"{name}: F1 {overall['f1']:.4f} "
            f"P {overall['precision']:.4f} R {overall['recall']:.4f}"
        )
        if name != "comparator_accepted_three_stage":
            versus = entry["vs_comparator"]
            line += (
                f" | regressions {len(versus['comparator_exact_regressions'])}"
                f" improved {len(versus['improved_pairs'])}"
                f" worsened {len(versus['worsened_pairs'])}"
            )
        print(line)


if __name__ == "__main__":
    main()
