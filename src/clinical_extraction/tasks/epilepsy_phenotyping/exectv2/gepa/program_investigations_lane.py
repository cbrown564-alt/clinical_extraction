"""Investigations-only recall lane for ExECTv2 de-dup facts (DeepSeek-reasoner task model).

Follow-up to the ev-recall consolidation re-examination, Phase 4
(``docs/experiments/exectv2/exectv2_rx_inv_ev_recall_consolidation_check_2026-06-30.md``):
unlike Diagnosis/SeizureFrequency/Prescription, Investigations' evidence-recall gap is a
clean negative (genuine retrieval miss, H-inflated only 25.9-29.6%, the lowest of any
family) with a SPECIFIC, actionable shape rather than a diffuse "retrieve more" target: of
its 20 genuine ``source_near`` misses, the large majority are an absent EEG in a letter that
ALSO reports an MRI -- the model extracts the MRI and silently drops the EEG entirely
(structural MRI-anchoring bias, not a representation or keying problem).

This program isolates that one fix. It reuses the Diagnosis / SeizureFrequency /
Prescription lanes UNCHANGED (``program_multifamily``'s lean original seeds, so neither
optimization budget nor reflection attention is spent re-litigating families with no
genuine residual there) and reseeds ONLY the Investigation predictor with an explicit
multi-modality-enumeration instruction that names the MRI-anchoring failure mode directly.

Baseline note: the GEPA-best per-family Investigations numbers the Phase 4 adjudication
audited (``exectv2_gepa_multifamily_dedup_gpt41mini_h2mb8_20260628``: headline 0.858,
``source_near`` recall 0.801) are NOT the right bar for this run -- a later, unrelated
DeepSeek-chat model swap (no Investigation-specific instruction change) already lifted
Investigations to headline ~0.92-0.93 / ev-recall ~0.93-0.94
(``exectv2_gepa_baseline_multifamily_deepseekchat_20260628``,
``exectv2_gepa_recall_lanes_deepseekchat_20260628``), at or above the v08 hybrid's 0.913.
This run's question is narrower: does a *targeted* instruction (plus deepseek-reasoner as
the task model, vs the chat baseline) close the remaining gap further -- not whether
DeepSeek alone helps, which is already shown.
"""

from __future__ import annotations

import json

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program import approx_tokens
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program_multifamily import (
    DIAGNOSIS_SCHEMA_JSON,
    INVESTIGATION_SCHEMA_JSON,
    PRESCRIPTION_SCHEMA_JSON,
    SEIZURE_FREQUENCY_SCHEMA_JSON,
    DiagnosisFactsSignature,
    PrescriptionFactsSignature,
    SeizureFrequencyFactsSignature,
    _facts_of,
)


class InvestigationRecallSignature(dspy.Signature):
    """You read one clinical letter and list its investigation facts EXHAUSTIVELY.

    Check independently for EACH of the four modalities: MRI, CT, EEG, and telemetry --
    do not stop after finding one. A letter that reports an MRI very often ALSO reports an
    EEG (or vice versa); these are reported in different parts of the letter and must BOTH
    be extracted. The most common mistake is anchoring on one modality (usually the MRI)
    and silently dropping another (usually the EEG) that is mentioned elsewhere in the same
    letter -- actively guard against this by scanning the whole letter for each modality in
    turn rather than stopping at the first investigation you find. If the letter reports more
    than one instance of the same modality (e.g. two EEGs from different dates, or with
    different results), emit each as its own distinct fact rather than merging or keeping
    only one. Emit each distinct completed-modality instance once with a result: normal,
    abnormal, or unknown. Do not invent a modality the letter does not state. Ground each by
    an exact substring of the letter as evidence. Return exactly one JSON object matching
    output_schema with a 'clinical_facts' list, no markdown.
    """

    letter_text: str = dspy.InputField(desc="One clinical letter.")
    output_schema: str = dspy.InputField(desc="Required JSON schema. Match it exactly.")
    clinical_facts_json: str = dspy.OutputField(
        desc="One JSON object with a 'clinical_facts' list of investigation facts. No markdown."
    )


#: Predictor attribute name -> (signature, family-specific schema). Order = emission order.
#: Diagnosis / SeizureFrequency / Prescription are the UNCHANGED program_multifamily seeds;
#: only Investigation is reseeded and is the intended optimization target.
_INVESTIGATIONS_LANE_PREDICTORS: tuple[tuple[str, type[dspy.Signature], str], ...] = (
    ("diagnosis", DiagnosisFactsSignature, DIAGNOSIS_SCHEMA_JSON),
    ("seizure_frequency", SeizureFrequencyFactsSignature, SEIZURE_FREQUENCY_SCHEMA_JSON),
    ("prescription", PrescriptionFactsSignature, PRESCRIPTION_SCHEMA_JSON),
    ("investigation", InvestigationRecallSignature, INVESTIGATION_SCHEMA_JSON),
)


class GepaInvestigationsLaneExtractor(dspy.Module):
    """Four per-family predictors; only the Investigation seed targets the MRI/EEG gap."""

    def __init__(self) -> None:
        super().__init__()
        for name, signature, _schema in _INVESTIGATIONS_LANE_PREDICTORS:
            setattr(self, name, dspy.Predict(signature))

    def _predictors(self) -> list[dspy.Predict]:
        return [getattr(self, name) for name, _sig, _schema in _INVESTIGATIONS_LANE_PREDICTORS]

    def forward(self, letter_text: str, output_schema: str | None = None) -> dspy.Prediction:
        merged: list[dict] = []
        for name, _signature, schema in _INVESTIGATIONS_LANE_PREDICTORS:
            predictor = getattr(self, name)
            out = predictor(letter_text=letter_text, output_schema=schema)
            merged.extend(_facts_of(str(getattr(out, "clinical_facts_json", "") or "")))

        prediction = dspy.Prediction(
            clinical_facts_json=json.dumps({"clinical_facts": merged}, ensure_ascii=False)
        )
        prediction.instruction_tokens = sum(
            approx_tokens(p.signature.instructions) for p in self._predictors()
        )
        prediction.demo_tokens = sum(
            approx_tokens(str(dict(demo)))
            for p in self._predictors()
            for demo in (p.demos or [])
        )
        return prediction


def build_investigations_lane_program() -> GepaInvestigationsLaneExtractor:
    """Per-family program with only the Investigation seed reset to a recall-oriented one."""

    return GepaInvestigationsLaneExtractor()


def combined_instruction(program: GepaInvestigationsLaneExtractor) -> str:
    """All four evolved per-family instructions, for the instruction artifact + tokens."""

    blocks = []
    for name, _signature, _schema in _INVESTIGATIONS_LANE_PREDICTORS:
        instructions = getattr(program, name).signature.instructions
        blocks.append(f"=== {name} ===\n{instructions}")
    return "\n\n".join(blocks)
