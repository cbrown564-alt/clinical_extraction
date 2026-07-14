"""Paper-derived ExECTv2 phrase, CUI, and all-feature scores.

The 2024 ExECTv2 paper reports mention-level and letter-level validation with
all evaluated features, says that ExECTv2 term matching used CUIs, and reports
the overall result as the mean of the nine entity results. These views stay
separate from the repository's clinical-recovery and legacy projection scores.
"""

from __future__ import annotations

from collections.abc import Callable, Hashable, Iterable, Mapping, Sequence
from dataclasses import dataclass

from pydantic import BaseModel

from clinical_extraction.core.scoring import PRF1, multiset_prf1, prf1_from_counts, sum_prf1
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    POINT_RANGE_TRIPLES,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.text import (
    normalize_phrase,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match import EntityScore
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.normalize import (
    canonicalize_attribute_value,
    canonicalize_point_range_attributes,
)

_CUI = "CUI"
_CUI_PHRASE = "CUIPhrase"
_CERTAINTY_ENTITIES = frozenset({"Diagnosis", "PatientHistory"})
_NEGATION_ENTITIES = frozenset({"PatientHistory"})


class MacroPRF1(BaseModel):
    """Unweighted mean of entity precision, recall, and F1 values."""

    model_config = {"frozen": True}

    precision: float
    recall: float
    f1: float


class PublishedViewScore(BaseModel):
    model_config = {"frozen": True}

    macro_per_item: MacroPRF1
    macro_per_letter: MacroPRF1
    per_entity: dict[str, EntityScore]


class MissingCuiCount(BaseModel):
    model_config = {"frozen": True}

    gold: int
    predicted: int


class MissingCuiSummary(MissingCuiCount):
    by_entity: dict[str, MissingCuiCount]


class PublishedMetricScores(BaseModel):
    model_config = {"frozen": True}

    normalized_phrase: PublishedViewScore
    cui: PublishedViewScore
    all_features: PublishedViewScore
    missing_cui: MissingCuiSummary


@dataclass(frozen=True)
class _KeyResult:
    key: Hashable | None


_KeyFunction = Callable[[ExectAnnotation], _KeyResult]


def score_published_metrics(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
    entities: Sequence[str],
) -> PublishedMetricScores:
    """Score independently attributable ExECTv2 published-metric views.

    ``normalized_phrase`` compares selected mention text after neutral surface
    normalization. ``cui`` requires a non-empty UMLS CUI. ``all_features``
    requires that CUI and every feature used by the published validation.
    Missing CUIs are deliberately unmatchable rather than a shared null value.
    """

    entity_names = tuple(dict.fromkeys(entities))
    if not entity_names:
        raise ValueError("published-metric scoring requires at least one entity")

    phrase_scores = _score_view(gold_letters, pred_letters, entity_names, _phrase_key)
    cui_scores = _score_view(gold_letters, pred_letters, entity_names, _cui_key)
    feature_scores = _score_view(gold_letters, pred_letters, entity_names, _all_features_key)
    missing_by_entity = {
        entity: MissingCuiCount(
            gold=_missing_cui_count(gold_letters, entity),
            predicted=_missing_cui_count(pred_letters, entity),
        )
        for entity in entity_names
    }
    return PublishedMetricScores(
        normalized_phrase=phrase_scores,
        cui=cui_scores,
        all_features=feature_scores,
        missing_cui=MissingCuiSummary(
            gold=sum(count.gold for count in missing_by_entity.values()),
            predicted=sum(count.predicted for count in missing_by_entity.values()),
            by_entity=missing_by_entity,
        ),
    )


def evaluated_attributes(annotation: ExectAnnotation) -> Mapping[str, str]:
    """Return the complete feature bundle used by the paper-derived view.

    ``CUIPhrase`` is the human-readable label for the CUI, not an independent
    clinical feature. The paper's validation used certainty for Diagnosis and
    Patient History and negation for Patient History only; other assertion
    fields are therefore not part of this comparison.
    """

    attributes: Mapping[str, str] = annotation.attributes
    triples = POINT_RANGE_TRIPLES.get(annotation.entity, ())
    if triples:
        attributes = canonicalize_point_range_attributes(attributes, triples)
    ignored = {_CUI_PHRASE}
    if annotation.entity not in _CERTAINTY_ENTITIES:
        ignored.add("Certainty")
    if annotation.entity not in _NEGATION_ENTITIES:
        ignored.add("Negation")
    return {
        key: canonicalize_attribute_value(key, value)
        for key, value in attributes.items()
        if key not in ignored
    }


def _score_view(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
    entities: Sequence[str],
    key_function: _KeyFunction,
) -> PublishedViewScore:
    per_entity = {
        entity: _score_entity(gold_letters, pred_letters, entity, key_function)
        for entity in entities
    }
    return PublishedViewScore(
        macro_per_item=_macro(score.per_item for score in per_entity.values()),
        macro_per_letter=_macro(score.per_letter for score in per_entity.values()),
        per_entity=per_entity,
    )


def _score_entity(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
    entity: str,
    key_function: _KeyFunction,
) -> EntityScore:
    gold_by_id = _letters_by_id(gold_letters)
    pred_by_id = _letters_by_id(pred_letters)
    all_ids = sorted(gold_by_id.keys() | pred_by_id.keys())
    item_parts: list[PRF1] = []
    letter_tp = letter_fp = letter_fn = 0

    for letter_id in all_ids:
        gold_mentions = gold_by_id[letter_id].entities(entity) if letter_id in gold_by_id else ()
        pred_mentions = pred_by_id[letter_id].entities(entity) if letter_id in pred_by_id else ()
        item_score = _score_mentions(gold_mentions, pred_mentions, key_function)
        item_parts.append(item_score)

        gold_present = bool(gold_mentions)
        pred_present = bool(pred_mentions)
        if gold_present and item_score.tp > 0:
            letter_tp += 1
        elif gold_present:
            letter_fn += 1
        elif pred_present:
            letter_fp += 1

    return EntityScore(
        entity=entity,
        per_item=sum_prf1(item_parts),
        per_letter=prf1_from_counts(letter_tp, letter_fp, letter_fn),
    )


def _score_mentions(
    gold_mentions: Sequence[ExectAnnotation],
    pred_mentions: Sequence[ExectAnnotation],
    key_function: _KeyFunction,
) -> PRF1:
    gold_results = [key_function(annotation) for annotation in gold_mentions]
    pred_results = [key_function(annotation) for annotation in pred_mentions]
    gold_keys = [result.key for result in gold_results if result.key is not None]
    pred_keys = [result.key for result in pred_results if result.key is not None]
    valid_score = multiset_prf1(gold_keys, pred_keys)
    invalid_gold = sum(result.key is None for result in gold_results)
    invalid_pred = sum(result.key is None for result in pred_results)
    return prf1_from_counts(
        valid_score.tp,
        valid_score.fp + invalid_pred,
        valid_score.fn + invalid_gold,
    )


def _phrase_key(annotation: ExectAnnotation) -> _KeyResult:
    source_text = annotation.raw_text if annotation.raw_text is not None else annotation.text
    return _KeyResult((annotation.entity, normalize_phrase(source_text)))


def _cui_key(annotation: ExectAnnotation) -> _KeyResult:
    cui = canonicalize_attribute_value(_CUI, annotation.attributes.get(_CUI, ""))
    if not cui:
        return _KeyResult(None)
    return _KeyResult((annotation.entity, cui))


def _all_features_key(annotation: ExectAnnotation) -> _KeyResult:
    attributes = evaluated_attributes(annotation)
    cui = attributes.get(_CUI, "")
    if not cui:
        return _KeyResult(None)
    return _KeyResult((annotation.entity, tuple(sorted(attributes.items()))))


def _macro(scores: Iterable[PRF1]) -> MacroPRF1:
    values = tuple(scores)
    return MacroPRF1(
        precision=sum(score.precision for score in values) / len(values),
        recall=sum(score.recall for score in values) / len(values),
        f1=sum(score.f1 for score in values) / len(values),
    )


def _letters_by_id(letters: Sequence[ExectLetter]) -> dict[str, ExectLetter]:
    by_id = {letter.letter_id: letter for letter in letters}
    if len(by_id) != len(letters):
        raise ValueError("duplicate ExECTv2 letter_id in published-metric input")
    return by_id


def _missing_cui_count(letters: Sequence[ExectLetter], entity: str) -> int:
    return sum(
        not canonicalize_attribute_value(_CUI, annotation.attributes.get(_CUI, ""))
        for letter in letters
        for annotation in letter.entities(entity)
    )


__all__ = [
    "MacroPRF1",
    "MissingCuiCount",
    "MissingCuiSummary",
    "PublishedMetricScores",
    "PublishedViewScore",
    "evaluated_attributes",
    "score_published_metrics",
]
