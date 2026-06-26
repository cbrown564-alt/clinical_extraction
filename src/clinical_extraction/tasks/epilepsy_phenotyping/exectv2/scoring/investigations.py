from __future__ import annotations

from collections.abc import Hashable, Iterable, Sequence

from pydantic import BaseModel

from clinical_extraction.core.scoring import PRF1, multiset_prf1, sum_prf1
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectAnnotation, ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match import _letters_by_id
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.normalize import (
    canonicalize_attribute_value,
    normalize_phrase,
)


class InvestigationsComponentScores(BaseModel):
    model_config = {"frozen": True}

    clinical_headline: PRF1
    eeg: PRF1
    mri: PRF1
    ct: PRF1
    performed: PRF1
    result: PRF1
    eeg_type: PRF1


def score_investigations_components(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
) -> InvestigationsComponentScores:
    components = {
        component: _score_investigations_component(gold_letters, pred_letters, component)
        for component in (
            "clinical_headline",
            "eeg",
            "mri",
            "ct",
            "performed",
            "result",
            "eeg_type",
        )
    }
    return InvestigationsComponentScores(**components)


def _score_investigations_component(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
    component: str,
) -> PRF1:
    gold_by_id = _letters_by_id(gold_letters)
    pred_by_id = _letters_by_id(pred_letters)
    all_ids = sorted(gold_by_id.keys() | pred_by_id.keys())
    return sum_prf1(
        multiset_prf1(
            _investigation_component_keys(
                gold_by_id[letter_id].entities("Investigations")
                if letter_id in gold_by_id
                else (),
                component,
            ),
            _investigation_component_keys(
                pred_by_id[letter_id].entities("Investigations")
                if letter_id in pred_by_id
                else (),
                component,
            ),
        )
        for letter_id in all_ids
    )


def _investigation_component_keys(
    annotations: Iterable[ExectAnnotation],
    component: str,
) -> list[Hashable]:
    keys: list[Hashable] = []
    for annotation in annotations:
        for modality in ("EEG", "MRI", "CT"):
            modality_key = _investigation_modality_key(annotation, modality)
            if modality_key is None:
                continue
            if component == "clinical_headline":
                keys.append(modality_key[:3])
            elif component == modality.lower():
                keys.append(modality_key)
            elif component == "performed" and modality_key[1] is not None:
                keys.append((modality, modality_key[1]))
            elif component == "result" and modality_key[2] is not None:
                keys.append((modality, modality_key[2]))
            elif component == "eeg_type" and modality == "EEG" and modality_key[3] is not None:
                keys.append((modality, modality_key[3]))
            elif component not in {
                "clinical_headline",
                "eeg",
                "mri",
                "ct",
                "performed",
                "result",
                "eeg_type",
            }:
                raise ValueError(f"Unknown investigations component {component!r}")
    return keys


def _investigation_modality_key(
    annotation: ExectAnnotation,
    modality: str,
) -> tuple[str, str | None, str | None, str | None] | None:
    attrs = annotation.attributes
    performed = attrs.get(f"{modality}_Performed")
    result = attrs.get(f"{modality}_Results")
    eeg_type = attrs.get("EEG_Type") if modality == "EEG" else None
    text_has_modality = modality.lower() in normalize_phrase(annotation.text).split()
    if not any((performed, result, eeg_type, text_has_modality)):
        return None
    return (
        modality,
        canonicalize_attribute_value(f"{modality}_Performed", performed) if performed else None,
        canonicalize_attribute_value(f"{modality}_Results", result) if result else None,
        canonicalize_attribute_value("EEG_Type", eeg_type) if eeg_type else None,
    )
