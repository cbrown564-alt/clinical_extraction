"""Tests for the recall-additive generate->verify SF GEPA program + state_profile metric."""

from __future__ import annotations

import json

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.metric import LengthPenaltyConfig
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program_sf_verify import (
    GENERATE_SEED,
    VERIFY_SEED,
    build_sf_verify_metric,
    build_sf_verify_program,
    combined_instruction,
    events_to_sf_facts,
)

NOTE = "He still has focal seizures about 2 per month. His tonic-clonic seizures have stopped."


def _gold() -> dspy.Example:
    letter = ExectLetter(
        letter_id="T1",
        note_text=NOTE,
        annotations=(
            ExectAnnotation(
                entity="SeizureFrequency",
                text="focal seizures",
                attributes={"CUI": "C0270834", "LowerNumberOfSeizures": "2", "TimePeriod": "Month"},
            ),
            ExectAnnotation(
                entity="SeizureFrequency",
                text="tonic-clonic seizures",
                attributes={"CUI": "C0494475", "NumberOfSeizures": "0"},
            ),
        ),
    )
    return dspy.Example(letter_text=NOTE, letter=letter)


def _pred(facts: list[dict]) -> dspy.Prediction:
    return dspy.Prediction(clinical_facts_json=json.dumps({"clinical_facts": facts}))


def test_events_to_sf_facts_maps_kinds_to_states() -> None:
    raw = json.dumps(
        {
            "events": [
                {"applies_to": "focal seizures", "kind": "frequency_rate", "evidence": "x"},
                {"applies_to": "gtc", "kind": "seizure_free", "evidence": "y"},
                {"applies_to": "absence", "kind": "changed", "change_direction": "decreased", "evidence": "z"},
            ]
        }
    )
    facts = events_to_sf_facts(raw)
    assert [f["state"] for f in facts] == ["active_rate", "seizure_free", "changed"]
    assert all(f["family"] == "seizure_frequency" for f in facts)


def test_verify_seed_is_recall_additive_not_a_filter() -> None:
    # The whole point of P2: the verify stage ADDS missing facts (the prior multistage
    # verify only filtered and cut recall).
    assert "add" in VERIFY_SEED.lower()
    assert "recall-additive" in VERIFY_SEED.lower()
    combined = combined_instruction(build_sf_verify_program())
    assert "=== generate ===" in combined and "=== verify ===" in combined
    assert GENERATE_SEED.split(".")[0] in combined


def test_metric_perfect_sf_scores_high_on_state_profile() -> None:
    metric = build_sf_verify_metric(LengthPenaltyConfig(enabled=False))
    out = metric(
        _gold(),
        _pred(
            [
                {"family": "seizure_frequency", "seizure_type": "focal seizures", "state": "active_rate", "evidence": "focal seizures"},
                {"family": "seizure_frequency", "seizure_type": "tonic-clonic seizures", "state": "seizure_free", "evidence": "tonic-clonic seizures"},
            ]
        ),
    )
    # state_profile is type-agnostic: both states present -> full credit even if CUIs differ.
    assert out.score >= 0.999
    assert "CORRECT" in out.feedback


def test_metric_missing_state_feedback_tells_reflection_to_add() -> None:
    metric = build_sf_verify_metric(LengthPenaltyConfig(enabled=False))
    out = metric(
        _gold(),
        _pred(
            [
                {"family": "seizure_frequency", "seizure_type": "focal seizures", "state": "active_rate", "evidence": "focal seizures"}
            ]
        ),
    )
    assert out.score < 0.999
    # Phase 5 per-(type, state) feedback: a residual MISSED list plus the per-type breakdown.
    assert "MISSED states to ADD" in out.feedback
    assert "seizure-free" in out.feedback
    assert "by seizure type" in out.feedback


def test_metric_feedback_flags_per_type_multiplicity() -> None:
    # Gold tags focal seizures with BOTH active-rate and changed; pred emits only the rate.
    # Phase 5 Category A: the feedback must name the type and tell the model to emit BOTH.
    metric = build_sf_verify_metric(LengthPenaltyConfig(enabled=False))
    gold_letter = ExectLetter(
        letter_id="T2",
        note_text="focal seizures 2 per month, now increased.",
        annotations=(
            ExectAnnotation(
                entity="SeizureFrequency",
                text="focal seizures",
                attributes={"CUI": "C0270834", "LowerNumberOfSeizures": "2", "TimePeriod": "Month"},
            ),
            ExectAnnotation(
                entity="SeizureFrequency",
                text="focal seizures",
                attributes={"CUI": "C0270834", "FrequencyChange": "Increased"},
            ),
        ),
    )
    out = metric(
        dspy.Example(letter=gold_letter),
        _pred(
            [
                {"family": "seizure_frequency", "seizure_type": "focal seizures", "state": "active_rate", "evidence": "focal seizures 2 per month"}
            ]
        ),
    )
    assert "PER-TYPE MULTIPLICITY" in out.feedback
    assert "changed" in out.feedback


def test_metric_feedback_flags_non_epileptic_over_emission() -> None:
    # Gold has no SF and NO epilepsy Dx (dissociative only); pred emits SF -> Category B "absent".
    metric = build_sf_verify_metric(LengthPenaltyConfig(enabled=False))
    gold_letter = ExectLetter(
        letter_id="T3",
        note_text="She reports episodes around twice a week of an unusual thought.",
        annotations=(
            ExectAnnotation(
                entity="Diagnosis",
                text="dissociative seizures",
                attributes={"Certainty": "3", "Negation": "Affirmed", "DiagCategory": "None"},
            ),
        ),
    )
    out = metric(
        dspy.Example(letter=gold_letter),
        _pred(
            [
                {"family": "seizure_frequency", "seizure_type": "episodes", "state": "active_rate", "evidence": "episodes around twice a week"}
            ]
        ),
    )
    assert "OVER-EMISSION" in out.feedback
    assert "no epilepsy diagnosis" in out.feedback.lower()


def test_metric_feedback_flags_uncertain_diagnosis_over_emission() -> None:
    # Gold has no SF but an epilepsy Dx that is only PROBABLE (Certainty 4) -> Category B "uncertain".
    # The reason must NOT claim "no confirmed diagnosis" (the smoke contradiction); it names non-definiteness.
    metric = build_sf_verify_metric(LengthPenaltyConfig(enabled=False))
    gold_letter = ExectLetter(
        letter_id="T4",
        note_text="Probable focal epilepsy, ?left temporal lobe. He reports events most weeks.",
        annotations=(
            ExectAnnotation(
                entity="Diagnosis",
                text="focal epilepsy",
                attributes={"Certainty": "4", "Negation": "Affirmed", "DiagCategory": "Epilepsy"},
            ),
        ),
    )
    out = metric(
        dspy.Example(letter=gold_letter),
        _pred(
            [
                {"family": "seizure_frequency", "seizure_type": "events", "state": "active_rate", "evidence": "events most weeks"}
            ]
        ),
    )
    assert "OVER-EMISSION" in out.feedback
    assert "not definite" in out.feedback.lower()


def test_metric_unscorable_output_scores_zero() -> None:
    metric = build_sf_verify_metric(LengthPenaltyConfig(enabled=False))
    out = metric(_gold(), dspy.Prediction(clinical_facts_json="not json"))
    assert out.score == 0.0
    assert "NOT SCORABLE" in out.feedback
