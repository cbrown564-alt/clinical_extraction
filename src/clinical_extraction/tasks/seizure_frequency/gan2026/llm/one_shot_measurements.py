"""Development-only v2: source measurements precede the declared benchmark answer.

No provider or dataset access. The frozen v1 implementation remains unchanged.
"""

from __future__ import annotations

import json
from typing import Annotated, Any, Literal, Self

import dspy
from dspy.adapters.chat_adapter import ChatAdapter
from pydantic import Field, ValidationError, model_validator

from clinical_extraction.tasks.seizure_frequency.gan2026.llm import one_shot_contract as v1

VERSION = "one_shot_frequency_v2_measurements_r4"
Text = Annotated[str, Field(min_length=1, pattern=r"\S")]
Number = Annotated[float, Field(ge=0, allow_inf_nan=False)]


class Exact(v1.StrictRecord):
    kind: Literal["exact"]
    value: Number
    approximate: bool


class Range(v1.StrictRecord):
    kind: Literal["range"]
    lower: Number
    upper: Number
    approximate: bool

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if self.lower > self.upper:
            raise ValueError("Range bounds must be ordered")
        return self


class Bound(v1.StrictRecord):
    kind: Literal["bound"]
    relation: Literal["at_least", "more_than", "at_most", "less_than"]
    value: Number
    approximate: bool


Quantity = Annotated[Exact | Range | Bound, Field(discriminator="kind")]


class Duration(v1.StrictRecord):
    quantity: Quantity
    unit: Literal["second", "minute", "hour", "day", "week", "month", "year"]

    @model_validator(mode="after")
    def positive(self) -> Self:
        minimum = self.quantity.lower if isinstance(self.quantity, Range) else self.quantity.value
        if minimum <= 0:
            raise ValueError("Duration must be positive")
        return self


class TimePoint(v1.StrictRecord):
    wording: Text
    form: Literal["calendar", "relative"]
    precision: Literal["day", "month", "year", "unspecified"]


class ObservationPeriod(v1.StrictRecord):
    wording: Text
    start: TimePoint | None
    end: TimePoint | None
    duration: Duration | None


class RecurringRate(v1.StrictRecord):
    kind: Literal["recurring_rate"]
    count: Quantity
    denominator: Duration


class ObservedCount(v1.StrictRecord):
    kind: Literal["observed_count"]
    count: Quantity
    interval: ObservationPeriod | None


class ClusterPattern(v1.StrictRecord):
    kind: Literal["cluster_pattern"]
    cadence: RecurringRate | None
    seizures_per_cluster: Quantity | None

    @model_validator(mode="after")
    def has_measurement(self) -> Self:
        if self.cadence is None and self.seizures_per_cluster is None:
            raise ValueError("Use qualitative frequency for an unquantified cluster pattern")
        return self


class SeizureFreeInterval(v1.StrictRecord):
    kind: Literal["seizure_free_interval"]
    duration: Duration | None
    since: TimePoint | None


class LastSeizure(v1.StrictRecord):
    kind: Literal["last_seizure"]
    when: TimePoint


class QualitativeFrequency(v1.StrictRecord):
    kind: Literal["qualitative_frequency"]
    wording: Text


Measurement = Annotated[
    RecurringRate
    | ObservedCount
    | ClusterPattern
    | SeizureFreeInterval
    | LastSeizure
    | QualitativeFrequency,
    Field(discriminator="kind"),
]


class EventScope(v1.StrictRecord):
    description: Text
    grouping: Literal["one_type", "explicit_combined_group", "unspecified"]
    seizure_interpretation: Literal[
        "stated_seizure", "uncertain_seizure", "explicitly_non_seizure", "not_specified"
    ]


class Finding(v1.StrictRecord):
    finding_id: Text
    event: EventScope
    measurement: Measurement
    temporal_status: Literal["current", "recent", "historical", "future", "unclear"]
    observation_period: ObservationPeriod | None
    condition: Text | None
    evidence: Text

    @model_validator(mode="after")
    def separate_periods(self) -> Self:
        if isinstance(self.measurement, ObservedCount) and self.observation_period is not None:
            raise ValueError("An observed count's period belongs in measurement.interval only")
        return self


class Rich(v1.StrictRecord):
    answer: v1.Answer
    findings: list[Finding]
    selected_finding_ids: list[Text]

    @model_validator(mode="after")
    def valid_references(self) -> Self:
        ids = [f.finding_id for f in self.findings]
        selected = self.selected_finding_ids
        if len(ids) != len(set(ids)) or len(selected) != len(set(selected)):
            raise ValueError("Finding IDs and answer links must be unique")
        if not set(selected) <= set(ids):
            raise ValueError("Selected finding IDs must exist")
        if self.answer.label == "no seizure frequency reference":
            if ids or selected or self.answer.evidence is not None:
                raise ValueError("No-reference requires empty findings/links and null evidence")
        elif not selected or not self.answer.evidence or not self.answer.evidence.strip():
            raise ValueError("A referenced answer and quotation are required")
        return self


