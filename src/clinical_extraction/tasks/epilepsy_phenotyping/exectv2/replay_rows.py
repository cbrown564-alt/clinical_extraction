"""Reconstruct ExECT letters from retained replay rows."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Literal, cast

from .contract.prediction import PredictedLetter, PredictedMention, to_exect_letter
from .data import ExectAnnotation, ExectLetter


def _confidence(value: object) -> Literal["low", "medium", "high"]:
    normalized = str(value)
    if normalized not in {"low", "medium", "high"}:
        return "medium"
    return cast(Literal["low", "medium", "high"], normalized)


def reconstruct_gold_letters(
    rows: Sequence[dict[str, Any]],
    *,
    entity_name: str,
) -> list[ExectLetter]:
    return [
        ExectLetter(
            letter_id=row["letter_id"],
            note_text="",
            annotations=tuple(
                ExectAnnotation(
                    entity=entity_name,
                    text=str(mention["text"]),
                    attributes={
                        str(key): str(value)
                        for key, value in dict(mention.get("attributes") or {}).items()
                    },
                )
                for mention in row.get("gold_mentions", [])
            ),
        )
        for row in rows
    ]


def reconstruct_pred_letters(
    rows: Sequence[dict[str, Any]],
    *,
    entity_name: str,
) -> list[ExectLetter]:
    letters: list[ExectLetter] = []
    for row in rows:
        predicted = PredictedLetter(
            letter_id=row["letter_id"],
            mentions=tuple(
                PredictedMention(
                    entity=entity_name,
                    text=str(mention["text"]),
                    attributes={
                        str(key): str(value)
                        for key, value in dict(mention.get("attributes") or {}).items()
                    },
                    evidence=str(mention.get("evidence", "")),
                    confidence=_confidence(mention.get("confidence", "medium")),
                    rationale=str(mention.get("rationale", "")),
                )
                for mention in row.get("predicted_mentions", [])
            ),
        )
        letters.append(to_exect_letter(predicted))
    return letters
