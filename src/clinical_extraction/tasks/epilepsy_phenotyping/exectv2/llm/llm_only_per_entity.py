"""ExECTv2 LLM-only per-entity candidate-source extractor.

One focused DSPy call per (entity, letter): an ``entity_name``-parameterized
frame that asks the model for a single entity's source-near state (anchor phrase
+ entity-legal attributes + exact evidence + diagnostic confidence/rationale).

Phase A of the GPT-first execution plan reframes this as a candidate-generation
probe, not a final-labeler: a single-entity frame cuts the attention dilution of
the all-9 single pass and lets real missed candidates surface. The
``source_near`` overlap recall in ``summarize_rows`` is the format-blind
candidate read this phase is about; the phrase/semantic/benchmark layers are the
format-sensitive headline.

Architecture family: ``llm_only``. The LLM owns every clinical fact;
deterministic code validates JSON shape, repairs neutral schema/closed-vocab
mismatches, drops evidence-non-substring mentions (never silently kept), and
projects CUIs as a separate post-step. ``confidence`` is diagnostic, never a
router.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import dspy

from clinical_extraction.core.run_resume import (
    merge_rows,
    pending_items,
    read_completed,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.benchmark_projection import (
    project_cuis,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ENTITY_REGISTRY,
    SEIZURE_FREQUENCY,
    EntitySpec,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.prediction import (
    PredictedLetter,
    PredictedMention,
    to_exect_letter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectAnnotation,
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.llm_only_single_pass import (
    MentionRecord,
    _has_blocking_parse_issue,
    check_evidence,
    parse_extraction_json,
    repair_attributes,
    write_jsonl,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.scoring import (
    PHRASE_ONLY,
    benchmark_config_for,
    score_entity,
    semantic_config_for,
    source_near_diagnostic,
)
from clinical_extraction.tasks.seizure_frequency.gan2026.llm_config import build_dspy_lm

PROMPT_VERSION = "exectv2_llm_only_per_entity_v0.4"
DEFAULT_ENTITY_NAME = SEIZURE_FREQUENCY.name
COMPONENT_OWNER = "llm_only_per_entity"

# Phase B target entities: all nine. Phase A specialized the four regime probes
# (Prescription, Investigations, Diagnosis, SeizureFrequency); Phase B fleshes out
# the remaining five (Onset, WhenDiagnosed, BirthHistory, EpilepsyCause,
# PatientHistory) so "one focused call per entity" is general and the full
# per-entity candidate-quality map can be read in one combined run.
TARGET_ENTITIES: tuple[str, ...] = (
    "BirthHistory",
    "Diagnosis",
    "EpilepsyCause",
    "Investigations",
    "Onset",
    "PatientHistory",
    "Prescription",
    "SeizureFrequency",
    "WhenDiagnosed",
)

PUBLISHED_PER_ENTITY_ITEM_F1: dict[str, float] = {
    "BirthHistory": 0.97,
    "Diagnosis": 0.85,
    "EpilepsyCause": 0.90,
    "Investigations": 0.95,
    "Onset": 0.96,
    "PatientHistory": 0.78,
    "Prescription": 0.87,
    "SeizureFrequency": 0.66,
    "WhenDiagnosed": 0.91,
}


# ── DSPy program ──────────────────────────────────────────────────────────────


class ExECTv2PerEntitySignature(dspy.Signature):
    """Read one clinical letter and list all findings for one entity type.

    Return exactly one JSON object with a 'mentions' list. No markdown wrapper.
    """

    prompt_input_json: str = dspy.InputField(
        desc="JSON containing one clinical letter and task instructions for one entity."
    )
    extraction_json: str = dspy.OutputField(
        desc=(
            "One strict JSON object: {\"mentions\": [{\"text\": ..., \"attributes\": {...}, "
            "\"evidence\": ..., \"confidence\": ..., \"rationale\": ...}, ...]}"
        )
    )


class DspyPerEntityExtractor(dspy.Module):
    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(ExECTv2PerEntitySignature)

    def forward(self, prompt_input_json: str) -> dspy.Prediction:
        return self.predict(prompt_input_json=prompt_input_json)


# ── Per-entity focused frames ─────────────────────────────────────────────────


@dataclass(frozen=True)
class EntityFrame:
    """The entity-specific clinical content of a focused per-entity prompt.

    Everything format-neutral (attribute vocabulary, the JSON envelope, the
    evidence/confidence/rationale field definitions) is derived from the registry
    in ``build_prompt_input``; this carries only the per-entity clinical guidance.
    """

    task: str
    text_definition: str
    clinical_rules: tuple[str, ...]
    worked_examples: tuple[dict[str, Any], ...] = field(default_factory=tuple)


_SF_FRAME = EntityFrame(
    task=(
        "Read the clinical letter. For each seizure type that has associated "
        "frequency information, produce one record in the 'mentions' list."
    ),
    text_definition=(
        "The seizure-type anchor phrase — the SHORT noun phrase naming the "
        "seizure or event type as it appears in the letter. Typically 2 to 6 "
        "words. Valid examples: 'focal seizures with altered awareness', "
        "'generalised tonic-clonic seizures', 'myoclonic jerks', 'absences', "
        "'seizures', 'seizure-free', 'cluster of seizures'. "
        "Must be an exact substring of the letter. "
        "Do NOT put the full frequency sentence in this field."
    ),
    clinical_rules=(
        "Each seizure TYPE that has frequency information gets one record.",
        (
            "text MUST be the SHORT seizure-type anchor phrase (2 to 6 words), "
            "not the full frequency sentence."
        ),
        "Both text and evidence must be exact substrings of the letter.",
        "Extract historical and current frequency statements as separate records.",
        (
            "Seizure-free: text='seizure-free' or 'seizure free'; encode duration "
            "in NumberOfTimePeriods + TimePeriod; use TimeSince_or_TimeOfEvent='Since'."
        ),
        (
            "Ranges: '2 to 4 per month' → LowerNumberOfSeizures='2', "
            "UpperNumberOfSeizures='4', TimePeriod='Month'."
        ),
        (
            "Cluster cadence: if clusters occur 'every 3 weeks', that is the "
            "frequency — not the per-episode daily burst rate."
        ),
        "Do NOT emit Certainty or Negation for SeizureFrequency.",
        "If no seizure frequency information is present, return {\"mentions\": []}.",
        "Return exactly one JSON object. No markdown code fences.",
    ),
    worked_examples=(
        {
            "note_fragment": (
                "She has had 2 to 3 focal seizures per month since the medication change."
            ),
            "correct": {
                "text": "focal seizures",
                "attributes": {
                    "LowerNumberOfSeizures": "2",
                    "UpperNumberOfSeizures": "3",
                    "NumberOfTimePeriods": "1",
                    "TimePeriod": "Month",
                    "TimeSince_or_TimeOfEvent": "Since",
                    "PointInTime": "DrugChange",
                },
                "evidence": "2 to 3 focal seizures per month since the medication change",
                "confidence": "high",
                "rationale": "2 to 3 focal seizures per month since medication change.",
            },
        },
        {
            "note_fragment": "He remains seizure-free for 8 months following surgery.",
            "correct": {
                "text": "seizure-free",
                "attributes": {
                    "TimeSince_or_TimeOfEvent": "Since",
                    "PointInTime": "Surgery",
                    "NumberOfTimePeriods": "8",
                    "TimePeriod": "Month",
                },
                "evidence": "seizure-free for 8 months following surgery",
                "confidence": "high",
                "rationale": "Seizure-free for 8 months since surgery.",
            },
        },
        {
            "note_fragment": (
                "His tonic-clonic seizures occur roughly twice a week, "
                "while his absence seizures have decreased."
            ),
            "correct": [
                {
                    "text": "tonic-clonic seizures",
                    "attributes": {
                        "NumberOfSeizures": "2",
                        "NumberOfTimePeriods": "1",
                        "TimePeriod": "Week",
                    },
                    "evidence": "tonic-clonic seizures occur roughly twice a week",
                    "confidence": "high",
                    "rationale": "Tonic-clonic seizures twice per week.",
                },
                {
                    "text": "absence seizures",
                    "attributes": {"FrequencyChange": "Decreased"},
                    "evidence": "absence seizures have decreased",
                    "confidence": "medium",
                    "rationale": "Absence seizures decreased — rate not stated.",
                },
            ],
            "note": "One record per seizure TYPE.",
        },
    ),
)

_PRESCRIPTION_FRAME = EntityFrame(
    task=(
        "Read the clinical letter. For each anti-seizure medication the patient "
        "is taking, produce one record in the 'mentions' list."
    ),
    text_definition=(
        "The medication concept — the SHORT drug name as it appears in the "
        "letter (e.g. 'lamotrigine', 'sodium valproate', 'carbamazepine'). "
        "Put dose, unit, and dosing frequency in attributes, NOT in this field. "
        "Must be an exact substring of the letter."
    ),
    clinical_rules=(
        "One record per medication.",
        "text is the medication name; dose/unit/frequency go in attributes.",
        "DrugDose is the numeric dose; DoseUnit is exactly 'mg' or 'g'.",
        (
            "Frequency is the dosing cadence coded as '1' (once daily), '2' "
            "(twice daily / bd), '3' (three times daily / tds), or 'As_Required' "
            "(prn / rescue / as needed)."
        ),
        "Both text and evidence must be exact substrings of the letter.",
        "If no medication is mentioned, return {\"mentions\": []}.",
        "Return exactly one JSON object. No markdown code fences.",
    ),
    worked_examples=(
        {
            "note_fragment": "He takes lamotrigine 200mg twice a day.",
            "correct": {
                "text": "lamotrigine",
                "attributes": {
                    "DrugName": "Lamotrigine",
                    "DrugDose": "200",
                    "DoseUnit": "mg",
                    "Frequency": "2",
                },
                "evidence": "lamotrigine 200mg twice a day",
                "confidence": "high",
                "rationale": "Lamotrigine 200 mg twice daily.",
            },
        },
        {
            "note_fragment": (
                "She is on sodium valproate 500mg in the morning and 1g at night, "
                "with buccal midazolam 10mg as required for prolonged seizures."
            ),
            "correct": [
                {
                    "text": "sodium valproate",
                    "attributes": {
                        "DrugName": "Sodium valproate",
                        "DrugDose": "500",
                        "DoseUnit": "mg",
                        "Frequency": "2",
                    },
                    "evidence": "sodium valproate 500mg in the morning and 1g at night",
                    "confidence": "high",
                    "rationale": "Sodium valproate dosed morning and night.",
                },
                {
                    "text": "buccal midazolam",
                    "attributes": {
                        "DrugName": "Midazolam",
                        "DrugDose": "10",
                        "DoseUnit": "mg",
                        "Frequency": "As_Required",
                    },
                    "evidence": "buccal midazolam 10mg as required for prolonged seizures",
                    "confidence": "high",
                    "rationale": "Rescue midazolam 10 mg as required.",
                },
            ],
            "note": "One record per medication; rescue meds use Frequency='As_Required'.",
        },
    ),
)

_INVESTIGATIONS_FRAME = EntityFrame(
    task=(
        "Read the clinical letter. For each investigation (EEG, MRI, CT, or "
        "telemetry) mentioned, produce one record in the 'mentions' list."
    ),
    text_definition=(
        "The investigation surface phrase as it appears in the letter — usually "
        "the bare modality token 'EEG', 'MRI', or 'CT'. Put performed/result "
        "information in attributes, NOT in this field. "
        "Must be an exact substring of the letter."
    ),
    clinical_rules=(
        "One record per investigation modality (EEG, MRI, CT).",
        (
            "Code whether the test was performed (MRI_Performed / CT_Performed / "
            "EEG_Performed = 'Yes' or 'No') and its result (MRI_Results / "
            "CT_Results / EEG_Results = 'Normal', 'Abnormal', or 'Unknown')."
        ),
        (
            "EEG_Type is 'Standard', 'SleepDeprived', or 'VideoTelemetry' when the "
            "type of EEG is stated."
        ),
        "text is the test phrase only; never put the result words in text.",
        "Both text and evidence must be exact substrings of the letter.",
        "If no investigation is mentioned, return {\"mentions\": []}.",
        "Return exactly one JSON object. No markdown code fences.",
    ),
    worked_examples=(
        {
            "note_fragment": "Her EEG was abnormal and her MRI brain was normal.",
            "correct": [
                {
                    "text": "EEG",
                    "attributes": {"EEG_Performed": "Yes", "EEG_Results": "Abnormal"},
                    "evidence": "EEG was abnormal",
                    "confidence": "high",
                    "rationale": "EEG performed, abnormal.",
                },
                {
                    "text": "MRI",
                    "attributes": {"MRI_Performed": "Yes", "MRI_Results": "Normal"},
                    "evidence": "MRI brain was normal",
                    "confidence": "high",
                    "rationale": "MRI performed, normal.",
                },
            ],
        },
        {
            "note_fragment": (
                "A sleep-deprived EEG is planned; a previous CT head showed no abnormality."
            ),
            "correct": [
                {
                    "text": "EEG",
                    "attributes": {"EEG_Performed": "No", "EEG_Type": "SleepDeprived"},
                    "evidence": "A sleep-deprived EEG is planned",
                    "confidence": "medium",
                    "rationale": "Sleep-deprived EEG planned, not yet performed.",
                },
                {
                    "text": "CT",
                    "attributes": {"CT_Performed": "Yes", "CT_Results": "Normal"},
                    "evidence": "a previous CT head showed no abnormality",
                    "confidence": "high",
                    "rationale": "CT performed, normal.",
                },
            ],
        },
    ),
)

_DIAGNOSIS_FRAME = EntityFrame(
    task=(
        "Read the clinical letter. For each diagnosis or diagnostic category "
        "stated, produce one record in the 'mentions' list."
    ),
    text_definition=(
        "The compact diagnostic phrase — the clean clinical term naming the "
        "diagnosis (e.g. 'focal epilepsy', 'juvenile myoclonic epilepsy', "
        "'single seizure'), not a whole explanatory clause. "
        "Must be an exact substring of the letter."
    ),
    clinical_rules=(
        "One record per distinct diagnosis.",
        (
            "DiagCategory is 'Epilepsy' (an epilepsy diagnosis), 'MultipleSeizures' "
            "(recurrent seizures not yet called epilepsy), or 'SingleSeizure'."
        ),
        (
            "Certainty is '1'-'5' (5 = definite, lower = more tentative); Negation "
            "is 'Affirmed' or 'Negated'. Use Negation='Negated' when the diagnosis "
            "is explicitly excluded."
        ),
        "text is the compact diagnostic term, not the surrounding sentence.",
        "Both text and evidence must be exact substrings of the letter.",
        "If no diagnosis is stated, return {\"mentions\": []}.",
        "Return exactly one JSON object. No markdown code fences.",
    ),
    worked_examples=(
        {
            "note_fragment": "He has a confirmed diagnosis of focal epilepsy.",
            "correct": {
                "text": "focal epilepsy",
                "attributes": {
                    "DiagCategory": "Epilepsy",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "confirmed diagnosis of focal epilepsy",
                "confidence": "high",
                "rationale": "Confirmed focal epilepsy.",
            },
        },
        {
            "note_fragment": (
                "This was a single seizure; there is no evidence of epilepsy at this stage."
            ),
            "correct": [
                {
                    "text": "single seizure",
                    "attributes": {
                        "DiagCategory": "SingleSeizure",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                    "evidence": "This was a single seizure",
                    "confidence": "high",
                    "rationale": "A single seizure occurred.",
                },
                {
                    "text": "epilepsy",
                    "attributes": {
                        "DiagCategory": "Epilepsy",
                        "Certainty": "5",
                        "Negation": "Negated",
                    },
                    "evidence": "no evidence of epilepsy at this stage",
                    "confidence": "high",
                    "rationale": "Epilepsy explicitly excluded.",
                },
            ],
        },
    ),
)

_ONSET_FRAME = EntityFrame(
    task=(
        "Read the clinical letter. For each condition or seizure type whose age "
        "or time of ONSET (when it first began) is stated, produce one record in "
        "the 'mentions' list."
    ),
    text_definition=(
        "The phrase naming the condition or seizure type whose onset is being "
        "dated (e.g. 'epilepsy', 'absence seizures', 'generalised tonic-clonic "
        "seizures'). Put the age/date/period in attributes, NOT in this field. "
        "Must be an exact substring of the letter."
    ),
    clinical_rules=(
        "One record per condition whose onset age or time is stated.",
        (
            "Onset at a stated age: Age = the number, AgeUnit = 'Year' or 'Month' "
            "(e.g. 'since the age of four' → Age='4', AgeUnit='Year')."
        ),
        (
            "Onset as a duration-ago: NumberOfTimePeriods + TimePeriod "
            "(e.g. 'epilepsy for the past 10 years' → NumberOfTimePeriods='10', "
            "TimePeriod='Year')."
        ),
        "Use PointInTime='From_Birth' when the condition is present from birth.",
        (
            "Certainty is '1'-'5' (5 = definite); Negation is 'Affirmed' or "
            "'Negated'."
        ),
        "ONSET is when the condition BEGAN — not when it was diagnosed.",
        "text is the condition phrase only, never the age/time clause.",
        "Both text and evidence must be exact substrings of the letter.",
        "If no onset information is present, return {\"mentions\": []}.",
        "Return exactly one JSON object. No markdown code fences.",
    ),
    worked_examples=(
        {
            "note_fragment": "He developed epilepsy at the age of four.",
            "correct": {
                "text": "epilepsy",
                "attributes": {
                    "Age": "4",
                    "AgeUnit": "Year",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "developed epilepsy at the age of four",
                "confidence": "high",
                "rationale": "Epilepsy onset at age 4.",
            },
        },
        {
            "note_fragment": "She has had absence seizures for the past 10 years.",
            "correct": {
                "text": "absence seizures",
                "attributes": {
                    "NumberOfTimePeriods": "10",
                    "TimePeriod": "Year",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "absence seizures for the past 10 years",
                "confidence": "high",
                "rationale": "Absence seizures began 10 years ago.",
            },
        },
    ),
)

_WHEN_DIAGNOSED_FRAME = EntityFrame(
    task=(
        "Read the clinical letter. For each condition whose age or date of "
        "DIAGNOSIS is stated, produce one record in the 'mentions' list."
    ),
    text_definition=(
        "The phrase naming the condition that was diagnosed (usually 'epilepsy'). "
        "Put the diagnosis age/date/period in attributes, NOT in this field. "
        "Must be an exact substring of the letter."
    ),
    clinical_rules=(
        "One record per condition with a stated diagnosis time.",
        (
            "Diagnosis at a stated age: Age + AgeUnit ('Year'/'Month') "
            "(e.g. 'diagnosed at 18' → Age='18', AgeUnit='Year')."
        ),
        (
            "Diagnosis on a calendar date: YearDate (and MonthDate as a number) "
            "(e.g. 'diagnosed in 2015' → YearDate='2015')."
        ),
        (
            "Diagnosis a duration ago: NumberOfTimePeriods + TimePeriod "
            "(e.g. 'diagnosed 6 years ago' → NumberOfTimePeriods='6', "
            "TimePeriod='Year')."
        ),
        "Certainty is '1'-'5'; Negation is 'Affirmed' or 'Negated'.",
        (
            "This entity is WHEN the condition was DIAGNOSED — distinct from Onset "
            "(when it first began)."
        ),
        "text is the condition phrase only, never the date clause.",
        "Both text and evidence must be exact substrings of the letter.",
        "If no diagnosis date/age is stated, return {\"mentions\": []}.",
        "Return exactly one JSON object. No markdown code fences.",
    ),
    worked_examples=(
        {
            "note_fragment": "She was diagnosed with epilepsy in 2015.",
            "correct": {
                "text": "epilepsy",
                "attributes": {
                    "YearDate": "2015",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "diagnosed with epilepsy in 2015",
                "confidence": "high",
                "rationale": "Epilepsy diagnosed in 2015.",
            },
        },
        {
            "note_fragment": "He was diagnosed with epilepsy at the age of 6.",
            "correct": {
                "text": "epilepsy",
                "attributes": {
                    "Age": "6",
                    "AgeUnit": "Year",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "diagnosed with epilepsy at the age of 6",
                "confidence": "high",
                "rationale": "Epilepsy diagnosed at age 6.",
            },
        },
    ),
)

_BIRTH_HISTORY_FRAME = EntityFrame(
    task=(
        "Read the clinical letter. For each birth-history finding (how the patient "
        "was born and perinatal events around birth), produce one record in the "
        "'mentions' list."
    ),
    text_definition=(
        "The compact birth-history phrase as it appears in the letter "
        "(e.g. 'born normally', 'born prematurely', 'full term', 'perinatal "
        "insult'). Put the gestation band in attributes. "
        "Must be an exact substring of the letter."
    ),
    clinical_rules=(
        "One record per birth-history finding.",
        (
            "PrematureBirth carries the gestation band when stated: "
            "'37+_TermBirth' (term), '34to<37_LatePreterm' / "
            "'34to<37_LatePretermBirth' (late preterm), "
            "'32to<37_ModerateToLatePreterm'."
        ),
        (
            "Certainty is '1'-'5'; Negation is 'Affirmed' or 'Negated'. A stated "
            "normal birth is Negation='Affirmed'."
        ),
        "text is the compact birth phrase, not the surrounding sentence.",
        "Both text and evidence must be exact substrings of the letter.",
        "If no birth-history finding is present, return {\"mentions\": []}.",
        "Return exactly one JSON object. No markdown code fences.",
    ),
    worked_examples=(
        {
            "note_fragment": "He was born normally with no perinatal problems.",
            "correct": {
                "text": "born normally",
                "attributes": {"Certainty": "5", "Negation": "Affirmed"},
                "evidence": "born normally with no perinatal problems",
                "confidence": "high",
                "rationale": "Normal birth.",
            },
        },
        {
            "note_fragment": "She was born prematurely at 34 weeks.",
            "correct": {
                "text": "born prematurely",
                "attributes": {
                    "PrematureBirth": "34to<37_LatePreterm",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "born prematurely at 34 weeks",
                "confidence": "high",
                "rationale": "Late-preterm birth at 34 weeks.",
            },
        },
    ),
)

_EPILEPSY_CAUSE_FRAME = EntityFrame(
    task=(
        "Read the clinical letter. For each cause, aetiology, syndrome, or risk "
        "factor offered for the patient's epilepsy, produce one record in the "
        "'mentions' list."
    ),
    text_definition=(
        "The compact cause/aetiology phrase as it appears in the letter "
        "(e.g. 'stroke', 'traumatic brain injury', 'meningitis', 'tuberous "
        "sclerosis'), not the surrounding explanatory clause. "
        "Must be an exact substring of the letter."
    ),
    clinical_rules=(
        "One record per distinct cause or risk factor for the epilepsy.",
        (
            "Certainty is '1'-'5' — use a lower value when the causal link is "
            "tentative ('possible', 'likely', 'thought to be due to')."
        ),
        (
            "Negation is 'Affirmed' or 'Negated'; use 'Negated' when a candidate "
            "cause is explicitly considered and excluded."
        ),
        "text is the compact cause phrase, not the whole clause.",
        "Both text and evidence must be exact substrings of the letter.",
        "If no cause is offered, return {\"mentions\": []}.",
        "Return exactly one JSON object. No markdown code fences.",
    ),
    worked_examples=(
        {
            "note_fragment": (
                "His epilepsy is due to a previous traumatic brain injury."
            ),
            "correct": {
                "text": "traumatic brain injury",
                "attributes": {"Certainty": "5", "Negation": "Affirmed"},
                "evidence": "epilepsy is due to a previous traumatic brain injury",
                "confidence": "high",
                "rationale": "TBI is the stated cause.",
            },
        },
        {
            "note_fragment": (
                "The likely cause is a previous stroke; meningitis was considered "
                "but excluded."
            ),
            "correct": [
                {
                    "text": "stroke",
                    "attributes": {"Certainty": "4", "Negation": "Affirmed"},
                    "evidence": "likely cause is a previous stroke",
                    "confidence": "medium",
                    "rationale": "Stroke is the likely (not definite) cause.",
                },
                {
                    "text": "meningitis",
                    "attributes": {"Certainty": "5", "Negation": "Negated"},
                    "evidence": "meningitis was considered but excluded",
                    "confidence": "high",
                    "rationale": "Meningitis explicitly excluded as a cause.",
                },
            ],
        },
    ),
)

_PATIENT_HISTORY_FRAME = EntityFrame(
    task=(
        "Read the clinical letter. For each past medical event, condition, attack "
        "type, or procedure in the patient's history, produce one record in the "
        "'mentions' list."
    ),
    text_definition=(
        "The compact clinical concept phrase as it appears in the letter — a past "
        "condition, event, attack type, or procedure (e.g. 'febrile seizures', "
        "'diabetes', 'hypothyroidism'), not the full historical sentence. "
        "Must be an exact substring of the letter."
    ),
    clinical_rules=(
        "One record per distinct historical concept.",
        (
            "Dates: YearDate (and MonthDate / DayDate as numbers) when a calendar "
            "date is given. Age + AgeUnit when an age is given. "
            "NumberOfTimePeriods + TimePeriod for a duration."
        ),
        "PointInTime is 'Last_Year' or 'Surgery' when applicable.",
        "Certainty is '1'-'5'; Negation is 'Affirmed' or 'Negated'.",
        "text is the compact concept phrase, not the full historical sentence.",
        "Both text and evidence must be exact substrings of the letter.",
        "If no relevant history is present, return {\"mentions\": []}.",
        "Return exactly one JSON object. No markdown code fences.",
    ),
    worked_examples=(
        {
            "note_fragment": (
                "He has a history of febrile seizures as a child and type 2 diabetes."
            ),
            "correct": [
                {
                    "text": "febrile seizures",
                    "attributes": {"Certainty": "5", "Negation": "Affirmed"},
                    "evidence": "history of febrile seizures as a child",
                    "confidence": "high",
                    "rationale": "Past febrile seizures.",
                },
                {
                    "text": "diabetes",
                    "attributes": {"Certainty": "5", "Negation": "Affirmed"},
                    "evidence": "type 2 diabetes",
                    "confidence": "high",
                    "rationale": "Comorbid diabetes.",
                },
            ],
        },
        {
            "note_fragment": "She had absence-like seizures in 2014.",
            "correct": {
                "text": "absence-like seizures",
                "attributes": {
                    "YearDate": "2014",
                    "Certainty": "5",
                    "Negation": "Affirmed",
                },
                "evidence": "absence-like seizures in 2014",
                "confidence": "high",
                "rationale": "Absence-like seizures recorded in 2014.",
            },
        },
    ),
)


def _generic_frame(entity_name: str) -> EntityFrame:
    """Fallback frame for any entity without a specialized frame.

    After Phase B all nine ExECTv2 entities have specialized frames; this remains
    only as a defensive fallback for an unexpected entity name.
    """
    return EntityFrame(
        task=(
            f"Read the clinical letter. For each {entity_name} finding stated, "
            "produce one record in the 'mentions' list."
        ),
        text_definition=(
            "The compact phrase naming the finding as it appears in the letter. "
            "Must be an exact substring of the letter."
        ),
        clinical_rules=(
            "One record per distinct finding.",
            "Include only attributes explicitly supported by the letter.",
            "Both text and evidence must be exact substrings of the letter.",
            f"If no {entity_name} finding is present, return {{\"mentions\": []}}.",
            "Return exactly one JSON object. No markdown code fences.",
        ),
    )


ENTITY_FRAMES: dict[str, EntityFrame] = {
    "SeizureFrequency": _SF_FRAME,
    "Prescription": _PRESCRIPTION_FRAME,
    "Investigations": _INVESTIGATIONS_FRAME,
    "Diagnosis": _DIAGNOSIS_FRAME,
    "Onset": _ONSET_FRAME,
    "WhenDiagnosed": _WHEN_DIAGNOSED_FRAME,
    "BirthHistory": _BIRTH_HISTORY_FRAME,
    "EpilepsyCause": _EPILEPSY_CAUSE_FRAME,
    "PatientHistory": _PATIENT_HISTORY_FRAME,
}


def frame_for(entity_name: str) -> EntityFrame:
    return ENTITY_FRAMES.get(entity_name) or _generic_frame(entity_name)


# ── Prompt builder ────────────────────────────────────────────────────────────


def _attribute_vocabulary(spec: EntitySpec) -> dict[str, Any]:
    """Registry-derived attribute vocabulary for one entity.

    Closed-vocab attributes expose their legal value set; CUI keys are documented
    as do-not-guess; the rest are free string values copied from the letter.
    """
    attrs: dict[str, Any] = {}
    for attr in sorted(spec.legal_attributes):
        if attr == "CUIPhrase":
            attrs[attr] = "Clean concept phrase if explicitly available; otherwise omit."
        elif attr == "CUI":
            attrs[attr] = "UMLS CUI only if explicitly available; never guess."
        elif attr in spec.closed_vocab:
            attrs[attr] = sorted(spec.closed_vocab[attr])
        else:
            attrs[attr] = "string value copied or normalized from the letter."
    return attrs


def build_prompt_input(
    letter: ExectLetter, *, entity_name: str = DEFAULT_ENTITY_NAME
) -> str:
    """Build a focused per-entity v0.3 prompt for one entity.

    The clinical content (task, text definition, worked examples, clinical rules)
    comes from the entity's :class:`EntityFrame`; the attribute vocabulary and the
    JSON envelope are derived from the registry so the frame stays in sync with
    the contract.
    """
    spec = ENTITY_REGISTRY[entity_name]
    eframe = frame_for(entity_name)
    payload = {
        "prompt_version": PROMPT_VERSION,
        "entity": entity_name,
        "task": eframe.task,
        "field_definitions": {
            "text": eframe.text_definition,
            "attributes": (
                "Coded clinical features for this finding. Include only those "
                "explicitly present. All values must be strings."
            ),
            "evidence": (
                "The exact clause or sentence from the letter that supports this "
                "finding and its attributes. Must be an exact substring of the letter."
            ),
            "confidence": (
                "'high': unambiguous finding, attributes clearly stated. "
                "'medium': finding clear but an attribute is vague, approximate, "
                "or conditional. "
                "'low': competing or ambiguous statements that cannot be resolved."
            ),
            "rationale": "One sentence: the deciding evidence and the coded result.",
        },
        "worked_examples": list(eframe.worked_examples),
        "attribute_vocabulary": _attribute_vocabulary(spec),
        "clinical_rules": list(eframe.clinical_rules),
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


# ── Adapter ───────────────────────────────────────────────────────────────────


def to_predicted_letter(
    letter_id: str,
    mentions: list[MentionRecord],
    *,
    spec: EntitySpec,
    note_text: str,
    entity_name: str,
) -> tuple[PredictedLetter, list[str]]:
    """Repair attributes and build a PredictedLetter from scored mentions.

    Only evidence-valid mentions with repaired (schema-legal) attributes survive.
    All drops/repairs are logged; no clinical fact is invented or altered.
    """
    all_warnings: list[str] = []
    evidence_valid, evidence_invalid, ev_warnings = check_evidence(
        mentions, note_text=note_text
    )
    all_warnings.extend(ev_warnings)

    predicted_mentions: list[PredictedMention] = []
    for mention in evidence_valid:
        repaired_attrs, attr_warnings = repair_attributes(
            dict(mention.attributes), spec=spec
        )
        all_warnings.extend(attr_warnings)
        predicted_mentions.append(
            PredictedMention(
                entity=entity_name,
                text=mention.text,
                attributes=repaired_attrs,
                evidence=mention.evidence,
                confidence=mention.confidence,
                rationale=mention.rationale,
                component_owner=COMPONENT_OWNER,
            )
        )

    return (
        project_cuis(
            PredictedLetter(
                letter_id=letter_id,
                mentions=tuple(predicted_mentions),
                diagnostics={
                    "prompt_version": PROMPT_VERSION,
                    "entity": entity_name,
                    "n_evidence_invalid": len(evidence_invalid),
                    "attribute_warnings": all_warnings,
                },
            )
        ),
        all_warnings,
    )


# ── Runner ────────────────────────────────────────────────────────────────────


def run_split(
    letters: Sequence[ExectLetter],
    *,
    entity_name: str = DEFAULT_ENTITY_NAME,
    split: str,
    model: str,
    temperature: float,
    max_tokens: int,
    mode: Literal["live", "prompt-only"],
    dspy_cache: bool = True,
    api_base: str | None = None,
    progress_every: int | None = None,
    checkpoint_jsonl_path: Path | None = None,
    checkpoint_report_path: Path | None = None,
    resume: bool = False,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Run the focused per-entity extractor for ``entity_name`` over a split.

    When ``resume`` is set and ``checkpoint_jsonl_path`` already holds a partial
    run, letters already present are skipped and only the remainder is processed
    (see ``core.run_resume``).
    """
    spec = ENTITY_REGISTRY[entity_name]
    program = DspyPerEntityExtractor()
    if mode == "live":
        dspy.configure(
            lm=build_dspy_lm(
                model,
                temperature=temperature,
                max_tokens=max_tokens,
                cache=dspy_cache,
                api_base=api_base,
            )
        )

    order = [letter.letter_id for letter in letters]
    requested = set(order)
    existing_rows, completed = read_completed(
        checkpoint_jsonl_path if resume else None, key="letter_id"
    )
    rows: list[dict[str, Any]] = [
        r for r in existing_rows if r.get("letter_id") in requested
    ]
    n_resumed = len(rows)
    todo = pending_items(letters, completed, key_of=lambda letter: letter.letter_id)

    for letter in todo:
        prompt_input_json = build_prompt_input(letter, entity_name=entity_name)
        raw_output = ""
        call_error: str | None = None

        if mode == "live":
            try:
                prediction = program(prompt_input_json=prompt_input_json)
                raw_output = str(prediction.extraction_json)
            except Exception as exc:  # pragma: no cover
                call_error = f"{type(exc).__name__}: {exc}"

        extraction, parse_errors = (
            parse_extraction_json(raw_output) if raw_output else (None, ["not_run"])
        )

        mentions = extraction.mentions if extraction else []
        predicted_letter, gate_warnings = to_predicted_letter(
            letter.letter_id,
            mentions,
            spec=spec,
            note_text=letter.note_text,
            entity_name=entity_name,
        )
        evidence_valid_count = len(predicted_letter.mentions)
        evidence_invalid_count = len(mentions) - evidence_valid_count

        gold = letter.entities(entity_name)
        rows.append(
            {
                "letter_id": letter.letter_id,
                "split": split,
                "entity": entity_name,
                "prompt_version": PROMPT_VERSION,
                "model": model,
                "mode": mode,
                "prompt_input_json": prompt_input_json,
                "raw_output": raw_output,
                "call_error": call_error,
                "parse_errors": parse_errors,
                "gate_warnings": gate_warnings,
                "n_mentions_raw": len(mentions),
                "n_mentions_scored": evidence_valid_count,
                "n_evidence_invalid": evidence_invalid_count,
                "predicted_mentions": [
                    {
                        "entity": m.entity,
                        "text": m.text,
                        "attributes": dict(m.attributes),
                        "evidence": m.evidence,
                        "confidence": m.confidence,
                        "rationale": m.rationale,
                        "component_owner": m.component_owner,
                        "source_lane": COMPONENT_OWNER,
                    }
                    for m in predicted_letter.mentions
                ],
                "gold_mentions": [
                    {
                        "entity": a.entity,
                        "text": a.text,
                        "attributes": dict(a.attributes),
                    }
                    for a in gold
                ],
            }
        )

        if progress_every and (len(rows) - n_resumed) % progress_every == 0:
            _emit_checkpoint(
                rows,
                entity_name=entity_name,
                total=len(letters),
                jsonl_path=checkpoint_jsonl_path,
                report_path=checkpoint_report_path,
                split=split,
                model=model,
                mode=mode,
            )

    rows = merge_rows(rows, order, key="letter_id")
    metadata = {
        "prompt_version": PROMPT_VERSION,
        "entity_name": entity_name,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "mode": mode,
        "split": split,
        "n_letters": len(letters),
        "n_resumed": n_resumed,
        "dspy_version": getattr(dspy, "__version__", "unknown"),
    }
    metadata["summary"] = summarize_rows(rows, entity_name=entity_name)
    return rows, metadata


