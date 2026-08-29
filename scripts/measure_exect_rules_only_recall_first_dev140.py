#!/usr/bin/env python3
"""Measure recall-first restructure arms against the promoted rules program.

Protocol:
docs/research/exectv2/exect_rules_only_recall_first_restructure_protocol_2026-08-27.md

For each requested arm this script reports the find/encode/select
stage rungs on dev140 (overall and per family) plus the Gate A2 /
Gate B select-stop identity check against the frozen comparator
``run_letter``. The test split is never loaded.

Usage: python scripts/measure_exect_rules_only_recall_first_dev140.py ARM [ARM ...]
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from dataclasses import replace
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
    DIAGNOSIS_COMPONENT_TOKEN,
    DIAGNOSIS_EXPANSION_SURFACE,
    DIAGNOSIS_HEADING_DECOMPOSITION,
    DIAGNOSIS_HIERARCHY_ANCESTOR,
    DIAGNOSIS_NESTED_ANCESTOR,
    DIAGNOSIS_NESTED_SURFACE,
    DIAGNOSIS_NONDIAGNOSTIC_CONTEXT,
    DIAGNOSIS_UNRESTRICTED_SURFACE,
    INV_RESULT_VARIANT,
    RX_RECALL_EXPANSION,
    SF_HEADING_STATE,
    SF_NAMED_TYPE,
    SF_SEIZURE_FREE,
    SF_STATE_VARIANT,
    FindConfig,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.select_rules import (
    INVESTIGATION_RESULTLESS_DROP,
    RECALL_FIRST_KEEP_RULE_BY_CLASS,
    RECALL_FIRST_UNSUPPORTED_DROP,
    SF_RATELESS_ANCHOR_DROP,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.orchestration.rules import (
    ACCEPTED_THREE_STAGE_CONFIG,
    RECALL_FIRST_THREE_STAGE_CONFIG,
    TRANSFERRED_RECALL_FIRST_THREE_STAGE_CONFIG,
    ThreeStageConfig,
    run_letter,
    three_stage_stop_mentions,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    CLINICAL_HEADLINE_FAMILIES,
    aggregate_scores,
    exact_clinical_inventory_scores,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match import (
    clinical_inventory_unit_keys,
)

OUT_DIR = (
    Path(__file__).resolve().parents[1]
    / "experiments/exect_rules_only_recall_first_20260827"
)
PROTOCOL = (
    "docs/research/exectv2/"
    "exect_rules_only_recall_first_restructure_protocol_2026-08-27.md"
)
TRANSFERRED_PROTOCOL = (
    "docs/research/exectv2/"
    "exect_rules_only_recall_first_transferred_protocol_2026-08-27.md"
)
FAMILIES = CLINICAL_HEADLINE_FAMILIES
STOPS = ("find", "encode", "select")

_ACCEPTED_FIND = ACCEPTED_THREE_STAGE_CONFIG.find or FindConfig()

# Arm registry. Every arm is a full ThreeStageConfig; add arms as the
# restructure progresses. "accepted" is the frozen comparator re-run
# through the stop reader (identity expected on all letters).
ARMS: dict[str, ThreeStageConfig] = {
    "accepted": ACCEPTED_THREE_STAGE_CONFIG,
    # Gate A2 relocation arm: SF rate-gate moves from extraction into
    # Select (emit rate-less anchors, drop them with the paired rule).
    "sf_rateless_relocation": ThreeStageConfig(
        find=replace(_ACCEPTED_FIND, sf_keep_unassociated_anchors=True),
        select_rule_ids=(
            *ACCEPTED_THREE_STAGE_CONFIG.select_rule_ids,
            SF_RATELESS_ANCHOR_DROP,
        ),
    ),
    # Gate A2: excluded-context Diagnosis occurrences as tagged direct.
    "dx_context_relocation": ThreeStageConfig(
        find=_ACCEPTED_FIND,
        select_rule_ids=(
            RECALL_FIRST_UNSUPPORTED_DROP,
            *ACCEPTED_THREE_STAGE_CONFIG.select_rule_ids,
        ),
        direct_classes=frozenset({DIAGNOSIS_NONDIAGNOSTIC_CONTEXT}),
    ),
    # Gate A2: nested ancestor Diagnosis concepts as tagged direct.
    "dx_ancestor_relocation": ThreeStageConfig(
        find=_ACCEPTED_FIND,
        select_rule_ids=(
            RECALL_FIRST_UNSUPPORTED_DROP,
            *ACCEPTED_THREE_STAGE_CONFIG.select_rule_ids,
        ),
        direct_classes=frozenset({DIAGNOSIS_NESTED_ANCESTOR}),
    ),
    # Gate A2: deferred SF classes as tagged direct.
    "sf_deferred_relocation": ThreeStageConfig(
        find=_ACCEPTED_FIND,
        select_rule_ids=(
            RECALL_FIRST_UNSUPPORTED_DROP,
            *ACCEPTED_THREE_STAGE_CONFIG.select_rule_ids,
        ),
        direct_classes=frozenset({SF_NAMED_TYPE, SF_HEADING_STATE, SF_SEIZURE_FREE}),
    ),
    # Gate A2: completed investigations without a bound result as direct.
    "inv_resultless_relocation": ThreeStageConfig(
        find=replace(_ACCEPTED_FIND, investigations_emit_resultless=True),
        select_rule_ids=(
            *ACCEPTED_THREE_STAGE_CONFIG.select_rule_ids,
            INVESTIGATION_RESULTLESS_DROP,
        ),
    ),
    # All Gate A2 relocations combined: the recall-first find stop.
    "recall_first_all_relocations": ThreeStageConfig(
        find=replace(
            _ACCEPTED_FIND,
            sf_keep_unassociated_anchors=True,
            investigations_emit_resultless=True,
        ),
        select_rule_ids=(
            RECALL_FIRST_UNSUPPORTED_DROP,
            *ACCEPTED_THREE_STAGE_CONFIG.select_rule_ids,
            SF_RATELESS_ANCHOR_DROP,
            INVESTIGATION_RESULTLESS_DROP,
        ),
        direct_classes=frozenset(
            {
                DIAGNOSIS_NONDIAGNOSTIC_CONTEXT,
                DIAGNOSIS_NESTED_ANCESTOR,
                SF_NAMED_TYPE,
                SF_HEADING_STATE,
                SF_SEIZURE_FREE,
            }
        ),
    ),
    # Phase B: Diagnosis recall levers (nested surfaces without hierarchy,
    # heading decomposition) on top of all relocations.
    "phase_b_dx_recall": ThreeStageConfig(
        find=replace(
            _ACCEPTED_FIND,
            sf_keep_unassociated_anchors=True,
            investigations_emit_resultless=True,
        ),
        select_rule_ids=(
            RECALL_FIRST_UNSUPPORTED_DROP,
            *ACCEPTED_THREE_STAGE_CONFIG.select_rule_ids,
            SF_RATELESS_ANCHOR_DROP,
            INVESTIGATION_RESULTLESS_DROP,
        ),
        direct_classes=frozenset(
            {
                DIAGNOSIS_NONDIAGNOSTIC_CONTEXT,
                DIAGNOSIS_NESTED_SURFACE,
                DIAGNOSIS_HEADING_DECOMPOSITION,
                DIAGNOSIS_UNRESTRICTED_SURFACE,
                DIAGNOSIS_EXPANSION_SURFACE,
                DIAGNOSIS_HIERARCHY_ANCESTOR,
                DIAGNOSIS_COMPONENT_TOKEN,
                SF_NAMED_TYPE,
                SF_HEADING_STATE,
                SF_SEIZURE_FREE,
                SF_STATE_VARIANT,
                RX_RECALL_EXPANSION,
                INV_RESULT_VARIANT,
            }
        ),
    ),
}

# Phase C isolated-keep arms: the Phase B ledger with exactly one class's
# keep rule enabled at Select. Arm name: keep_<class>.
_PHASE_B = ARMS["phase_b_dx_recall"]
for _cls in sorted(_PHASE_B.direct_classes):
    _keep_rule = RECALL_FIRST_KEEP_RULE_BY_CLASS[_cls]
    ARMS[f"keep_{_cls}"] = replace(
        _PHASE_B,
        select_rule_ids=(*_PHASE_B.select_rule_ids, _keep_rule),
    )

# Phase C combined arm: every keep rule enabled (updated as classes are
# accepted or rejected during Phase C gating).
ARMS["phase_c_all_keeps"] = replace(
    _PHASE_B,
    select_rule_ids=(
        *_PHASE_B.select_rule_ids,
        *sorted(
            RECALL_FIRST_KEEP_RULE_BY_CLASS[cls] for cls in _PHASE_B.direct_classes
        ),
    ),
)

# Phase C candidate: the accepted keep set. Isolated-positive classes only;
# FP-dominated classes stay find-only (their recall lives at the
# find stop, Select owns precision).
_PHASE_C_KEPT_CLASSES: tuple[str, ...] = (
    DIAGNOSIS_HEADING_DECOMPOSITION,
    SF_STATE_VARIANT,
    RX_RECALL_EXPANSION,
    INV_RESULT_VARIANT,
)
ARMS["phase_c_candidate"] = RECALL_FIRST_THREE_STAGE_CONFIG
if frozenset(RECALL_FIRST_THREE_STAGE_CONFIG.select_rule_ids) != frozenset(
    (
        *_PHASE_B.select_rule_ids,
        *(RECALL_FIRST_KEEP_RULE_BY_CLASS[cls] for cls in _PHASE_C_KEPT_CLASSES),
    )
) or RECALL_FIRST_THREE_STAGE_CONFIG.direct_classes != _PHASE_B.direct_classes:
    raise RuntimeError(
        "frozen RECALL_FIRST_THREE_STAGE_CONFIG drifted from the Phase C arm"
    )

# Post–Phase D transferred keep set: Rx + SF state variant only.
_TRANSFERRED_KEPT_CLASSES: tuple[str, ...] = (
    SF_STATE_VARIANT,
    RX_RECALL_EXPANSION,
)
ARMS["transferred_candidate"] = TRANSFERRED_RECALL_FIRST_THREE_STAGE_CONFIG
if (
    frozenset(TRANSFERRED_RECALL_FIRST_THREE_STAGE_CONFIG.select_rule_ids)
    != frozenset(
        (
            RECALL_FIRST_UNSUPPORTED_DROP,
            *ACCEPTED_THREE_STAGE_CONFIG.select_rule_ids,
            *(
                RECALL_FIRST_KEEP_RULE_BY_CLASS[cls]
                for cls in _TRANSFERRED_KEPT_CLASSES
            ),
        )
    )
    or TRANSFERRED_RECALL_FIRST_THREE_STAGE_CONFIG.direct_classes
    != frozenset(_TRANSFERRED_KEPT_CLASSES)
):
    raise RuntimeError(
        "TRANSFERRED_RECALL_FIRST_THREE_STAGE_CONFIG drifted from the "
        "transferred keep set"
    )
for _held_out in _TRANSFERRED_KEPT_CLASSES:
    ARMS[f"transferred_loo_{_held_out}"] = replace(
        TRANSFERRED_RECALL_FIRST_THREE_STAGE_CONFIG,
        select_rule_ids=tuple(
            rule_id
            for rule_id in TRANSFERRED_RECALL_FIRST_THREE_STAGE_CONFIG.select_rule_ids
            if rule_id != RECALL_FIRST_KEEP_RULE_BY_CLASS[_held_out]
        ),
    )

# Leave-one-out arms over the candidate keep set (Gate: removing any kept
# class must not improve the candidate score).
for _held_out in _PHASE_C_KEPT_CLASSES:
    ARMS[f"phase_c_loo_{_held_out}"] = replace(
        _PHASE_B,
        select_rule_ids=(
            *_PHASE_B.select_rule_ids,
            *(
                RECALL_FIRST_KEEP_RULE_BY_CLASS[cls]
                for cls in _PHASE_C_KEPT_CLASSES
                if cls != _held_out
            ),
        ),
    )


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


def _gold_view(letter: ExectLetter) -> ExectLetter:
    return ExectLetter(
        letter_id=letter.letter_id,
        note_text=letter.note_text,
        annotations=tuple(
            annotation
            for annotation in letter.annotations
            if annotation.entity in FAMILIES
        ),
    )


def _pair_errors(
    letter: ExectLetter,
    mentions: tuple[PredictedMention, ...],
) -> dict[str, tuple[int, int]]:
    """Per-family (fn, fp) unit errors for one letter's select-stop mentions."""

    pred = _to_exect(letter.letter_id, mentions)
    errors: dict[str, tuple[int, int]] = {}
    for family in FAMILIES:
        gold_keys = Counter(
            clinical_inventory_unit_keys(
                family,
                [a for a in letter.annotations if a.entity == family],
                letter.note_text,
            )
        )
        pred_keys = Counter(
            clinical_inventory_unit_keys(
                family,
                [a for a in pred.annotations if a.entity == family],
                letter.note_text,
            )
        )
        errors[family] = (
            sum((gold_keys - pred_keys).values()),
            sum((pred_keys - gold_keys).values()),
        )
    return errors


