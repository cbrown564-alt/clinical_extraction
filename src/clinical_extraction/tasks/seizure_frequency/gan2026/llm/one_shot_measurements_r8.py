"""R8 development schema aligned with annotation guide v0.7; no provider or dataset access.

R8 keeps the r5/r7 task wording, selection cases, label forms, answer endpoint and
request envelope. Only the finding schema and its population instructions change:
two timing values, an eight-value qualitative list, no approximation or inclusivity
flags, anchored seizure freedom, quantified clusters and derived event scope. The
same ``Finding`` model defines the v0.7 annotation reference through ``Annotation``.
"""

from __future__ import annotations

import json
import re
from typing import Annotated, Any, Literal, Self

from dspy.adapters.chat_adapter import ChatAdapter
from pydantic import Field, model_validator

from clinical_extraction.tasks.seizure_frequency.gan2026.llm import one_shot_measurements_r5 as r5

r4 = r5.r4
VERSION = "one_shot_frequency_v2_measurements_r8"
REVISION = "guide_v07_v1"
GUIDE_VERSION = "seizure_finding_annotation_v0.7"
Record = r4.v1.StrictRecord
Unit = Literal["second", "minute", "hour", "day", "week", "month", "quarter", "year"]
Timing = Literal["current", "historical"]
QualitativeValue = Literal[
    "rare", "occasional", "frequent", "increased", "decreased", "unchanged", "variable", "unknown"
]
Scope = Literal["specific", "combined", "unspecified"]
SeizureStatus = Literal["stated", "uncertain", "non_seizure"]

TYPE_WORDS = re.compile(
    r"\b(absence|absences|petit[- ]mal|grand[- ]mal|tonic|clonic|atonic|myoclon\w*|focal|partial|"
    r"generali[sz]ed|convuls\w*|drop[- ]attacks?|spasms?|status|aura|auras|gtcs?|tcs?|"
    r"impaired[- ]awareness|aware|dyscognitive|gelastic|infantile|jerks?|blank\w*|staring|"
    r"seizure[- ]days?|clusters?)\b",
    re.IGNORECASE,
)
COMBINED_WORDS = re.compile(r"\b(and|plus|combined|total|all types|both)\b|&|\+", re.IGNORECASE)


def derive_scope(label: str) -> Scope:
    """Scope is a function of the event label, not an annotation judgement."""
    types = TYPE_WORDS.findall(label)
    if len(set(t.lower() for t in types)) >= 2 and COMBINED_WORDS.search(label):
        return "combined"
    if types:
        return "specific"
    return "unspecified"


class Number(Record):
    type: Literal["number"]
    value: r4.Number


class Range(Record):
    type: Literal["range"]
    lower: r4.Number
    upper: r4.Number

    @model_validator(mode="after")
    def ordered(self) -> Self:
        if self.lower >= self.upper:
            raise ValueError("Range needs lower < upper; use number for a single value")
        return self


class Bound(Record):
    type: Literal["bound"]
    relation: Literal["at_least", "more_than", "at_most", "less_than"]
    value: r4.Number | Range


class QualitativeQuantity(Record):
    type: Literal["qualitative"]
    quantity: r4.Text = Field(description="The source's vague count, such as several.")


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


class TimePoint(Record):
    time: r4.Text = Field(description="The source time expression; do not resolve relative dates.")
    form: Literal["calendar", "relative"]


class DocumentDate(TimePoint):
    role: Literal["clinic", "letter", "unspecified"]
    evidence: r4.Text


class Period(Record):
    time: r4.Text = Field(description="The source observation window, such as the past month.")
    start: TimePoint | None = None
    end: TimePoint | None = None
    duration: Duration | None = None


class Event(Record):
    type: r4.Text = Field(description="The source's words for the measured event.")
    scope: Scope
    seizure_status: SeizureStatus = "stated"


class RateDetails(Record):
    count: Quantity
    per: Duration


class Rate(RateDetails):
    type: Literal["rate"]


class Count(Record):
    type: Literal["count"]
    count: Quantity
    occurred_at: TimePoint | None = None


class Cluster(Record):
    type: Literal["cluster"]
    rate: RateDetails | None = None
    count: Quantity | None = None
    seizures_per_cluster: Quantity | None = None
    occurred_at: TimePoint | None = None

    @model_validator(mode="after")
    def quantified(self) -> Self:
        if self.rate is None and self.count is None and self.seizures_per_cluster is None:
            raise ValueError("A cluster finding needs a rate, count or size")
        return self


