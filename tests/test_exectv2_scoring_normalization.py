from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectAnnotation
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    PHRASE_AND_FEATURES,
    match_key,
)


def _ann(entity: str, text: str, **attrs: str) -> ExectAnnotation:
    return ExectAnnotation(entity=entity, text=text, attributes=dict(attrs))


def test_match_key_canonicalizes_time_period_case_and_plural_noise() -> None:
    # EA0169's gold value is the schema-format variant "days". This is a
    # format-only repair: the model-selected count and time unit remain intact.
    gold = _ann(SEIZURE_FREQUENCY.name, "seizures", NumberOfSeizures="10", TimePeriod="days")
    prediction = _ann(SEIZURE_FREQUENCY.name, "seizures", NumberOfSeizures="10", TimePeriod="Day")

    assert match_key(gold, PHRASE_AND_FEATURES) == match_key(prediction, PHRASE_AND_FEATURES)