SCOPE = [
    "Return all seizure-frequency findings and one declared current-frequency answer in JSON.",
    "Represent what the source states before projecting it into the answer label. Preserve "
    "approximation, ranges and one-sided bounds rather than replacing them with a midpoint.",
    "A recurring rate is distinct from a count observed during an interval. Do not convert "
    "an observed count into a recurring finding. Any task-label conversion belongs only in answer.",
    "Keep cluster cadence separate from seizures per cluster in source measurements. "
    "The cases still govern arithmetic for the answer label.",
    "For each event copy its description. Distinguish one type, an explicitly combined group "
    "and unspecified seizures. Preserve explicit uncertainty about whether events are seizures; "
    "do not infer a diagnosis from an event name.",
    "Retain observation periods separately from rate denominators. Use measurement.interval "
    "for observed counts and observation_period for other findings only when explicitly stated.",
    "Preserve calendar or relative time wording and its stated precision. Do not infer calendar "
    "dates, missing years or a duration from dates in source measurements. Use null for unstated "
    "time information. The cases still govern time conversion for the answer label.",
    "Use seizure_free_interval for absence of seizures, "
    "retaining the stated event type and period. "
    "Do not turn absence of one seizure type into absence of all seizures. "
    "No more than twice weekly is an upper bound, not a denied rate. Preserve wording such as "
    "not clustered or less frequent but not absent as qualitative frequency. "
    "Not documented means missing information, not a zero count or seizure freedom.",
    "Keep qualitative wording when a measurement cannot be quantified. Retain an explicit "
    "condition such as only when medication is missed; do not infer restrictions.",
    "Evidence must be an exact source quotation. Do not add a duplicate raw-value field, model "
    "confidence or rationale. Link the answer to the relevant unique finding IDs. For no-reference "
    "return empty findings/links and null answer evidence. "
    "Do not silently omit uncertain findings.",
]


def prompt_payload(note: str, condition: v1.Condition) -> dict[str, Any]:
    """Original authored task/cases; only output-field instructions are adapted."""
    if condition not in v1.CONDITIONS:
        raise ValueError("Unknown condition")
    original = v1.historical
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
    payload = original.llm_extract_encode_select_prompt_template()
    payload["instructions"] = instructions
    del payload["fact_schema"]
    del payload["selection_schema"]
    payload["output_schema"] = (Rich if condition == "rich" else v1.Simple).model_json_schema()
    payload["schema_instructions"] = [
        "The cases show intermediate facts and selections, not the response schema. "
        "Their raw_value/evidence preserve source wording; normalised_label illustrates "
        "label conversion. Populate answer.label with the case's answer label, or the "
        "selected fact's normalised_label when no new label is given. Always declare the "
        "answer label, including unknown and no seizure frequency reference, and copy its "
        "supporting quotation into answer.evidence. Only no-reference has null evidence.",
        "Source measurements preserve what was stated; the original cases govern the final "
        "answer, including combining counts and interpreting time. An answer conversion "
        "must not overwrite source measurements.",
        *(
            [
                "For each finding, populate the source measurement and evidence fields. "
                "Keep original wording in evidence and measurement-specific wording fields. "
                "Retain findings even when their answer label is unknown. Map the cases' "
                "fact_id to finding_id and selected_fact_ids to selected_finding_ids.",
                *SCOPE,
            ]
            if condition == "rich"
            else [
                "Use all relevant facts and the same cases to decide the answer. Return only "
                "answer.label and answer.evidence. The intermediate facts in the cases "
                "are decision examples, not additional fields to return."
            ]
        ),
    ]
    payload["note_text"] = note
    return payload


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


def messages(note: str, condition: v1.Condition) -> list[dict[str, Any]]:
    """Keep the original ChatAdapter envelope and self-contained user request."""
    return ChatAdapter().format(
        MeasurementSignature,
        demos=[],
        inputs={
            "prompt_input_json": json.dumps(
                prompt_payload(note, condition), ensure_ascii=False, sort_keys=True
            )
        },
    )


def inspect_output(raw: str | None, note: str, condition: v1.Condition) -> dict[str, Any]:
    """No repair, date inference, arithmetic, or rewriting of the declared answer."""
    if condition == "simple":
        return v1.inspect_output(raw, note, "simple")
    if condition != "rich":
        raise ValueError("Unknown condition")
    result: dict[str, Any] = {
        "failure": None,
        "output": None,
        "categories": None,
        "quote_slots": 0,
        "exact_quotes": 0,
    }
    if raw is None or not raw.strip():
        return {**result, "failure": "no_response"}
    try:
        payload = json.loads(raw, object_pairs_hook=v1._unique_object)
    except ValueError:
        return {**result, "failure": "invalid_syntax"}
    try:
        output = Rich.model_validate(payload)
    except ValidationError:
        return {**result, "failure": "invalid_schema"}
    try:
        categories = v1.native_categories(output.answer.label)
    except (ValueError, ZeroDivisionError, OverflowError):
        return {**result, "failure": "invalid_target_label"}
    quotes = [f.evidence for f in output.findings]
    if output.answer.evidence is not None:
        quotes.append(output.answer.evidence)
    return {
        **result,
        "output": output.model_dump(),
        "categories": categories,
        "quote_slots": len(quotes),
        "exact_quotes": sum(q in note for q in quotes),
    }


