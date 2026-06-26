"""Artifact loading helpers for LLM-first essential evaluation replays."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)


def _annotation_from_mention(mention: dict[str, Any]) -> ExectAnnotation:
    return ExectAnnotation(
        entity=str(mention["entity"]),
        text=str(mention.get("text", "")),
        attributes={str(k): str(v) for k, v in dict(mention.get("attributes", {})).items()},
    )


def _predicted_mention(mention: dict[str, Any]) -> PredictedMention:
    return PredictedMention(
        entity=str(mention["entity"]),
        text=str(mention.get("text", "")),
        attributes={str(k): str(v) for k, v in dict(mention.get("attributes", {})).items()},
        evidence=str(mention.get("evidence", "")),
        rationale=str(mention.get("rationale", "")),
        confidence=mention.get("confidence"),
    )


def letters_from_artifact(
    path: Path,
) -> tuple[list[ExectLetter], list[PredictedLetter]]:
    """Reconstruct (gold_letters, predicted_letters) from a saved JSONL artifact."""

    gold_letters: list[ExectLetter] = []
    pred_letters: list[PredictedLetter] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        letter_id = str(row["letter_id"])
        gold_letters.append(
            ExectLetter(
                letter_id=letter_id,
                note_text="",
                annotations=tuple(
                    _annotation_from_mention(m) for m in row.get("gold_mentions", [])
                ),
            )
        )
        pred_letters.append(
            PredictedLetter(
                letter_id=letter_id,
                mentions=tuple(
                    _predicted_mention(m) for m in row.get("predicted_mentions", [])
                ),
            )
        )
    return gold_letters, pred_letters


def predicted_by_id_from_artifact(path: Path) -> dict[str, PredictedLetter]:
    """Return predicted letters keyed by ``letter_id`` from a JSONL artifact."""

    by_id: dict[str, PredictedLetter] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        letter_id = str(row["letter_id"])
        by_id[letter_id] = PredictedLetter(
            letter_id=letter_id,
            mentions=tuple(_predicted_mention(m) for m in row.get("predicted_mentions", [])),
        )
    return by_id


def align_predictions_to_gold(
    gold_letters: Sequence[ExectLetter],
    predicted_by_id: dict[str, PredictedLetter],
) -> list[PredictedLetter]:
    """Order predictions to match ``gold_letters``; emit empty letters for misses."""

    return [
        predicted_by_id.get(g.letter_id, PredictedLetter(letter_id=g.letter_id, mentions=()))
        for g in gold_letters
    ]
