"""Prompt-input construction for the target-indicators single call.

Pure relocation from ``llm_target_indicators_single_call``. The prompt strings,
worked examples, and attribute vocabulary are copied verbatim.
"""

from __future__ import annotations

import json
from typing import Any

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.contract.entities import (
    ENTITY_REGISTRY,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.reports.target_indicator_report import (  # noqa: E501
    TARGET_INDICATORS,
)

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.target_indicators_single_call.constants import (  # noqa: E501
    PROMPT_VERSION,
)


def build_prompt_input(letter: ExectLetter) -> str:
    """Build the one-call target-only prompt payload."""

    payload = {
        "prompt_version": PROMPT_VERSION,
        "task": (
            "Read one epilepsy clinic letter and extract ONLY these four ExECTv2 "
            "target indicators: Diagnosis, SeizureFrequency, Prescription, and "
            "Investigations. Candidate generation and final selection happen in this "
            "single response. Deterministic code will later validate evidence, repair "
            "schema/format, normalize attributes, and project CUIs."
        ),
        "output_schema": {
            "entity": f"One of: {', '.join(TARGET_INDICATORS)}.",
            "text": (
                "Short phrase naming the clinical fact. For Diagnosis, use the "
                "normalized core clinical concept when the source includes certainty "
                "words such as probable/possible."
            ),
            "attributes": "String-to-string object; use only legal attributes below.",
            "evidence": (
                "Exact source substring supporting the mention and attributes. Evidence "
                "must appear verbatim in the letter."
            ),
            "confidence": "low | medium | high",
            "rationale": "Optional. Prefer an empty string; never include deliberation.",
        },
        "attribute_vocabulary": _target_attribute_vocabulary(),
        "indicator_policy": {
            "Diagnosis": [
                (
                    "Extract patient diagnoses: epilepsy, epilepsy syndromes, and "
                    "named epileptic seizure diagnoses."
                ),
                (
                    "Every named epileptic seizure type in a diagnosis, history, "
                    "current-seizure, or frequency statement is also a Diagnosis "
                    "fact, even when you also emit SeizureFrequency."
                ),
                (
                    "Always preserve the diagnosis header/impression syndrome or "
                    "category as its own Diagnosis fact, such as temporal lobe "
                    "epilepsy, intractable epilepsy, primary/generalised epilepsy, "
                    "epileptic attack, or single focal seizure."
                ),
                (
                    "Do not replace a specific diagnosis header with a looser parent. "
                    "If the header says temporal lobe epilepsy, emit temporal lobe "
                    "epilepsy; if it says focal epilepsy or possible focal onset, emit "
                    "focal epilepsy with the appropriate Certainty."
                ),
                (
                    "If the source says epilepsy with generalised tonic clonic "
                    "seizures alone/on awakening, keep that full syndrome Diagnosis "
                    "as well as any seizure-type Diagnosis facts."
                ),
                (
                    "If a diagnosis header gives a broad epilepsy category and the "
                    "history gives seizure types, emit both the category/syndrome "
                    "and the seizure types."
                ),
                (
                    "Phrases such as 'I suspect epilepsy' or 'possible epilepsy' "
                    "are Diagnosis facts with lower Certainty, not omissions."
                ),
                (
                    "Do not extract family history, education, driving advice, or "
                    "hypothetical risk as Diagnosis. Do not extract migraine, "
                    "headache, anxiety, depression, syncope, or learning difficulty "
                    "as Diagnosis."
                ),
                (
                    "Split coordinated diagnosis phrases into atomic concepts when "
                    "each is explicitly present."
                ),
                (
                    "Use Certainty 5 for established, 4 for likely/probable, 3 for "
                    "possible/query/suspected."
                ),
                "Use Negation=Affirmed unless the diagnosis is explicitly negated.",
                (
                    "Use DiagCategory=Epilepsy for epilepsy/syndrome, "
                    "MultipleSeizures for plural seizure types, SingleSeizure for a "
                    "single seizure type."
                ),
            ],
            "SeizureFrequency": [
                (
                    "Extract each seizure type with current or stated frequency, "
                    "seizure-free state, or explicit frequency change."
                ),
                "Mention text is the seizure anchor only, not the full frequency clause.",
                (
                    "Use NumberOfSeizures=0 for seizure-free statements with a "
                    "duration, date, or since-anchor."
                ),
                (
                    "For 'no seizures since <date/year/event>', emit a seizure-free "
                    "SeizureFrequency mention with NumberOfSeizures=0, "
                    "TimeSince_or_TimeOfEvent=Since, and YearDate/MonthDate or "
                    "PointInTime when stated."
                ),
                (
                    "For 'no further seizures' or 'no recurrent seizures' with no "
                    "date, emit NumberOfSeizures=0 on the seizure anchor."
                ),
                (
                    "For 'since last clinic' or similar clinic anchors, use "
                    "TimeSince_or_TimeOfEvent=Since and PointInTime=LastClinic."
                ),
                (
                    "For 'last week', 'last month', or 'last year' occurrence "
                    "windows, use TimeSince_or_TimeOfEvent=During with "
                    "PointInTime=Last_Week, Last_Month, or Last_Year rather than "
                    "converting to a per-week/month/year rate."
                ),
                (
                    "For explicit change words such as increased, decreased, better, "
                    "worse, rare, infrequent, or clusters, emit a separate "
                    "SeizureFrequency mention carrying FrequencyChange or the "
                    "stated dated/windowed count."
                ),
                (
                    "If the text says seizures became infrequent, controlled, or "
                    "changed after a drug change, use PointInTime=DrugChange with "
                    "the FrequencyChange value when stated."
                ),
                (
                    "Do not emit SeizureFrequency for historical seizure descriptions "
                    "unless a count, rate, date-window, since-anchor, seizure-free "
                    "state, or explicit change word is stated."
                ),
                (
                    "Do not emit SeizureFrequency for 'frequency unknown', diagnostic "
                    "seizure types, or old history without a current/stated state."
                ),
                (
                    "Remote lifetime history such as childhood febrile seizures or "
                    "'last seizures were in teenage years' is not an active rate; "
                    "only emit a seizure-free/since state if the text gives a clear "
                    "since-anchor."
                ),
                "Use NumberOfTimePeriods=1 with TimePeriod for per-day/week/month/year cadence.",
                (
                    "Do not collapse states: the same seizure anchor can have both "
                    "an active rate and a seizure-free/since-date fact."
                ),
                "Do not emit bare seizure words with no frequency/state attributes.",
            ],
            "Prescription": [
                "Extract current anti-seizure medication regimens and rescue medication.",
                (
                    "Do not extract stopped, previous, conditional future, or merely "
                    "discussed medications."
                ),
                "Use DrugName, DrugDose, DoseUnit, and Frequency when stated.",
                (
                    "Map once daily to Frequency=1, bd/twice daily to 2, "
                    "tds/three times daily to 3, PRN/rescue to As_Required."
                ),
            ],
            "Investigations": [
                "Extract EEG, MRI, CT, telemetry, and similar investigation statements.",
                "Mention text should be the test phrase, usually EEG, MRI, CT, telemetry, or scan.",
                "Set performed/result/type attributes when explicitly stated.",
                "Normal and abnormal results must be attached to the correct modality.",
                (
                    "Extract completed historical investigations when a result is "
                    "stated, for example a previous CT showing infarct is CT "
                    "performed with abnormal result."
                ),
                (
                    "Always scan previous/current investigation lines for completed "
                    "MRI, EEG, or CT results such as MRI 2011 Normal or MRI scan "
                    "showing a lesion."
                ),
                (
                    "Words such as showed, showing, revealed, demonstrated, "
                    "consistent with, slowing, gliosis, infarct, lesion, or "
                    "epileptiform indicate an abnormal result for the named test."
                ),
                (
                    "Phrases such as no epileptiform activity, normal EEG, or normal "
                    "MRI indicate a normal result for the named test."
                ),
                (
                    "Do not extract planned, requested, to-be-arranged, or future "
                    "tests unless the letter also gives a completed result for "
                    "that modality."
                ),
            ],
        },
        "worked_examples": _worked_examples(),
        "global_rules": [
            "Return only the four target indicators; omit all other ExECT families.",
            "Evidence must be an exact source substring for every mention.",
            (
                "Evidence must come from letter_text only. Never copy or adapt "
                "text from worked_examples."
            ),
            "For non-Diagnosis mentions, text should also be an exact source substring.",
            "Do not invent CUI or CUIPhrase values.",
            "Do not include empty-attribute SeizureFrequency mentions.",
            (
                "Be exhaustive for the target indicators. Clinic letters often contain "
                "more than one Diagnosis and more than one SeizureFrequency fact."
            ),
            (
                "Scan in this order before answering: diagnosis header/impression, "
                "current medication lines, seizure frequency/history paragraphs, "
                "investigation result paragraphs."
            ),
            (
                "Do not collapse target facts. If one sentence contains a diagnosis "
                "and a seizure-frequency state, emit both target mentions."
            ),
            (
                "Named seizure types with current/history frequency usually need both "
                "a Diagnosis mention and a SeizureFrequency mention."
            ),
            (
                "Emit every distinct SeizureFrequency state for the same anchor when "
                "the letter states multiple dates, windows, zero-since facts, or "
                "frequency-change facts."
            ),
            (
                "Before final JSON, explicitly check whether each named seizure "
                "type appears in both Diagnosis and SeizureFrequency when the "
                "letter gives both the clinical type and a frequency/state."
            ),
            "If no target findings are present, return {\"mentions\": []}.",
            "Return exactly one JSON object. No markdown fences.",
            "Do not write analysis, corrections, caveats, or revised JSON after the object.",
            "Use rationale=\"\" or a short phrase only; do not explain uncertainty there.",
        ],
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def _target_attribute_vocabulary() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for entity in TARGET_INDICATORS:
        spec = ENTITY_REGISTRY[entity]
        attrs: dict[str, Any] = {}
        for attr in sorted(spec.legal_attributes):
            if attr in {"CUI", "CUIPhrase"}:
                attrs[attr] = "Do not emit; deterministic projection handles this."
            elif attr in spec.closed_vocab:
                attrs[attr] = sorted(spec.closed_vocab[attr])
            else:
                attrs[attr] = "string copied or normalized from the letter"
        out[entity] = attrs
    return out


def _worked_examples() -> list[dict[str, Any]]:
    return [
        {
            "letter_fragment": (
                "Diagnosis: probable focal epilepsy. She has focal seizures twice "
                "a month. Current medication is lamotrigine 100 mg bd. MRI was normal."
            ),
            "mentions": [
                {
                    "entity": "Diagnosis",
                    "text": "focal epilepsy",
                    "attributes": {
                        "DiagCategory": "Epilepsy",
                        "Certainty": "4",
                        "Negation": "Affirmed",
                    },
                    "evidence": "probable focal epilepsy",
                },
                {
                    "entity": "SeizureFrequency",
                    "text": "focal seizures",
                    "attributes": {
                        "NumberOfSeizures": "2",
                        "NumberOfTimePeriods": "1",
                        "TimePeriod": "Month",
                    },
                    "evidence": "focal seizures twice a month",
                },
                {
                    "entity": "Prescription",
                    "text": "lamotrigine 100 mg bd",
                    "attributes": {
                        "DrugName": "lamotrigine",
                        "DrugDose": "100",
                        "DoseUnit": "mg",
                        "Frequency": "2",
                    },
                    "evidence": "lamotrigine 100 mg bd",
                },
                {
                    "entity": "Investigations",
                    "text": "MRI",
                    "attributes": {"MRI_Performed": "Yes", "MRI_Results": "Normal"},
                    "evidence": "MRI was normal",
                },
            ],
        },
        {
            "letter_fragment": (
                "He previously tried carbamazepine. If attacks recur we may start "
                "levetiracetam. No EEG has been arranged."
            ),
            "mentions": [
                {
                    "entity": "Investigations",
                    "text": "EEG",
                    "attributes": {"EEG_Performed": "No"},
                    "evidence": "No EEG has been arranged",
                }
            ],
            "note": "Previous and conditional future medications are not current prescriptions.",
        },
        {
            "letter_fragment": (
                "Diagnosis: temporal lobe epilepsy with focal seizures with altered "
                "awareness and focal to bilateral convulsive seizures. She has focal "
                "seizures with altered awareness once every 2 weeks and has had no "
                "focal to bilateral convulsive seizures since December 2017."
            ),
            "mentions": [
                {
                    "entity": "Diagnosis",
                    "text": "temporal lobe epilepsy",
                    "attributes": {
                        "DiagCategory": "Epilepsy",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                    "evidence": "temporal lobe epilepsy",
                },
                {
                    "entity": "Diagnosis",
                    "text": "focal seizures with altered awareness",
                    "attributes": {
                        "DiagCategory": "MultipleSeizures",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                    "evidence": "focal seizures with altered awareness",
                },
                {
                    "entity": "Diagnosis",
                    "text": "focal to bilateral convulsive seizures",
                    "attributes": {
                        "DiagCategory": "MultipleSeizures",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                    "evidence": "focal to bilateral convulsive seizures",
                },
                {
                    "entity": "SeizureFrequency",
                    "text": "focal seizures with altered awareness",
                    "attributes": {
                        "NumberOfSeizures": "1",
                        "NumberOfTimePeriods": "2",
                        "TimePeriod": "Week",
                    },
                    "evidence": "focal seizures with altered awareness once every 2 weeks",
                },
                {
                    "entity": "SeizureFrequency",
                    "text": "focal to bilateral convulsive seizures",
                    "attributes": {
                        "NumberOfSeizures": "0",
                        "TimeSince_or_TimeOfEvent": "Since",
                        "MonthDate": "12",
                        "YearDate": "2017",
                    },
                    "evidence": "no focal to bilateral convulsive seizures since December 2017",
                },
            ],
            "note": (
                "Named seizure diagnoses and their frequency states are both target "
                "facts; zero-since statements are not active rates."
            ),
        },
        {
            "letter_fragment": (
                "There was a previous CT scan from 2017 showing a left hemisphere "
                "infarct. I will request an MRI of the brain and EEG."
            ),
            "mentions": [
                {
                    "entity": "Investigations",
                    "text": "CT scan",
                    "attributes": {
                        "CT_Performed": "Yes",
                        "CT_Results": "Abnormal",
                    },
                    "evidence": (
                        "previous CT scan from 2017 showing a left hemisphere infarct"
                    ),
                }
            ],
            "note": (
                "Completed historical CT with a result counts; requested future "
                "MRI/EEG does not."
            ),
        },
        {
            "letter_fragment": (
                "Diagnosis: epilepsy - unclassified, possibly generalised. In 2014 "
                "she had two generalised tonic clonic seizures and one absence-like "
                "seizure."
            ),
            "mentions": [
                {
                    "entity": "Diagnosis",
                    "text": "generalised epilepsy",
                    "attributes": {
                        "DiagCategory": "Epilepsy",
                        "Certainty": "3",
                        "Negation": "Affirmed",
                    },
                    "evidence": "epilepsy - unclassified, possibly generalised",
                },
                {
                    "entity": "Diagnosis",
                    "text": "generalised tonic clonic seizures",
                    "attributes": {
                        "DiagCategory": "MultipleSeizures",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                    "evidence": "generalised tonic clonic seizures",
                },
                {
                    "entity": "Diagnosis",
                    "text": "absence-like seizure",
                    "attributes": {
                        "DiagCategory": "SingleSeizure",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                    "evidence": "absence-like seizure",
                },
                {
                    "entity": "SeizureFrequency",
                    "text": "generalised tonic clonic seizures",
                    "attributes": {
                        "NumberOfSeizures": "2",
                        "TimeSince_or_TimeOfEvent": "During",
                        "YearDate": "2014",
                    },
                    "evidence": "In 2014 she had two generalised tonic clonic seizures",
                },
                {
                    "entity": "SeizureFrequency",
                    "text": "absence-like seizure",
                    "attributes": {
                        "NumberOfSeizures": "1",
                        "TimeSince_or_TimeOfEvent": "During",
                        "YearDate": "2014",
                    },
                    "evidence": (
                        "2014 she had two generalised tonic clonic seizures and "
                        "one absence-like seizure"
                    ),
                },
            ],
            "note": (
                "Diagnosis category and seizure types are separate facts; dated "
                "counts are SF facts."
            ),
        },
        {
            "letter_fragment": (
                "Diagnosis: intractable epilepsy with complex partial seizures. "
                "No seizure frequency was documented today."
            ),
            "mentions": [
                {
                    "entity": "Diagnosis",
                    "text": "intractable epilepsy",
                    "attributes": {
                        "DiagCategory": "Epilepsy",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                    "evidence": "intractable epilepsy",
                },
                {
                    "entity": "Diagnosis",
                    "text": "complex partial seizures",
                    "attributes": {
                        "DiagCategory": "MultipleSeizures",
                        "Certainty": "5",
                        "Negation": "Affirmed",
                    },
                    "evidence": "complex partial seizures",
                },
            ],
            "note": "Do not emit SeizureFrequency when the note says frequency is not documented.",
        },
    ]
