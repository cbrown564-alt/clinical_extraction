#!/usr/bin/env python3
"""Development audit of ExECT rules-only against the inventory scorer.

No model calls. Loads ``dev140`` only. Does not load ``test60``.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.assembly.views import (
    mention_to_dict,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
    load_letters_for_split,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    diagnosis as diagnosis_mod,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    extract_deterministic_all9,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.all_entities import (
    investigations as inv_mod,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.normalization import (
    canonicalize_diagnosis_concept,
    is_diagnosis_descendant,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.deterministic.select_rules import (
    INVENTORY_SELECT_RULE_IDS,
    apply_select_rules,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.clinical_headline import (
    CLINICAL_HEADLINE_FAMILIES,
    aggregate_scores,
    annotation_from_mapping,
    exact_clinical_headline_scores,
    exact_clinical_inventory_scores,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match import (
    clinical_headline_unit_keys,
    clinical_inventory_unit_keys,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "experiments/exect_rules_only_inventory_retune_audit_20260827"
FAMILIES = CLINICAL_HEADLINE_FAMILIES


def _four_family(mentions: tuple[PredictedMention, ...]) -> tuple[PredictedMention, ...]:
    return tuple(mention for mention in mentions if mention.entity in FAMILIES)


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
        ),
    )


def _from_dicts(letter_id: str, rows: list[dict[str, Any]]) -> ExectLetter:
    return ExectLetter(
        letter_id=letter_id,
        note_text="",
        annotations=tuple(annotation_from_mapping(row) for row in rows),
    )


def _score_pair(
    gold_letters: list[ExectLetter],
    pred_letters: list[ExectLetter],
) -> dict[str, Any]:
    headline = exact_clinical_headline_scores(gold_letters, pred_letters)
    inventory = exact_clinical_inventory_scores(gold_letters, pred_letters)
    return {
        "headline": {"overall": aggregate_scores(headline.values()), "by_family": headline},
        "inventory": {"overall": aggregate_scores(inventory.values()), "by_family": inventory},
    }


def _concept_set(annotations: tuple[ExectAnnotation, ...], family: str) -> set[str]:
    keys = clinical_inventory_unit_keys(family, annotations)
    concepts: set[str] = set()
    for key in keys:
        if isinstance(key, tuple) and len(key) >= 2:
            concepts.add(str(key[1]))
    return concepts


def _extract_diagnoses_no_overlap(
    text: str,
) -> tuple[tuple[PredictedMention, ...], tuple[PredictedMention, ...]]:
    matches = sorted(
        diagnosis_mod._BASELINE_DIAGNOSIS_PATTERN.finditer(text),
        key=lambda match: match.end() - match.start(),
        reverse=True,
    )
    kept: list[PredictedMention] = []
    recovered: list[PredictedMention] = []
    occupied: list[tuple[int, int]] = []
    for match in matches:
        overlaps_kept = any(diagnosis_mod._overlaps(match.span(), span) for span in occupied)
        phrase = match.group(1)
        concept = diagnosis_mod.diagnosis_concept(phrase)
        if concept is None:
            continue
        if diagnosis_mod._is_diagnosis_phrase_inside_onset_statement(text, match):
            continue
        if diagnosis_mod._is_diagnosis_phrase_inside_cause_statement(text, match):
            continue
        attrs = {
            "DiagCategory": concept.canonical,
            "Certainty": "5",
            "Negation": "Affirmed",
        }
        attrs = diagnosis_mod.attach_benchmark_concept(attrs, concept)
        mention = PredictedMention(
            entity="Diagnosis",
            text=phrase,
            attributes=attrs,
            evidence=phrase,
            evidence_span=diagnosis_mod.match_span(match),
        )
        if not overlaps_kept:
            occupied.append(match.span())
            kept.append(mention)
            continue
        recovered.append(mention)
        kept.append(mention)
    return tuple(kept), tuple(recovered)


def _extract_investigations_no_collapse(text: str) -> tuple[PredictedMention, ...]:
    original = inv_mod._collapse_same_result
    inv_mod._collapse_same_result = lambda mentions: tuple(mentions)
    try:
        return inv_mod._extract_investigations(text)
    finally:
        inv_mod._collapse_same_result = original


def main() -> None:
    letters = list(load_letters_for_split("dev"))
    letters.sort(key=lambda item: item.letter_id)
    if len(letters) != 140:
        raise RuntimeError(f"expected 140 development letters, found {len(letters)}")

    gold_letters = [
        ExectLetter(
            letter_id=letter.letter_id,
            note_text=letter.note_text,
            annotations=tuple(
                annotation for annotation in letter.annotations if annotation.entity in FAMILIES
            ),
        )
        for letter in letters
    ]

    current_preds: list[ExectLetter] = []
    recall_dx_preds: list[ExectLetter] = []
    no_inv_collapse_preds: list[ExectLetter] = []
    select_on_current_preds: list[ExectLetter] = []
    select_on_recall_dx_preds: list[ExectLetter] = []

    parent_fn_while_child: list[dict[str, Any]] = []
    overlap_recoveries: Counter[str] = Counter()
    inv_collapse_drops = 0
    select_actions: Counter[str] = Counter()
    select_on_recall_actions: Counter[str] = Counter()

    for gold, letter in zip(gold_letters, letters, strict=True):
        current = extract_deterministic_all9(letter)
        current_four = _four_family(current.mentions)
        current_preds.append(_to_exect(letter.letter_id, current_four))

        recall_dx, recovered = _extract_diagnoses_no_overlap(letter.note_text)
        overlap_recoveries["letters_with_overlap_recovery"] += 1 if recovered else 0
        overlap_recoveries["recovered_mentions"] += len(recovered)
        for mention in recovered:
            concept = canonicalize_diagnosis_concept(mention.text)
            gold_concepts = _concept_set(gold.entities("Diagnosis"), "Diagnosis")
            if concept in gold_concepts:
                overlap_recoveries["recovered_gold_inventory_concepts"] += 1
            overlap_recoveries[f"concept:{concept}"] += 1

        recall_mentions = tuple(
            mention for mention in current_four if mention.entity != "Diagnosis"
        ) + recall_dx
        recall_dx_preds.append(_to_exect(letter.letter_id, recall_mentions))

        inv_full = _extract_investigations_no_collapse(letter.note_text)
        inv_collapsed = tuple(
            mention for mention in current_four if mention.entity == "Investigations"
        )
        inv_collapse_drops += max(0, len(inv_full) - len(inv_collapsed))
        no_inv_mentions = tuple(
            mention for mention in current_four if mention.entity != "Investigations"
        ) + inv_full
        no_inv_collapse_preds.append(_to_exect(letter.letter_id, no_inv_mentions))

        gold_dx = _concept_set(gold.entities("Diagnosis"), "Diagnosis")
        pred_dx = _concept_set(
            tuple(
                ExectAnnotation(entity=m.entity, text=m.text, attributes=dict(m.attributes))
                for m in current_four
                if m.entity == "Diagnosis"
            ),
            "Diagnosis",
        )
        headline_gold = {
            str(key[1])
            for key in clinical_headline_unit_keys("Diagnosis", gold.entities("Diagnosis"))
            if isinstance(key, tuple) and len(key) >= 2
        }
        for missing in gold_dx - pred_dx:
            if any(is_diagnosis_descendant(child, missing) for child in pred_dx):
                parent_fn_while_child.append(
                    {
                        "letter_id": letter.letter_id,
                        "missing_parent": missing,
                        "predicted_children": sorted(
                            child
                            for child in pred_dx
                            if is_diagnosis_descendant(child, missing)
                        ),
                        "headline_would_collapse": missing not in headline_gold,
                    }
                )

        current_rows = [mention_to_dict(mention) for mention in current_four]
        selected, actions = apply_select_rules(
            current_rows,
            source_mentions=current_rows,
            note_text=letter.note_text,
            enabled_rule_ids=set(INVENTORY_SELECT_RULE_IDS),
        )
        for action in actions:
            select_actions[str(action.get("rule_id"))] += 1
        select_on_current_preds.append(_from_dicts(letter.letter_id, selected))

        recall_rows = [mention_to_dict(mention) for mention in recall_mentions]
        selected_recall, recall_actions = apply_select_rules(
            recall_rows,
            source_mentions=recall_rows,
            note_text=letter.note_text,
            enabled_rule_ids=set(INVENTORY_SELECT_RULE_IDS),
        )
        for action in recall_actions:
            select_on_recall_actions[str(action.get("rule_id"))] += 1
        select_on_recall_dx_preds.append(_from_dicts(letter.letter_id, selected_recall))

    arms = {
        "current_rules": _score_pair(gold_letters, current_preds),
        "diagnosis_no_overlap_suppression": _score_pair(gold_letters, recall_dx_preds),
        "investigations_no_same_result_collapse": _score_pair(
            gold_letters, no_inv_collapse_preds
        ),
        "inventory_select_on_current": _score_pair(gold_letters, select_on_current_preds),
        "inventory_select_on_recall_diagnosis": _score_pair(
            gold_letters, select_on_recall_dx_preds
        ),
    }

    summary = {
        "schema_version": "exect.rules_only.inventory_retune_audit.dev140.v1",
        "date": date.today().isoformat(),
        "protocol": (
            "docs/research/exectv2/exect_rules_only_inventory_retune_audit_protocol_2026-08-27.md"
        ),
        "split": "dev140",
        "row_policy": "development_review_permitted",
        "holdout_loaded": False,
        "model_calls": 0,
        "scorers": ["clinical_headline_unit_keys", "clinical_inventory_unit_keys"],
        "arms": arms,
        "diagnosis_parent_fn_while_child_present": {
            "count": len(parent_fn_while_child),
            "letters": len({row["letter_id"] for row in parent_fn_while_child}),
            "headline_would_have_collapsed": sum(
                1 for row in parent_fn_while_child if row["headline_would_collapse"]
            ),
            "examples": parent_fn_while_child[:20],
        },
        "diagnosis_overlap_suppression": dict(overlap_recoveries),
        "investigations_same_result_drops": inv_collapse_drops,
        "inventory_select_actions_on_current": dict(select_actions),
        "inventory_select_actions_on_recall_diagnosis": dict(select_on_recall_actions),
        "claim_boundary": (
            "Development mechanism only. Not a cited five-cell replacement. "
            "test60 was not loaded."
        ),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "summary.json"
    out_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(out_path)
    current_inv = arms["current_rules"]["inventory"]["overall"]
    print(
        "current inventory",
        current_inv["f1"],
        "P",
        current_inv["precision"],
        "R",
        current_inv["recall"],
    )
    recall_inv = arms["diagnosis_no_overlap_suppression"]["inventory"]["overall"]
    print(
        "no-overlap inventory",
        recall_inv["f1"],
        "P",
        recall_inv["precision"],
        "R",
        recall_inv["recall"],
    )
    print("parent FN while child", len(parent_fn_while_child))


if __name__ == "__main__":
    main()
