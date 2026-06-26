from __future__ import annotations

import re
from collections.abc import Hashable, Iterable, Sequence

from pydantic import BaseModel

from clinical_extraction.core.scoring import PRF1, multiset_prf1, sum_prf1
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectAnnotation, ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.drug_lexicon import (
    canonicalize_medication_name,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match import (
    PHRASE_ONLY,
    _letters_by_id,
    benchmark_config_for,
    score_entity,
    semantic_config_for,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.normalize import (
    canonicalize_attribute_value,
    normalize_phrase,
)

_PRESCRIPTION_ENTITY = "Prescription"
_AS_REQUIRED = "as_required"
_PRESCRIPTION_SOURCE_FREQUENCY = re.compile(
    r"(?<!\w)(?:prn|p\.r\.n\.|as\s+required|when\s+required|as\s+needed|rescue|"
    r"bd|b\.d\.|twice\s+(?:a\s+)?day|twice\s+daily|od|o\.d\.|"
    r"once\s+(?:a\s+)?day|once\s+daily|daily|mane|nocte|nightly|"
    r"morning|afternoon|evening|am|pm|at\s+night|tds|t\.d\.s\.|tid|"
    r"three\s+times\s+(?:a\s+)?day|qds|q\.d\.s\.|qid|"
    r"four\s+times\s+(?:a\s+)?day)(?!\w)",
    re.IGNORECASE,
)
_PRESCRIPTION_FUTURE_PLAN = re.compile(
    r"\b(?:commence|start(?:ing)?|increase|increasing|titrate|titration|"
    r"reduce|reducing|target\s+dose|future|option|consider|suggest|"
    r"planned|plan|every\s+(?:two\s+)?weeks|every\s+fortnight|until)\b",
    re.IGNORECASE,
)
_PRESCRIPTION_WEIGHT_BASED_DOSE = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:mg|mgs|mgms|g|grams?)\s*/?\s*kg(?:\s*/?\s*day)?\b",
    re.IGNORECASE,
)


class PrescriptionComponentScores(BaseModel):
    model_config = {"frozen": True}

    clinical_headline: PRF1
    name: PRF1
    dose: PRF1
    frequency: PRF1
    source_stated_frequency: PRF1
    guideline_defaulted_frequency: PRF1
    complete: PRF1
    ordinary_complete: PRF1
    rescue_regimen: PRF1
    future_medication: PRF1
    weight_based_dosing: PRF1


class PrescriptionBenchmarkProjectionScores(BaseModel):
    model_config = {"frozen": True}

    phrase_scope: PRF1
    semantic_without_cui: PRF1
    benchmark_with_cui: PRF1
    clinical_medication_identity: PRF1
    drugname_cui_projection: PRF1
    source_stated_frequency: PRF1
    guideline_defaulted_frequency: PRF1


def score_prescription_components(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
) -> PrescriptionComponentScores:
    """Score Prescription clinical headline and diagnostic component layers.

    These diagnostics deliberately ignore mention phrase scope and benchmark CUI
    projection. The clinical headline combines ordinary complete regimen tuples
    with dose-optional rescue regimens; supporting component scores remain
    diagnostic so partial or projection-specific gains are not overstated.
    """

    components = {
        component: _score_prescription_component(gold_letters, pred_letters, component)
        for component in (
            "clinical_headline",
            "name",
            "dose",
            "frequency",
            "source_stated_frequency",
            "guideline_defaulted_frequency",
            "complete",
            "ordinary_complete",
            "rescue_regimen",
            "future_medication",
            "weight_based_dosing",
        )
    }
    return PrescriptionComponentScores(**components)