# ── Scoring / summary ─────────────────────────────────────────────────────────


def _entity_of(rows: Sequence[dict[str, Any]]) -> str:
    for row in rows:
        entity = row.get("entity")
        if entity:
            return str(entity)
    return DEFAULT_ENTITY_NAME


def summarize_rows(
    rows: Sequence[dict[str, Any]], *, entity_name: str | None = None
) -> dict[str, Any]:
    """Aggregate gate stats plus the three-layer + source-near scorecard.

    The three format layers (phrase_only / semantic / benchmark) are the
    headline; ``source_near`` overlap recall is the format-blind candidate read
    Phase A turns on. ``over_emission`` is the source-near FP count.
    """
    n = len(rows)
    if n == 0:
        return {"examples": 0}

    entity = entity_name or _entity_of(rows)

    call_failures = sum(bool(r.get("call_error")) for r in rows)
    parse_failures = sum(_has_blocking_parse_issue(r.get("parse_errors")) for r in rows)
    n_mentions_raw = sum(int(r.get("n_mentions_raw", 0)) for r in rows)
    n_scored = sum(int(r.get("n_mentions_scored", 0)) for r in rows)
    n_evidence_invalid = sum(int(r.get("n_evidence_invalid", 0)) for r in rows)

    gold_letters = _reconstruct_gold_letters(rows, entity)
    pred_letters = _reconstruct_pred_letters(rows, entity)

    scores: dict[str, Any] = {}
    for config_name, config in (
        ("phrase_only", PHRASE_ONLY),
        ("semantic", semantic_config_for(entity)),
        ("benchmark", benchmark_config_for(entity)),
    ):
        scores[config_name] = _entity_score_to_dict(
            score_entity(gold_letters, pred_letters, entity, config)
        )

    source_near = source_near_diagnostic(
        gold_letters, pred_letters, [entity], semantic_config_for
    ).per_entity[entity]

    return {
        "entity": entity,
        "examples": n,
        "call_failures": call_failures,
        "parse_failures": parse_failures,
        "n_mentions_raw": n_mentions_raw,
        "n_mentions_scored": n_scored,
        "n_evidence_invalid": n_evidence_invalid,
        "evidence_validity_rate": (
            round((n_mentions_raw - n_evidence_invalid) / n_mentions_raw, 4)
            if n_mentions_raw
            else 1.0
        ),
        "published_per_item_target": PUBLISHED_PER_ENTITY_ITEM_F1.get(entity),
        "scores": scores,
        "source_near": {
            "overlap": _prf1_to_dict(source_near.overlap),
            "attribute_agreement_tp": source_near.attribute_agreement_tp,
            "attribute_agreement_total": source_near.attribute_agreement_total,
            "attribute_agreement_rate": round(source_near.attribute_agreement_rate, 4),
        },
        "over_emission": source_near.overlap.fp,
    }


