"""Native-quarter R7 candidate, isolated from the original R7 parser and saved runs."""

from __future__ import annotations

import json
from typing import Annotated, Any, Literal, Self

from dspy.adapters.chat_adapter import ChatAdapter
from pydantic import Field, TypeAdapter, model_validator

from clinical_extraction.tasks.seizure_frequency.gan2026.llm import one_shot_measurements_r5 as r5

r4 = r5.r4
VERSION = "one_shot_frequency_v2_measurements_r7_quarter"
REVISION = "native_quarter_v1"
Record = r4.v1.StrictRecord
Unit = Literal["second", "minute", "hour", "day", "week", "month", "quarter", "year"]


class Number(Record):
    type: Literal["number"]
    value: r4.Number


class Range(Record):
    type: Literal["range"]
    lower: r4.Number
    upper: r4.Number
    lower_inclusive: bool = True
    upper_inclusive: bool = True

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if self.lower > self.upper or (
            self.lower == self.upper and not (self.lower_inclusive and self.upper_inclusive)
        ):
            raise ValueError("Bounds must describe a nonempty ordered interval")
        return self


class Bound(Record):
    type: Literal["bound"]
    relation: Literal["at_least", "more_than", "at_most", "less_than"]
    value: r4.Number | Range


class QualitativeQuantity(Record):
    type: Literal["qualitative"]
    quantity: r4.Text = Field(description="The source's quantity, such as several or multiple.")


Quantity = Annotated[Number | Range | Bound | QualitativeQuantity, Field(discriminator="type")]


class NumberDuration(Number):
    value: Annotated[float, Field(gt=0, allow_inf_nan=False)]
    unit: Unit


class RangeDuration(Range):
    lower: Annotated[float, Field(gt=0, allow_inf_nan=False)]
    unit: Unit


class BoundDuration(Bound):
    unit: Unit

    @model_validator(mode="after")
    def positive(self) -> Self:
        minimum = self.value.lower if isinstance(self.value, Range) else self.value
        if minimum <= 0:
            raise ValueError("Duration must be positive")
        return self


Duration = Annotated[NumberDuration | RangeDuration | BoundDuration, Field(discriminator="type")]
DURATION_ADAPTER: TypeAdapter[NumberDuration | RangeDuration | BoundDuration] = TypeAdapter(
    Duration
)


class TimePoint(Record):
    time: r4.Text = Field(description="The source time expression; do not resolve relative dates.")
    form: Literal["calendar", "relative"]


class DocumentDate(TimePoint):
    role: Literal["clinic", "letter", "unspecified"]
    evidence: r4.Text


class Period(Record):
    time: r4.Text = Field(
        description="The source observation window, such as since the last review."
    )
    start: TimePoint | None = None
    end: TimePoint | None = None
    duration: Duration | None = None


class Event(Record):
    type: r4.Text = Field(description="The source's event name, not an inferred diagnosis.")
    scope: Literal["specific", "combined", "unspecified"]
    seizure_status: Literal["stated", "uncertain", "non_seizure", "unspecified"]


class RateDetails(Record):
    count: Quantity
    per: Duration


class MeasurementBase(Record):
    approximate: bool = Field(
        default=False,
        description="True if any numeric part of this measurement or its period is approximate.",
    )


class Rate(RateDetails, MeasurementBase):
    type: Literal["rate"]


class Count(MeasurementBase):
    type: Literal["count"]
    count: Quantity
    occurred_at: TimePoint | None = None


class Cluster(MeasurementBase):
    type: Literal["cluster"]
    rate: RateDetails | None = None
    count: Quantity | None = None
    seizures_per_cluster: Quantity | None = None
    occurred_at: TimePoint | None = None


class SeizureFree(MeasurementBase):
    type: Literal["seizure_free"]
    duration: Duration | None = None
    since: TimePoint | None = None


class LastSeizure(MeasurementBase):
    type: Literal["last_seizure"]
    occurred_at: TimePoint


class QualitativeFrequency(MeasurementBase):
    type: Literal["qualitative"]
    frequency: r4.Text = Field(description="The source frequency, such as occasional or most days.")


Measurement = Annotated[
    Rate | Count | Cluster | SeizureFree | LastSeizure | QualitativeFrequency,
    Field(discriminator="type"),
]


