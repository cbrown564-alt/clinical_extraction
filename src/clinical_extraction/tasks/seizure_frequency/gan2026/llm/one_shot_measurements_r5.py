"""R5 source measurements; r4 remains frozen for replay."""

from __future__ import annotations

import copy
import json
from typing import Annotated, Any, Literal, Self

from dspy.adapters.chat_adapter import ChatAdapter
from pydantic import Field, model_validator

from clinical_extraction.tasks.seizure_frequency.gan2026.llm import one_shot_measurements as r4

VERSION = "one_shot_frequency_v2_measurements_r5"


class QualitativeQuantity(r4.v1.StrictRecord):
    kind: Literal["qualitative"]
    wording: r4.Text


Quantity = Annotated[
    r4.Exact | r4.Range | r4.Bound | QualitativeQuantity, Field(discriminator="kind")
]


class TimePoint(r4.v1.StrictRecord):
    wording: r4.Text
    form: Literal["calendar", "relative"]
    precision: Literal["second", "minute", "hour", "day", "week", "month", "year", "unspecified"]


class ObservationPeriod(r4.v1.StrictRecord):
    wording: r4.Text
    start: TimePoint | None
    end: TimePoint | None
    duration: r4.Duration | None


class RecurringRate(r4.v1.StrictRecord):
    kind: Literal["recurring_rate"]
    count: Quantity
    denominator: r4.Duration


class ObservedCount(r4.v1.StrictRecord):
    kind: Literal["observed_count"]
    count: Quantity


class ClusterPattern(r4.v1.StrictRecord):
    kind: Literal["cluster_pattern"]
    cadence: RecurringRate | None
    seizures_per_cluster: Quantity | None


class SeizureFreeInterval(r4.v1.StrictRecord):
    kind: Literal["seizure_free_interval"]
    duration: r4.Duration | None
    since: TimePoint | None


class LastSeizure(r4.v1.StrictRecord):
    kind: Literal["last_seizure"]
    when: TimePoint


Measurement = Annotated[
    RecurringRate
    | ObservedCount
    | ClusterPattern
    | SeizureFreeInterval
    | LastSeizure
    | r4.QualitativeFrequency,
    Field(discriminator="kind"),
]


class Finding(r4.v1.StrictRecord):
    finding_id: r4.Text
    event: r4.EventScope
    measurement: Measurement
    temporal_status: Literal["current", "recent", "historical", "future", "unclear"]
    observation_period: ObservationPeriod | None
    condition: r4.Text | None
    evidence: r4.Text


class Rich(r4.v1.StrictRecord):
    answer: r4.v1.Answer
    findings: list[Finding]
    selected_finding_ids: list[r4.Text]

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


def prompt_payload(note: str) -> dict[str, Any]:
    payload = copy.deepcopy(r4.prompt_payload(note, "rich"))
    payload["output_schema"] = Rich.model_json_schema()
    instructions = payload["schema_instructions"]
    old = (
        "Retain observation periods separately from rate denominators. Use "
        "measurement.interval for observed counts and observation_period for other "
        "findings only when explicitly stated."
    )
    new = (
        "Retain observation periods separately from rate denominators. Use "
        "observation_period for every finding, including observed counts, only when "
        "explicitly stated. There is no interval field inside an observed-count "
        "measurement."
    )
    assert old in instructions
    instructions[instructions.index(old)] = new
    instructions.extend(
        [
            (
                "A cluster_pattern may have null cadence and null seizures_per_cluster when "
                "neither is quantified. The evidence preserves the stated cluster pattern. A "
                "qualitative quantity uses kind qualitative and wording such as multiple; do "
                "not invent a number."
            ),
            (
                "Time precision may be second, minute, hour, day, week, month, year or "
                "unspecified, following the stated expression. Preserve its original wording "
                "without inventing dates."
            ),
            (
                "Durations must be positive. Ongoing seizures are not a zero-duration "
                "seizure-free interval. Use null duration only when a seizure-free statement "
                "gives no duration."
            ),
            (
                "An unknown answer still links to its supporting findings. For example, for "
                "Possible seizures continue but their frequency is unclear, a "
                "qualitative_frequency finding f1 retains frequency is unclear and "
                "uncertainty about the events; answer.label is unknown and "
                "selected_finding_ids is [f1]. Copy the supporting source text into "
                "answer.evidence."
            ),
        ]
    )
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
    cases = copy.deepcopy(r4.fictional_cases())
    for case in cases:
        for finding in case["output"]["findings"]:
            if finding["measurement"]["kind"] == "observed_count":
                finding["observation_period"] = finding["measurement"].pop("interval")
    base = copy.deepcopy(cases[0])
    specs = [
        (
            "unquantified_cluster",
            "Seizures occur in clusters.",
            "unknown",
            {"kind": "cluster_pattern", "cadence": None, "seizures_per_cluster": None},
        ),
        (
            "qualitative_cluster_size",
            "She has weekly clusters with multiple seizures per cluster.",
            "1 cluster per week, multiple per cluster",
            {
                "kind": "cluster_pattern",
                "cadence": {
                    "kind": "recurring_rate",
                    "count": r4._exact(1),
                    "denominator": r4._duration(1, "week"),
                },
                "seizures_per_cluster": {"kind": "qualitative", "wording": "multiple"},
            },
        ),
        (
            "weekly_precision",
            "Her last seizure was two weeks ago.",
            "unknown",
            {
                "kind": "last_seizure",
                "when": {"wording": "two weeks ago", "form": "relative", "precision": "week"},
            },
        ),
        (
            "unknown_link",
            "Possible seizures continue but their frequency is unclear.",
            "unknown",
            {"kind": "qualitative_frequency", "wording": "frequency is unclear"},
        ),
    ]
    for name, note, label, measurement in specs:
        case = copy.deepcopy(base)
        case.update(name=name, note_text=note)
        case["output"]["answer"] = {"label": label, "evidence": note}
        finding = case["output"]["findings"][0]
        finding.update(
            measurement=measurement,
            evidence=note,
            event={
                "description": "seizures",
                "grouping": "unspecified",
                "seizure_interpretation": "uncertain_seizure"
                if name == "unknown_link"
                else "stated_seizure",
            },
        )
        cases.append(case)
    return cases