def score_prescription_benchmark_projection(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
) -> PrescriptionBenchmarkProjectionScores:
    """Score Prescription benchmark-format sublayers without changing the headline.

    The projection table separates clinical medication identity from exact
    phrase scope, benchmark-facing DrugName/CUI conventions, and defaulted
    frequency projection. It is diagnostic: gains here should not be reported as
    pure clinical extraction gains.
    """

    return PrescriptionBenchmarkProjectionScores(
        phrase_scope=score_entity(
            gold_letters,
            pred_letters,
            _PRESCRIPTION_ENTITY,
            PHRASE_ONLY,
        ).per_item,
        semantic_without_cui=score_entity(
            gold_letters,
            pred_letters,
            _PRESCRIPTION_ENTITY,
            semantic_config_for(_PRESCRIPTION_ENTITY),
        ).per_item,
        benchmark_with_cui=score_entity(
            gold_letters,
            pred_letters,
            _PRESCRIPTION_ENTITY,
            benchmark_config_for(_PRESCRIPTION_ENTITY),
        ).per_item,
        clinical_medication_identity=_score_prescription_component(
            gold_letters,
            pred_letters,
            "name",
        ),
        drugname_cui_projection=_score_prescription_drugname_cui_projection(
            gold_letters,
            pred_letters,
        ),
        source_stated_frequency=_score_prescription_component(
            gold_letters,
            pred_letters,
            "source_stated_frequency",
        ),
        guideline_defaulted_frequency=_score_prescription_component(
            gold_letters,
            pred_letters,
            "guideline_defaulted_frequency",
        ),
    )


def _prescription_component_key(
    annotation: ExectAnnotation,
    component: str,
    note_text: str = "",
) -> Hashable | None:
    attrs = annotation.attributes
    if component == "name":
        value = attrs.get("DrugName")
        return canonicalize_medication_name(value) if value else None
    if component == "dose":
        dose = attrs.get("DrugDose")
        unit = attrs.get("DoseUnit")
        if not dose or not unit:
            return None
        return (
            canonicalize_attribute_value("DrugDose", dose),
            canonicalize_attribute_value("DoseUnit", unit),
        )
    if component == "frequency":
        frequency = attrs.get("Frequency")
        return canonicalize_attribute_value("Frequency", frequency).lower() if frequency else None
    if component == "source_stated_frequency":
        frequency = _prescription_component_key(annotation, "frequency", note_text)
        if frequency and _has_source_stated_frequency(annotation, note_text):
            return frequency
        return None
    if component == "guideline_defaulted_frequency":
        frequency = _prescription_component_key(annotation, "frequency", note_text)
        if frequency and not _has_source_stated_frequency(annotation, note_text):
            return frequency
        return None
    if component == "complete":
        name = _prescription_component_key(annotation, "name", note_text)
        dose = _prescription_component_key(annotation, "dose", note_text)
        frequency = _prescription_component_key(annotation, "frequency", note_text)
        if name is None or dose is None or frequency is None:
            return None
        return (name, *dose, frequency)
    if component == "ordinary_complete":
        complete = _prescription_component_key(annotation, "complete", note_text)
        frequency = _prescription_component_key(annotation, "frequency", note_text)
        if (
            complete is None
            or frequency == _AS_REQUIRED
            or _is_future_medication(annotation)
            or _is_weight_based_dosing(annotation)
        ):
            return None
        return complete
    if component == "rescue_regimen":
        name = _prescription_component_key(annotation, "name", note_text)
        frequency = _prescription_component_key(annotation, "frequency", note_text)
        if (
            name is None
            or frequency != _AS_REQUIRED
            or _is_future_medication(annotation)
            or _is_weight_based_dosing(annotation)
        ):
            return None
        return (name, _AS_REQUIRED)
    if component == "clinical_headline":
        rescue = _prescription_component_key(annotation, "rescue_regimen", note_text)
        if rescue is not None:
            return ("rescue", *rescue)
        ordinary = _prescription_component_key(annotation, "ordinary_complete", note_text)
        if ordinary is not None:
            return ("ordinary", *ordinary)
        return None
    if component == "future_medication":
        if not _is_future_medication(annotation):
            return None
        name = _prescription_component_key(annotation, "name", note_text)
        return (name or normalize_phrase(annotation.text), normalize_phrase(annotation.text))
    if component == "weight_based_dosing":
        if not _is_weight_based_dosing(annotation):
            return None
        name = _prescription_component_key(annotation, "name", note_text)
        return (name or normalize_phrase(annotation.text), normalize_phrase(annotation.text))
    raise ValueError(f"Unknown prescription component {component!r}")


def _prescription_component_keys(
    annotations: Iterable[ExectAnnotation],
    component: str,
    note_text: str = "",
) -> list[Hashable]:
    keys: list[Hashable] = []
    for annotation in annotations:
        key = _prescription_component_key(annotation, component, note_text)
        if key is not None:
            keys.append(key)
    return keys


