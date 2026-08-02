"""Tests for the ExECTv2 extraction contract (prediction schema, adapter, validation)."""

from __future__ import annotations

from collections import defaultdict

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ENTITY_REGISTRY,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.validate import (
    validate_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    load_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import score_entity

SF_ENTITY = SEIZURE_FREQUENCY.name


def _gold_schema() -> dict[str, dict[str, set[str]]]:
    schema: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for letter in load_letters():
        for ann in letter.annotations:
            for key, value in ann.attributes.items():
                schema[ann.entity][key].add(value)
    return schema


def test_registry_has_nine_entities():
    expected = {
        "BirthHistory",
        "Diagnosis",
        "EpilepsyCause",
        "Investigations",
        "Onset",
        "PatientHistory",
        "Prescription",
        "SeizureFrequency",
        "WhenDiagnosed",
    }
    assert len(ENTITY_REGISTRY) == 9
    assert set(ENTITY_REGISTRY.keys()) == expected


def test_registry_attribute_and_vocab_match_gold():
    schema = _gold_schema()
    assert set(schema) == set(ENTITY_REGISTRY)
    for name, spec in ENTITY_REGISTRY.items():
        observed = set(schema[name])
        assert observed - spec.noise_attributes == spec.legal_attributes, (
            f"{name}: gold(non-noise)={sorted(observed - spec.noise_attributes)} "
            f"!= legal={sorted(spec.legal_attributes)}"
        )
        assert spec.noise_attributes <= observed, (
            f"{name}: declared noise {sorted(spec.noise_attributes - observed)} absent from gold"
        )
        for attr, vocab in spec.closed_vocab.items():
            assert attr in spec.legal_attributes, f"{name}.{attr} is closed-vocab but not legal"
            observed_values = schema[name].get(attr, set())
            assert observed_values <= vocab, (
                f"{name}.{attr}: gold values {sorted(observed_values - vocab)} not in "
                f"vocab {sorted(vocab)}"
            )


def _predicted_mention(ann: ExectAnnotation) -> PredictedMention:
    return PredictedMention(
        entity=ann.entity,
        text=ann.text,
        attributes=dict(ann.attributes),
        evidence=ann.text.replace("-", " "),
        rationale="gold stub",
        component_owner="gold",
    )


def _gold_to_predicted_letter(letter) -> PredictedLetter:
    return PredictedLetter(
        letter_id=letter.letter_id,
        mentions=tuple(_predicted_mention(a) for a in letter.annotations),
        diagnostics={},
    )


def test_gold_as_predicted_letter_scores_perfect():
    letters = load_letters()
    predicted = [_gold_to_predicted_letter(letter) for letter in letters]
    adapted = [
        to_exect_letter(predicted_letter, letter.note_text)
        for predicted_letter, letter in zip(predicted, letters, strict=True)
    ]

    score = score_entity(letters, adapted, SF_ENTITY)
    assert score.per_item.f1 == 1.0
    assert score.per_letter.f1 == 1.0
    assert score.per_item.tp == 263
    assert score.per_letter.tp == 142


def test_unknown_entity_is_error():
    mention = PredictedMention(
        entity="Bogus",
        text="something",
        attributes={},
        evidence="something",
    )
    letter = PredictedLetter(letter_id="X1", mentions=(mention,), diagnostics={})
    result = validate_letter(letter)
    assert not result.ok
    assert any(i.code == "unknown_entity" for i in result.issues)


def test_illegal_attribute_is_error():
    mention = PredictedMention(
        entity=SF_ENTITY,
        text="two-seizures",
        attributes={"NumberOfSeizures": "2", "NotARealAttr": "oops"},
        evidence="two seizures",
    )
    letter = PredictedLetter(letter_id="X1", mentions=(mention,), diagnostics={})
    result = validate_letter(letter)
    assert not result.ok
    assert any(i.code == "illegal_attribute" for i in result.issues)


def test_missing_evidence_is_warning_not_error():
    mention = PredictedMention(
        entity=SF_ENTITY,
        text="two-seizures",
        attributes={"NumberOfSeizures": "2"},
        evidence="",
    )
    letter = PredictedLetter(letter_id="X1", mentions=(mention,), diagnostics={})
    result = validate_letter(letter)
    assert result.ok
    assert any(i.code == "missing_evidence" and i.severity == "warning" for i in result.issues)
