"""Tests for the ExECTv2 GEPA length-penalized clinical_headline feedback metric."""

from __future__ import annotations

import inspect
import json

import dspy
import pytest

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.metric import (
    LengthPenaltyConfig,
    build_metric,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program import (
    OUTPUT_SCHEMA_JSON,
    GepaDedupFactsSignature,
)

NOTE = "He has epilepsy with seizures."


def _gold_letter() -> ExectLetter:
    return ExectLetter(
        letter_id="T0001",
        note_text=NOTE,
        annotations=(
            ExectAnnotation(
                entity="Diagnosis",
                text="epilepsy",
                attributes={"Negation": "Affirmed", "CUI": "C0014544"},
            ),
            # Real gold SeizureFrequency annotations carry a CUI; the projector also
            # stamps one onto predictions, so the clinical_headline key uses it.
            ExectAnnotation(
                entity="SeizureFrequency",
                text="seizures",
                attributes={"NumberOfSeizures": "1", "CUI": "C0036572"},
            ),
        ),
    )


def _gold() -> dspy.Example:
    return dspy.Example(
        letter_text=NOTE,
        output_schema=OUTPUT_SCHEMA_JSON,
        letter_id="T0001",
        letter=_gold_letter(),
    )


def _pred(facts: list[dict] | str) -> dspy.Prediction:
    payload = facts if isinstance(facts, str) else json.dumps({"clinical_facts": facts})
    return dspy.Prediction(clinical_facts_json=payload)


def _correct_pred() -> dspy.Prediction:
    return _pred(
        [
            {
                "family": "diagnosis",
                "concept": "epilepsy",
                "negation": "affirmed",
                "evidence": "epilepsy",
            },
            {
                "family": "seizure_frequency",
                "seizure_type": "seizures",
                "state": "active_rate",
                "evidence": "seizures",
            },
        ]
    )


def _pred_trace_with_instruction(instruction: str):
    predictor = dspy.Predict(GepaDedupFactsSignature)
    predictor.signature = predictor.signature.with_instructions(instruction)
    return [(predictor, {}, {})]


def test_gepa_signature_instructions_preserve_the_frozen_prompt_text() -> None:
    assert inspect.cleandoc(GepaDedupFactsSignature.__doc__ or "") == (
        "You read one clinical letter and list its de-duplicated clinical facts in four "
        "families: diagnosis, seizure_frequency, prescription, and investigation.\n\n"
        "Emit each distinct clinical fact once, grounded by an exact substring of the\n"
        "letter as evidence; do not repeat a diagnosis, seizure-type state, drug\n"
        "regimen, or investigation you have already listed. Return exactly one JSON\n"
        "object matching output_schema, with a 'clinical_facts' list and no markdown or\n"
        "commentary outside the JSON."
    )


def test_correct_scores_high():
    metric = build_metric(LengthPenaltyConfig(enabled=False))
    out = metric(_gold(), _correct_pred())
    assert out.score == pytest.approx(1.0)
    assert "CORRECT" in out.feedback


def test_quality_ordered_correct_partial_unscorable():
    metric = build_metric(LengthPenaltyConfig(enabled=False))
    gold = _gold()
    correct = metric(gold, _correct_pred()).score
    partial = metric(
        gold,
        _pred(
            [
                {
                    "family": "diagnosis",
                    "concept": "epilepsy",
                    "negation": "affirmed",
                    "evidence": "epilepsy",
                }
            ]
        ),
    ).score
    unscorable_out = metric(gold, _pred("not json"))
    assert correct > partial > 0.0
    assert unscorable_out.score == 0.0
    assert "OUTPUT NOT SCORABLE" in unscorable_out.feedback


def test_stamped_instruction_tokens_penalize_in_selection_path():
    metric = build_metric(LengthPenaltyConfig())
    gold = _gold()
    lean = _correct_pred()
    lean.instruction_tokens = 300  # under the 600 budget
    lean.demo_tokens = 0
    bloated = _correct_pred()
    bloated.instruction_tokens = 3000  # far over budget
    bloated.demo_tokens = 0
    assert metric(gold, lean).score == pytest.approx(1.0)
    assert metric(gold, bloated).score < metric(gold, lean).score
    assert "TOO LONG" in metric(gold, bloated).feedback


def test_length_penalty_lowers_score_monotonically():
    metric = build_metric(LengthPenaltyConfig())
    gold = _gold()
    pred = _correct_pred()
    short = metric(gold, pred, None, "extract", _pred_trace_with_instruction("Be concise.")).score
    longer = metric(gold, pred, None, "extract", _pred_trace_with_instruction("word " * 4000)).score
    assert short == pytest.approx(1.0)
    assert longer < short
    assert longer >= 1.0 - LengthPenaltyConfig().max_penalty - 1e-9


def test_disabled_penalty_ignores_instruction_length():
    metric = build_metric(LengthPenaltyConfig(enabled=False))
    out = metric(
        _gold(), _correct_pred(), None, "extract", _pred_trace_with_instruction("word " * 4000)
    )
    assert out.score == pytest.approx(1.0)


def test_feedback_diff_shows_missed_gold():
    metric = build_metric(LengthPenaltyConfig(enabled=False))
    # Diagnosis correct, SeizureFrequency omitted -> diff must name the missed SF gold.
    out = metric(
        _gold(),
        _pred(
            [
                {
                    "family": "diagnosis",
                    "concept": "epilepsy",
                    "negation": "affirmed",
                    "evidence": "epilepsy",
                }
            ]
        ),
    )
    assert "DIFF" in out.feedback
    assert "MISSED gold" in out.feedback
    assert "SeizureFrequency" in out.feedback


def test_feedback_diff_shows_spurious_pred():
    metric = build_metric(LengthPenaltyConfig(enabled=False))
    # Correct SF, but a spurious diagnosis the gold does not contain.
    out = metric(
        _gold(),
        _pred(
            [
                {
                    "family": "seizure_frequency",
                    "seizure_type": "seizures",
                    "state": "active_rate",
                    "evidence": "seizures",
                },
                {
                    "family": "diagnosis",
                    "concept": "migraine",
                    "negation": "affirmed",
                    "evidence": "epilepsy",
                },
            ]
        ),
    )
    assert "WRONG you emitted" in out.feedback
    assert "migraine" in out.feedback
    # And the missed real diagnosis (epilepsy) should be flagged too.
    assert "MISSED gold" in out.feedback


def test_feedback_warns_on_bare_unknown_seizure_frequency_drop():
    metric = build_metric(LengthPenaltyConfig(enabled=False))
    # A bare 'unknown' SF state maps to no attributes and is dropped by the render
    # gate before scoring; the feedback must tell reflection to emit a concrete state.
    out = metric(
        _gold(),
        _pred(
            [
                {
                    "family": "diagnosis",
                    "concept": "epilepsy",
                    "negation": "affirmed",
                    "evidence": "epilepsy",
                },
                {
                    "family": "seizure_frequency",
                    "seizure_type": "seizures",
                    "state": "unknown",
                    "evidence": "seizures",
                },
            ]
        ),
    )
    assert "concrete state" in out.feedback
    assert "bare 'unknown' state" in out.feedback


def test_seizure_frequency_feedback_names_state_class_and_guides():
    metric = build_metric(LengthPenaltyConfig(enabled=False))
    # SF omitted -> the diff must render the missed fact by its change-aware STATE class
    # (the actionable signal), not the old opaque raw-attribute bracket, and the
    # targeted SF state-classification guidance must fire.
    out = metric(
        _gold(),
        _pred(
            [
                {
                    "family": "diagnosis",
                    "concept": "epilepsy",
                    "negation": "affirmed",
                    "evidence": "epilepsy",
                }
            ]
        ),
    )
    assert "seizures: active-rate" in out.feedback
    assert "[NumberOfSeizures" not in out.feedback  # old opaque rendering is gone
    assert "distinct 'changed' fact" in out.feedback


def test_correct_prediction_has_no_diff():
    metric = build_metric(LengthPenaltyConfig(enabled=False))
    out = metric(_gold(), _correct_pred())
    assert "DIFF" not in out.feedback
    assert "MISSED gold" not in out.feedback


# --- Phase 2 (docs/plans/exectv2_exploratory_directions_implementation_plan_2026-07-01.md):
# stage-local verify feedback, independent of the shared end-to-end score. ---

_MIGRAINE = {
    "family": "diagnosis",
    "concept": "migraine",
    "negation": "affirmed",
    "evidence": "epilepsy",
}
_EPILEPSY = {
    "family": "diagnosis",
    "concept": "epilepsy",
    "negation": "affirmed",
    "evidence": "epilepsy",
}


def _verify_pred_trace(draft_facts: list[dict], verified_facts: list[dict]):
    inputs = {"draft_facts_json": json.dumps({"clinical_facts": draft_facts})}
    outputs = dspy.Prediction(verified_facts_json=json.dumps({"clinical_facts": verified_facts}))
    return [(None, inputs, outputs)]


def test_verify_stage_feedback_replaces_whole_program_diff():
    metric = build_metric(LengthPenaltyConfig(enabled=False))
    out = metric(
        _gold(),
        _correct_pred(),
        None,
        "verify_diagnosis",
        _verify_pred_trace([_EPILEPSY, _MIGRAINE], [_EPILEPSY]),
    )
    assert "VERIFY STAGE (Diagnosis)" in out.feedback
    assert "DIFF —" not in out.feedback  # the whole-program diff text is gone


def test_verify_stage_feedback_credits_correct_keep_and_reject():
    metric = build_metric(LengthPenaltyConfig(enabled=False))
    out = metric(
        _gold(),
        _correct_pred(),
        None,
        "verify_diagnosis",
        _verify_pred_trace([_EPILEPSY, _MIGRAINE], [_EPILEPSY]),
    )
    assert "correctly kept 1/1" in out.feedback
    assert "correctly rejected 1/1" in out.feedback
    assert "WRONGLY" not in out.feedback


def test_verify_stage_feedback_flags_wrong_reject():
    metric = build_metric(LengthPenaltyConfig(enabled=False))
    # Verify drops BOTH drafts, including the one gold actually wants kept.
    out = metric(
        _gold(), _correct_pred(), None, "verify_diagnosis", _verify_pred_trace([_EPILEPSY], [])
    )
    assert "WRONGLY DROPPED 1" in out.feedback
    assert "epilepsy" in out.feedback


def test_verify_stage_feedback_flags_wrong_keep():
    metric = build_metric(LengthPenaltyConfig(enabled=False))
    # Verify keeps the spurious draft fact instead of rejecting it.
    out = metric(
        _gold(),
        _correct_pred(),
        None,
        "verify_diagnosis",
        _verify_pred_trace([_EPILEPSY, _MIGRAINE], [_EPILEPSY, _MIGRAINE]),
    )
    assert "WRONGLY KEPT 1" in out.feedback
    assert "migraine" in out.feedback


def test_verify_stage_feedback_credits_correct_add():
    metric = build_metric(LengthPenaltyConfig(enabled=False))
    # Draft missed the gold fact entirely; verify adds it (recall-additive rescue).
    out = metric(
        _gold(), _correct_pred(), None, "verify_diagnosis", _verify_pred_trace([], [_EPILEPSY])
    )
    assert "Correctly ADDED 1" in out.feedback


def test_non_verify_pred_name_keeps_whole_program_feedback():
    metric = build_metric(LengthPenaltyConfig(enabled=False))
    out = metric(
        _gold(),
        _pred([_EPILEPSY]),
        None,
        "generate_diagnosis",
        _verify_pred_trace([_EPILEPSY], [_EPILEPSY]),
    )
    assert "VERIFY STAGE" not in out.feedback
    assert "DIFF" in out.feedback  # SeizureFrequency still missing from the merged pred


def test_verify_stage_feedback_does_not_change_selection_score():
    metric = build_metric(LengthPenaltyConfig(enabled=False))
    trace = _verify_pred_trace([_EPILEPSY, _MIGRAINE], [_EPILEPSY])
    whole_program = metric(_gold(), _correct_pred())
    stage_local = metric(_gold(), _correct_pred(), None, "verify_diagnosis", trace)
    assert whole_program.score == pytest.approx(stage_local.score)
