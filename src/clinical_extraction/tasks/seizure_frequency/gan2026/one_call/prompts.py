"""Model-facing requests for the two one-call conditions.

``minimal`` is the r4 answer-only request, byte-identical to the request scored on
dev750 in September 2026. ``expanded`` shares its task, cases, label forms,
instructions and envelope; only ``output_schema`` and the condition-specific
``schema_instructions`` differ. The expanded instructions restate the
[annotation guide](docs/research/gan2026/seizure_frequency_annotation_guide.md).
No provider or dataset access.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

import dspy
from dspy.adapters.chat_adapter import ChatAdapter
from pydantic import BaseModel, ConfigDict

from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    prompt_llm_extract_encode_select as original,
)

Condition = Literal["minimal", "expanded"]
CONDITIONS: tuple[Condition, ...] = ("minimal", "expanded")
SCHEMA_PATH = Path(__file__).with_name("expanded.schema.json")
EXPANDED_SCHEMA: dict[str, Any] = json.loads(SCHEMA_PATH.read_text())


class StrictRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Answer(StrictRecord):
    label: str
    evidence: str | None


class Simple(StrictRecord):
    answer: Answer


SHARED_SCHEMA_INSTRUCTIONS = [
    "The cases show intermediate facts and selections, not the response schema. "
    "Their raw_value/evidence preserve source wording; normalised_label illustrates "
    "label conversion. Populate answer.label with the case's answer label, or the "
    "selected fact's normalised_label when no new label is given. Always declare the "
    "answer label, including unknown and no seizure frequency reference, and copy its "
    "supporting quotation into answer.evidence. Only no-reference has null evidence.",
    "Source measurements preserve what was stated; the original cases govern the final "
    "answer, including combining counts and interpreting time. An answer conversion "
    "must not overwrite source measurements.",
]

MINIMAL_SCHEMA_INSTRUCTIONS = [
    "Use all relevant facts and the same cases to decide the answer. Return only "
    "answer.label and answer.evidence. The intermediate facts in the cases "
    "are decision examples, not additional fields to return.",
]

EXPANDED_SCHEMA_INSTRUCTIONS = [
    "Decide answer.label exactly as if only the answer were requested: use the decision "
    "cases and label forms, including their arithmetic such as adding month counts and "
    "their time conversion. The finding rules below apply only to the findings array; "
    "they never change how the answer is chosen or calculated.",
    "Also return findings: one entry for each seizure-frequency statement in the note, "
    "current or historical. The cases' facts illustrate answer selection; findings use "
    "the output schema instead. answer.claim_indices lists the zero-based positions of "
    "the findings that support the answer; leave it empty when none does.",
    "A statement is a finding when it gives a rate, a count in a stated window or on a "
    "date, a cluster pattern, a seizure-free period with a duration or since-anchor, an "
    "explicitly latest event with its time, a stated median interval between events, or "
    "a standalone occasional or frequent level. Exclude plans, thresholds, family "
    "history, medication schedules, explicit non-seizures, symptoms not linked to "
    "seizures, denials with no duration or anchor, and wording that states only "
    "occurrence, trend or pattern.",
    "Record each claim once. A restatement of the same events, measurement and window "
    "adds its quotation to that finding's evidence. Trend or variability wording about a "
    "measured claim belongs in its evidence, not in another finding. Keep different "
    "seizure types, windows and measurements as separate findings; never sum, split or "
    "link counts across seizure types.",
    "A diary or list of counts for the same events across listed months or dates is one "
    "observed_count over that span when the components do not overlap. Do not fill an "
    "unreported month with zero, count a subtype twice, or treat a cluster as one seizure.",
    "event.label uses the note's words for the counted events. event.scope is overall "
    "only for an explicit whole-population total, named for a stated seizure type, "
    "combined for an explicit joint total of several types, and otherwise unspecified. "
    "status is uncertain only when the note questions whether the events are seizures.",
    "counted_unit is individual_seizure unless the note counts affected days "
    "(seizure_day), affected nights (seizure_night), clusters (cluster), cluster days "
    "(cluster_day) or status epilepticus episodes (status_episode). Seizure-free, "
    "last-event and median-interval findings use not_applicable.",
    "measurement.kind: rate for a stated recurrence (a bare cadence such as weekly is 1 "
    "per week; bimonthly is 1 per 2 months unless the note defines it); observed_count "
    "for events in a stated window or on a date; cluster for cluster count, cadence and "
    "seizures per cluster together; seizure_free for an absence of at least two weeks or "
    "since a stated anchor, not for shorter gaps or ordinary gaps between clusters; "
    "last_event only when the note calls the event the last or most recent; "
    "median_interval for a stated median time between events; qualitative only when no "
    "more precise measurement of the same events and window is given. Keep stated "
    "numbers, ranges and bounds; use verbatim for vague amounts such as few weeks. Do "
    "not convert units or compute values.",
    "time.phase is ongoing when the finding describes the patient at this assessment, "
    "superseded when the note states a later state that replaces it, and past_or_unclear "
    "otherwise. time.source holds the note's concise window or date wording when one is "
    "stated; do not calculate dates, durations or recency.",
    "restriction records only a stated limit on which events were counted, such as while "
    "asleep or witnessed only.",
    "Each evidence item is a short exact quotation from the note; together they support "
    "the finding. For no seizure frequency reference, findings and answer.claim_indices "
    "are empty.",
]


def payload(note: str, condition: Condition) -> dict[str, Any]:
    """Original authored task and cases; only output-field instructions differ by condition."""
    if condition not in CONDITIONS:
        raise ValueError("Unknown condition")
    instructions = list(original.INSTRUCTIONS)
    instructions[1] = (
        "For each fact, distinguish the original wording from its normalized label. "
        "Write answer.label using only the allowed forms. Copy an example and change "
        "the numbers if needed. Consider facts even when their label is unknown."
    )
    instructions[2] = "Return only the fields defined in the supplied output schema."
    instructions[3] = (
        "Use no seizure frequency reference only when the note contains no usable "
        "seizure-frequency evidence. Write answer.label as no seizure frequency reference "
        "and answer.evidence as null. Do not use this state when seizures are discussed "
        "but frequency is unclear; use unknown instead."
    )
    request = original.llm_extract_encode_select_prompt_template()
    request["instructions"] = instructions
    del request["fact_schema"]
    del request["selection_schema"]
    minimal = condition == "minimal"
    request["output_schema"] = Simple.model_json_schema() if minimal else EXPANDED_SCHEMA
    request["schema_instructions"] = [
        *SHARED_SCHEMA_INSTRUCTIONS,
        *(MINIMAL_SCHEMA_INSTRUCTIONS if minimal else EXPANDED_SCHEMA_INSTRUCTIONS),
    ]
    request["note_text"] = note
    return request


class MeasurementSignature(dspy.Signature):
    """Extract source-near seizure-frequency events and choose a final answer.

    Return exactly one JSON object following the supplied output schema.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical note, task instructions, and output schemas."
    )
    structured_json: str = dspy.OutputField(
        desc="One strict JSON object following the supplied output schema."
    )


def messages(note: str, condition: Condition) -> list[dict[str, Any]]:
    """ChatAdapter envelope with a self-contained JSON request, as in r4."""
    return ChatAdapter().format(
        MeasurementSignature,
        demos=[],
        inputs={
            "prompt_input_json": json.dumps(
                payload(note, condition), ensure_ascii=False, sort_keys=True
            )
        },
    )
