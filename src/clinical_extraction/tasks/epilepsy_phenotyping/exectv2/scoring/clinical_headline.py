"""Helpers for scoring saved ExECT clinical-headline predictions."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from clinical_extraction.core.scoring import PRF1, multiset_prf1
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.investigations import (
    score_investigations_components,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match import (
    clinical_headline_unit_keys,
    score_concept_identity,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.prescription import (
    score_prescription_components,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.seizure_frequency import (
    score_frequency_state,
)


def annotation_from_mapping(mention: dict[str, Any]) -> ExectAnnotation:
    """Build one scorer annotation from a saved prediction mapping."""

    return ExectAnnotation(
        entity=str(mention.get("entity", "")),
        text=str(mention.get("text", "")),
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


def clinical_headline_scores(
    gold_letters: list[ExectLetter],
    pred_letters: list[ExectLetter],
) -> dict[str, dict[str, Any]]:
    """Score the four selected ExECT clinical-headline families."""

    return {
        "Diagnosis": score_dict(
            score_concept_identity(gold_letters, pred_letters, "Diagnosis").concept_only
        ),
        "SeizureFrequency": score_dict(
            score_frequency_state(gold_letters, pred_letters).clinical_headline
        ),
        "Prescription": score_dict(
            score_prescription_components(gold_letters, pred_letters).clinical_headline
        ),
        "Investigations": score_dict(
            score_investigations_components(gold_letters, pred_letters).clinical_headline
        ),
    }


def score_dict(score: Any) -> dict[str, Any]:
    """Serialize one PRF-style score without losing asymmetric match counts."""

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
    """Aggregate family scores using their scorer-defined count surfaces."""

    precision_tp = recall_tp = pred_count = gold_count = 0
    for score in scores:
        precision_tp += int(score.get("precision_tp", score.get("tp", 0)))
        recall_tp += int(score.get("recall_tp", score.get("tp", 0)))
        pred_default = int(score.get("tp", 0)) + int(score.get("fp", 0))
        gold_default = int(score.get("tp", 0)) + int(score.get("fn", 0))
        pred_count += int(score.get("pred_count", pred_default))
        gold_count += int(score.get("gold_count", gold_default))
    precision = precision_tp / pred_count if pred_count else 0.0
    recall = recall_tp / gold_count if gold_count else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "tp": recall_tp,
        "precision_tp": precision_tp,
        "recall_tp": recall_tp,
        "fp": max(0, pred_count - precision_tp),
        "fn": max(0, gold_count - recall_tp),
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