class Finding(Record):
    id: r4.Text
    event: Event
    measurement: Measurement
    timing: Literal["current", "historical", "future", "unclear"]
    period: Period | None = None
    condition: r4.Text | None = None
    evidence: r4.Text

    @model_validator(mode="after")
    def cluster_time(self) -> Self:
        if (
            isinstance(self.measurement, Cluster)
            and self.measurement.count is not None
            and self.period is None
            and self.measurement.occurred_at is None
        ):
            raise ValueError("Observed cluster counts require period or occurred_at")
        return self


class Rich(Record):
    document_dates: list[DocumentDate] = Field(default_factory=list)
    answer: r4.v1.Answer
    findings: list[Finding]
    selected_ids: list[r4.Text]

    @model_validator(mode="after")
    def valid_references(self) -> Self:
        ids = [f.id for f in self.findings]
        selected = self.selected_ids
        if len(ids) != len(set(ids)) or len(selected) != len(set(selected)):
            raise ValueError("Finding IDs and answer links must be unique")
        if not set(selected) <= set(ids):
            raise ValueError("Selected IDs must exist")
        if self.answer.label == "no seizure frequency reference":
            if ids or selected or self.answer.evidence is not None:
                raise ValueError("No-reference requires empty findings/links and null evidence")
        elif not selected or not self.answer.evidence or not self.answer.evidence.strip():
            raise ValueError("A referenced answer and quotation are required")
        return self

    def output(self) -> dict[str, Any]:
        """Compact representation; preserve the existing answer's explicit null evidence."""
        result = self.model_dump(exclude_none=True, exclude_defaults=True)
        result["answer"] = self.answer.model_dump()
        return result


SCHEMA_INSTRUCTIONS = [
    "The cases show intermediate facts and selections, not the response schema. Their "
    "raw_value/evidence preserve source text; normalised_label illustrates label conversion. "
    "Populate answer.label with the case's answer label, or the selected fact's normalised_label "
    "when no new label is given. Always declare answer.label, including unknown and no seizure "
    "frequency reference. Copy its supporting quotation into answer.evidence. Only no-reference "
    "has null answer.evidence. Map fact_id to id and selected_fact_ids to selected_ids.",
    "Return all seizure-frequency findings and one declared current-frequency answer. Source "
    "measurements preserve what was stated; the original cases govern the answer, including "
    "combining counts and interpreting time. Answer conversion must not overwrite measurements.",
    "Use measurement types rate, count, cluster, seizure_free, last_seizure and qualitative. "
    "A rate asserts recurrence (count per duration). A count is observed during a period or at "
    "occurred_at, not an inferred recurring rate. Do not divide an observed count by its period "
    "to create a source rate. Preserve unspecified observation times by omitting the fields.",
    "A cluster separates rate, observed cluster count and seizures_per_cluster. Its nested rate "
    "contains count and per without a type field. Cluster count requires period or occurred_at. "
    "An unquantified cluster may omit all numeric fields; evidence retains the cluster statement. "
    "Do not invent a cluster rate or infer a numeric cluster size from the word clusters.",
    "Use type number for a single number, range for two endpoints, bound for a one-sided limit, "
    "and qualitative with quantity for text such as multiple. Bounds retain relation at_least, "
    "more_than, at_most or less_than. For up to 2-3, use a bound with relation at_most and a range "
    "value from 2 to 3. Do not replace it with an endpoint or midpoint. Range endpoints default "
    "to inclusive; for more than 2 but at most 5 set lower_inclusive false and upper 5. "
    "Durations use the same numeric forms with unit alongside the value/endpoints, without a "
    "quantity wrapper. Duration values must be positive. Preserve quarter as a native unit: "
    "per quarter is per 1 quarter, never a conversion to months or days. Quarter is also "
    "available for explicit observation windows and seizure-free durations.",
    "Set approximate true once on the measurement if any numeric part, including its period "
    "duration, is explicitly approximate. Never put approximate inside a count, range, bound, "
    "per or nested cluster rate. Omission defaults to false. Evidence retains which part was "
    "approximate; the flag does not imply that every part is approximate.",
    "Use event.type for the source event name without inferring a diagnosis. Scope is specific "
    "for named events, combined only when the source explicitly measures events together, and "
    "unspecified otherwise. Seizure_status is stated, uncertain, non_seizure or unspecified. "
    "Preserve uncertainty about whether events are seizures; do not omit uncertain findings.",
    "Timing is current, historical, future or unclear. Current includes recent findings used "
    "to describe the present situation; dates and periods retain their finer timing. Do not "
    "turn a past event into a recurring present rate. Keep explicit conditions in condition.",
    "Use period for an observation window, keeping its source expression in time and any "
    "explicit start, end or duration. It is distinct from a rate's per. Use occurred_at on "
    "count and cluster for individual dated events and on last_seizure for the last event. "
    "Separate separately dated counts only when supported; do not distribute a combined count "
    "across dates. A cluster spanning days may retain its window in period.",
    "Time points contain time and form (calendar or relative). Preserve partial dates and "
    "relative references, including that date. Do not infer missing years, resolve references, "
    "calculate calendar dates, or derive source durations from dates. Include enough exact "
    "evidence to retain the antecedent of a relative reference. The original cases still govern "
    "time conversion for answer.label.",
    "Collect explicitly labelled document dates in document_dates with role clinic, letter or "
    "unspecified, source time, form and exact evidence. A clinic date is not automatically a "
    "letter date. Do not copy patient birth dates or seizure dates into document_dates. "
    "Document dates alone are not seizure-frequency findings and do not change no-reference.",
    "Seizure_free retains absence of the specified event, optionally duration or since. "
    "Absence of one event type is not absence of all seizures. Ongoing seizures are not a "
    "zero-duration seizure-free interval. No more than twice weekly is an upper bound, not "
    "absence. Use qualitative with frequency for expressions such as less frequent but not "
    "absent or not clustered. Not documented is not a zero count or seizure freedom.",
    "Evidence must be an exact source quotation. Link the answer to unique finding IDs in "
    "selected_ids; an unknown answer still needs supporting findings and evidence. For "
    "no-reference return empty findings and selected_ids and null answer.evidence. "
    "Overlapping findings are not additive: a dated cluster within a period total is not an "
    "additional cluster. Last seizure and none since can describe distinct claims from one quote.",
    "Omit absent optional fields rather than emitting null. Omission means no value extracted, "
    "not proof that the source lacks information. Omit approximate when false and range "
    "inclusivity flags when true. Keep required answer, findings and selected_ids, even when "
    "the latter two are empty. Do not add confidence, rationale or duplicate raw-value fields.",
]


