"""Helpers for scoring saved ExECT clinical-headline predictions."""

from __future__ import annotations

from collections.abc import Hashable, Iterable, Sequence
from typing import Any

from clinical_extraction.core.scoring import PRF1, multiset_prf1
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match import (
    clinical_headline_unit_keys,
)

CLINICAL_HEADLINE_FAMILIES = (
    "Diagnosis",
    "SeizureFrequency",
    "Prescription",
    "Investigations",
)


def annotation_from_mapping(mention: dict[str, Any]) -> ExectAnnotation:
    """Build one scorer annotation from a saved prediction mapping."""

    return ExectAnnotation(
        entity=str(mention.get("entity", "")),
        text=str(mention.get("standard_name") or mention.get("text", "")),
        attributes={
            str(key): str(value)
            for key, value in (mention.get("attributes") or {}).items()
            if value is not None
        },
    )


def letters_for_rows(
    rows: list[dict[str, Any]],
) -> tuple[list[ExectLetter], list[ExectLetter]]:
    """Project saved row dictionaries into aligned gold and prediction letters."""

    gold_letters = []
    pred_letters = []
    for row in rows:
        gold_letters.append(
            ExectLetter(
                letter_id=str(row["letter_id"]),
                note_text="",
                annotations=tuple(
                    annotation_from_mapping(mention) for mention in row.get("gold_mentions", [])
                ),
            )
        )
        pred_letters.append(
            ExectLetter(
                letter_id=str(row["letter_id"]),
                note_text="",
                annotations=tuple(
                    annotation_from_mapping(mention)
                    for mention in row.get("predicted_mentions", [])
                ),
            )
        )
    return gold_letters, pred_letters


def exact_clinical_headline_scores(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
) -> dict[str, dict[str, Any]]:
    """Score the four ExECT clinical-fact families with exact unit keys."""

    return {
        family: score_dict(score)
        for family, score in exact_clinical_headline_prf1_scores(
            gold_letters,
            pred_letters,
        ).items()
    }


def exact_clinical_headline_prf1_scores(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
) -> dict[str, PRF1]:
    """Return canonical exact ExECT clinical-fact PRF objects by family."""

    # Canonical ExECT result scorer: every reported pipeline, rung, and paper
    # clinical-fact score must use exact per-letter ``clinical_headline_unit_keys``.
    # ``score_concept_identity`` is a permissive diagnostic and must never replace
    # this scorer; it allows hierarchy and cross-family recall credit.
    gold_by_id = {letter.letter_id: letter for letter in gold_letters}
    pred_by_id = {letter.letter_id: letter for letter in pred_letters}
    letter_ids = sorted(gold_by_id.keys() | pred_by_id.keys())
    scores: dict[str, PRF1] = {}
    for family in CLINICAL_HEADLINE_FAMILIES:
        gold_units: list[tuple[str, Hashable]] = []
        pred_units: list[tuple[str, Hashable]] = []
        for letter_id in letter_ids:
            gold = gold_by_id.get(letter_id)
            pred = pred_by_id.get(letter_id)
            note_text = (
                gold.note_text
                if gold is not None
                else pred.note_text if pred is not None else ""
            )
            if gold is not None:
                gold_units.extend(
                    (letter_id, key)
                    for key in clinical_headline_unit_keys(
                        family,
                        gold.entities(family),
                        note_text,
                    )
                )
            if pred is not None:
                pred_units.extend(
                    (letter_id, key)
                    for key in clinical_headline_unit_keys(
                        family,
                        pred.entities(family),
                        note_text,
                    )
                )
        scores[family] = multiset_prf1(gold_units, pred_units)
    return scores


def score_dict(score: Any) -> dict[str, Any]:
    """Serialize one PRF-style score, retaining any diagnostic match counts."""

    pred_count = int(getattr(score, "pred_count", score.tp + score.fp))
    gold_count = int(getattr(score, "gold_count", score.tp + score.fn))
    return {
        "tp": score.tp,
        "precision_tp": int(getattr(score, "precision_tp", score.tp)),
        "recall_tp": int(getattr(score, "recall_tp", score.tp)),
        "fp": score.fp,
        "fn": score.fn,
        "pred_count": pred_count,
        "gold_count": gold_count,
        "precision": score.precision,
        "recall": score.recall,
        "f1": score.f1,
    }


def aggregate_scores(scores: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate exact family scores; reject asymmetric diagnostic counts."""

    tp = fp = fn = pred_count = gold_count = 0
    for score in scores:
        precision_tp = int(score.get("precision_tp", score.get("tp", 0)))
        recall_tp = int(score.get("recall_tp", score.get("tp", 0)))
        if precision_tp != recall_tp:
            raise ValueError(
                "reported ExECT clinical-headline scores must use symmetric exact unit keys"
            )
        tp += int(score.get("tp", 0))
        fp += int(score.get("fp", 0))
        fn += int(score.get("fn", 0))
        pred_default = int(score.get("tp", 0)) + int(score.get("fp", 0))
        gold_default = int(score.get("tp", 0)) + int(score.get("fn", 0))
        pred_count += int(score.get("pred_count", pred_default))
        gold_count += int(score.get("gold_count", gold_default))
    precision = tp / pred_count if pred_count else 0.0
    recall = tp / gold_count if gold_count else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "tp": tp,
        "precision_tp": tp,
        "recall_tp": tp,
        "fp": fp,
        "fn": fn,
        "pred_count": pred_count,
        "gold_count": gold_count,
    }


def headline_keys(
    row: dict[str, Any],
    family: str,
    *,
    field: str = "predicted_mentions",
) -> list[str]:
    """Return stable scorer keys for one saved row and family."""

    mentions = [
        annotation_from_mapping(mention)
        for mention in row.get(field, [])
        if str(mention.get("entity", "")) == family
    ]
    return [repr(key) for key in clinical_headline_unit_keys(family, mentions)]


def row_family_score(row: dict[str, Any], family: str) -> PRF1:
    """Score one saved row for one clinical family."""

    return multiset_prf1(
        headline_keys(row, family, field="gold_mentions"),
        headline_keys(row, family),
    )
