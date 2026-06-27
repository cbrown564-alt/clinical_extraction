"""GEPA-native DSPy program for Gan 2026 seizure-frequency extraction.

The single optimizable surface is the signature *instruction* (its docstring).
GEPA evolves that text; everything else is fixed scaffolding:

* ``note_text`` carries the clinical note.
* ``output_schema`` carries a constant JSON schema so the format never has to be
  re-derived by the model and is never mutated by the optimizer.
* ``structured_json`` is the same string output the deterministic stack already
  knows how to parse, repair, normalize, and score.

This deliberately moves the ~25 hand-written rules *out* of the input payload
(where the legacy ``build_prompt_input`` crammed them, invisible to any
optimizer) and lets GEPA discover a concise rule set under a length penalty.
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
# model never has to invent the output shape. Mirrors the event/selection schema
# used by the production hybrid structured-events pipeline.
OUTPUT_SCHEMA: dict[str, object] = {
    "events": [
        {
            "event_id": "stable string such as e1",
            "kind": [
                "frequency_rate",
                "cluster_frequency",
                "seizure_free",
                "last_event_only",
                "unknown_frequency",
                "no_reference",
            ],
            "raw_value": "source-near expression or null",
            "applies_to": "seizure type or clinical target, or null",
            "time_window": "source-near current/recent/historical window, or null",
            "temporality": ["current", "recent", "historical", "future", "unclear"],
            "assertion_status": [
                "asserted",
                "negated",
                "historical",
                "hypothetical",
                "unknown",
            ],
            "evidence": "exact note substring",
            "notes": "optional short note or null",
        }
    ],
    "selection": {
        "selected_event_ids": "list of selected event_id strings",
        "final_kind": [
            "frequency",
            "seizure_free",
            "unknown",
            "no_reference",
            "unresolved_multiple",
        ],
        "final_label": (
            "normalized label such as '1 per day', '2 to 3 per month', "
            "'multiple per week', '1 cluster per week', 'seizure free for 6 month', "
            "'unknown', or 'no seizure frequency reference'; or null if not countable"
        ),
        "evidence": "exact note substring supporting the final selection",
        "confidence": ["low", "medium", "high"],
        "rationale": "one concise clinical sentence, not step-by-step reasoning",
    },
}

OUTPUT_SCHEMA_JSON: str = json.dumps(OUTPUT_SCHEMA, ensure_ascii=False, sort_keys=True)

# Near-minimal seed instruction for the "from-scratch" experiment. The whole
# point is to start lean and let GEPA add only the rules that earn their length.
FROM_SCRATCH_SEED_INSTRUCTION = (
    "You read one clinical note and report how often the patient is currently "
    "having seizures.\n"
    "First list the seizure-frequency facts in the note as events, then choose "
    "the events that describe the current or most recent seizure burden and give "
    "a single final_label for it.\n"
    "Return exactly one JSON object matching output_schema, with an 'events' list "
    "and a 'selection' object, and no markdown or commentary outside the JSON."
)


class GepaSeizureFrequencySignature(dspy.Signature):
    """You read one clinical note and report how often the patient is currently having seizures.

    First list the seizure-frequency facts in the note as events, then choose the
    events that describe the current or most recent seizure burden and give a
    single final_label for it. Return exactly one JSON object matching
    output_schema, with an 'events' list and a 'selection' object, and no markdown
    or commentary outside the JSON.
    """

    note_text: str = dspy.InputField(desc="One clinical note.")
    output_schema: str = dspy.InputField(
        desc="Required JSON schema for the answer. Match it exactly; do not add or rename keys."
    )
    structured_json: str = dspy.OutputField(
        desc="One JSON object with 'events' and 'selection' per output_schema. No markdown."
    )


class GepaStructuredExtractor(dspy.Module):
    """Single-predict GEPA program: the instruction is the evolved prompt."""

    def __init__(self, seed_instruction: str | None = None) -> None:
        super().__init__()
        self.extract = dspy.Predict(GepaSeizureFrequencySignature)
        if seed_instruction is not None:
            self.extract.signature = self.extract.signature.with_instructions(
                seed_instruction
            )

    def forward(self, note_text: str, output_schema: str = OUTPUT_SCHEMA_JSON) -> dspy.Prediction:
        prediction = self.extract(note_text=note_text, output_schema=output_schema)
        # Stamp the candidate's own prompt size onto the prediction. GEPA scores
        # candidates with a plain metric(example, pred) call (no trace, no program),
        # so this is the only place the length penalty can observe the *evolved*
        # instruction during selection — making the penalty bite where it matters.
        prediction.instruction_tokens = approx_tokens(self.extract.signature.instructions)
        prediction.demo_tokens = sum(
            approx_tokens(str(dict(demo))) for demo in (self.extract.demos or [])
        )
        return prediction


def build_from_scratch_program() -> GepaStructuredExtractor:
    """Program seeded with the lean from-scratch instruction."""

    return GepaStructuredExtractor(seed_instruction=FROM_SCRATCH_SEED_INSTRUCTION)
