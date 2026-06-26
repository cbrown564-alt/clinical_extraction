"""Stage 3: clinical-findings finalization (LLM rewrite)."""

from __future__ import annotations

import json
from collections.abc import Sequence

import dspy

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.clinical_findings.constants import (
    PROMPT_VERSION,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.clinical_findings.types import (
    ClinicalFindingRecord,
)

class ExECTv2ClinicalFindingsFinalizerSignature(dspy.Signature):
    """Rewrite raw findings into the final scored seizure-frequency findings.

    Return a strict JSON object with key 'findings'. No markdown wrapper.
    """

    prompt_input_json: str = dspy.InputField(
        desc=(
            "JSON containing one clinical letter, raw findings, output schema, "
            "and finalization instructions."
        )
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"findings\": [{\"text\": ..., "
            "\"evidence\": ..., \"clinical_kind\": ..., "
            "\"frequency_statement_type\": ..., \"source_role\": ..., "
            "\"count\": ..., \"period_unit\": ..., \"confidence\": ..., "
            "\"rationale\": ...}, ...]}"
        )
    )


class DspyClinicalFindingsSFFinalizer(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2ClinicalFindingsFinalizerSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)

def build_finalization_prompt_input(
    letter: ExectLetter,
    raw_findings: Sequence[ClinicalFindingRecord],
) -> str:
    """Build the second-pass final-findings rewrite payload for one letter."""

    payload = {
        "prompt_version": f"{PROMPT_VERSION}_finalizer",
        "task": (
            "Review the clinical letter and raw seizure-frequency findings. "
            "Return the complete final model-owned findings list as one JSON "
            "object with key 'findings'. Do not return edit decisions."
        ),
        "raw_findings": [finding.model_dump(mode="json") for finding in raw_findings],
        "output_schema": {
            "text": (
                "Exact short phrase from the letter naming the seizure type or "
                "seizure-free state."
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
                "header_count_since_anchor, calendar_count, "
                "calendar_occurrence_no_count, recurrence_interval, last_event_date, "
                "background_rate, seizure_free_duration, current_control_no_duration, "
                "current_zero_no_duration, change_only, or other_frequency."
            ),
            "source_role": "compact_section, narrative, or both.",
            "count": "Single seizure count when stated.",
            "count_low": "Lower seizure count when a range is stated.",
            "count_high": "Upper seizure count when a range is stated.",
            "period_count": "Number of time periods, usually 1.",
            "period_low": "Lower time-period count when a period range is stated.",
            "period_high": "Upper time-period count when a period range is stated.",
            "period_unit": "day, week, month, year, or fortnight when stated.",
            "time_relation": "during or since when explicitly stated.",
            "point_in_time": (
                "Clinical anchor when explicitly stated, for example medication "
                "change, last clinic, last week, surgery, or birthday."
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
            "rationale": "One concise sentence explaining the final clinical reading.",
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
        "finalization_checks": [
            (
                "Return the final findings list, not a list of decisions. If a raw "
                "finding is wrong, omit it. If a missing finding is present in the "
                "letter, add a complete finding. If an attribute is wrong, return the "
                "correct full finding."
            ),
            (
                "Use raw_findings as the starting point. When a raw finding is target "
                "and its fields are clinically correct, copy the entire raw finding "
                "object into final findings with all numeric, date, time_relation, "
                "point_in_time, source_role, confidence, and rationale fields preserved."
            ),
            (
                "Do not drop fields that were correct in raw_findings. In particular, "
                "preserve month, year, time_relation, count, count_low, count_high, "
                "period_count, period_unit, frequency_change, and point_in_time unless "
                "you are intentionally correcting that field."
            ),
            (
                "Every final finding object must contain all required keys, using null "
                "for unknown optional fields. A kept finding should look like the raw "
                "finding object, not a shortened summary."
            ),
            (
                "Keep target epileptic seizure-frequency findings: dated counts, "
                "dated occurrences, last-event dates, recurrent rates, current zero "
                "seizure status, and frequency-change-only statements."
            ),
            (
                "Remove non-target findings: migraine/headache frequency, blackouts, "
                "dizzy spells, dissociative or nonepileptic events, febrile history, "
                "family history, driving rules, medication titration intervals, vague "
                "diagnosis-level epilepsy control, and diagnostic episode descriptions "
                "whose frequency clause does not itself name seizures."
            ),
            (
                "Preserve source wording. If the evidence says seizures, text should "
                "be seizures even when the diagnosis names a specific seizure type. "
                "If the evidence says no further seizures, text should be seizures."
            ),
            (
                "If the evidence says focal seizures without change in awareness, "
                "text should be focal seizures. If it says focal seizures with "
                "altered or impaired awareness, keep that modifier."
            ),
            (
                "For compact-section and narrative repeats, include both findings "
                "when both source statements are present. Do not collapse repeated "
                "annotatable facts solely because they refer to the same seizure type."
            ),
            (
                "A current controlled or seizure-free statement does not replace "
                "historical dated compact-section facts; return both when both are "
                "target findings."
            ),
            (
                "For last-event plus previous-event summaries, return the most recent "
                "last event and do not return the older previous-event row."
            ),
            (
                "For a recent event such as last week or last month, set "
                "time_relation during and point_in_time to last week or last month."
            ),
            (
                "For has not had any further seizures, return text seizures, "
                "clinical_kind seizure_free, frequency_statement_type "
                "current_zero_no_duration, and count 0."
            ),
            (
                "For specific epileptic seizures completely under control after a "
                "medication increase, return the specific seizure zero-count finding "
                "and a separate seizures frequency_change infrequent finding when "
                "the improvement since medication change is stated."
            ),
            (
                "For a cluster of seizures in a dated month where a within-cluster "
                "rate is also stated, return both the cluster occurrence and the "
                "within-cluster seizure rate."
            ),
            (
                "For 6-9 seizures every week for 3 weeks, period_count is 1 and "
                "period_unit is week; 3 weeks is episode duration, not denominator."
            ),
            (
                "Use null for unknown optional fields, but every final finding should "
                "include all required keys. Return {\"findings\": []} when no target "
                "seizure-frequency finding is present."
            ),
            "Return exactly one JSON object. No markdown code fences.",
        ],
        "worked_examples": [
            {
                "note_fragment": "She has not had any further seizures.",
                "final_findings": [
                    {
                        "text": "seizures",
                        "evidence": "has not had any further seizures",
                        "clinical_kind": "seizure_free",
                        "frequency_statement_type": "current_zero_no_duration",
                        "source_role": "narrative",
                        "count": "0",
                        "count_low": None,
                        "count_high": None,
                        "period_count": None,
                        "period_low": None,
                        "period_high": None,
                        "period_unit": None,
                        "time_relation": None,
                        "point_in_time": None,
                        "day": None,
                        "month": None,
                        "year": None,
                        "age_low": None,
                        "age_high": None,
                        "age_unit": None,
                        "frequency_change": None,
                        "confidence": "high",
                        "rationale": "The source states no further seizures.",
                    }
                ],
            },
            {
                "note_fragment": (
                    "The epilepsy seems to be under control on medication. "
                    "Review in nine months."
                ),
                "final_findings": [],
            },
            {
                "note_fragment": (
                    "Diagnosis: generalised tonic clonic seizures. She is still "
                    "having approximately 15 seizures over 4 months."
                ),
                "final_findings": [
                    {
                        "text": "seizures",
                        "evidence": "approximately 15 seizures over 4 months",
                        "clinical_kind": "frequency_rate",
                        "frequency_statement_type": "background_rate",
                        "source_role": "narrative",
                        "count": "15",
                        "count_low": None,
                        "count_high": None,
                        "period_count": "4",
                        "period_low": None,
                        "period_high": None,
                        "period_unit": "month",
                        "time_relation": None,
                        "point_in_time": None,
                        "day": None,
                        "month": None,
                        "year": None,
                        "age_low": None,
                        "age_high": None,
                        "age_unit": None,
                        "frequency_change": None,
                        "confidence": "high",
                        "rationale": (
                            "The frequency evidence says generic seizures, so text "
                            "remains seizures."
                        ),
                    }
                ],
            },
        ],
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
