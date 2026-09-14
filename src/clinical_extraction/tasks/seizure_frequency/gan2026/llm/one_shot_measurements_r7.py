"""Final R7 development schema; no provider, dataset access or frozen-run changes."""

from __future__ import annotations

import json
from typing import Annotated, Any, Literal, Self

from dspy.adapters.chat_adapter import ChatAdapter
from pydantic import Field, TypeAdapter, model_validator

from clinical_extraction.tasks.seizure_frequency.gan2026.llm import one_shot_measurements_r5 as r5

r4 = r5.r4
VERSION = "one_shot_frequency_v2_measurements_r7"
REVISION = "simplified_dates_v1"
Record = r4.v1.StrictRecord
Unit = Literal["second", "minute", "hour", "day", "week", "month", "year"]


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
    "quantity wrapper. Duration values must be positive.",
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
    """Adapt authored fixtures only; this is not an output-repair or replay adapter."""
    names = {
        "kind": "type",
        "finding_id": "id",
        "selected_finding_ids": "selected_ids",
        "description": "type",
        "grouping": "scope",
        "seizure_interpretation": "seizure_status",
        "temporal_status": "timing",
        "observation_period": "period",
        "denominator": "per",
        "cadence": "rate",
        "when": "occurred_at",
    }
    types = {
        "exact": "number",
        "recurring_rate": "rate",
        "observed_count": "count",
        "cluster_pattern": "cluster",
        "seizure_free_interval": "seizure_free",
        "qualitative_frequency": "qualitative",
    }

    def convert(value: Any) -> Any:
        if isinstance(value, list):
            return [convert(v) for v in value]
        if not isinstance(value, dict):
            return value
        if "quantity" in value and "unit" in value:
            return {**convert(value["quantity"]), "unit": value["unit"]}
        result = {}
        for key, v in value.items():
            if key in ("approximate", "precision") or v is None:
                continue
            new_key = names.get(key, key)
            if key == "wording":
                new_key = {"qualitative": "quantity", "qualitative_frequency": "frequency"}.get(
                    value.get("kind", ""), "time"
                )
            if key == "kind":
                v = types.get(v, v)
            elif key == "grouping":
                v = {"one_type": "specific", "explicit_combined_group": "combined"}.get(v, v)
            elif key == "seizure_interpretation":
                v = {
                    "stated_seizure": "stated",
                    "uncertain_seizure": "uncertain",
                    "explicitly_non_seizure": "non_seizure",
                    "not_specified": "unspecified",
                }[v]
            elif key == "temporal_status" and v == "recent":
                v = "current"
            result[new_key] = convert(v)
        if "rate" in result:
            result["rate"].pop("type", None)
        return result

    def approximate(value: Any) -> bool:
        return isinstance(value, dict) and (
            value.get("approximate") is True or any(approximate(v) for v in value.values())
        )

    cases = []
    for old in r5.fictional_cases():
        case = convert(old)
        case["output"]["answer"] = old["output"]["answer"].copy()
        for old_finding, finding in zip(
            old["output"]["findings"], case["output"]["findings"], strict=True
        ):
            if approximate(old_finding):
                finding["measurement"]["approximate"] = True
        cases.append(case)

    def add(name: str, note: str, measurement: dict[str, Any], **fields: Any) -> None:
        cases.append(
            {
                "name": name,
                "note_text": note,
                "scope": "representation only; answer placeholder",
                "output": {
                    "answer": {"label": "unknown", "evidence": note},
                    "selected_ids": ["f1"],
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
                            **fields,
                        }
                    ],
                },
            }
        )

    add(
        "observed_clusters",
        "There were three clusters in the past six weeks.",
        {"type": "cluster", "count": {"type": "number", "value": 3}},
        period={
            "time": "the past six weeks",
            "duration": {"type": "number", "value": 6, "unit": "week"},
        },
    )
    add(
        "bound_on_range",
        "She has up to 2-3 seizures per week.",
        {
            "type": "rate",
            "count": {
                "type": "bound",
                "relation": "at_most",
                "value": {"type": "range", "lower": 2, "upper": 3},
            },
            "per": {"type": "number", "value": 1, "unit": "week"},
        },
    )
    add(
        "compound_duration",
        "She has one seizure every more than 2 but at most 5 days.",
        {
            "type": "rate",
            "count": {"type": "number", "value": 1},
            "per": {
                "type": "range",
                "lower": 2,
                "upper": 5,
                "lower_inclusive": False,
                "unit": "day",
            },
        },
    )
    add(
        "dated_count",
        "She had two seizures on 12 May.",
        {
            "type": "count",
            "count": {"type": "number", "value": 2},
            "occurred_at": {"time": "12 May", "form": "calendar"},
        },
    )
    add(
        "relative_cluster",
        "One cluster occurred two weeks ago.",
        {
            "type": "cluster",
            "count": {"type": "number", "value": 1},
            "occurred_at": {"time": "two weeks ago", "form": "relative"},
        },
    )
    no_reference = {
        "name": "document_dates_without_findings",
        "note_text": "Clinic Date: 14 September 2026. Blood pressure was measured.",
        "output": {
            "document_dates": [
                {
                    "role": "clinic",
                    "time": "14 September 2026",
                    "form": "calendar",
                    "evidence": "Clinic Date: 14 September 2026",
                }
            ],
            "answer": {"label": "no seizure frequency reference", "evidence": None},
            "findings": [],
            "selected_ids": [],
        },
    }
    cases.append(no_reference)
    cases.append(complete_example())
    return cases