class SeizureFree(Record):
    type: Literal["seizure_free"]
    duration: Duration | None = None
    since: TimePoint | None = None

    @model_validator(mode="after")
    def anchored(self) -> Self:
        if self.duration is None and self.since is None:
            raise ValueError("Seizure freedom needs a duration or a since anchor")
        return self


class LastSeizure(Record):
    type: Literal["last_seizure"]
    occurred_at: TimePoint


class QualitativeFrequency(Record):
    type: Literal["qualitative"]
    frequency: QualitativeValue


Measurement = Annotated[
    Rate | Count | Cluster | SeizureFree | LastSeizure | QualitativeFrequency,
    Field(discriminator="type"),
]


class Finding(Record):
    id: r4.Text
    event: Event
    measurement: Measurement
    timing: Timing = "current"
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
        result = self.model_dump(exclude_none=True, exclude_defaults=True)
        result["answer"] = self.answer.model_dump()
        return result


class Annotation(Record):
    """Guide v0.7 reference wrapper: findings only, no candidate or relation ledgers."""

    guide_version: Literal["seizure_finding_annotation_v0.7"]
    source_id: str
    source_row_index: Annotated[int, Field(ge=0)]
    source_sha256: Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
    annotation_state: Literal["complete", "needs_review", "source_unavailable"]
    document_dates: list[DocumentDate]
    findings: list[Finding]
    review_reason: str | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def consistent(self) -> Self:
        ids = [f.id for f in self.findings]
        if len(ids) != len(set(ids)):
            raise ValueError("Finding IDs must be unique")
        if self.annotation_state == "needs_review" and not (self.review_reason or "").strip():
            raise ValueError("needs_review requires review_reason")
        if self.annotation_state != "needs_review" and self.review_reason:
            raise ValueError("review_reason only accompanies needs_review")
        return self