def _has_source_stated_frequency(annotation: ExectAnnotation, note_text: str = "") -> bool:
    return any(
        _PRESCRIPTION_SOURCE_FREQUENCY.search(candidate)
        for candidate in _prescription_frequency_source_candidates(annotation, note_text)
    )


def _prescription_frequency_source_candidates(
    annotation: ExectAnnotation,
    note_text: str,
) -> tuple[str, ...]:
    candidates = [annotation.text, annotation.text.replace("-", " ")]
    if annotation.raw_text and annotation.raw_text != annotation.text:
        candidates.extend([annotation.raw_text, annotation.raw_text.replace("-", " ")])
    if note_text:
        candidates.extend(_note_windows_for_annotation_phrase(annotation, note_text))
    return tuple(candidate for candidate in candidates if candidate)


def _note_windows_for_annotation_phrase(
    annotation: ExectAnnotation,
    note_text: str,
) -> tuple[str, ...]:
    normalized_note = normalize_phrase(note_text)
    windows: list[str] = []
    for phrase in _annotation_frequency_search_phrases(annotation):
        start = 0
        while True:
            index = normalized_note.find(phrase, start)
            if index == -1:
                break
            windows.append(normalized_note[max(0, index - 48) : index + len(phrase) + 128])
            start = index + max(1, len(phrase))
    return tuple(windows)


def _annotation_frequency_search_phrases(annotation: ExectAnnotation) -> tuple[str, ...]:
    raw_terms = [
        annotation.text,
        annotation.raw_text or "",
        annotation.attributes.get("DrugName", ""),
        annotation.attributes.get("CUIPhrase", ""),
        canonicalize_medication_name(annotation.attributes.get("DrugName", "")),
    ]
    phrases: list[str] = []
    seen: set[str] = set()
    for term in raw_terms:
        phrase = normalize_phrase(term)
        if phrase and phrase not in seen:
            seen.add(phrase)
            phrases.append(phrase)
    return tuple(phrases)


def _is_future_medication(annotation: ExectAnnotation) -> bool:
    return bool(_PRESCRIPTION_FUTURE_PLAN.search(annotation.text))


def _is_weight_based_dosing(annotation: ExectAnnotation) -> bool:
    return bool(_PRESCRIPTION_WEIGHT_BASED_DOSE.search(annotation.text))


def _prescription_drugname_cui_keys(
    annotations: Iterable[ExectAnnotation],
) -> list[Hashable]:
    keys: list[Hashable] = []
    for annotation in annotations:
        attrs = annotation.attributes
        drug_name = attrs.get("DrugName")
        cui = attrs.get("CUI")
        if not drug_name or not cui:
            continue
        keys.append(
            (
                canonicalize_medication_name(drug_name),
                canonicalize_attribute_value("CUI", cui),
            )
        )
    return keys


def _score_prescription_component(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
    component: str,
) -> PRF1:
    gold_by_id = _letters_by_id(gold_letters)
    pred_by_id = _letters_by_id(pred_letters)
    all_ids = sorted(gold_by_id.keys() | pred_by_id.keys())
    return sum_prf1(
        multiset_prf1(
            _prescription_component_keys(
                gold_by_id[letter_id].entities(_PRESCRIPTION_ENTITY)
                if letter_id in gold_by_id
                else (),
                component,
                gold_by_id[letter_id].note_text if letter_id in gold_by_id else "",
            ),
            _prescription_component_keys(
                pred_by_id[letter_id].entities(_PRESCRIPTION_ENTITY)
                if letter_id in pred_by_id
                else (),
                component,
                pred_by_id[letter_id].note_text if letter_id in pred_by_id else "",
            ),
        )
        for letter_id in all_ids
    )


def _score_prescription_drugname_cui_projection(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
) -> PRF1:
    gold_by_id = _letters_by_id(gold_letters)
    pred_by_id = _letters_by_id(pred_letters)
    all_ids = sorted(gold_by_id.keys() | pred_by_id.keys())
    return sum_prf1(
        multiset_prf1(
            _prescription_drugname_cui_keys(
                gold_by_id[letter_id].entities(_PRESCRIPTION_ENTITY)
                if letter_id in gold_by_id
                else ()
            ),
            _prescription_drugname_cui_keys(
                pred_by_id[letter_id].entities(_PRESCRIPTION_ENTITY)
                if letter_id in pred_by_id
                else ()
            ),
        )
        for letter_id in all_ids
    )
