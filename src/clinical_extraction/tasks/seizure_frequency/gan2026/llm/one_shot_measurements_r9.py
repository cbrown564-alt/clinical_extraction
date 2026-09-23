"""Prospective R9 prompt candidate for the v0.8.1 finding rules.

This is not the saved R8 prompt. No model response or result is attributed to it.
"""

from __future__ import annotations

import json
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    one_shot_measurements_r8 as r8,
)

VERSION = "one_shot_frequency_v2_measurements_r9"
REVISION = "guide_v081_concise_event_labels_candidate"
GUIDE_VERSION = "seizure_finding_annotation_v0.8.1"
Rich = r8.Rich


def replace_instruction(prefix: str, replacement: str) -> None:
    matches = [i for i, line in enumerate(SCHEMA_INSTRUCTIONS) if line.startswith(prefix)]
    if len(matches) != 1:
        raise ValueError(f"Expected one R8 instruction beginning {prefix!r}")
    SCHEMA_INSTRUCTIONS[matches[0]] = replacement


SCHEMA_INSTRUCTIONS = list(r8.SCHEMA_INSTRUCTIONS)
replace_instruction(
    "Count is events",
    "Count is observed events in a stated window or on a date; a count in one "
    "past week is not an ongoing per-week rate. Keep event type separate from the "
    "counted unit: 'absence seizures on two to three days per week' measures "
    "absence-seizure days, not two to three individual seizures. Add counts for "
    "the same event across named diary months or individually dated occurrences "
    "into one count over the listed interval; do not combine distinct event types.",
)
replace_instruction(
    "Cluster keeps",
    "For a simple count of clusters, use ordinary count with the counted event "
    "named as clusters. Use cluster measurement when the source states seizures "
    "per cluster or a recurring cluster cadence. Never treat a count of clusters "
    "as the same number of individual seizures.",
)
replace_instruction(
    "Seizure_free requires",
    "Seizure_free requires a duration or since anchor. When a duration is stated, "
    "it is the scored interval; retain a co-stated since anchor as additional "
    "source detail. For an anchor-only claim, keep the source anchor. One continuous "
    "absence interval for the same event scope is one finding even if restated "
    "elsewhere. A single denial listing several named seizure types is one combined "
    "finding that retains the named types; do not broaden a limited list to all "
    "events. A last-seizure statement remains a separate finding.",
)
replace_instruction(
    "Qualitative frequency must",
    "A standalone qualitative frequency must be occasional or frequent. Map rare, "
    "infrequent, intermittent and sporadic to occasional. Do not score trend or "
    "variability words such as increased, decreased, unchanged or variable as "
    "separate findings, and do not add a qualitative duplicate when a numeric "
    "measurement already expresses the same claim.",
)
replace_instruction(
    "Event.type is",
    "Event.type is a short, source-supported name for the measured event and its "
    "counted unit. Omit incidental descriptors such as 'brief' when they do not "
    "identify a different event: 'brief nocturnal episodes' and 'nocturnal "
    "episodes' use the same label. Put triggers and observation time in condition "
    "or period instead of extending the event name. Preserve a stated seizure "
    "subtype, including when the next sentence says only 'seizure frequency' "
    "for the event just described. Preserve the distinction between seizures, "
    "seizure days and clusters, and "
    "a combined list only when the same measurement applies to every named type. "
    "For a combined absence list, retain the named types in one event label. "
    "Do not infer a more specific seizure diagnosis from a symptom description. "
    "Keep distinct seizure types, observation windows, seizure-day units and "
    "individual seizure counts separate. "
    "Seizure_status is stated unless the source explicitly questions whether "
    "events are seizures or excludes seizure identity.",
)
replace_instruction(
    "Timing is",
    "Use the clinic date, or the letter date if no clinic date is available, as "
    "the timing reference. Historical means the measured event or observation "
    "interval ended more than one calendar year before that date. Exactly one "
    "year ago and anything more recent are current, even when the event is called "
    "'initial' or 'previous'. A window that reaches into the last year is current. "
    "An ongoing present pattern or seizure-free state is current even if it began "
    "more than a year ago. If no usable date can be determined, explicit past "
    "wording such as 'previously' or 'in childhood' makes the finding historical; "
    "otherwise default to current. Compare dates only to assign timing. Preserve "
    "the source time phrase in occurred_at, period and evidence; do not invent a "
    "new date, duration or year.",
)
replace_instruction(
    "Evidence is",
    "Evidence is an exact source quotation supporting the event, measurement "
    "and time. One clinical claim in one observation interval is one finding "
    "when repeated across the letter. Keep the first suitable quotation unless "
    "a later statement corrects it. Separate genuinely distinct event types, "
    "counted units and observation windows.",
)


def prompt_payload(note: str) -> dict[str, Any]:
    payload = r8.prompt_payload(note)
    schema = payload["output_schema"]
    schema["$defs"]["QualitativeFrequency"]["properties"]["frequency"]["enum"] = [
        "occasional",
        "frequent",
    ]
    payload["schema_instructions"] = SCHEMA_INSTRUCTIONS
    return payload


def messages(note: str) -> list[dict[str, Any]]:
    return r8.ChatAdapter().format(
        r8.r4.MeasurementSignature,
        demos=[],
        inputs={
            "prompt_input_json": json.dumps(
                prompt_payload(note), ensure_ascii=False, sort_keys=True
            )
        },
    )