def measure_arm(
    arm: str,
    config: ThreeStageConfig,
    letters: list[ExectLetter],
    gold: list[ExectLetter],
    comparator_select: dict[str, tuple[PredictedMention, ...]],
    comparator_errors: dict[str, dict[str, tuple[int, int]]],
) -> dict[str, object]:
    stop_preds: dict[str, list[ExectLetter]] = {stop: [] for stop in STOPS}
    select_mismatch_ids: list[str] = []
    regressions: list[str] = []
    improved: list[str] = []
    worsened: list[str] = []
    for letter in letters:
        stops = three_stage_stop_mentions(letter, config)
        if stops.select != comparator_select[letter.letter_id]:
            select_mismatch_ids.append(letter.letter_id)
        stop_preds["find"].append(_to_exect(letter.letter_id, stops.find))
        stop_preds["encode"].append(_to_exect(letter.letter_id, stops.encode))
        stop_preds["select"].append(_to_exect(letter.letter_id, stops.select))
        arm_errors = _pair_errors(letter, stops.select)
        for family, (fn, fp) in arm_errors.items():
            base_fn, base_fp = comparator_errors[letter.letter_id][family]
            if base_fn + base_fp == 0 and fn + fp > 0:
                regressions.append(f"{letter.letter_id}/{family}")
            delta = (fn + fp) - (base_fn + base_fp)
            if delta:
                (improved if delta < 0 else worsened).append(
                    f"{letter.letter_id}/{family}"
                )

    stage_rungs: dict[str, object] = {}
    for stop in STOPS:
        by_family = exact_clinical_inventory_scores(gold, stop_preds[stop])
        stage_rungs[stop] = {
            "overall": aggregate_scores(by_family.values()),
            "by_family": by_family,
        }
    return {
        "arm": arm,
        "stage_rungs": stage_rungs,
        "select_stop_identity": {
            "identical_letters": len(letters) - len(select_mismatch_ids),
            "mismatched_letters": len(select_mismatch_ids),
            "mismatched_letter_ids": select_mismatch_ids,
        },
        "vs_comparator": {
            "comparator_exact_regressions": sorted(regressions),
            "improved_pairs": sorted(improved),
            "worsened_pairs": sorted(worsened),
        },
    }