def _entity_score_to_dict(score: Any) -> dict[str, Any]:
    return {
        "per_item": _prf1_to_dict(score.per_item),
        "per_letter": _prf1_to_dict(score.per_letter),
    }


def _prf1_to_dict(score: Any) -> dict[str, Any]:
    return {
        "precision": round(score.precision, 4),
        "recall": round(score.recall, 4),
        "f1": round(score.f1, 4),
        "tp": score.tp,
        "fp": score.fp,
        "fn": score.fn,
    }


def _reconstruct_gold_letters(
    rows: Sequence[dict[str, Any]], entity: str
) -> list[ExectLetter]:
    letters: list[ExectLetter] = []
    for row in rows:
        annotations = tuple(
            ExectAnnotation(
                entity=entity,
                text=m["text"],
                attributes=m["attributes"],
            )
            for m in (row.get("gold_mentions") or [])
        )
        letters.append(
            ExectLetter(
                letter_id=row["letter_id"],
                note_text="",
                annotations=annotations,
            )
        )
    return letters


def _reconstruct_pred_letters(
    rows: Sequence[dict[str, Any]], entity: str
) -> list[ExectLetter]:
    letters: list[ExectLetter] = []
    for row in rows:
        pred_letter = PredictedLetter(
            letter_id=row["letter_id"],
            mentions=tuple(
                PredictedMention(
                    entity=entity,
                    text=m["text"],
                    attributes=m["attributes"],
                    evidence=m.get("evidence", ""),
                    confidence=m.get("confidence", "medium"),
                    rationale=m.get("rationale", ""),
                )
                for m in (row.get("predicted_mentions") or [])
            ),
        )
        letters.append(to_exect_letter(pred_letter))
    return letters


