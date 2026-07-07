"""CUI stripping and deterministic projection helpers."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    project_cuis,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.llm_first.constants import (
    CUI,
    CUI_PHRASE,
)


def strip_and_project(pred_letters: Sequence[PredictedLetter]) -> list[PredictedLetter]:
    """Strip model-supplied CUI/CUIPhrase, then deterministically re-attach CUIs."""

    projected: list[PredictedLetter] = []
    for letter in pred_letters:
        stripped = PredictedLetter(
            letter_id=letter.letter_id,
            mentions=tuple(
                m.model_copy(
                    update={
                        "attributes": {
                            k: v for k, v in m.attributes.items() if k not in (CUI, CUI_PHRASE)
                        }
                    }
                )
                for m in letter.mentions
            ),
            diagnostics=letter.diagnostics,
        )
        try:
            projected.append(project_cuis(stripped))
        except Exception:  # pragma: no cover - projection is best-effort here
            projected.append(stripped)
    return projected


def strip_prediction_cui(pred_letters: Sequence[PredictedLetter]) -> list[PredictedLetter]:
    stripped: list[PredictedLetter] = []
    for letter in pred_letters:
        stripped.append(
            PredictedLetter(
                letter_id=letter.letter_id,
                mentions=tuple(
                    m.model_copy(
                        update={
                            "attributes": {
                                k: v for k, v in m.attributes.items() if k not in (CUI, CUI_PHRASE)
                            }
                        }
                    )
                    for m in letter.mentions
                ),
                diagnostics=letter.diagnostics,
            )
        )
    return stripped


def strip_gold_cui(gold_letters: Sequence[ExectLetter]) -> list[ExectLetter]:
    return [
        ExectLetter(
            letter_id=letter.letter_id,
            note_text=letter.note_text,
            annotations=tuple(
                ExectAnnotation(
                    entity=ann.entity,
                    text=ann.text,
                    attributes={
                        k: v for k, v in ann.attributes.items() if k not in (CUI, CUI_PHRASE)
                    },
                    raw_text=ann.raw_text,
                )
                for ann in letter.annotations
            ),
        )
        for letter in gold_letters
    ]


def as_predicted(pred_letters: Sequence[Any]) -> list[PredictedLetter]:
    out: list[PredictedLetter] = []
    for letter in pred_letters:
        if isinstance(letter, PredictedLetter):
            out.append(letter)
        else:
            out.append(
                PredictedLetter(
                    letter_id=letter.letter_id,
                    mentions=tuple(
                        PredictedMention(
                            entity=a.entity,
                            text=a.text,
                            attributes=dict(a.attributes),
                            evidence="",
                        )
                        for a in letter.annotations
                    ),
                )
            )
    return out


def as_exect(pred_letters: Sequence[Any]) -> list[ExectLetter]:
    out: list[ExectLetter] = []
    for letter in pred_letters:
        if isinstance(letter, ExectLetter):
            out.append(letter)
        else:
            out.append(to_exect_letter(letter))
    return out
