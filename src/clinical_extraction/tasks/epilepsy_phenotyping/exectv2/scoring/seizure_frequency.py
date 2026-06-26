from __future__ import annotations

from collections.abc import Hashable, Iterable, Mapping, Sequence

from pydantic import BaseModel

from clinical_extraction.core.scoring import PRF1, multiset_prf1, sum_prf1
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectAnnotation, ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.match import (
    _letters_by_id,
    benchmark_config_for,
    score_entity,
    semantic_config_for,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring.normalize import (
    canonicalize_attribute_value,
    normalize_phrase,
)

# Rate-bearing attributes for active-rate fidelity: seizure counts and cadence,
# excluding dates / point-in-time so this isolates burden magnitude, not timing.
_FREQUENCY_RATE_ATTRIBUTES: frozenset[str] = frozenset(
    {
        "NumberOfSeizures",
        "LowerNumberOfSeizures",
        "UpperNumberOfSeizures",
        "NumberOfTimePeriods",
        "LowerNumberOfTimePeriods",
        "UpperNumberOfTimePeriods",
        "TimePeriod",
    }
)


class FrequencyStateScores(BaseModel):
    model_config = {"frozen": True}

    clinical_headline: PRF1
    active_rate: PRF1
    active_rate_fidelity: PRF1
    seizure_free: PRF1
    unknown: PRF1
    exact_semantic: PRF1
    benchmark_with_cui: PRF1


def score_frequency_state(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
) -> FrequencyStateScores:
    return FrequencyStateScores(
        clinical_headline=_score_frequency_state_component(
            gold_letters,
            pred_letters,
            "clinical_headline",
        ),
        active_rate=_score_frequency_state_component(gold_letters, pred_letters, "active-rate"),
        active_rate_fidelity=_score_frequency_active_rate_fidelity(gold_letters, pred_letters),
        seizure_free=_score_frequency_state_component(gold_letters, pred_letters, "seizure-free"),
        unknown=_score_frequency_state_component(gold_letters, pred_letters, "unknown"),
        exact_semantic=score_entity(
            gold_letters,
            pred_letters,
            "SeizureFrequency",
            semantic_config_for("SeizureFrequency"),
        ).per_item,
        benchmark_with_cui=score_entity(
            gold_letters,
            pred_letters,
            "SeizureFrequency",
            benchmark_config_for("SeizureFrequency"),
        ).per_item,
    )


def _score_frequency_state_component(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
    component: str,
) -> PRF1:
    gold_by_id = _letters_by_id(gold_letters)
    pred_by_id = _letters_by_id(pred_letters)
    all_ids = sorted(gold_by_id.keys() | pred_by_id.keys())
    return sum_prf1(
        multiset_prf1(
            _frequency_state_keys(
                gold_by_id[letter_id].entities("SeizureFrequency")
                if letter_id in gold_by_id
                else (),
                component,
            ),
            _frequency_state_keys(
                pred_by_id[letter_id].entities("SeizureFrequency")
                if letter_id in pred_by_id
                else (),
                component,
            ),
        )
        for letter_id in all_ids
    )


def _frequency_state_keys(
    annotations: Iterable[ExectAnnotation],
    component: str,
) -> list[Hashable]:
    keys: list[Hashable] = []
    for annotation in annotations:
        state = _frequency_state(annotation.attributes)
        if component != "clinical_headline" and component != state:
            continue
        keys.append((_frequency_type_key(annotation), state))
    return list(dict.fromkeys(keys))


def _score_frequency_active_rate_fidelity(
    gold_letters: Sequence[ExectLetter],
    pred_letters: Sequence[ExectLetter],
) -> PRF1:
    """Among active-rate states, does the seizure-burden magnitude agree?

    The ``clinical_headline`` key collapses every active rate to the single token
    ``active-rate``, so "2-4 per month" and "6-9 per week" score as the same key.
    This companion keys the rate-bearing attributes (counts + cadence, excluding
    dates) per seizure type, so a wrong rate among matched active states is no
    longer silently forgiven.
    """

    gold_by_id = _letters_by_id(gold_letters)
    pred_by_id = _letters_by_id(pred_letters)
    all_ids = sorted(gold_by_id.keys() | pred_by_id.keys())
    return sum_prf1(
        multiset_prf1(
            _frequency_active_rate_keys(
                gold_by_id[letter_id].entities("SeizureFrequency")
                if letter_id in gold_by_id
                else (),
            ),
            _frequency_active_rate_keys(
                pred_by_id[letter_id].entities("SeizureFrequency")
                if letter_id in pred_by_id
                else (),
            ),
        )
        for letter_id in all_ids
    )


def _frequency_active_rate_keys(annotations: Iterable[ExectAnnotation]) -> list[Hashable]:
    keys: list[Hashable] = []
    for annotation in annotations:
        if _frequency_state(annotation.attributes) != "active-rate":
            continue
        rate = tuple(
            sorted(
                (key, canonicalize_attribute_value(key, value))
                for key, value in annotation.attributes.items()
                if key in _FREQUENCY_RATE_ATTRIBUTES and value
            )
        )
        keys.append((_frequency_type_key(annotation), rate))
    return list(dict.fromkeys(keys))


def _frequency_type_key(annotation: ExectAnnotation) -> Hashable:
    cui = annotation.attributes.get("CUI")
    if cui:
        return ("cui", canonicalize_attribute_value("CUI", cui))
    return ("phrase", normalize_phrase(annotation.text))


def _frequency_state(attributes: Mapping[str, str]) -> str:
    count_values = [
        attributes.get("NumberOfSeizures"),
        attributes.get("LowerNumberOfSeizures"),
        attributes.get("UpperNumberOfSeizures"),
    ]
    if any(value == "0" for value in count_values if value is not None):
        return "seizure-free"
    if any(value for value in count_values):
        return "active-rate"
    return "unknown"
