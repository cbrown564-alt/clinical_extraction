"""GEPA-native DSPy program for ExECTv2 de-duplicated clinical-fact extraction.

The single optimizable surface is the signature *instruction* (its docstring).
GEPA evolves that text; everything else is fixed scaffolding:

* ``letter_text`` carries the clinical letter.
* ``output_schema`` carries a constant JSON schema so the simplified four-family
  ``clinical_facts`` shape never has to be re-derived by the model and is never
  mutated by the optimizer.
* ``clinical_facts_json`` is the same string output the existing de-dup route
  already knows how to parse, evidence-gate, project, and score on the
  ``clinical_headline`` (clinical-recovery) surface.

This deliberately moves the hand-written de-dup/schema rules *out* of the input
payload (where ``build_single_call_dedup_facts_prompt_payload`` crammed ~dozens
of them, invisible to any optimizer) and lets GEPA discover a concise rule set
under a length penalty. The research question (plan 13): every prior single-prompt
de-dup attempt was hand-tuned and plateaued at ~0.71-0.75 clinical_headline F1 on
dev140, below the v08 hybrid's 0.9155 — can an auto-evolved lean prompt do better?
"""

from __future__ import annotations

import json

import dspy


def approx_tokens(text: str | None) -> int:
    """Provider-agnostic token estimate (~4 chars/token). Consistent across models."""

    if not text:
        return 0
    return (len(text) + 3) // 4


# Constant format scaffolding. This is NOT optimized by GEPA (it is input data,
# not the instruction), so the evolved prompt cannot bloat the schema and the
# model never has to invent the output shape. It mirrors the simplified
# ``clinical_facts`` schema the existing de-dup adapter (``clinical_facts_to_mentions``)
# reads, restricted to the fields that drive the clinical_headline scorers.
OUTPUT_SCHEMA: dict[str, object] = {
    "clinical_facts": [
        {
            "family": "diagnosis",
            "concept": "short diagnosis concept",
            "negation": "affirmed | negated",
            "evidence": "exact substring copied from the letter",
        },
        {
            "family": "seizure_frequency",
            "seizure_type": "named seizure type, or 'seizures' if generic",
            "state": "active_rate | seizure_free | changed | unknown",
            "evidence": "exact substring copied from the letter",
        },
        {
            "family": "prescription",
            "drug": "current drug name",
            "dose": "number only when stated",
            "dose_unit": "mg | g",
            "frequency": "1 | 2 | 3 | As_Required",
            "evidence": "exact substring copied from the letter",
        },
        {
            "family": "investigation",
            "modality": "MRI | CT | EEG | telemetry",
            "result": "normal | abnormal | unknown",
            "evidence": "exact substring copied from the letter",
        },
    ]
}

OUTPUT_SCHEMA_JSON: str = json.dumps(OUTPUT_SCHEMA, ensure_ascii=False, sort_keys=True)

# Near-minimal seed instruction for the "from-scratch" experiment. The whole
# point is to start lean and let GEPA add only the rules that earn their length.
FROM_SCRATCH_SEED_INSTRUCTION = (
    "You read one clinical letter and list its de-duplicated clinical facts in "
    "four families: diagnosis, seizure_frequency, prescription, and investigation.\n"
    "Emit each distinct clinical fact once, grounded by an exact substring of the "
    "letter as evidence; do not repeat a diagnosis, seizure-type state, drug "
    "regimen, or investigation you have already listed.\n"
    "Return exactly one JSON object matching output_schema, with a 'clinical_facts' "
    "list and no markdown or commentary outside the JSON."
)


class GepaDedupFactsSignature(dspy.Signature):
    (
        "You read one clinical letter and list its de-duplicated clinical facts "
        "in four families: diagnosis, seizure_frequency, prescription, and "
        "investigation.\n\n"
        "Emit each distinct clinical fact once, grounded by an exact substring of the\n"
        "letter as evidence; do not repeat a diagnosis, seizure-type state, drug\n"
        "regimen, or investigation you have already listed. Return exactly one JSON\n"
        "object matching output_schema, with a 'clinical_facts' list and no markdown or\n"
        "commentary outside the JSON."
    )

    letter_text: str = dspy.InputField(desc="One clinical letter.")
    output_schema: str = dspy.InputField(
        desc="Required JSON schema for the answer. Match it exactly; do not add or rename keys."
    )
    clinical_facts_json: str = dspy.OutputField(
        desc="One JSON object with a 'clinical_facts' list per output_schema. No markdown."
    )


class GepaDedupFactsExtractor(dspy.Module):
    """Single-predict GEPA program: the instruction is the evolved prompt."""

    def __init__(self, seed_instruction: str | None = None) -> None:
        super().__init__()
        self.extract = dspy.Predict(GepaDedupFactsSignature)
        if seed_instruction is not None:
            self.extract.signature = self.extract.signature.with_instructions(seed_instruction)

    def forward(self, letter_text: str, output_schema: str = OUTPUT_SCHEMA_JSON) -> dspy.Prediction:
        prediction = self.extract(letter_text=letter_text, output_schema=output_schema)
        # Stamp the candidate's own prompt size onto the prediction. GEPA scores
        # candidates with a plain metric(example, pred) call (no trace, no program),
        # so this is the only place the length penalty can observe the *evolved*
        # instruction during selection — making the penalty bite where it matters.
        prediction.instruction_tokens = approx_tokens(self.extract.signature.instructions)
        prediction.demo_tokens = sum(
            approx_tokens(str(dict(demo))) for demo in (self.extract.demos or [])
        )
        return prediction


def build_from_scratch_program() -> GepaDedupFactsExtractor:
    """Program seeded with the lean from-scratch instruction."""

    return GepaDedupFactsExtractor(seed_instruction=FROM_SCRATCH_SEED_INSTRUCTION)
