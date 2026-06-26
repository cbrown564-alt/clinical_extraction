"""Stage 1: clinical-findings extraction (LLM + parse/coerce)."""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any

import dspy
from pydantic import ValidationError

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.clinical_findings.constants import (
    PROMPT_VERSION,
    _CLINICAL_KIND_VALUES,
    _DISALLOWED_MODEL_PROJECTION_FIELDS,
    _SCALAR_EVENT_FRAME_FIELDS,
    _SCALAR_FINDING_FIELDS,
    _STATEMENT_TYPE_TO_KIND,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.clinical_findings.types import (
    ClinicalFindingRecord,
    ClinicalFindingsRecord,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.json_parse import (
    loads_json_or_literal,
)

class ExECTv2ClinicalFindingsSFSignature(dspy.Signature):
    """Read one clinical letter and return seizure frequency findings as JSON.

    Return a strict JSON object with key 'findings'. No markdown wrapper.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter and task instructions."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"event_frames\": [{\"event_id\": ..., "
            "\"evidence\": ..., \"seizure_phrase\": ..., \"target_status\": ..., "
            "\"statement_family\": ...}], \"findings\": [{\"text\": ..., "
            "\"evidence\": ..., \"clinical_kind\": ..., "
            "\"frequency_statement_type\": ..., \"source_role\": ..., "
            "\"count\": ..., \"period_unit\": ..., \"confidence\": ..., "
            "\"rationale\": ...}, ...]}"
        )
    )


class DspyClinicalFindingsSFExtractor(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2ClinicalFindingsSFSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)

def build_prompt_input(letter: ExectLetter) -> str:
    """Build the clinical-findings prompt payload for one letter."""

    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": (
            "Read the clinical letter and list each seizure type or seizure-free "
            "state that has frequency information. First enumerate model-owned "
            "event_frames for every possible seizure-frequency or non-target episode "
            "fact, then convert only target event_frames into the final 'findings' "
            "list. Return one JSON object."
        ),
        "event_frame_schema": {
            "event_id": "Short stable id such as e1, e2, e3.",
            "evidence": (
                "Exact source substring containing the seizure-frequency or "
                "non-target episode fact."
            ),
            "seizure_phrase": (
                "Exact source-near phrase naming the seizure type, seizure-free "
                "state, or non-target episode. Do not include context words that "
                "describe preserved awareness, triggers, symptoms, or uncertainty "
                "unless they are part of the scored seizure-type phrase."
            ),
            "target_status": (
                "target_epileptic_seizure_frequency, non_target_episode, "
                "history_context_only, diagnosis_without_frequency, "
                "future_risk_or_driving, or uncertain_not_scored."
            ),
            "statement_family": (
                "header_count_since_anchor, calendar_count, "
                "calendar_occurrence_no_count, recurrence_interval, last_event_date, "
                "background_rate, seizure_free_duration, current_control_no_duration, "
                "current_zero_no_duration, change_only, cluster, non_target, or "
                "other_frequency."
            ),
            "source_role": "compact_section, narrative, or both.",
            "count": "Single seizure count when stated or implied by one event.",
            "count_low": "Lower seizure count when a range is stated.",
            "count_high": "Upper seizure count when a range is stated.",
            "period_count": "Number of denominator time periods, usually 1.",
            "period_low": "Lower denominator period count when a range is stated.",
            "period_high": "Upper denominator period count when a range is stated.",
            "period_unit": "day, week, month, or year when stated.",
            "time_relation": "during or since when explicitly stated.",
            "point_in_time": "Clinical anchor such as last clinic or medication change.",
            "day/month/year": "Calendar date fields when explicitly stated.",
            "age_low/age_high/age_unit": "Age anchor when explicitly stated.",
            "frequency_change": "decreased, frequent, increased, infrequent, or same.",
            "finding_text": (
                "Exact text that should be used in findings if include_as_finding is "
                "true. This may be shorter than seizure_phrase when evidence includes "
                "context such as 'without change in awareness'."
            ),
            "include_as_finding": (
                "true only for event_frames that should become scored findings."
            ),
            "rationale": "One concise clinical reading of this event frame.",
        },
        "output_schema": {
            "text": (
                "Exact short phrase from the letter naming the seizure type or "
                "seizure-free state, such as 'focal seizures', 'absences', "
                "'generalised tonic-clonic seizures', or 'seizure free'."
            ),
            "evidence": (
                "Exact substring from the letter that supports this finding. Use "
                "the smallest clause or sentence that includes the frequency."
            ),
            "clinical_kind": (
                "One of frequency_rate, seizure_free, frequency_change, dated_count, "
                "last_event, cluster_frequency, other_frequency."
            ),
            "frequency_statement_type": (
                "Classify the statement before filling fields: header_count_since_anchor, "
                "calendar_count, calendar_occurrence_no_count, recurrence_interval, "
                "last_event_date, background_rate, seizure_free_duration, "
                "current_control_no_duration, current_zero_no_duration, change_only, "
                "or other_frequency."
            ),
            "source_role": (
                "compact_section, narrative, or both. Use compact_section for facts "
                "listed in short headed lines such as seizure type and frequency."
            ),
            "count": (
                "Single seizure count when stated. For every 3 to 4 weeks, "
                "the count is 1."
            ),
            "count_low": "Lower seizure count when a range is stated.",
            "count_high": "Upper seizure count when a range is stated.",
            "period_count": "Number of time periods, usually 1.",
            "period_low": "Lower time-period count when a period range is stated.",
            "period_high": "Upper time-period count when a period range is stated.",
            "period_unit": "day, week, month, or year when stated.",
            "time_relation": "during or since when explicitly stated.",
            "point_in_time": (
                "Clinical anchor when explicitly stated, for example medication "
                "change, last clinic, last month, last week, last year, surgery, "
                "or birthday."
            ),
            "day": "Day of month when explicitly stated.",
            "month": "Month when explicitly stated.",
            "year": "Year when explicitly stated.",
            "age_low": "Lower patient age when an age or age range is stated.",
            "age_high": "Upper patient age when an age range is stated.",
            "age_unit": "year or month when age_low or age_high is stated.",
            "frequency_change": (
                "decreased, frequent, increased, infrequent, or same when a change "
                "or relative frequency is stated."
            ),
            "confidence": "high, medium, or low.",
            "rationale": "One concise sentence explaining the clinical reading.",
        },
        "required_keys_per_finding": [
            "text",
            "evidence",
            "clinical_kind",
            "frequency_statement_type",
            "source_role",
            "count",
            "count_low",
            "count_high",
            "period_count",
            "period_low",
            "period_high",
            "period_unit",
            "time_relation",
            "point_in_time",
            "day",
            "month",
            "year",
            "age_low",
            "age_high",
            "age_unit",
            "frequency_change",
            "confidence",
            "rationale",
        ],
        "clinical_rules": [
            (
                "Fill event_frames before findings. Each event_frame is a model-owned "
                "clinical reading of one possible seizure-frequency, seizure-free, "
                "last-event, change, cluster, or non-target episode fact."
            ),
            (
                "Use event_frames to separate coverage from scoring: include target "
                "epileptic seizure-frequency frames in findings, but keep non-target "
                "episode/history/driving/diagnosis frames out of findings."
            ),
            (
                "Every finding should correspond to one target event_frame. If a "
                "target event_frame has include_as_finding true, copy its exact "
                "finding_text when supplied; otherwise copy its seizure_phrase. Also "
                "copy evidence, statement family, count, period, and time fields "
                "unless there is a clear reason not to score it."
            ),
            (
                "event_frames are planning and audit output, not a shortcut. Do not "
                "invent a finding without exact source evidence, and do not let a "
                "non-target event_frame become a scored finding."
            ),
            (
                "Every finding must include frequency_statement_type and source_role. "
                "Use null for unknown optional numeric/date fields, but do not omit keys."
            ),
            (
                "Use one finding per seizure type. If the letter separately describes "
                "focal seizures and tonic-clonic seizures, return two findings."
            ),
            (
                "Pay close attention to compact sections headed seizure type and "
                "frequency. Treat comma-separated items in those sections as findings, "
                "not only the prose paragraphs."
            ),
            (
                "If the same seizure type has two distinct frequency facts with "
                "different time context, return two findings for that same text."
            ),
            (
                "If a compact frequency section states a fact and a later narrative "
                "sentence repeats the same fact, return both findings with their own "
                "exact evidence strings."
            ),
            (
                "A current seizure-free or controlled statement does not replace "
                "historical compact-section seizure-frequency facts. If a compact "
                "section lists dated seizure-type facts and the narrative later says "
                "the patient remains seizure free, return the dated facts as findings "
                "and treat the current-control statement separately."
            ),
            (
                "Both text and evidence must be copied exactly from the letter. If no "
                "exact phrase can be copied, omit that finding."
            ),
            (
                "Prefer source-near wording. Do not rewrite the seizure type into a "
                "different clinical concept."
            ),
            (
                "For rates such as 2 to 3 per month, set count_low, count_high, "
                "period_count, and period_unit."
            ),
            (
                "For header counts anchored to clinic review, such as several "
                "seizures since clinic review, set frequency_statement_type to "
                "header_count_since_anchor, count to 3 when the word is several, "
                "time_relation to since, and point_in_time to last clinic."
            ),
            (
                "For dated counts such as in March she had 2 to 3 seizures, set "
                "clinical_kind to dated_count, fill month and time_relation, and "
                "do not fill period_count or period_unit unless words like per "
                "month or every month are present."
            ),
            (
                "For a dated occurrence with no explicit count, such as absence "
                "like seizures in 2018, set frequency_statement_type to "
                "calendar_occurrence_no_count, clinical_kind to dated_count, "
                "year to 2018, and time_relation to during."
            ),
            (
                "For every 2 to 3 weeks, set count to 1, period_low to 2, "
                "period_high to 3, and period_unit to week."
            ),
            (
                "For seizure-free duration, set clinical_kind to seizure_free and "
                "fill period_count and period_unit when stated."
            ),
            (
                "For last-event statements such as last event July 2016, use the "
                "seizure type as text, clinical_kind last_event, count 0, "
                "time_relation since, and fill month and year."
            ),
            (
                "For vague counts, use these conventions: few or couple is 2, "
                "several is 3, and none or no is 0. Do not turn these words into "
                "count ranges."
            ),
            (
                "If evidence says generic seizures, keep text as seizures even if "
                "the diagnosis names a more specific seizure syndrome elsewhere. "
                "Do not replace generic seizures with the diagnosis term."
            ),
            (
                "If the evidence says focal seizures with altered, impaired, or "
                "lost awareness, keep that awareness modifier in text."
            ),
            (
                "If the evidence says focal seizures without change in awareness, "
                "use text focal seizures. Without change in awareness is context, "
                "not an impaired-awareness seizure-type modifier."
            ),
            (
                "Do not extract migraine/headache frequency, febrile-seizure history, "
                "family history, driving rules, future risk statements, or medication "
                "titration intervals."
            ),
            (
                "Do not extract blackouts, loss of consciousness episodes, dizzy "
                "spells, dissociative seizures, nonepileptic events, or generic events "
                "unless the evidence itself states these are epileptic seizures."
            ),
            (
                "Do not convert a diagnostic episode description into a seizure-frequency "
                "finding just because another sentence says the clinician suspects "
                "epilepsy or thinks the episodes may be seizures. The frequency evidence "
                "itself must name epileptic seizures or a seizure type."
            ),
            (
                "Do not extract minor seizures as target frequency when the evidence "
                "describes dizzy spells, headache, nausea, unresponsiveness, shaking, "
                "or other nonspecific episodes rather than a scored seizure type."
            ),
            (
                "Do not extract minor seizures, jerks, or episodes as scored seizure "
                "frequency even when a rate is stated, unless the same frequency clause "
                "itself explicitly names epileptic seizures or a standard seizure type "
                "such as focal seizures, absences, tonic-clonic seizures, myoclonic "
                "jerks, or convulsive seizures."
            ),
            (
                "Do not treat 'continues to get seizures' as a scored frequency-change "
                "finding unless the same evidence gives a count, rate, date, last-event "
                "anchor, or explicit qualitative change word such as increased, "
                "decreased, frequent, or infrequent."
            ),
            (
                "For a first or single diagnostic seizure encounter, do not score "
                "no previous seizures, no further episodes, future risk of seizures, "
                "or driving-clearance seizure windows as seizure-frequency findings."
            ),
            (
                "For last-event summaries, extract the most recent last event only. "
                "Do not add previous events as separate last-event findings."
            ),
            (
                "If a compact line says last event plus previous event, return the "
                "last event and do not return the older previous event. The previous "
                "event is context for the last-event summary, not another scored "
                "last-event finding."
            ),
            (
                "For a rate stated during a finite episode, keep the denominator "
                "separate from the episode duration. In '6-9 seizures every week "
                "for 3 weeks', the period_count is 1 and period_unit is week; the "
                "3 weeks is the duration of that episode, not the rate denominator."
            ),
            (
                "For cluster wording such as a cluster of seizures in August where "
                "seizures happened 6-9 every week, return one dated cluster-of-seizures "
                "finding and one separate within-cluster seizure-rate finding."
            ),
            (
                "When evidence says seizures have returned after seizure freedom, "
                "return a frequency_change finding with frequency_change increased "
                "if there is no exact count in that phrase."
            ),
            (
                "When evidence says a seizure type is infrequent, return a "
                "frequency_change finding with frequency_change infrequent. Do not "
                "turn older historical counts such as two in the year of diagnosis "
                "into a current rate unless the same clause gives a current period."
            ),
            (
                "For no further seizures or epileptic seizures under control, return "
                "a zero-count finding. If control follows a drug increase or medication "
                "change, set point_in_time to medication change."
            ),
            (
                "Do not score a bare current statement such as he remains seizure free "
                "or she remains seizure free when there is no duration, no date, no "
                "medication-change/surgery/clinic anchor, and no wording such as no "
                "further seizures. Put it in event_frames as current_control_no_duration "
                "with include_as_finding false."
            ),
            (
                "Use current_control_no_duration only for vague diagnosis-level phrases "
                "such as epilepsy seems under control, especially when no seizure type "
                "or no further seizures phrase is stated. For a specific seizure type "
                "or epileptic seizures completely under control after a medication "
                "increase, use current_zero_no_duration with count 0 and point_in_time "
                "medication change."
            ),
            (
                "For no further seizures, use text seizures and count 0. Do not rewrite "
                "the source phrase to seizure free unless the letter itself says seizure "
                "free."
            ),
            (
                "For last seizures in teenage years, use text seizures, count 0, "
                "time_relation since, age_low 13, age_high 19, and age_unit year. "
                "Do not extract accompanying migraine or febrile-seizure counts."
            ),
            (
                "Do not return a current seizure-free finding unless a duration, date, "
                "or clinical anchor is explicitly stated."
            ),
            (
                "For change-only statements, set clinical_kind to frequency_change "
                "and fill frequency_change."
            ),
            (
                "Only fill time_relation, point_in_time, day, month, or year when "
                "that context is explicitly stated in the letter."
            ),
            (
                "If the letter has no seizure frequency information, return "
                "{\"event_frames\": [], \"findings\": []}."
            ),
            "Return exactly one JSON object. No markdown code fences.",
        ],
        "event_frame_examples": [
            {
                "note_fragment": (
                    "In March she had 2 to 3 of her focal seizures without change "
                    "in awareness."
                ),
                "event_frames": [
                    {
                        "event_id": "e1",
                        "evidence": (
                            "In March she had 2 to 3 of her focal seizures without "
                            "change in awareness"
                        ),
                        "seizure_phrase": "focal seizures",
                        "target_status": "target_epileptic_seizure_frequency",
                        "statement_family": "calendar_count",
                        "source_role": "narrative",
                        "count_low": "2",
                        "count_high": "3",
                        "time_relation": "during",
                        "month": "March",
                        "finding_text": "focal seizures",
                        "include_as_finding": True,
                        "rationale": (
                            "Without change in awareness is context, so the scored "
                            "seizure phrase is focal seizures."
                        ),
                    }
                ],
            },
            {
                "note_fragment": (
                    "Seizure type and frequency: Generalised tonic clonic seizure-"
                    "last event July 2016. Previous event December 2015."
                ),
                "event_frames": [
                    {
                        "event_id": "e1",
                        "evidence": "Generalised tonic clonic seizure-last event July 2016",
                        "seizure_phrase": "Generalised tonic clonic seizure",
                        "target_status": "target_epileptic_seizure_frequency",
                        "statement_family": "last_event_date",
                        "source_role": "compact_section",
                        "count": "0",
                        "time_relation": "since",
                        "month": "July",
                        "year": "2016",
                        "finding_text": "Generalised tonic clonic seizure",
                        "include_as_finding": True,
                        "rationale": "The most recent last-event date is a scored finding.",
                    },
                    {
                        "event_id": "e2",
                        "evidence": "Previous event December 2015",
                        "seizure_phrase": "event",
                        "target_status": "history_context_only",
                        "statement_family": "last_event_date",
                        "source_role": "compact_section",
                        "count": "0",
                        "time_relation": "since",
                        "month": "December",
                        "year": "2015",
                        "include_as_finding": False,
                        "rationale": (
                            "Older previous event is context once a newer last event "
                            "is given."
                        ),
                    },
                ],
            },
            {
                "note_fragment": (
                    "Seizure type and frequency: 2 generalised tonic clonic seizures "
                    "2014, absence like seizures 2014. He remains seizure free."
                ),
                "event_frames": [
                    {
                        "event_id": "e1",
                        "evidence": "2 generalised tonic clonic seizures 2014",
                        "seizure_phrase": "generalised tonic clonic seizures",
                        "target_status": "target_epileptic_seizure_frequency",
                        "statement_family": "calendar_count",
                        "source_role": "compact_section",
                        "count": "2",
                        "time_relation": "during",
                        "year": "2014",
                        "finding_text": "generalised tonic clonic seizures",
                        "include_as_finding": True,
                        "rationale": "Historical dated compact-section count is scored.",
                    },
                    {
                        "event_id": "e2",
                        "evidence": "absence like seizures 2014",
                        "seizure_phrase": "absence like seizures",
                        "target_status": "target_epileptic_seizure_frequency",
                        "statement_family": "calendar_occurrence_no_count",
                        "source_role": "compact_section",
                        "time_relation": "during",
                        "year": "2014",
                        "finding_text": "absence like seizures",
                        "include_as_finding": True,
                        "rationale": "Dated occurrence without count is scored as one occurrence.",
                    },
                    {
                        "event_id": "e3",
                        "evidence": "He remains seizure free",
                        "seizure_phrase": "seizure free",
                        "target_status": "uncertain_not_scored",
                        "statement_family": "current_control_no_duration",
                        "source_role": "narrative",
                        "include_as_finding": False,
                        "rationale": (
                            "Bare remains seizure free has no duration, date, or "
                            "clinical anchor, so it is not a scored finding."
                        ),
                    },
                ],
            },
            {
                "note_fragment": (
                    "She gets dizzy episodes twice a week. These are thought to be "
                    "nonepileptic events."
                ),
                "event_frames": [
                    {
                        "event_id": "e1",
                        "evidence": "dizzy episodes twice a week",
                        "seizure_phrase": "dizzy episodes",
                        "target_status": "non_target_episode",
                        "statement_family": "non_target",
                        "source_role": "narrative",
                        "count": "2",
                        "period_count": "1",
                        "period_unit": "week",
                        "include_as_finding": False,
                        "rationale": "The frequency belongs to non-target dizzy episodes.",
                    }
                ],
            },
        ],
        "worked_examples": [
            {
                "note_fragment": (
                    "She has 2 to 3 focal seizures with impaired awareness per month "
                    "since the medication change."
                ),
                "correct": {
                    "text": "focal seizures with impaired awareness",
                    "evidence": (
                        "2 to 3 focal seizures with impaired awareness per month "
                        "since the medication change"
                    ),
                    "clinical_kind": "frequency_rate",
                    "frequency_statement_type": "background_rate",
                    "source_role": "narrative",
                    "count_low": "2",
                    "count_high": "3",
                    "period_count": "1",
                    "period_unit": "month",
                    "time_relation": "since",
                    "point_in_time": "medication change",
                    "confidence": "high",
                    "rationale": "Focal seizures occur 2 to 3 per month since medication change.",
                },
            },
            {
                "note_fragment": (
                    "In April she had 2 to 3 of her focal seizures without change "
                    "in awareness."
                ),
                "correct": {
                    "text": "focal seizures",
                    "evidence": (
                        "In April she had 2 to 3 of her focal seizures without "
                        "change in awareness"
                    ),
                    "clinical_kind": "dated_count",
                    "frequency_statement_type": "calendar_count",
                    "source_role": "narrative",
                    "count_low": "2",
                    "count_high": "3",
                    "time_relation": "during",
                    "month": "April",
                    "confidence": "high",
                    "rationale": "The count is stated during April, not as a per-month rate.",
                },
            },
            {
                "note_fragment": "He has been seizure free for 6 months after surgery.",
                "correct": {
                    "text": "seizure free",
                    "evidence": "seizure free for 6 months after surgery",
                    "clinical_kind": "seizure_free",
                    "frequency_statement_type": "seizure_free_duration",
                    "source_role": "narrative",
                    "period_count": "6",
                    "period_unit": "month",
                    "time_relation": "since",
                    "point_in_time": "surgery",
                    "confidence": "high",
                    "rationale": "Seizure-free state has lasted 6 months since surgery.",
                },
            },
            {
                "note_fragment": (
                    "Seizure frequency: several seizures since clinic review, "
                    "a few seizures per year."
                ),
                "correct": [
                    {
                        "text": "seizures",
                        "evidence": "several seizures since clinic review",
                        "clinical_kind": "dated_count",
                        "frequency_statement_type": "header_count_since_anchor",
                        "source_role": "compact_section",
                        "count": "3",
                        "time_relation": "since",
                        "point_in_time": "last clinic",
                        "confidence": "medium",
                        "rationale": "Several means 3 seizures since clinic review.",
                    },
                    {
                        "text": "seizures",
                        "evidence": "a few seizures per year",
                        "clinical_kind": "frequency_rate",
                        "frequency_statement_type": "background_rate",
                        "source_role": "compact_section",
                        "count": "2",
                        "period_count": "1",
                        "period_unit": "year",
                        "confidence": "medium",
                        "rationale": "Few means 2 seizures per year.",
                    },
                ],
            },
            {
                "note_fragment": (
                    "Seizure type and frequency: seizures every 3 to 4 weeks. "
                    "She currently has seizures every 3 to 4 weeks."
                ),
                "correct": [
                    {
                        "text": "seizures",
                        "evidence": "seizures every 3 to 4 weeks",
                        "clinical_kind": "frequency_rate",
                        "frequency_statement_type": "recurrence_interval",
                        "source_role": "compact_section",
                        "count": "1",
                        "period_low": "3",
                        "period_high": "4",
                        "period_unit": "week",
                        "confidence": "high",
                        "rationale": (
                            "The compact section states one seizure interval every "
                            "3 to 4 weeks."
                        ),
                    },
                    {
                        "text": "seizures",
                        "evidence": "seizures every 3 to 4 weeks",
                        "clinical_kind": "frequency_rate",
                        "frequency_statement_type": "recurrence_interval",
                        "source_role": "narrative",
                        "count": "1",
                        "period_low": "3",
                        "period_high": "4",
                        "period_unit": "week",
                        "confidence": "high",
                        "rationale": "The narrative repeats the same seizure interval.",
                    },
                ],
            },
            {
                "note_fragment": (
                    "Diagnosis: generalised epilepsy. He has had roughly two "
                    "seizures per year."
                ),
                "correct": {
                    "text": "seizures",
                    "evidence": "roughly two seizures per year",
                    "clinical_kind": "frequency_rate",
                    "frequency_statement_type": "background_rate",
                    "source_role": "narrative",
                    "count": "2",
                    "period_count": "1",
                    "period_unit": "year",
                    "confidence": "high",
                    "rationale": (
                        "The evidence says generic seizures, so the text remains "
                        "seizures."
                    ),
                },
            },
            {
                "note_fragment": (
                    "His last seizures were in his teenage years. He had migraines "
                    "three times per month and febrile seizures as a child."
                ),
                "correct": {
                    "text": "seizures",
                    "evidence": "His last seizures were in his teenage years",
                    "clinical_kind": "last_event",
                    "frequency_statement_type": "last_event_date",
                    "source_role": "narrative",
                    "count": "0",
                    "time_relation": "since",
                    "age_low": "13",
                    "age_high": "19",
                    "age_unit": "year",
                    "confidence": "medium",
                    "rationale": (
                        "Last seizures were in teenage years; migraine and febrile "
                        "history are not target frequency facts."
                    ),
                },
            },
            {
                "note_fragment": "Seizure type and frequency: absence like seizures 2018",
                "correct": {
                    "text": "absence like seizures",
                    "evidence": "absence like seizures 2018",
                    "clinical_kind": "dated_count",
                    "frequency_statement_type": "calendar_occurrence_no_count",
                    "source_role": "compact_section",
                    "year": "2018",
                    "time_relation": "during",
                    "confidence": "medium",
                    "rationale": "The line records an occurrence in 2018 without an exact count.",
                },
            },
            {
                "note_fragment": (
                    "Seizure type and frequency: 2 generalised tonic clonic seizures "
                    "2018, absence like seizures 2018. He remains seizure free."
                ),
                "correct": [
                    {
                        "text": "generalised tonic clonic seizures",
                        "evidence": "2 generalised tonic clonic seizures 2018",
                        "clinical_kind": "dated_count",
                        "frequency_statement_type": "calendar_count",
                        "source_role": "compact_section",
                        "count": "2",
                        "year": "2018",
                        "time_relation": "during",
                        "confidence": "high",
                        "rationale": (
                            "The compact section states a dated count of generalised "
                            "tonic clonic seizures."
                        ),
                    },
                    {
                        "text": "absence like seizures",
                        "evidence": "absence like seizures 2018",
                        "clinical_kind": "dated_count",
                        "frequency_statement_type": "calendar_occurrence_no_count",
                        "source_role": "compact_section",
                        "year": "2018",
                        "time_relation": "during",
                        "confidence": "medium",
                        "rationale": (
                            "The compact section records absence like seizures in "
                            "2018 without an exact count."
                        ),
                    },
                ],
            },
            {
                "note_fragment": (
                    "Seizure type and frequency: Generalised tonic clonic seizure-last "
                    "event July 2016. Previous event December 2015."
                ),
                "correct": {
                    "text": "Generalised tonic clonic seizure",
                    "evidence": "Generalised tonic clonic seizure-last event July 2016.",
                    "clinical_kind": "last_event",
                    "frequency_statement_type": "last_event_date",
                    "source_role": "compact_section",
                    "count": "0",
                    "month": "July",
                    "year": "2016",
                    "time_relation": "since",
                    "confidence": "high",
                    "rationale": (
                        "The July 2016 last event is the most recent event; the "
                        "older previous event is context."
                    ),
                },
            },
            {
                "note_fragment": (
                    "She had a cluster of seizures in August 2017 where she had "
                    "6-9 seizures every week for 3 weeks."
                ),
                "correct": [
                    {
                        "text": "cluster of seizures",
                        "evidence": "a cluster of seizures in August 2017",
                        "clinical_kind": "cluster_frequency",
                        "frequency_statement_type": "calendar_occurrence_no_count",
                        "source_role": "narrative",
                        "count": "1",
                        "month": "August",
                        "year": "2017",
                        "time_relation": "during",
                        "confidence": "high",
                        "rationale": "The cluster itself is a dated occurrence.",
                    },
                    {
                        "text": "seizures",
                        "evidence": "6-9 seizures every week for 3 weeks",
                        "clinical_kind": "frequency_rate",
                        "frequency_statement_type": "background_rate",
                        "source_role": "narrative",
                        "count_low": "6",
                        "count_high": "9",
                        "period_count": "1",
                        "period_unit": "week",
                        "month": "August",
                        "year": "2017",
                        "time_relation": "during",
                        "confidence": "high",
                        "rationale": (
                            "The rate is every week; the 3 weeks is episode duration."
                        ),
                    },
                ],
            },
            {
                "note_fragment": (
                    "The seizures have returned. He can get infrequent focal to "
                    "bilateral convulsive seizures having around two in the year "
                    "of his diagnosis."
                ),
                "correct": [
                    {
                        "text": "seizures",
                        "evidence": "The seizures have returned",
                        "clinical_kind": "frequency_change",
                        "frequency_statement_type": "change_only",
                        "source_role": "narrative",
                        "frequency_change": "increased",
                        "confidence": "medium",
                        "rationale": (
                            "Seizures returning after seizure freedom is an increase."
                        ),
                    },
                    {
                        "text": "focal to bilateral convulsive seizures",
                        "evidence": "infrequent focal to bilateral convulsive seizures",
                        "clinical_kind": "frequency_change",
                        "frequency_statement_type": "change_only",
                        "source_role": "narrative",
                        "frequency_change": "infrequent",
                        "confidence": "medium",
                        "rationale": (
                            "Infrequent is a qualitative frequency-change statement; "
                            "the old count at diagnosis is not a current rate."
                        ),
                    },
                ],
            },
            {
                "note_fragment": (
                    "The epilepsy seems to be under control on levetiracetam. "
                    "I will review her again in nine months."
                ),
                "correct": [],
                "rationale": (
                    "Vague diagnosis-level control without a seizure type, count, "
                    "date, duration, or no-further-seizures phrase is not scored."
                ),
            },
            {
                "note_fragment": (
                    "There has been significant improvement since increasing lamotrigine. "
                    "The focal seizures are completely under control on lamotrigine."
                ),
                "correct": [
                    {
                        "text": "focal seizures",
                        "evidence": "The focal seizures are completely under control",
                        "clinical_kind": "seizure_free",
                        "frequency_statement_type": "current_zero_no_duration",
                        "source_role": "narrative",
                        "count": "0",
                        "point_in_time": "medication change",
                        "confidence": "high",
                        "rationale": (
                            "A specific seizure type is completely controlled after "
                            "a medication increase."
                        ),
                    },
                    {
                        "text": "seizures",
                        "evidence": (
                            "There has been significant improvement since increasing "
                            "lamotrigine"
                        ),
                        "clinical_kind": "frequency_change",
                        "frequency_statement_type": "change_only",
                        "source_role": "narrative",
                        "frequency_change": "infrequent",
                        "point_in_time": "medication change",
                        "confidence": "medium",
                        "rationale": (
                            "Improvement since medication increase means seizure "
                            "frequency became infrequent."
                        ),
                    },
                ],
            },
            {
                "note_fragment": (
                    "She has not had any further seizures on levetiracetam."
                ),
                "correct": {
                    "text": "seizures",
                    "evidence": "has not had any further seizures",
                    "clinical_kind": "seizure_free",
                    "frequency_statement_type": "current_zero_no_duration",
                    "source_role": "narrative",
                    "count": "0",
                    "confidence": "high",
                    "rationale": (
                        "The source says no further seizures, so text remains seizures."
                    ),
                },
            },
            {
                "note_fragment": (
                    "She has episodes twice a week of deja vu. I think these are "
                    "focal seizures."
                ),
                "correct": [],
                "rationale": (
                    "The frequency clause names episodes, and the seizure interpretation "
                    "is separate diagnostic reasoning rather than a source-near seizure "
                    "frequency statement."
                ),
            },
            {
                "note_fragment": (
                    "Despite medication she continues to get general and complex "
                    "partial seizures. She continues to get chronic daily headaches."
                ),
                "correct": [],
                "rationale": (
                    "Continues to get seizures is not a scored frequency without a "
                    "count, rate, date, or explicit qualitative frequency change."
                ),
            },
            {
                "note_fragment": (
                    "He developed some minor seizures. The episodes last no longer "
                    "than 3 minutes and occur 4 to 5 times a year."
                ),
                "correct": [],
                "rationale": (
                    "The rate belongs to nonspecific minor episodes rather than a "
                    "standard scored seizure type."
                ),
            },
            {
                "note_fragment": (
                    "Diagnosis: single focal seizure. He has not had any previous "
                    "seizures and is at risk of further seizures."
                ),
                "correct": [],
                "rationale": (
                    "A single diagnostic seizure encounter plus no previous seizures "
                    "or future risk is not scored as recurrent seizure frequency."
                ),
            },
            {
                "note_fragment": (
                    "Diagnosis: generalised tonic clonic seizures with myoclonic jerks. "
                    "She is still having approximately 15 seizures over 4 months."
                ),
                "correct": {
                    "text": "seizures",
                    "evidence": "approximately 15 seizures over 4 months",
                    "clinical_kind": "frequency_rate",
                    "frequency_statement_type": "background_rate",
                    "source_role": "narrative",
                    "count": "15",
                    "period_count": "4",
                    "period_unit": "month",
                    "confidence": "high",
                    "rationale": (
                        "The frequency evidence says generic seizures, so text "
                        "remains seizures."
                    ),
                },
            },
        ],
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def parse_clinical_findings_json(
    raw_output: str,
) -> tuple[ClinicalFindingsRecord | None, list[str]]:
    """Parse and schema-validate one model output string."""

    payload, load_errors = loads_json_or_literal(raw_output)
    if payload is None:
        return None, load_errors

    payload, coerce_notes = _coerce_payload(payload)
    errors: list[str] = [
        *load_errors,
        *_dropped_projection_field_notes(payload),
        *coerce_notes,
    ]

    try:
        record = ClinicalFindingsRecord.model_validate(payload)
    except ValidationError as exc:
        return None, [f"schema_validation_error: {exc.errors()[0]['msg']}"]

    return record, errors


def _dropped_projection_field_notes(payload: Any) -> list[str]:
    """Report model-supplied benchmark/guideline fields ignored by the schema."""

    if not isinstance(payload, dict):
        return []
    notes: list[str] = []
    for collection_name in ("event_frames", "findings"):
        records = payload.get(collection_name)
        if not isinstance(records, list):
            continue
        for index, record in enumerate(records):
            if not isinstance(record, dict):
                continue
            for key in sorted(_DISALLOWED_MODEL_PROJECTION_FIELDS & record.keys()):
                notes.append(
                    "dropped_model_supplied_projection_field: "
                    f"{collection_name}[{index}] {key!r}"
                )
    return notes


def parse_verification_decisions_json(
    raw_output: str,
) -> tuple[VerificationDecisionList | None, list[str]]:
    """Parse and schema-validate one verifier output string."""

    payload, load_errors = loads_json_or_literal(raw_output)
    if payload is None:
        return None, load_errors
    payload, coerce_notes = _coerce_verification_payload(payload)
    errors = [*load_errors, *coerce_notes]

    try:
        record = VerificationDecisionList.model_validate(payload)
    except ValidationError as exc:
        return None, [*errors, f"schema_validation_error: {exc.errors()[0]['msg']}"]

    return record, errors


def _coerce_verification_payload(payload: Any) -> tuple[Any, list[str]]:
    notes: list[str] = []
    if not isinstance(payload, dict):
        return payload, notes

    additions = payload.get("findings_to_add")
    if not isinstance(additions, list):
        return payload, notes

    kept: list[Any] = []
    for i, addition in enumerate(additions):
        if not isinstance(addition, dict):
            kept.append(addition)
            continue
        if addition.get("text") and addition.get("clinical_kind"):
            kept.append(addition)
            continue
        notes.append(
            f"dropped_invalid_findings_to_add_record: index={i} "
            "missing text/clinical_kind"
        )
    return {**payload, "findings_to_add": kept}, notes


def apply_verification_decisions(
    raw_findings: Sequence[ClinicalFindingRecord],
    decisions: VerificationDecisionList,
) -> tuple[list[ClinicalFindingRecord], list[str]]:
    """Apply model-authored verifier decisions to first-pass findings."""

    warnings: list[str] = []
    by_index = {decision.raw_index: decision for decision in decisions.decisions}
    final_findings: list[ClinicalFindingRecord] = []

    for index, finding in enumerate(raw_findings):
        decision = by_index.get(index)
        if decision is None:
            warnings.append(f"verification_missing_decision_kept: raw_index={index}")
            final_findings.append(finding)
            continue
        if decision.action == "remove":
            warnings.append(f"verification_removed: raw_index={index}")
            continue
        if decision.action == "keep":
            final_findings.append(finding)
            continue

        revisable_fields = _SCALAR_FINDING_FIELDS - {"confidence"}
        updates = {
            key: getattr(decision, key)
            for key in revisable_fields
            if key in decision.model_fields_set
        }
        if "rationale" in updates and not updates["rationale"]:
            updates.pop("rationale")
        try:
            final_findings.append(
                ClinicalFindingRecord.model_validate({
                    **finding.model_dump(mode="json"),
                    **updates,
                })
            )
        except ValidationError as exc:
            warnings.append(
                f"verification_revise_invalid_kept: raw_index={index} "
                f"{exc.errors()[0]['msg']}"
            )
            final_findings.append(finding)

    for extra in decisions.findings_to_add:
        final_findings.append(extra)
        warnings.append(f"verification_added: text={extra.text!r}")

    return final_findings, warnings


def _coerce_payload(payload: Any) -> tuple[Any, list[str]]:
    notes: list[str] = []
    if not isinstance(payload, dict):
        return payload, notes
    findings_raw = payload.get("findings")
    if findings_raw is None and isinstance(payload.get("mentions"), list):
        findings_raw = payload.get("mentions")
        notes.append("coerced_mentions_key_to_findings")
    coerced_payload = dict(payload)

    if isinstance(findings_raw, list):
        coerced_payload["findings"] = _coerce_record_list(
            findings_raw,
            scalar_fields=_SCALAR_FINDING_FIELDS,
            notes=notes,
            record_name="finding",
            coerce_statement_type=True,
        )

    event_frames_raw = payload.get("event_frames")
    if isinstance(event_frames_raw, list):
        coerced_payload["event_frames"] = _coerce_record_list(
            event_frames_raw,
            scalar_fields=_SCALAR_EVENT_FRAME_FIELDS,
            notes=notes,
            record_name="event_frame",
            coerce_statement_type=False,
        )

    return coerced_payload, notes


def _coerce_record_list(
    records: Sequence[Any],
    *,
    scalar_fields: frozenset[str],
    notes: list[str],
    record_name: str,
    coerce_statement_type: bool,
) -> list[Any]:
    coerced_records: list[Any] = []
    for i, record in enumerate(records):
        if not isinstance(record, dict):
            coerced_records.append(record)
            continue
        new_record = dict(record)
        clinical_kind = str(new_record.get("clinical_kind", ""))
        if (
            coerce_statement_type
            and clinical_kind
            and clinical_kind not in _CLINICAL_KIND_VALUES
            and clinical_kind in _STATEMENT_TYPE_TO_KIND
        ):
            new_record.setdefault("frequency_statement_type", clinical_kind)
            new_record["clinical_kind"] = _STATEMENT_TYPE_TO_KIND[clinical_kind]
            notes.append(
                f"coerced_statement_type_from_clinical_kind: {record_name}[{i}] "
                f"{clinical_kind!r}"
            )
        for key, value in record.items():
            if key not in scalar_fields or value is None:
                continue
            if not isinstance(value, str):
                new_record[key] = str(value)
                notes.append(
                    f"coerced_field_value: {record_name}[{i}] {key!r} "
                    f"{value!r} -> {new_record[key]!r}"
                )
        coerced_records.append(new_record)
    return coerced_records
