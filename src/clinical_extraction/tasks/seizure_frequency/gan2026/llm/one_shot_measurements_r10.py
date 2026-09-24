"""R10 compact v0.3 prompt candidate with bounded diary totals.

The native selected-frequency answer and its decision cases still use one call.
The returned findings follow the owner-reviewed compact annotation policy.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from clinical_extraction.tasks.seizure_frequency.gan2026.llm import (
    one_shot_measurements_r8 as r8,
)

VERSION = "one_shot_frequency_v2_measurements_r10"
REVISION = "compact_scored_terms_v03_diary_totals_v01"
GUIDE_VERSION = "seizure_finding_annotation_compact_v0.3"
SCHEMA_PATH = (
    Path(__file__).resolve().parents[6]
    / "results/letter-benchmarks/gan/one_shot_frequency_compact_scope_candidate_no_call/"
    "rich.v0_2.schema.json"
)

TASK = (
    "Read the full clinical note, decide how often the patient's seizures are happening "
    "now, and return that answer with the compact seizure-activity claims that qualify "
    "under the supplied policy."
)

INSTRUCTIONS = [
    "Consider all seizure-frequency evidence in the note when choosing answer.label. "
    "Use the allowed label forms and the decision cases below for that native answer. "
    "The cases' facts are intermediate evidence, not a request to return every fact "
    "as a finding. Their fact IDs, raw values and normalized labels are not response fields.",
    "Return answer and findings together in exactly one JSON object matching output_schema. "
    "Do not add explanation, confidence, document dates or fields from the cases.",
    "Use no seizure frequency reference only when the note has no usable seizure-frequency "
    "evidence; then answer.evidence is null, answer.claim_indices and findings are empty. "
    "When seizures are discussed but their frequency is unclear, use unknown with an "
    "exact supporting answer quotation. A native answer may use context that does not "
    "qualify as a compact finding; leave claim_indices empty in that case rather than "
    "inventing a finding.",
    "Keep an explicitly identified last event separate from a current seizure-free "
    "claim. The native answer cases may combine or convert source facts for the answer; "
    "do not overwrite the literal measurements in findings with that conversion.",
    "Every evidence fragment and non-null answer.evidence must be an exact substring "
    "of the note. Use answer.claim_indices only for findings that actually support "
    "the answer; indices are zero-based positions in the returned findings array.",
    "Use the decision cases below to choose the patient's current seizure-frequency "
    "answer. If a case matches, follow it; create a new label only when no single "
    "source fact supplies the answer.",
]

SCHEMA_INSTRUCTIONS = [
    "Emit only primary findings: each distinct source-stated measurement of current "
    "seizure activity, one explicitly identified last or most recent event, at most "
    "the nearest earlier measured state explicitly contrasted with each current "
    "event population, and the most recent measured activity claim if no current "
    "measurement is given. An ordinary dated event is not automatically the last event. "
    "Do not infer a comparison from diary chronology. A separately changed named "
    "subtype may warrant its own nearest comparator.",
    "Decide eligibility in this order: establish a patient seizure or explicit clinical "
    "link to an established seizure type; identify a supported measurement; determine "
    "event population, counted unit, source window and meaningful restriction; select "
    "current, explicit last event, nearest linked comparator or fallback; then combine "
    "only true restatements of the same population, unit and window. Exclude plans, "
    "thresholds, family history, explicit non-seizures and unlinked symptoms. A linked "
    "possible seizure retains status uncertain. A seizure-frequency heading can link "
    "its immediately listed events; a diagnosis or diary heading alone does not make "
    "every nearby symptom a seizure.",
    "Current means applying at the clinical assessment, not merely dated within a "
    "year. Set time.phase to ongoing, superseded or past_or_unclear from the clinical "
    "sequence. Preserve time.source literally when the source gives a window or date. "
    "An old count is past_or_unclear by default, not a current rate. Do not calculate "
    "recency, repair contradictory dates or invent a transition date. Preserve distinct "
    "contradictory source assertions as separate findings with their own windows and "
    "evidence; do not let one silently override the other.",
    "Use event.scope overall for an explicitly overall population, named for a stated "
    "subtype, combined for an explicit joint population, and unspecified when the "
    "source leaves the population unresolved. Event.label is concise and source "
    "supported. Carry a subtype into its measurement only when the source links them. "
    "Do not narrow an overall total to the predominant subtype or infer tonic-clonic "
    "seizures from the broader phrase generalised seizures. Keep two named counts "
    "separate when their overlap is unstated.",
    "Use familiar named seizure types when the source supports them: focal aware, "
    "focal impaired-awareness, focal to bilateral tonic-clonic, generalised "
    "tonic-clonic, absence, myoclonic, tonic, atonic, aura, epileptic spasm, "
    "or status epilepticus. Preserve a source-supported unclassified label "
    "when no type is established. Words such as brief, nocturnal, awake, "
    "clustered or provoked do not by themselves establish a formal subtype. "
    "Use restriction and counted_unit for meaningful limits; do not make a "
    "more specific subtype solely to repeat a descriptive modifier.",
    "Set counted_unit to individual_seizure, seizure_day, seizure_night, cluster, "
    "cluster_day, status_episode or not_applicable as the source warrants. Affected "
    "days or nights are not counts of individual seizures. Explicit seizures every "
    "night without a per-night event count measure affected seizure_nights; most "
    "nights does not imply an exact nightly rate. A named status-epilepticus episode "
    "count is status_episode, not individual seizures, attendances or rescue doses.",
    "Use measurement.kind rate only for a stated recurrence; observed_count requires "
    "a source window or date in time.source. Keep stated quantity, bound and denominator "
    "without converting a source measurement. Bare daily cadence uses one per day "
    "only when its counted unit is supported. For this candidate, bimonthly means "
    "once every two months unless the source explicitly defines it differently. "
    "An explicitly stated median inter-seizure duration is median_interval with "
    "counted_unit not_applicable, never a regular rate. A prior comparator with an "
    "irreducibly unclear counted unit is context, not a guessed rate.",
    "For a bounded diary, return one observed_count total when its explicitly "
    "listed components are disjoint, have the same counted unit and belong to "
    "the same assessed window. Sum across listed months or complementary "
    "sleep/awake counts only when overlap is ruled out by the source. Preserve "
    "the supported population and its limits. A cluster's stated size counts "
    "individual seizures; the cluster itself is not another seizure. Do not "
    "add subtype progressions or other subsets twice. Do not fill unreported "
    "months with zero, invent a recurring rate, or sum ambiguous components. "
    "Return the diary total once; individual month or timing components are "
    "evidence or context unless they are a distinct named subtype finding.",
    "Use one cluster measurement for stated cluster count, cadence and size. A "
    "single grouped occurrence can be one cluster. For two cluster days this month, "
    "usually six seizures each within 24 hours, use counted_unit cluster_day, "
    "cluster count two, seizures_per_cluster six and time.source this month. The "
    "within-cluster span belongs in evidence, not the observation window. Do not "
    "duplicate the cluster-day claim as a seizure-day count or treat a cluster "
    "as one individual seizure.",
    "Use seizure_free only for explicit zero activity over a stated duration or "
    "since anchor. A known interval under two weeks, an unanchored denial, and "
    "ordinary or typical gaps between recurring events are context. An explicit "
    "longest or maximum seizure-free gap of at least two weeks is a separate "
    "past_or_unclear claim; preserve its literal event scope. An anchor with "
    "unresolved duration remains eligible when it states an absence and is not "
    "known to be shorter than two weeks. Restrict a device, diary or appointment "
    "absence to what was actually recorded or reported; it does not prove global "
    "clinical seizure freedom. A limited subtype absence is not overall freedom.",
    "Use qualitative only for a standalone occasional or frequent frequency level "
    "with no more precise measurement of the same population and window. Trend-only "
    "wording, most-weeks/months occupancy without an accepted event quantity, "
    "corroboration, old diary details, trigger or time-of-day breakdowns without "
    "a distinct named subtype, and less precise restatements remain context. "
    "Do not add a qualitative duplicate of a numeric finding.",
    "Use restriction only when it changes the counted population or denominator, "
    "including witnessed-only, while asleep or recorded-since-visit scope. Keep "
    "source-supported event labels and windows separate from restrictions. Each "
    "finding.evidence is one or more exact fragments collectively supporting "
    "its event, unit, status, measurement, phase, source window and restriction. "
    "Apart from the bounded diary sum above, do not infer arithmetic, duration, "
    "subtype, seizure status or missing dates. "
    "When a precise statement and a less precise one measure the same claim, "
    "return the precise one once and add the other quotation only if useful.",
]


def prompt_payload(note: str) -> dict[str, Any]:
    """Keep native label forms and cases while replacing the inventory contract."""
    payload = r8.prompt_payload(note)
    payload["task"] = TASK
    payload["instructions"] = list(INSTRUCTIONS)
    payload["schema_instructions"] = list(SCHEMA_INSTRUCTIONS)
    payload["output_schema"] = json.loads(SCHEMA_PATH.read_text())
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