def complete_example() -> dict[str, Any]:
    """The agreed fictional design example, with an explicit placeholder answer."""
    rate = (
        "She currently reports about three brief staring episodes per week. "
        "It remains uncertain whether these are seizures."
    )
    total = (
        "Between 1 June and 31 August 2026, she reported two clusters of tonic-clonic "
        "seizures, with three to four seizures in each cluster."
    )
    dated = "The latest cluster occurred on 28 August 2026."
    since = "Her last tonic-clonic seizure was on that date, and she has had none since."
    note = (
        "Clinic Date: 14 September 2026\nLetter Date: 16 September 2026\n\n"
        f"{rate}\n\n{total} {dated} {since}"
    )
    event = {"type": "tonic-clonic seizures", "scope": "specific", "seizure_status": "stated"}
    relative = {"time": "that date", "form": "relative"}
    findings: list[dict[str, Any]] = [
        {
            "id": "f1",
            "event": {
                "type": "brief staring episodes",
                "scope": "specific",
                "seizure_status": "uncertain",
            },
            "measurement": {
                "type": "rate",
                "count": {"type": "number", "value": 3},
                "per": {"type": "number", "value": 1, "unit": "week"},
                "approximate": True,
            },
            "timing": "current",
            "evidence": rate,
        },
        {
            "id": "f2",
            "event": event.copy(),
            "measurement": {
                "type": "cluster",
                "count": {"type": "number", "value": 2},
                "seizures_per_cluster": {"type": "range", "lower": 3, "upper": 4},
            },
            "period": {
                "time": "Between 1 June and 31 August 2026",
                "start": {"time": "1 June", "form": "calendar"},
                "end": {"time": "31 August 2026", "form": "calendar"},
            },
            "timing": "current",
            "evidence": total,
        },
        {
            "id": "f3",
            "event": event.copy(),
            "measurement": {
                "type": "cluster",
                "count": {"type": "number", "value": 1},
                "occurred_at": {"time": "28 August 2026", "form": "calendar"},
            },
            "timing": "current",
            "evidence": dated,
        },
        {
            "id": "f4",
            "event": event.copy(),
            "measurement": {"type": "last_seizure", "occurred_at": relative.copy()},
            "timing": "current",
            "evidence": dated + " " + since,
        },
        {
            "id": "f5",
            "event": event.copy(),
            "measurement": {"type": "seizure_free", "since": relative.copy()},
            "timing": "current",
            "evidence": dated + " " + since,
        },
    ]
    return {
        "name": "complete_dates_example",
        "note_text": note,
        "scope": (
            "representation only; unknown answer and links are placeholders, "
            "not native-label conversion evidence"
        ),
        "output": {
            "document_dates": [
                {
                    "role": "clinic",
                    "time": "14 September 2026",
                    "form": "calendar",
                    "evidence": "Clinic Date: 14 September 2026",
                },
                {
                    "role": "letter",
                    "time": "16 September 2026",
                    "form": "calendar",
                    "evidence": "Letter Date: 16 September 2026",
                },
            ],
            "answer": {"label": "unknown", "evidence": rate},
            "findings": findings,
            "selected_ids": ["f1"],
        },
    }