# ── Reports ───────────────────────────────────────────────────────────────────


def write_report(
    rows: Sequence[dict[str, Any]],
    metadata: dict[str, Any],
    path: Path,
    *,
    jsonl_path: Path,
) -> None:
    """Write a concise per-entity Markdown run report."""
    path.parent.mkdir(parents=True, exist_ok=True)
    entity = metadata.get("entity_name") or _entity_of(rows)
    summary = metadata.get("summary") or summarize_rows(rows, entity_name=entity)
    scores = summary.get("scores", {})
    source_near = summary.get("source_near", {})
    overlap = source_near.get("overlap", {})
    target = summary.get("published_per_item_target")
    is_checkpoint = bool(metadata.get("is_checkpoint"))

    lines = [f"# ExECTv2 LLM-Only Per-Entity — {entity}", ""]
    if is_checkpoint:
        total = int(metadata.get("total_letters") or summary.get("examples", 0))
        lines.extend([f"CHECKPOINT ONLY: processed {summary.get('examples', 0)} / {total}", ""])
    lines.extend([
        f"- JSONL: `{jsonl_path}`",
        f"- Prompt version: `{metadata.get('prompt_version', PROMPT_VERSION)}`",
        f"- Entity: `{entity}`",
        f"- Split: `{metadata.get('split')}`",
        f"- Model: `{metadata.get('model')}`",
        f"- Mode: `{metadata.get('mode')}`",
        f"- Letters: {summary.get('examples', 0)}",
        f"- Published per-item F1 target: {target if target is None else f'{target:.2f}'}",
        "",
        "## Gate Summary",
        "",
        f"- Call failures: {summary.get('call_failures', 0)}",
        f"- Parse/schema failures: {summary.get('parse_failures', 0)}",
        f"- Mentions raw: {summary.get('n_mentions_raw', 0)}",
        f"- Mentions scored (evidence-valid): {summary.get('n_mentions_scored', 0)}",
        f"- Evidence-invalid dropped: {summary.get('n_evidence_invalid', 0)}",
        f"- Evidence validity rate: {summary.get('evidence_validity_rate', 0.0):.4f}",
        "",
        "## Format Layers",
        "",
        "| Layer | Item F1 | Item P | Item R | Letter F1 | TP | FP | FN |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for config_name in ("phrase_only", "semantic", "benchmark"):
        s = scores.get(config_name, {})
        pi = s.get("per_item", {})
        pl = s.get("per_letter", {})
        lines.append(
            f"| {config_name} | {pi.get('f1', 0):.3f} | {pi.get('precision', 0):.3f} "
            f"| {pi.get('recall', 0):.3f} | {pl.get('f1', 0):.3f} "
            f"| {pi.get('tp', 0)} | {pi.get('fp', 0)} | {pi.get('fn', 0)} |"
        )
    lines.extend([
        "",
        "## Source-Near Candidate Diagnostic (format-blind)",
        "",
        f"- Overlap recall: {overlap.get('recall', 0):.3f} "
        f"(TP={overlap.get('tp', 0)} FN={overlap.get('fn', 0)})",
        f"- Overlap F1: {overlap.get('f1', 0):.3f}",
        f"- Over-emission (overlap FP): {summary.get('over_emission', 0)}",
        f"- Attribute agreement on overlaps: "
        f"{source_near.get('attribute_agreement_rate', 0):.3f} "
        f"({source_near.get('attribute_agreement_tp', 0)}/"
        f"{source_near.get('attribute_agreement_total', 0)})",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def _emit_checkpoint(
    rows: Sequence[dict[str, Any]],
    *,
    entity_name: str,
    total: int,
    jsonl_path: Path | None,
    report_path: Path | None,
    split: str,
    model: str,
    mode: str,
) -> None:
    summary = summarize_rows(rows, entity_name=entity_name)
    if jsonl_path is not None:
        write_jsonl(rows, jsonl_path)
    if report_path is not None and jsonl_path is not None:
        write_report(
            rows,
            {
                "prompt_version": PROMPT_VERSION,
                "entity_name": entity_name,
                "split": split,
                "model": model,
                "mode": mode,
                "summary": summary,
                "is_checkpoint": True,
                "total_letters": total,
            },
            report_path,
            jsonl_path=jsonl_path,
        )
    progress = {
        "entity": entity_name,
        "processed": len(rows),
        "total": total,
        "call_failures": summary.get("call_failures", 0),
        "parse_failures": summary.get("parse_failures", 0),
        "n_mentions_scored": summary.get("n_mentions_scored", 0),
    }
    print(json.dumps(progress, sort_keys=True), file=sys.stderr, flush=True)
