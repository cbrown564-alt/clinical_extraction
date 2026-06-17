"""Tests for the ExECTv2 extraction contract (prediction schema, adapter, validation)."""
from __future__ import annotations

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    DIAGNOSIS,
    ENTITY_REGISTRY,
    PATIENT_HISTORY,
    SEIZURE_FREQUENCY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.evaluation import (
    ENTITY_EVALUATION_POLICIES,
    benchmark_ignore_attributes_for,
    preserves_distinct_occurrences,
    semantic_ignore_attributes_for,
    uses_cuiphrase_as_gold_text,
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
    SEIZURE_FREQUENCY as SF_ENTITY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    load_letters,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import score_entity

# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


def test_registry_has_nine_entities():
    assert len(ENTITY_REGISTRY) == 9


def test_all_nine_entity_names_present():
    expected = {
        "BirthHistory", "Diagnosis", "EpilepsyCause", "Investigations",
        "Onset", "PatientHistory", "Prescription", "SeizureFrequency", "WhenDiagnosed",
    }
    assert set(ENTITY_REGISTRY.keys()) == expected


def test_seizure_frequency_spec_has_closed_vocab():
    assert "TimeSince_or_TimeOfEvent" in SEIZURE_FREQUENCY.closed_vocab
    assert SEIZURE_FREQUENCY.closed_vocab["TimeSince_or_TimeOfEvent"] == frozenset(
        {"During", "Since"}
    )
    assert "FrequencyChange" in SEIZURE_FREQUENCY.closed_vocab


def test_evaluation_policy_covers_entity_registry():
    assert set(ENTITY_EVALUATION_POLICIES) == set(ENTITY_REGISTRY)


def test_gold_phrase_target_policy_is_entity_specific():
    assert uses_cuiphrase_as_gold_text(SEIZURE_FREQUENCY.name)
    assert uses_cuiphrase_as_gold_text(DIAGNOSIS.name)
    assert not uses_cuiphrase_as_gold_text(PATIENT_HISTORY.name)


def test_scoring_ignore_policy_keeps_sf_guideline_exception_centralized():
    assert benchmark_ignore_attributes_for(SEIZURE_FREQUENCY.name) == frozenset({
        "CUIPhrase",
        "Certainty",
        "Negation",
    })
    assert semantic_ignore_attributes_for(DIAGNOSIS.name) == frozenset({"CUIPhrase", "CUI"})


def test_occurrence_policy_is_patient_history_only():
    assert preserves_distinct_occurrences(PATIENT_HISTORY.name)
    assert not preserves_distinct_occurrences(DIAGNOSIS.name)


# ---------------------------------------------------------------------------
# Registry ⟷ gold drift guard
#
# Derives the schema live from load_letters() and asserts the registry stays in
# lockstep with the gold corpus: entity set and attribute set must match
# *exactly* (no spurious or missing entries), while closed-vocab values need
# only *cover* gold — physical-unit/binary/scale attributes are deliberately
# widened past observed gold (see entities.py).  This is the automated form of
# exit criterion 3 ("registry matches the committed gold profile exactly").
# ---------------------------------------------------------------------------


def _gold_schema() -> dict[str, dict[str, set[str]]]:
    from collections import defaultdict

    schema: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for letter in load_letters():
        for ann in letter.annotations:
            for key, value in ann.attributes.items():
                schema[ann.entity][key].add(value)
    return schema


def test_registry_entity_set_matches_gold_exactly():
    assert set(_gold_schema()) == set(ENTITY_REGISTRY)


def test_registry_attribute_set_matches_gold_exactly():
    schema = _gold_schema()
    for name, spec in ENTITY_REGISTRY.items():
        observed = set(schema[name])
        # legal attributes must be exactly the gold-observed keys minus documented noise
        assert observed - spec.noise_attributes == spec.legal_attributes, (
            f"{name}: gold(non-noise)={sorted(observed - spec.noise_attributes)} "
            f"!= legal={sorted(spec.legal_attributes)}"
        )
        # every declared noise attribute must actually occur in gold
        assert spec.noise_attributes <= observed, (
            f"{name}: declared noise {sorted(spec.noise_attributes - observed)} absent from gold"
        )


def test_registry_closed_vocab_covers_gold_values():
    schema = _gold_schema()
    for name, spec in ENTITY_REGISTRY.items():
        for attr, vocab in spec.closed_vocab.items():
            assert attr in spec.legal_attributes, f"{name}.{attr} is closed-vocab but not legal"
            observed = schema[name].get(attr, set())
            assert observed <= vocab, (
                f"{name}.{attr}: gold values {sorted(observed - vocab)} not in "
                f"vocab {sorted(vocab)}"
            )


# ---------------------------------------------------------------------------
# Adapter: PredictedLetter → ExectLetter
# ---------------------------------------------------------------------------


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


def test_adapter_drops_transparency_fields():
    mention = PredictedMention(
        entity=SF_ENTITY,
        text="two-seizures",
        attributes={"NumberOfSeizures": "2"},
        evidence="two seizures",
        rationale="test",
        confidence="high",
        uncertainty_flags=("low_context",),
        component_owner="rules",
    )
    letter = PredictedLetter(letter_id="X1", mentions=(mention,), diagnostics={"k": "v"})
    exect = to_exect_letter(letter, note_text="two seizures per week")

    assert exect.letter_id == "X1"
    assert len(exect.annotations) == 1
    ann = exect.annotations[0]
    assert ann.entity == SF_ENTITY
    assert ann.text == "two-seizures"
    assert ann.attributes == {"NumberOfSeizures": "2"}
    # no transparency fields on ExectAnnotation
    assert not hasattr(ann, "rationale")
    assert not hasattr(ann, "confidence")


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------


def test_gold_as_predictions_validates_clean():
    """Gold mentions converted to PredictedLetters must pass schema validation."""
    letters = load_letters()
    errors = []
    for letter in letters:
        pred = _gold_to_predicted_letter(letter)
        result = validate_letter(pred, source_text=letter.note_text)
        errors.extend(
            (letter.letter_id, i.code, i.message)
            for i in result.issues
            if i.severity == "error"
        )
    assert errors == [], f"Unexpected validation errors: {errors[:5]}"


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


def test_illegal_closed_vocab_value_is_error():
    mention = PredictedMention(
        entity=SF_ENTITY,
        text="two-seizures",
        attributes={"TimeSince_or_TimeOfEvent": "INVALID"},
        evidence="two seizures",
    )
    letter = PredictedLetter(letter_id="X1", mentions=(mention,), diagnostics={})
    result = validate_letter(letter)
    assert not result.ok
    assert any(i.code == "illegal_attribute_value" for i in result.issues)


def test_valid_mention_passes():
    mention = PredictedMention(
        entity=SF_ENTITY,
        text="two-seizures",
        attributes={"NumberOfSeizures": "2", "TimePeriod": "Month"},
        evidence="two seizures",
    )
    letter = PredictedLetter(letter_id="X1", mentions=(mention,), diagnostics={})
    result = validate_letter(letter)
    assert result.ok


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


def test_noise_attribute_on_seizure_frequency_passes():
    """DiagCategory on SF is noise — should not trigger an illegal_attribute error."""
    mention = PredictedMention(
        entity=SF_ENTITY,
        text="multiple-seizures",
        attributes={"NumberOfSeizures": "3", "DiagCategory": "MultipleSeizures"},
        evidence="multiple seizures",
    )
    letter = PredictedLetter(letter_id="X1", mentions=(mention,), diagnostics={})
    result = validate_letter(letter)
    assert result.ok


def test_evidence_not_substring_is_warning():
    mention = PredictedMention(
        entity=SF_ENTITY,
        text="two-seizures",
        attributes={"NumberOfSeizures": "2"},
        evidence="completely made up text not in note",
    )
    letter = PredictedLetter(letter_id="X1", mentions=(mention,), diagnostics={})
    result = validate_letter(letter, source_text="patient had two seizures last month")
    assert result.ok
    assert any(i.code == "evidence_not_substring" for i in result.issues)