def prompt_payload(note: str) -> dict[str, Any]:
    payload = r5.prompt_payload(note)
    payload["output_schema"] = Rich.model_json_schema()
    payload["schema_instructions"] = list(SCHEMA_INSTRUCTIONS)
    return payload


def messages(note: str) -> list[dict[str, Any]]:
    return ChatAdapter().format(
        r4.MeasurementSignature,
        demos=[],
        inputs={
            "prompt_input_json": json.dumps(
                prompt_payload(note), ensure_ascii=False, sort_keys=True
            )
        },
    )


def fictional_cases() -> list[dict[str, Any]]:
    """Original fictional fixtures plus native-quarter representation checks."""
    from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
        one_shot_measurements_r7 as original,
    )

    cases = original.fictional_cases()
    measurements: list[tuple[str, str, dict[str, Any]]] = [
        (
            "quarter_rate",
            "Seizures occur at an estimated 8 to 16 per quarter.",
            {
                "type": "rate",
                "approximate": True,
                "count": {"type": "range", "lower": 8, "upper": 16},
                "per": {"type": "number", "value": 1, "unit": "quarter"},
            },
        ),
        (
            "quarter_cluster_rate",
            "Seizures occur in two clusters every one to two quarters.",
            {
                "type": "cluster",
                "rate": {
                    "count": {"type": "number", "value": 2},
                    "per": {"type": "range", "lower": 1, "upper": 2, "unit": "quarter"},
                },
            },
        ),
        (
            "quarter_freedom",
            "There have been no seizures for at least two quarters.",
            {
                "type": "seizure_free",
                "duration": {
                    "type": "bound",
                    "relation": "at_least",
                    "value": 2,
                    "unit": "quarter",
                },
            },
        ),
    ]
    for name, note, measurement in measurements:
        cases.append(
            {
                "name": name,
                "note_text": note,
                "scope": "fictional representation only; unknown answer is a placeholder",
                "output": {
                    "answer": {"label": "unknown", "evidence": note},
                    "findings": [
                        {
                            "id": "f1",
                            "event": {
                                "type": "seizures",
                                "scope": "unspecified",
                                "seizure_status": "stated",
                            },
                            "measurement": measurement,
                            "timing": "current",
                            "evidence": note,
                        }
                    ],
                    "selected_ids": ["f1"],
                },
            }
        )
    return cases


def complete_example() -> dict[str, Any]:
    from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
        one_shot_measurements_r7 as original,
    )

    return original.complete_example()