def main() -> None:
    requested = sys.argv[1:] or ["accepted"]
    unknown = [arm for arm in requested if arm not in ARMS]
    if unknown:
        raise SystemExit(f"unknown arm(s): {unknown}; known: {sorted(ARMS)}")

    letters = sorted(load_letters_for_split("dev"), key=lambda item: item.letter_id)
    if len(letters) != 140:
        raise RuntimeError(f"expected 140 development letters, found {len(letters)}")
    gold = [_gold_view(letter) for letter in letters]
    comparator_select = {
        letter.letter_id: run_letter(letter).comparison_projection.mentions
        for letter in letters
    }
    comparator_errors = {
        letter.letter_id: _pair_errors(letter, comparator_select[letter.letter_id])
        for letter in letters
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for arm in requested:
        result = measure_arm(
            arm, ARMS[arm], letters, gold, comparator_select, comparator_errors
        )
        payload = {
            "schema_version": "exect.rules_only.recall_first.dev140.v1",
            "date": date.today().isoformat(),
            "protocol": (
                TRANSFERRED_PROTOCOL if arm.startswith("transferred_") else PROTOCOL
            ),
            "split": "dev140",
            "holdout_loaded": False,
            "model_calls": 0,
            "scorer": "clinical_inventory_unit_keys",
            "comparator": "run_letter (ACCEPTED_THREE_STAGE_CONFIG)",
            **result,
        }
        out_path = OUT_DIR / f"{arm}.json"
        out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        rungs = result["stage_rungs"]
        identity = result["select_stop_identity"]
        versus = result["vs_comparator"]
        print(
            f"== {arm} (select identity: {identity['identical_letters']}/140; "
            f"regressions {len(versus['comparator_exact_regressions'])} "  # type: ignore[index]
            f"improved {len(versus['improved_pairs'])} "  # type: ignore[index]
            f"worsened {len(versus['worsened_pairs'])})"  # type: ignore[index]
        )
        for stop in STOPS:
            overall = rungs[stop]["overall"]  # type: ignore[index]
            print(
                f"  {stop:9s} F1 {overall['f1']:.4f} "
                f"P {overall['precision']:.4f} R {overall['recall']:.4f}"
            )
            for family in sorted(FAMILIES):
                fam = rungs[stop]["by_family"][family]  # type: ignore[index]
                print(
                    f"    {family:16s} F1 {fam['f1']:.4f} "
                    f"P {fam['precision']:.4f} R {fam['recall']:.4f}"
                )


if __name__ == "__main__":
    main()
