"""Recall-oriented per-family GEPA program for ExECTv2 de-dup facts.

Follow-up to the GEPA-vs-hybrid evidence decomposition
(``docs/research/exectv2_gepa_vs_hybrid_evidence_decomposition_2026-06-28.md``): the
GEPA->hybrid gap is producer evidence-RETRIEVAL (ev-recall 0.694 vs 0.883), not the
deterministic stack. The per-family program already splits into four lanes
(``program_multifamily.py``) but evolved under an F1 objective into a *parsimonious*
optimum — each lane drafts the single most-specific fact, not the exhaustive set gold
rewards.

This program reuses the same four-lane merge machinery but **reseeds the two gap lanes
(Diagnosis, SeizureFrequency) with recall-oriented instructions** so GEPA evolves from an
exhaustive prior instead of a consolidating one:

* Diagnosis — emit every co-present distinct concept (generic condition + specific
  syndrome + each named seizure type; expand combined diagnoses), the
  exhaustive-multi-concept convention the decomposition pinned as Dx's genuine-miss class.
* SeizureFrequency — one fact per (seizure type x distinct frequency statement) with an
  explicit ``changed`` class, the P3 Gan structured-event content
  (``experiments/exectv2_sf_gan_representation.py``, validated change-recall 0.15->0.52)
  ported into the ``clinical_facts`` framing (no output-format change — ``state`` already
  accepts ``changed``).

Prescription and Investigation lanes are unchanged (already ~0.88/0.86, near the hybrid's
0.94/0.91). The merge / parser / adapter / scorers are reused exactly as in
``program_multifamily``; only two seed instructions differ.
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
    InvestigationFactsSignature,
    PrescriptionFactsSignature,
    _facts_of,
)


class DiagnosisRecallSignature(dspy.Signature):
    """You read one clinical letter and list its diagnosis facts EXHAUSTIVELY.

    List EVERY distinct diagnosis or syndrome concept the letter supports, not only the
    single most specific one. When several co-present concepts are stated, emit each as
    its own fact: the generic condition stated in its own right (e.g. 'epilepsy'), the
    specific syndrome (e.g. 'temporal lobe epilepsy'), and each named seizure type (e.g.
    'focal seizures', 'tonic-clonic seizures'). Expand a combined or hyphenated diagnosis
    into its distinct parts (e.g. 'focal epilepsy - probable temporal' -> 'focal epilepsy'
    AND 'temporal lobe epilepsy'). Include comorbid neurological or psychiatric
    conditions. Use negation=affirmed, or negated if the diagnosis is explicitly excluded
    (a negated diagnosis is still a fact). Do not invent concepts the letter does not
    state. Ground each by an exact substring of the letter as evidence. Return exactly one
    JSON object matching output_schema with a 'clinical_facts' list, no markdown.
    """

    letter_text: str = dspy.InputField(desc="One clinical letter.")
    output_schema: str = dspy.InputField(desc="Required JSON schema. Match it exactly.")
    clinical_facts_json: str = dspy.OutputField(
        desc="One JSON object with a 'clinical_facts' list of diagnosis facts. No markdown."
    )


class SeizureFrequencyRecallSignature(dspy.Signature):
    """You read one clinical letter and list its seizure-frequency facts EXHAUSTIVELY.

    Emit one fact per (seizure type x distinct frequency statement). List the SAME seizure
    type more than once when the letter gives it more than one distinct statement — e.g. a
    current numeric rate AND a separately-reported change. For each fact give the seizure
    type (the named type, or 'seizures' if generic) and a state:
    - active_rate: an explicit count, rate, or cluster cadence (e.g. '2-3 per month', 'weekly').
    - seizure_free: seizures have stopped / none / a seizure-free period (e.g. 'no seizures
      since March', 'seizure-free for 6 months').
    - changed: a reported increase, decrease, improvement, or worsening WITHOUT a usable
      number (e.g. 'seizures more frequent', 'improved') — a DISTINCT fact, do not fold it
      into an active rate.
    - unknown: a seizure type mentioned with no usable frequency.
    Do not default every mention to active_rate, and do not enumerate individual dated
    events. Ground each by an exact substring of the letter as evidence. Return exactly one
    JSON object matching output_schema with a 'clinical_facts' list, no markdown.
    """

    letter_text: str = dspy.InputField(desc="One clinical letter.")
    output_schema: str = dspy.InputField(desc="Required JSON schema. Match it exactly.")
    clinical_facts_json: str = dspy.OutputField(
        desc="One JSON object with a 'clinical_facts' list of seizure_frequency facts. No markdown."
    )


#: Predictor attribute name -> (signature, family-specific schema). Order = emission order.
_RECALL_PREDICTORS: tuple[tuple[str, type[dspy.Signature], str], ...] = (
    ("diagnosis", DiagnosisRecallSignature, DIAGNOSIS_SCHEMA_JSON),
    ("seizure_frequency", SeizureFrequencyRecallSignature, SEIZURE_FREQUENCY_SCHEMA_JSON),
    ("prescription", PrescriptionFactsSignature, PRESCRIPTION_SCHEMA_JSON),
    ("investigation", InvestigationFactsSignature, INVESTIGATION_SCHEMA_JSON),
)


class GepaRecallLanesExtractor(dspy.Module):
    """Four per-family predictors with recall-oriented Dx/SF seeds; each evolved by GEPA."""

    def __init__(self) -> None:
        super().__init__()
        for name, signature, _schema in _RECALL_PREDICTORS:
            setattr(self, name, dspy.Predict(signature))

    def _predictors(self) -> list[dspy.Predict]:
        return [getattr(self, name) for name, _sig, _schema in _RECALL_PREDICTORS]

    def forward(self, letter_text: str, output_schema: str | None = None) -> dspy.Prediction:
        merged: list[dict] = []
        for name, _signature, schema in _RECALL_PREDICTORS:
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
            approx_tokens(str(dict(demo))) for p in self._predictors() for demo in (p.demos or [])
        )
        return prediction


def build_recall_lanes_program() -> GepaRecallLanesExtractor:
    """Per-family program seeded with recall-oriented Diagnosis + SeizureFrequency lanes."""

    return GepaRecallLanesExtractor()


def combined_instruction(program: GepaRecallLanesExtractor) -> str:
    """All four evolved per-family instructions, for the instruction artifact + tokens."""

    blocks = []
    for name, _signature, _schema in _RECALL_PREDICTORS:
        instructions = getattr(program, name).signature.instructions
        blocks.append(f"=== {name} ===\n{instructions}")
    return "\n\n".join(blocks)
