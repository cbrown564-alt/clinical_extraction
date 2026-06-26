"""Stage 2: clinical-findings verification (LLM review + decisions)."""

from __future__ import annotations

import json
from collections.abc import Sequence
from typing import Any

import dspy
from pydantic import ValidationError

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.clinical_findings.constants import (
    PROMPT_VERSION,
    _SCALAR_FINDING_FIELDS,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.clinical_findings.types import (
    ClinicalFindingRecord,
    EventFrameRecord,
    VerificationDecisionList,
    VerificationDecisionRecord,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.shared.json_parse import (
    loads_json_or_literal,
)

class ExECTv2ClinicalFindingsVerifierSignature(dspy.Signature):
    """Review one letter and raw findings, then return edit decisions.

    Return a strict JSON object with keys 'decisions' and 'findings_to_add'.
    No markdown wrapper.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter, raw findings, and review instructions."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"decisions\": [{\"raw_index\": 0, "
            "\"target_status\": ..., \"action\": \"keep|remove|revise\", \"text\": ..., "
            "\"evidence\": ..., \"rationale\": ...}], "
            "\"findings_to_add\": [...]}"
        )
    )


class DspyClinicalFindingsSFVerifier(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2ClinicalFindingsVerifierSignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)

def build_verification_prompt_input(
    letter: ExectLetter,
    raw_findings: Sequence[ClinicalFindingRecord],
    event_frames: Sequence[EventFrameRecord] | None = None,
) -> str:
    """Build the second-pass clinical review payload for one letter."""

    payload = {
        "prompt_version": f"{PROMPT_VERSION}_verification",
        "task": (
            "Review the clinical letter and raw seizure-frequency findings. "
            "Return model decisions as one JSON object with a 'decisions' list and "
            "a 'findings_to_add' list."
        ),
        "raw_findings": [finding.model_dump(mode="json") for finding in raw_findings],
        "event_frames": [
            frame.model_dump(mode="json") for frame in (event_frames or [])
        ],
        "decision_schema": {
            "raw_index": "Zero-based index into raw_findings.",
            "target_status": (
                "Optional clinical category: target_epileptic_seizure_frequency, "
                "non_target_episode, history_context_only, diagnosis_without_frequency, "
                "future_risk_or_driving, or uncertain_not_scored."
            ),
            "action": "keep, remove, or revise.",
            "text": "Only for revise: corrected exact source phrase.",
            "evidence": "Only for revise: corrected exact supporting substring.",
            "clinical_kind": "Only for revise when the raw kind is clinically wrong.",
            "frequency_statement_type": (
                "Only for revise when the raw statement type is clinically wrong."
            ),
            "source_role": "Only for revise when the raw source role is clinically wrong.",
            "count/date/period fields": (
                "Only for revise when raw numeric, date, period, time_relation, "
                "point_in_time, age, or frequency_change fields are clinically wrong. "
                "Omit fields that should be preserved."
            ),
            "rationale": "Brief clinical reason for the decision.",
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
        "review_checks": [
            "Return exactly one decision for every raw finding.",
            (
                "Use event_frames as the model's first-pass clinical map. If a target "
                "event_frame has include_as_finding true but raw_findings omit it, add "
                "a complete finding in findings_to_add when exact supporting evidence "
                "exists."
            ),
            (
                "If an event_frame has target_status non_target_episode, "
                "history_context_only, diagnosis_without_frequency, "
                "future_risk_or_driving, or uncertain_not_scored, verify that no "
                "matching raw finding is kept unless the frame is actually a target "
                "epileptic seizure-frequency fact."
            ),
            (
                "Do not blindly trust an event_frame phrase if it copied contextual "
                "words into the seizure type. For focal seizures without change in "
                "awareness, revise the raw text to focal seizures even when the "
                "event_frame used the longer phrase."
            ),
            (
                "Use a brief final rationale only. Do not discuss alternatives or "
                "write step-by-step deliberation."
            ),
            (
                "Several seizures since last clinic and a few seizures per year are "
                "target epileptic seizure-frequency findings, even if the note also "
                "uses the word uncertain."
            ),
            (
                "Do not use uncertain_not_scored merely because a section heading says "
                "uncertain. Use uncertain_not_scored only when the evidence gives no "
                "count, rate, dated occurrence, last-event date, or zero-seizure status."
            ),
            (
                "Target epileptic seizure-frequency findings include historical dated "
                "counts, dated occurrences, last-event dates, recurrent rates, and "
                "zero-seizure status. Do not remove a finding merely because it is "
                "historical; ExECTv2 scores dated historical seizure-frequency facts."
            ),
            (
                "Keep compact-section dated seizure-type facts even when later prose "
                "says the patient is currently seizure free or controlled. Current "
                "control and historical dated counts are distinct clinical facts."
            ),
            (
                "Keep only epileptic seizure-frequency findings. Remove migraine, "
                "headache, blackout, dissociative, nonepileptic, dizzy spell, "
                "loss-of-consciousness, febrile-history, family-history, driving-rule, "
                "future-risk, and medication-titration facts unless the evidence itself "
                "states an epileptic seizure frequency."
            ),
            (
                "Keep generic wording generic. If the evidence says seizures, use "
                "text 'seizures' even when a diagnosis elsewhere names a specific "
                "seizure syndrome."
            ),
            (
                "Classify a single first seizure or one-off diagnostic encounter "
                "without recurrent epilepsy frequency as diagnosis_without_frequency "
                "unless the evidence states current seizure frequency."
            ),
            (
                "Classify minor seizures, jerks, blackouts, dizzy spells, loss of "
                "consciousness, episodes, events, and spells as non_target_episode "
                "unless the evidence explicitly says epileptic seizure frequency."
            ),
            (
                "Remove minor seizures, jerks, or episodes even when a rate is stated "
                "if the frequency evidence describes nonspecific spells rather than "
                "a standard scored seizure type."
            ),
            (
                "A diagnostic episode description plus a separate clinician impression "
                "that episodes may be seizures is not enough for a target finding. "
                "Remove it unless the frequency evidence itself names epileptic seizures "
                "or a seizure type."
            ),
            (
                "Remove vague ongoing-seizure statements such as continues to get "
                "seizures when the evidence does not give a count, rate, date, "
                "last-event anchor, or explicit qualitative change word."
            ),
            (
                "Remove vague diagnosis-level control such as epilepsy seems under "
                "control when there is no seizure type, count, date, duration, or "
                "no-further-seizures phrase."
            ),
            (
                "Remove bare remains seizure free findings when there is no duration, "
                "date, medication-change/surgery/clinic anchor, or no-further-seizures "
                "wording. Historical compact-section seizure counts remain scored."
            ),
            (
                "Classify febrile seizures, childhood febrile history, family history, "
                "and old background context as history_context_only unless the finding "
                "is a last-seizure status for the patient."
            ),
            (
                "If target_status is non_target_episode, history_context_only, "
                "diagnosis_without_frequency, future_risk_or_driving, or "
                "uncertain_not_scored, the action should usually be remove. Keep is "
                "reserved for target_epileptic_seizure_frequency."
            ),
            (
                "Classify driving clearance windows, no-seizure requirements for "
                "driving, medication titration intervals, and future-risk statements "
                "as future_risk_or_driving."
            ),
            (
                "Keep source-near seizure-type modifiers. If the evidence says focal "
                "seizures with altered awareness, keep that full phrase."
            ),
            (
                "If compact-section evidence says absence like seizures, keep text "
                "absence like seizures. Do not revise it to absence-like episodes."
            ),
            (
                "If a raw text includes focal seizures without change in awareness, "
                "revise text to focal seizures. Without change in awareness is context, "
                "not an impaired-awareness seizure-type modifier."
            ),
            (
                "For cluster sentences, return both the cluster mention and the "
                "within-cluster seizure rate when both are explicitly stated."
            ),
            (
                "For compact-section and narrative repeats, include both only when "
                "both evidence strings are present in the letter."
            ),
            (
                "For last-event summaries, keep the most recent last event. Do not "
                "add older previous-event rows."
            ),
            (
                "For no further seizures, no seizures, or seizures controlled, return "
                "a scored zero-count finding only when the evidence is about epileptic "
                "seizures, not a general diagnosis or non-target event."
            ),
            (
                "For no further seizures, text should be seizures unless the exact "
                "evidence says seizure free."
            ),
            (
                "Both text and evidence must be exact substrings from the letter. "
                "If a raw finding has the right clinical idea but the text is too "
                "specific or too broad, use action revise and provide corrected text."
            ),
            (
                "Do not copy all numeric/date fields into a revise decision. If a raw "
                "finding's counts, dates, or periods are already correct, leave those "
                "fields absent from the decision so they are preserved."
            ),
            (
                "If a raw finding has the wrong count, date, period, time_relation, "
                "point_in_time, age, or frequency_change, use action revise and include "
                "only the corrected fields. Omit fields that should stay unchanged."
            ),
            (
                "If a compact line has a last event plus a previous event, keep the "
                "last event and remove the older previous-event finding."
            ),
            (
                "For focal seizures without change in awareness, revise text to focal "
                "seizures even if the raw finding copied the full context phrase."
            ),
            (
                "Use findings_to_add only for a seizure-frequency finding that is "
                "clearly present in the letter but missing from raw_findings."
            ),
            "Return exactly one JSON object. No markdown code fences.",
        ],
        "decision_examples": [
            {
                "raw_finding": {
                    "text": "seizures",
                    "evidence": "several seizures since the last clinic appointment",
                },
                "decision": {
                    "raw_index": 0,
                    "target_status": "target_epileptic_seizure_frequency",
                    "action": "keep",
                    "rationale": "Counted seizures since last clinic are target frequency.",
                },
            },
            {
                "raw_finding": {
                    "text": "seizures",
                    "evidence": "definitely having a few seizures per year",
                },
                "decision": {
                    "raw_index": 1,
                    "target_status": "target_epileptic_seizure_frequency",
                    "action": "keep",
                    "rationale": "A few seizures per year is a target frequency estimate.",
                },
            },
            {
                "raw_finding": {
                    "text": "blackouts",
                    "evidence": "unwitnessed blackouts after reducing alcohol",
                },
                "decision": {
                    "raw_index": 2,
                    "target_status": "non_target_episode",
                    "action": "remove",
                    "rationale": "Blackouts are not stated as epileptic seizures.",
                },
            },
            {
                "raw_finding": {
                    "text": "generalised tonic clonic seizures",
                    "evidence": "2 generalised tonic clonic seizures 2018",
                    "clinical_kind": "dated_count",
                    "frequency_statement_type": "calendar_count",
                    "source_role": "compact_section",
                    "count": "2",
                    "year": "2018",
                },
                "decision": {
                    "raw_index": 3,
                    "target_status": "target_epileptic_seizure_frequency",
                    "action": "keep",
                    "rationale": (
                        "Historical dated seizure counts are target "
                        "seizure-frequency findings."
                    ),
                },
            },
            {
                "raw_finding": {
                    "text": "Generalised tonic clonic seizure",
                    "evidence": "Generalised tonic clonic seizure-last event July 2016.",
                    "clinical_kind": "last_event",
                    "frequency_statement_type": "last_event_date",
                    "month": "July",
                    "year": "2016",
                },
                "decision": {
                    "raw_index": 4,
                    "target_status": "target_epileptic_seizure_frequency",
                    "action": "keep",
                    "rationale": (
                        "Last-event dates are target seizure-frequency findings."
                    ),
                },
            },
            {
                "raw_finding": {
                    "text": "generalised tonic clonic seizure",
                    "evidence": "had a generalised tonic clonic seizure",
                    "clinical_kind": "dated_count",
                    "frequency_statement_type": "calendar_count",
                },
                "decision": {
                    "raw_index": 5,
                    "target_status": "target_epileptic_seizure_frequency",
                    "action": "revise",
                    "evidence": "last week and had a generalised tonic clonic seizure",
                    "time_relation": "during",
                    "point_in_time": "last week",
                    "rationale": (
                        "The event occurred last week, so the time anchor belongs "
                        "on the finding."
                    ),
                },
            },
            {
                "raw_finding": {
                    "text": "focal seizures without change in awareness",
                    "evidence": (
                        "In March she had 2 to 3 of her focal seizures without "
                        "change in awareness"
                    ),
                    "clinical_kind": "dated_count",
                    "frequency_statement_type": "calendar_count",
                },
                "decision": {
                    "raw_index": 6,
                    "target_status": "target_epileptic_seizure_frequency",
                    "action": "revise",
                    "text": "focal seizures",
                    "rationale": (
                        "Without change in awareness is context, not an "
                        "impaired-awareness seizure type."
                    ),
                },
            },
            {
                "raw_finding": {
                    "text": "Generalised tonic clonic seizure",
                    "evidence": "Previous event December 2015.",
                    "clinical_kind": "last_event",
                    "frequency_statement_type": "last_event_date",
                },
                "decision": {
                    "raw_index": 7,
                    "target_status": "history_context_only",
                    "action": "remove",
                    "rationale": (
                        "An older previous event is context when a newer last-event "
                        "date is also present."
                    ),
                },
            },
            {
                "raw_finding": {
                    "text": "seizure free",
                    "evidence": "The epilepsy seems to be under control on levetiracetam.",
                    "clinical_kind": "frequency_change",
                    "frequency_statement_type": "change_only",
                },
                "decision": {
                    "raw_index": 8,
                    "target_status": "diagnosis_without_frequency",
                    "action": "remove",
                    "rationale": (
                        "Vague epilepsy control is not a source-near seizure-frequency "
                        "finding."
                    ),
                },
            },
            {
                "raw_finding": {
                    "text": "episodes",
                    "evidence": "episodes around twice a week of an unusual thought",
                    "clinical_kind": "frequency_rate",
                    "frequency_statement_type": "background_rate",
                },
                "decision": {
                    "raw_index": 9,
                    "target_status": "non_target_episode",
                    "action": "remove",
                    "rationale": (
                        "The frequency clause names episodes, not epileptic seizures."
                    ),
                },
            },
            {
                "raw_finding": {
                    "text": "minor seizures",
                    "evidence": (
                        "minor seizures. The episodes last no longer than 3 minutes "
                        "and occur 4 to 5 times a year"
                    ),
                    "clinical_kind": "frequency_rate",
                    "frequency_statement_type": "background_rate",
                    "count_low": "4",
                    "count_high": "5",
                    "period_count": "1",
                    "period_unit": "year",
                },
                "decision": {
                    "raw_index": 10,
                    "target_status": "non_target_episode",
                    "action": "remove",
                    "rationale": (
                        "The frequency belongs to nonspecific minor episodes rather "
                        "than a standard scored seizure type."
                    ),
                },
            },
            {
                "raw_finding": {
                    "text": "general and complex partial seizures",
                    "evidence": "she continues to get general and complex partial seizures",
                    "clinical_kind": "frequency_change",
                    "frequency_statement_type": "change_only",
                },
                "decision": {
                    "raw_index": 11,
                    "target_status": "uncertain_not_scored",
                    "action": "remove",
                    "rationale": (
                        "Continues to get seizures is not a scored frequency without "
                        "a count, rate, date, or qualitative change word."
                    ),
                },
            },
            {
                "raw_finding": {
                    "text": "focal seizure",
                    "evidence": "He has not had any previous seizures.",
                    "clinical_kind": "seizure_free",
                    "frequency_statement_type": "current_zero_no_duration",
                    "count": "0",
                },
                "decision": {
                    "raw_index": 12,
                    "target_status": "diagnosis_without_frequency",
                    "action": "remove",
                    "rationale": (
                        "No previous seizures in a single diagnostic seizure encounter "
                        "is not recurrent seizure frequency."
                    ),
                },
            },
            {
                "raw_finding": {
                    "text": "generalised tonic clonic seizures",
                    "evidence": "approximately 15 seizures over 4 months",
                    "clinical_kind": "frequency_rate",
                    "frequency_statement_type": "background_rate",
                    "count": "15",
                    "period_count": "4",
                    "period_unit": "month",
                },
                "decision": {
                    "raw_index": 13,
                    "target_status": "target_epileptic_seizure_frequency",
                    "action": "revise",
                    "text": "seizures",
                    "rationale": (
                        "The frequency evidence says generic seizures, so the text "
                        "should stay generic."
                    ),
                },
            },
        ],
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)

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