def _exact(value: float) -> dict[str, Any]:
    return {"kind": "exact", "value": value, "approximate": False}


def _duration(value: float, unit: str) -> dict[str, Any]:
    return {"quantity": _exact(value), "unit": unit}


def fictional_cases() -> list[dict[str, Any]]:
    """Fixed authored examples; no clinical corpus or previous model outputs."""
    rate = {"kind": "recurring_rate", "count": _exact(2), "denominator": _duration(1, "month")}
    specs = [
        (
            "approximate_range",
            "Approximately two to three focal seizures occur per month.",
            "2 to 3 per month",
            {**rate, "count": {"kind": "range", "lower": 2, "upper": 3, "approximate": True}},
        ),
        (
            "observed_count",
            "She had three seizures over the last six months.",
            "3 per 6 months",
            {
                "kind": "observed_count",
                "count": _exact(3),
                "interval": {
                    "wording": "over the last six months",
                    "start": None,
                    "end": None,
                    "duration": _duration(6, "month"),
                },
            },
        ),
        (
            "cluster",
            "She has two clusters per month with three to five seizures per cluster.",
            "2 cluster per month, 3 to 5 per cluster",
            {
                "kind": "cluster_pattern",
                "cadence": rate,
                "seizures_per_cluster": {
                    "kind": "range",
                    "lower": 3,
                    "upper": 5,
                    "approximate": False,
                },
            },
        ),
        (
            "seizure_free",
            "She has had no seizures for six months.",
            "seizure free for 6 months",
            {"kind": "seizure_free_interval", "duration": _duration(6, "month"), "since": None},
        ),
        (
            "last_seizure",
            "Her last seizure was in March.",
            "unknown",
            {
                "kind": "last_seizure",
                "when": {"wording": "in March", "form": "calendar", "precision": "month"},
            },
        ),
        (
            "qualitative",
            "Possible seizures are less frequent.",
            "unknown",
            {"kind": "qualitative_frequency", "wording": "less frequent"},
        ),
        (
            "nonclustered_pattern",
            "Her seizures were not clustered.",
            "unknown",
            {"kind": "qualitative_frequency", "wording": "not clustered"},
        ),
        (
            "upper_bound",
            "She has no more than two seizures per week.",
            "2 per week",
            {
                **rate,
                "count": {"kind": "bound", "relation": "at_most", "value": 2, "approximate": False},
                "denominator": _duration(1, "week"),
            },
        ),
        (
            "conditional",
            "Seizures occur only when medication is missed.",
            "unknown",
            {"kind": "qualitative_frequency", "wording": "only when medication is missed"},
        ),
        (
            "reduced_not_absent",
            "Her seizures are less frequent but not absent.",
            "unknown",
            {"kind": "qualitative_frequency", "wording": "less frequent but not absent"},
        ),
        (
            "subtype_seizure_free",
            "She has had no tonic-clonic seizures for six months.",
            "seizure free for 6 months",
            {"kind": "seizure_free_interval", "duration": _duration(6, "month"), "since": None},
        ),
    ]
    cases = []
    for name, note, label, measurement in specs:
        finding = {
            "finding_id": "f1",
            "event": {
                "description": "focal seizures"
                if name == "approximate_range"
                else (
                    "tonic-clonic seizures"
                    if name == "subtype_seizure_free"
                    else ("Seizures" if note.startswith("Seizures") else "seizures")
                ),
                "grouping": "one_type"
                if name in {"approximate_range", "subtype_seizure_free"}
                else "unspecified",
                "seizure_interpretation": "uncertain_seizure"
                if name == "qualitative"
                else "stated_seizure",
            },
            "measurement": measurement,
            "temporal_status": "historical" if name == "last_seizure" else "current",
            "observation_period": None,
            "condition": "only when medication is missed" if name == "conditional" else None,
            "evidence": note,
        }
        cases.append(
            {
                "name": name,
                "note_text": note,
                "output": {
                    "answer": {"label": label, "evidence": note},
                    "findings": [finding],
                    "selected_finding_ids": ["f1"],
                },
            }
        )
    cases.append(
        {
            "name": "no_reference",
            "note_text": "Blood pressure was measured.",
            "output": {
                "answer": {"label": "no seizure frequency reference", "evidence": None},
                "findings": [],
                "selected_finding_ids": [],
            },
        }
    )
    return cases
