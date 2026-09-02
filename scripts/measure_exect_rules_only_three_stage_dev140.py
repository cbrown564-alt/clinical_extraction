#!/usr/bin/env python3
"""Measure the rules-only three-stage reconstruction on development letters only.

Protocol: docs/research/exectv2/exect_rules_only_three_stage_reconstruction_protocol_2026-08-27.md
Arms are development evidence; the test split is never loaded.
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
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
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.find_ledger import (
    DEFERRED_CANDIDATE_CLASSES,
    FindConfig,
    build_find_ledger,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.select_rules import (
    INVENTORY_WEAK_EPISODE_DROP,
    RULES_ONLY_SELECT_RULE_IDS,
    SF_GENERIC_DUPLICATE_DROP,
    SF_SEIZURE_FREE_POSITIVE_COUNT_DROP,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.rules import (
    ACCEPTED_THREE_STAGE_CONFIG,
    ThreeStageConfig,
    run_letter_retune_stack,
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
    / "experiments/exect_rules_only_three_stage_reconstruction_20260827/summary.json"
)
FAMILIES = CLINICAL_HEADLINE_FAMILIES

D1 = "d1_service_context_exclusion"
D2 = "d2_secondary_to_retention"
D3 = "d3_focal_onset_alias"
S1 = "s1_sf_generic_duplicate_drop"
S2 = "s2_sf_seizure_free_positive_count_drop"
W1 = "w1_inventory_weak_episode_drop"
CANDIDATE_COMPONENTS: tuple[str, ...] = (D1, D2, D3, S2, W1)
ISOLATED_COMPONENTS: tuple[str, ...] = (D1, D2, D3, S1, S2, W1)


def config_for(components: Iterable[str]) -> ThreeStageConfig:
    active = frozenset(components)
    find_cfg = FindConfig(
        diagnosis_service_context_exclusion=D1 in active,
        diagnosis_secondary_to_retention=D2 in active,
        diagnosis_focal_onset_alias=D3 in active,
    )
    select_ids = list(RULES_ONLY_SELECT_RULE_IDS)
    if S1 in active:
        select_ids.append(SF_GENERIC_DUPLICATE_DROP)
    if S2 in active:
        select_ids.append(SF_SEIZURE_FREE_POSITIVE_COUNT_DROP)
    if W1 in active:
        select_ids.append(INVENTORY_WEAK_EPISODE_DROP)
    return ThreeStageConfig(find=find_cfg, select_rule_ids=tuple(select_ids))


def build_arms() -> dict[str, ThreeStageConfig | None]:
    arms: dict[str, ThreeStageConfig | None] = {
        "comparator_run_letter": None,
        "default_three_stage": ThreeStageConfig(),
    }
    for component in ISOLATED_COMPONENTS:
        arms[f"isolated_{component}"] = config_for([component])
    arms["candidate_full"] = config_for(CANDIDATE_COMPONENTS)
    for component in CANDIDATE_COMPONENTS:
        rest = [c for c in CANDIDATE_COMPONENTS if c != component]
        arms[f"loo_without_{component}"] = config_for(rest)
    return arms


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


def ledger_coverage(letters: list[ExectLetter]) -> dict[str, dict[str, float]]:
    coverage: dict[str, dict[str, float]] = {}
    totals = {family: 0 for family in FAMILIES}
    direct_hits = {family: 0 for family in FAMILIES}
    full_hits = {family: 0 for family in FAMILIES}
    for letter in letters:
        ledger, _ = build_find_ledger(
            letter,
            enabled_deferred_classes=frozenset(DEFERRED_CANDIDATE_CLASSES),
        )
        direct_ann = [
            ExectAnnotation(entity=m.entity, text=m.text, attributes=dict(m.attributes))
            for m in ledger.direct_mentions()
        ]
        all_ann = direct_ann + [
            ExectAnnotation(
                entity=c.mention.entity,
                text=c.mention.text,
                attributes=dict(c.mention.attributes),
            )
            for c in ledger.deferred_candidates()
        ]
        for family in FAMILIES:
            gold_keys = set(
                clinical_inventory_unit_keys(
                    family,
                    [a for a in letter.annotations if a.entity == family],
                    letter.note_text,
                )
            )
            direct_keys = set(
                clinical_inventory_unit_keys(
                    family,
                    [a for a in direct_ann if a.entity == family],
                    letter.note_text,
                )
            )
            full_keys = set(
                clinical_inventory_unit_keys(
                    family,
                    [a for a in all_ann if a.entity == family],
                    letter.note_text,
                )
            )
            totals[family] += len(gold_keys)
            direct_hits[family] += len(gold_keys & direct_keys)
            full_hits[family] += len(gold_keys & full_keys)
    for family in FAMILIES:
        total = totals[family] or 1
        coverage[family] = {
            "gold_units": totals[family],
            "direct_recall": round(direct_hits[family] / total, 4),
            "ledger_recall": round(full_hits[family] / total, 4),
        }
    return coverage


def main() -> None:
    if config_for(CANDIDATE_COMPONENTS) != ACCEPTED_THREE_STAGE_CONFIG:
        raise RuntimeError(
            "candidate components drifted from ACCEPTED_THREE_STAGE_CONFIG"
        )
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
    arms = build_arms()
    arm_preds: dict[str, list[ExectLetter]] = {name: [] for name in arms}
    arm_pairs: dict[str, dict[str, dict[str, PairScore]]] = {name: {} for name in arms}
    for letter in letters:
        for name, config in arms.items():
            if config is None:
                result = run_letter_retune_stack(letter)
            else:
                result = run_letter_three_stage(letter, config)
            pred = _to_exect(letter.letter_id, result.comparison_projection.mentions)
            arm_preds[name].append(pred)
            arm_pairs[name][letter.letter_id] = pair_scores(
                next(g for g in gold if g.letter_id == letter.letter_id),
                pred,
                letter.note_text,
            )
    summary_arms: dict[str, object] = {}
    comparator_pairs = arm_pairs["comparator_run_letter"]
    for name in arms:
        by_family = exact_clinical_inventory_scores(gold, arm_preds[name])
        entry: dict[str, object] = {
            "overall": aggregate_scores(by_family.values()),
            "by_family": by_family,
        }
        if name != "comparator_run_letter":
            entry["vs_comparator"] = compare_pairs(comparator_pairs, arm_pairs[name])
        summary_arms[name] = entry
    summary = {
        "schema_version": "exect.rules_only.three_stage_reconstruction.dev140.v1",
        "date": date.today().isoformat(),
        "protocol": (
            "docs/research/exectv2/"
            "exect_rules_only_three_stage_reconstruction_protocol_2026-08-27.md"
        ),
        "split": "dev140",
        "holdout_loaded": False,
        "model_calls": 0,
        "scorer": "clinical_inventory_unit_keys",
        "comparator": "run_letter accepted 2026-08-27 retune stack",
        "candidate_components": CANDIDATE_COMPONENTS,
        "select_rule_order_candidate": [
            *RULES_ONLY_SELECT_RULE_IDS,
            SF_SEIZURE_FREE_POSITIVE_COUNT_DROP,
            INVENTORY_WEAK_EPISODE_DROP,
        ],
        "rejected_components": {
            S1: (
                "gold keeps generic+named duplicate units in 4 letters; "
                "stack scores higher without it"
            ),
        },
        "ledger_coverage_all_deferred_classes": ledger_coverage(letters),
        "arms": summary_arms,
        "claim_boundary": (
            "Development mechanism only. Cited test60 rules cell 0.7725 is unchanged."
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2, sort_keys=True, default=str) + "\n")
    print(OUT)
    for name, entry in summary_arms.items():
        overall = entry["overall"]
        line = (
            f"{name}: F1 {overall['f1']:.4f}"
            f" P {overall['precision']:.4f} R {overall['recall']:.4f}"
        )
        if name != "comparator_run_letter":
            versus = entry["vs_comparator"]
            line += (
                f" | regressions {len(versus['comparator_exact_regressions'])}"
                f" improved {len(versus['improved_pairs'])}"
                f" worsened {len(versus['worsened_pairs'])}"
            )
        print(line)


if __name__ == "__main__":
    main()