SCHEMA_INSTRUCTIONS = [
    "The cases show intermediate facts and selections, not the response schema. Their "
    "raw_value/evidence preserve source text; normalised_label illustrates label conversion. "
    "Populate answer.label with the case's answer label, or the selected fact's normalised_label "
    "when no new label is given. Always declare answer.label, including unknown and no seizure "
    "frequency reference. Copy its supporting quotation into answer.evidence. Only no-reference "
    "has null answer.evidence. Map fact_id to id and selected_fact_ids to selected_ids.",
    "Return every statement that quantifies or bounds how often the patient's seizures or "
    "seizure-like events occur, plus one declared current-frequency answer. The original cases "
    "govern the answer, including combining counts and interpreting time; answer conversion must "
    "not overwrite findings. A finding must be one of rate, count, cluster, seizure_free, "
    "last_seizure or qualitative; a statement that cannot be written as one of these is not a "
    "finding.",
    "Not findings: denials without a time anchor (no auras, no history of status epilepticus, no "
    "nocturnal events); occurrence-only statements (recurrent seizures, ongoing, history of "
    "epilepsy, developed jerks); pattern or circumstance without a frequency (predominantly "
    "nocturnal, clusters around menses, no catamenial pattern); typical gaps (may go five days "
    "without seizures); general control or benefit; device or diary signals; plans, thresholds "
    "and future expectations; family history; medication schedules; diagnostic, aetiological or "
    "classification uncertainty.",
    "Rate is recurrence per time. Read cadence as a rate of one per interval: every 4-6 weeks is "
    "count 1 per range 4-6 week; an absence every night, daily, weekly, q2wk and a focal seizure "
    "monthly are all count 1 per 1 unit; a median interval of six weeks is 1 per 6 weeks; up to "
    "3 a week is a bound at_most 3 per 1 week; several per week keeps qualitative quantity "
    "several. Keep the stated unit, including quarter; never convert units.",
    "Count is events in a stated window or on a date, kept as a count with period or "
    "occurred_at; never divide it into a rate. Read N or M as the range N-M. Affected-period "
    "counts such as seizure days 8/30 this month are counts whose event type is seizure days.",
    "Cluster keeps the cluster unit: monthly clusters of 3-4 is rate 1 per 1 month with "
    "seizures_per_cluster range 3-4; clusters spaced five days apart is rate 1 per 5 day; two "
    "clusters this month is count 2 with the period. Clusters with no cadence, count or size "
    "are not findings. Observed cluster counts require period or occurred_at.",
    "Seizure_free requires duration or since: seizure-free for 14 months, none since March, no "
    "seizures in the past year. Absence of one event type is not absence of all seizures. "
    "Last_seizure requires occurred_at and is used only when the source calls the event the "
    "latest or last; a dated event without that is a count.",
    "Qualitative frequency must be one of rare, occasional, frequent, increased, decreased, "
    "unchanged, variable or unknown. Map infrequent, intermittent and sporadic to occasional; "
    "most days and near-daily to frequent; more frequent and worsening frequency to increased; "
    "less frequent and reduced to decreased; not documented or unable to quantify to unknown. "
    "Use increased, decreased or unchanged only when the sentence is about frequency.",
    "Quantities are number, range, bound (at_least, more_than, at_most, less_than) or "
    "qualitative quantity. There is no approximate flag and no inclusivity flag: the quotation "
    "carries about, roughly and on average. Durations use number, range or bound with a unit.",
    "Event.type is the source's words for the measured event; each quantified statement is one "
    "finding under its own label. Never merge, sum, distribute or link findings because two "
    "labels might name the same events. Scope is specific when the label itself names a seizure "
    "type, combined only for an explicit joint total, otherwise unspecified. Seizure_status is "
    "stated unless the source explicitly questions whether the events are seizures (uncertain) "
    "or excludes it (non_seizure); uncertain subtype, aetiology or classification does not "
    "change it.",
    "Timing is current by default and historical only when the source explicitly marks a "
    "superseded period (previously, before treatment, in 2015). Period and time points copy the "
    "source expression; add a numeric duration only when stated. Do not resolve relative dates, "
    "infer years or compute durations; annotate an impossible date literally.",
    "Condition is only a stated circumstance that restricts when the events occur (sleep or "
    "wake, time of day, a named trigger). Reporter, recording scope and hedges such as reported, "
    "witnessed, diary, typically and usually are not conditions; strip a leading hedge and keep "
    "the circumstance.",
    "Evidence is an exact quotation of the shortest contiguous span containing the measurement "
    "and its time or window. Extend backwards by at most one sentence, and only when the event "
    "label is absent from the measurement sentence. An identical measurement, label, timing, "
    "period and condition repeated within the letter is one finding; keep the first occurrence. "
    "A correction keeps only the corrected value.",
    "Collect explicitly labelled document dates in document_dates with role clinic, letter or "
    "unspecified, source time, form and exact evidence. Do not copy birth dates or seizure dates "
    "into document_dates. Document dates alone are not findings and do not change no-reference.",
    "Link the answer to unique finding IDs in selected_ids; an unknown answer still needs "
    "supporting findings and evidence. For no-reference return empty findings and selected_ids "
    "and null answer.evidence. Omit absent optional fields rather than emitting null; keep "
    "required answer, findings and selected_ids even when the latter two are empty. Do not add "
    "confidence, rationale or duplicate raw-value fields.",
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


def _case(
    name: str,
    note: str,
    findings: list[dict[str, Any]],
    *,
    answer: dict[str, Any] | None = None,
    selected: list[str] | None = None,
    document_dates: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    for index, finding in enumerate(findings, start=1):
        finding.setdefault("id", f"f{index}")
        finding["event"].setdefault("scope", derive_scope(finding["event"]["type"]))
        finding["event"].setdefault("seizure_status", "stated")
        finding.setdefault("timing", "current")
    output: dict[str, Any] = {
        "answer": answer or {"label": "unknown", "evidence": findings[0]["evidence"]},
        "findings": findings,
        "selected_ids": selected
        if selected is not None
        else ([findings[0]["id"]] if findings else []),
    }
    if document_dates:
        output["document_dates"] = document_dates
    return {
        "name": name,
        "note_text": note,
        "scope": "representation only; answer placeholder unless stated",
        "output": output,
    }


def fictional_cases() -> list[dict[str, Any]]:
    """Fictional representation checks for guide v0.7 conventions; not prompt examples."""
    one = {"type": "number", "value": 1}
    week = {"type": "number", "value": 1, "unit": "week"}
    month = {"type": "number", "value": 1, "unit": "month"}

    def rate(count: dict[str, Any], per: dict[str, Any]) -> dict[str, Any]:
        return {"type": "rate", "count": count, "per": per}

    gtc = "He has a generalised tonic-clonic seizure every four to six weeks."
    monthly = "She has monthly clusters, typically three to four seizures over 24 hours."
    last = "His last seizure was on 12 June 2025 and he has been seizure-free since then."
    denial = (
        "She has about two absences a week. There are no auras and no"
        " history of status epilepticus."
    )
    hist = "Previously he had frequent nocturnal convulsions; these are now rare."
    vague = (
        "He describes several possible seizures per month; it is uncl"
        "ear whether these are epileptic."
    )

    cases = [
        _case(
            "cadence_range_is_rate",
            gtc,
            [
                {
                    "event": {"type": "generalised tonic-clonic seizure"},
                    "measurement": rate(
                        one, {"type": "range", "lower": 4, "upper": 6, "unit": "week"}
                    ),
                    "evidence": gtc,
                }
            ],
        ),
        _case(
            "singular_article_cadence_is_rate",
            "She reports an absence seizure every night.",
            [
                {
                    "event": {"type": "absence seizure"},
                    "measurement": rate(one, {"type": "number", "value": 1, "unit": "day"}),
                    "condition": "at night",
                    "evidence": "She reports an absence seizure every night.",
                }
            ],
        ),
        _case(
            "bounded_rate",
            "He has up to three focal seizures a week, usually on waking.",
            [
                {
                    "event": {"type": "focal seizures"},
                    "measurement": rate({"type": "bound", "relation": "at_most", "value": 3}, week),
                    "condition": "on waking",
                    "evidence": "He has up to three focal seizures a week, usually on waking.",
                }
            ],
        ),
        _case(
            "alternative_count_is_range",
            "She had three or five seizures last month.",
            [
                {
                    "event": {"type": "seizures"},
                    "measurement": {
                        "type": "count",
                        "count": {"type": "range", "lower": 3, "upper": 5},
                    },
                    "period": {"time": "last month"},
                    "evidence": "She had three or five seizures last month.",
                }
            ],
        ),
        _case(
            "seizure_days_count",
            "Seizure days: 8/30 this month.",
            [
                {
                    "event": {"type": "seizure days"},
                    "measurement": {"type": "count", "count": {"type": "number", "value": 8}},
                    "period": {"time": "this month"},
                    "evidence": "Seizure days: 8/30 this month.",
                }
            ],
        ),
        _case(
            "cluster_rate_with_size",
            monthly,
            [
                {
                    "event": {"type": "clusters"},
                    "measurement": {
                        "type": "cluster",
                        "rate": {"count": one, "per": month},
                        "seizures_per_cluster": {"type": "range", "lower": 3, "upper": 4},
                    },
                    "evidence": monthly,
                }
            ],
        ),
        _case(
            "anchored_freedom_and_last_event",
            last,
            [
                {
                    "event": {"type": "seizure"},
                    "measurement": {
                        "type": "last_seizure",
                        "occurred_at": {"time": "12 June 2025", "form": "calendar"},
                    },
                    "evidence": last,
                },
                {
                    "id": "f2",
                    "event": {"type": "seizure"},
                    "measurement": {
                        "type": "seizure_free",
                        "since": {"time": "since then", "form": "relative"},
                    },
                    "evidence": last,
                },
            ],
        ),
        _case(
            "bare_denials_excluded",
            denial,
            [
                {
                    "event": {"type": "absences"},
                    "measurement": rate({"type": "number", "value": 2}, week),
                    "evidence": "She has about two absences a week.",
                }
            ],
        ),
        _case(
            "closed_vocabulary_and_historical",
            hist,
            [
                {
                    "event": {"type": "nocturnal convulsions"},
                    "measurement": {"type": "qualitative", "frequency": "frequent"},
                    "timing": "historical",
                    "condition": "nocturnal",
                    "evidence": hist,
                },
                {
                    "id": "f2",
                    "event": {"type": "nocturnal convulsions"},
                    "measurement": {"type": "qualitative", "frequency": "rare"},
                    "condition": "nocturnal",
                    "evidence": hist,
                },
            ],
        ),
        _case(
            "uncertain_identity_with_vague_count",
            vague,
            [
                {
                    "event": {"type": "possible seizures", "seizure_status": "uncertain"},
                    "measurement": rate({"type": "qualitative", "quantity": "several"}, month),
                    "evidence": vague,
                }
            ],
        ),
        _case(
            "combined_total_and_quarter",
            "Focal and tonic-clonic seizures total four per quarter.",
            [
                {
                    "event": {"type": "Focal and tonic-clonic seizures"},
                    "measurement": rate(
                        {"type": "number", "value": 4},
                        {"type": "number", "value": 1, "unit": "quarter"},
                    ),
                    "evidence": "Focal and tonic-clonic seizures total four per quarter.",
                }
            ],
        ),
        _case(
            "document_dates_without_findings",
            "Clinic Date: 14 September 2026. Blood pressure was measured.",
            [],
            answer={"label": "no seizure frequency reference", "evidence": None},
            selected=[],
            document_dates=[
                {
                    "role": "clinic",
                    "time": "14 September 2026",
                    "form": "calendar",
                    "evidence": "Clinic Date: 14 September 2026",
                }
            ],
        ),
    ]
    assert cases[10]["output"]["findings"][0]["event"]["scope"] == "combined"
    return cases
