"""GEPA-native multi-signature (per-family) program for ExECTv2 de-dup facts.

Follow-up to the monolith finding: a single evolved instruction plateaued at
~0.63 clinical_headline F1 (below the hand-tuned 0.71 and the v08 hybrid 0.9155),
and the shortfall was concentrated in Diagnosis (~0.45) and SeizureFrequency
(~0.52) — the two families the hybrid closes with dedicated per-family components.

This program gives each family its OWN ``dspy.Predict`` with its OWN evolvable
instruction, so GEPA can grow dedicated per-family scaffolding (the structure the
monolith could not). ``forward`` runs the four predictors and merges their facts
back into one ``clinical_facts_json``, so the metric / adapter / scorers are reused
unchanged. The single optimizable surface is now four instructions instead of one;
the length penalty (config with a larger total budget) reads the summed token count
stamped onto the prediction, so bloat in any one predictor is penalized in selection.
"""

from __future__ import annotations

import json

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.gepa.program import (
    OUTPUT_SCHEMA,
    approx_tokens,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.json_parse import (
    extract_json_object,
)


def _family_schema_json(family: str) -> str:
    fact = next(f for f in OUTPUT_SCHEMA["clinical_facts"] if f["family"] == family)
    return json.dumps({"clinical_facts": [fact]}, ensure_ascii=False, sort_keys=True)


DIAGNOSIS_SCHEMA_JSON = _family_schema_json("diagnosis")
SEIZURE_FREQUENCY_SCHEMA_JSON = _family_schema_json("seizure_frequency")
PRESCRIPTION_SCHEMA_JSON = _family_schema_json("prescription")
INVESTIGATION_SCHEMA_JSON = _family_schema_json("investigation")


class DiagnosisFactsSignature(dspy.Signature):
    """You read one clinical letter and list its distinct diagnosis facts.

    Emit every distinct diagnosis or syndrome concept once (epilepsy type and any
    comorbid conditions), with negation=affirmed, or negated if the diagnosis is
    explicitly excluded (a negated diagnosis is still a fact). Ground each by an
    exact substring of the letter as evidence. Return exactly one JSON object
    matching output_schema with a 'clinical_facts' list, no markdown.
    """

    letter_text: str = dspy.InputField(desc="One clinical letter.")
    output_schema: str = dspy.InputField(desc="Required JSON schema. Match it exactly.")
    clinical_facts_json: str = dspy.OutputField(
        desc="One JSON object with a 'clinical_facts' list of diagnosis facts. No markdown."
    )


class SeizureFrequencyFactsSignature(dspy.Signature):
    """You read one clinical letter and list its seizure-frequency facts.

    Emit one fact per distinct seizure type (use the named type, or 'seizures' if
    generic) with a coarse state: active_rate, seizure_free, changed, or unknown.
    Do not enumerate individual dated events. Ground each by an exact substring of
    the letter as evidence. Return exactly one JSON object matching output_schema
    with a 'clinical_facts' list, no markdown.
    """

    letter_text: str = dspy.InputField(desc="One clinical letter.")
    output_schema: str = dspy.InputField(desc="Required JSON schema. Match it exactly.")
    clinical_facts_json: str = dspy.OutputField(
        desc="One JSON object with a 'clinical_facts' list of seizure_frequency facts. No markdown."
    )


class PrescriptionFactsSignature(dspy.Signature):
    """You read one clinical letter and list its current prescription facts.

    Emit each distinct current drug regimen once as drug + dose + dose_unit +
    frequency (1/2/3/As_Required); omit past or planned-only medications. Ground
    each by an exact substring of the letter as evidence. Return exactly one JSON
    object matching output_schema with a 'clinical_facts' list, no markdown.
    """

    letter_text: str = dspy.InputField(desc="One clinical letter.")
    output_schema: str = dspy.InputField(desc="Required JSON schema. Match it exactly.")
    clinical_facts_json: str = dspy.OutputField(
        desc="One JSON object with a 'clinical_facts' list of prescription facts. No markdown."
    )


class InvestigationFactsSignature(dspy.Signature):
    """You read one clinical letter and list its investigation facts.

    Emit each distinct completed modality once (MRI, CT, EEG, or telemetry) with a
    result: normal, abnormal, or unknown. Ground each by an exact substring of the
    letter as evidence. Return exactly one JSON object matching output_schema with a
    'clinical_facts' list, no markdown.
    """

    letter_text: str = dspy.InputField(desc="One clinical letter.")
    output_schema: str = dspy.InputField(desc="Required JSON schema. Match it exactly.")
    clinical_facts_json: str = dspy.OutputField(
        desc="One JSON object with a 'clinical_facts' list of investigation facts. No markdown."
    )


#: Predictor attribute name -> (signature, family-specific schema). Order is the
#: emission order in the merged output.
_FAMILY_PREDICTORS: tuple[tuple[str, type[dspy.Signature], str], ...] = (
    ("diagnosis", DiagnosisFactsSignature, DIAGNOSIS_SCHEMA_JSON),
    ("seizure_frequency", SeizureFrequencyFactsSignature, SEIZURE_FREQUENCY_SCHEMA_JSON),
    ("prescription", PrescriptionFactsSignature, PRESCRIPTION_SCHEMA_JSON),
    ("investigation", InvestigationFactsSignature, INVESTIGATION_SCHEMA_JSON),
)


def _facts_of(raw_output: str) -> list[dict]:
    """Extract one family predictor's raw fact dicts (robust; no model round-trip).

    Returns the raw ``clinical_facts`` dicts exactly as the model emitted them, so
    the merged output carries no synthetic ``attributes`` key — the metric's parser
    coerces an empty attributes dict into a string and rejects it, the same failure
    the monolith avoids by emitting no attributes field at all.
    """

    if not raw_output:
        return []
    try:
        payload = json.loads(extract_json_object(raw_output))
    except Exception:
        return []
    if not isinstance(payload, dict):
        return []
    facts = payload.get("clinical_facts") or payload.get("facts") or []
    return [fact for fact in facts if isinstance(fact, dict)]


class GepaPerFamilyExtractor(dspy.Module):
    """Four per-family predictors; each instruction is independently evolved by GEPA."""

    def __init__(self) -> None:
        super().__init__()
        for name, signature, _schema in _FAMILY_PREDICTORS:
            setattr(self, name, dspy.Predict(signature))

    def _predictors(self) -> list[dspy.Predict]:
        return [getattr(self, name) for name, _sig, _schema in _FAMILY_PREDICTORS]

    def forward(self, letter_text: str, output_schema: str | None = None) -> dspy.Prediction:
        merged: list[dict] = []
        for name, _signature, schema in _FAMILY_PREDICTORS:
            predictor = getattr(self, name)
            out = predictor(letter_text=letter_text, output_schema=schema)
            merged.extend(_facts_of(str(getattr(out, "clinical_facts_json", "") or "")))

        prediction = dspy.Prediction(
            clinical_facts_json=json.dumps({"clinical_facts": merged}, ensure_ascii=False)
        )
        # Stamp the summed prompt size across all four predictors so the length
        # penalty sees the whole evolved surface during GEPA selection.
        prediction.instruction_tokens = sum(
            approx_tokens(p.signature.instructions) for p in self._predictors()
        )
        prediction.demo_tokens = sum(
            approx_tokens(str(dict(demo)))
            for p in self._predictors()
            for demo in (p.demos or [])
        )
        return prediction


def build_per_family_program() -> GepaPerFamilyExtractor:
    """Per-family multi-signature program seeded with the lean family instructions."""

    return GepaPerFamilyExtractor()


def combined_instruction(program: GepaPerFamilyExtractor) -> str:
    """All four evolved per-family instructions, for the instruction artifact + tokens."""

    blocks = []
    for name, _signature, _schema in _FAMILY_PREDICTORS:
        instructions = getattr(program, name).signature.instructions
        blocks.append(f"=== {name} ===\n{instructions}")
    return "\n\n".join(blocks)
