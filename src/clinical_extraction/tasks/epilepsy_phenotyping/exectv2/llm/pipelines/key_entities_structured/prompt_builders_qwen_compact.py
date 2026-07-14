"""Qwen-compact prompt builder for the structured-event extractor."""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import ExectLetter

from .constants import (
    prompt_version_for,
)
from .prompt_content import (
    _attribute_vocabulary,
    _event_lane_guide,
    _qwen_compact_examples,
    candidate_evidence_ledger_for_letter,
    high_priority_evidence_ledger_for_letter,
)


def _build_qwen_compact_prompt_input(letter: ExectLetter) -> str:
    """Build a shorter Qwen-oriented event-frame prompt.

    The full v0.9 prompt is intentionally comprehensive, but local Qwen has
    shown diagnosis-enumeration and SF-state drift on dev25. This profile keeps
    the same output contract while reducing prompt bulk and emphasizing one
    event frame per clinically supported fact.
    """

    payload = {
        "prompt_version": prompt_version_for("qwen_compact"),
        "prompt_profile": "qwen_compact",
        "task": (
            "Read the letter once and emit source-near clinical event frames for "
            "Prescription, Diagnosis, SeizureFrequency, and Investigations. The "
            "candidate ledger is attention scaffolding only; final keep/reject/"
            "split decisions are yours."
        ),
        "output_schema": {
            "clinical_events": [
                {
                    "family": "medication | diagnosis | seizure_frequency | investigation",
                    "anchor_text": "short exact source substring",
                    "evidence": "exact source clause/sentence supporting every mention",
                    "event_state": "strings only; lane/state/count/dose/result details",
                    "mentions": [
                        {
                            "entity": (
                                "Prescription | Diagnosis | SeizureFrequency | Investigations"
                            ),
                            "text": "short source-near scoring text",
                            "attributes": "legal attributes only; omit CUI/CUIPhrase",
                        }
                    ],
                    "confidence": "low | medium | high",
                    "rationale": "empty string or <= 8 words; no analysis",
                }
            ]
        },
        "candidate_evidence_ledger": candidate_evidence_ledger_for_letter(letter, max_items=64),
        "high_priority_evidence_ledger": high_priority_evidence_ledger_for_letter(letter),
        "event_lane_guide": _event_lane_guide(),
        "attribute_vocabulary": _attribute_vocabulary(),
        "rules": [
            (
                "Return exactly one JSON object with clinical_events; no markdown, "
                "no analysis transcript, no first-person reasoning, no quoted "
                "prompt rules."
            ),
            (
                "Set rationale to an empty string unless a short phrase is needed. "
                "Never write deliberation such as 'I will', 'let us', 'however', "
                "or alternatives inside JSON strings."
            ),
            (
                "Each event must be source-near: evidence must be copied exactly "
                "from the letter and must support all rendered mentions."
            ),
            (
                "Use high_priority_evidence_ledger rows as verified attention "
                "cues for target facts previous Qwen runs often missed. They are "
                "not predictions: check the evidence in the letter, choose the "
                "right family/state, and emit the fact only if the source supports it."
            ),
            (
                "Medication: render only current ordinary regimens and as-required "
                "rescue regimens. Reject previous/stopped drugs, allergy trials, "
                "future starts, target doses, if-further-seizures plans, and "
                "requested dose increases."
            ),
            (
                "Medication split rule: if one current medication line lists "
                "unequal daily doses such as '750mg mane, 500 mg nocte' or "
                "'100 mg in the morning, 175 mg in the afternoon', render one "
                "Prescription mention per dose with Frequency='1'. A single "
                "'800mg bd' regimen has Frequency='2'."
            ),
            (
                "Diagnosis: enumerate every explicit patient diagnosis concept in "
                "Diagnosis/problem/impression statements. If generic epilepsy and "
                "a specific type/syndrome are both stated, render both separately."
            ),
            (
                "Do not add generic epilepsy as a companion to a specific epilepsy "
                "subtype unless the letter separately asserts the patient has "
                "epilepsy. Keep modifiers in diagnoses such as 'intractable "
                "epilepsy'."
            ),
            (
                "Diagnosis certainty: Certainty='5' for stated/known/diagnosed; "
                "'4' for probable/likely; '3' for possible/query. Always include "
                "Negation='Affirmed' unless the diagnosis itself is negated."
            ),
            (
                "Diagnosis boundaries: do not render vague symptoms, bare 'events', "
                "blackouts, dissociative/non-epileptic attacks, family history, "
                "education/SUDEP advice, or negated resemblance statements. Do not "
                "render myoclonic jerks unless the phrase is an explicit named "
                "epileptic seizure diagnosis."
            ),
            (
                "Diagnosis text: do not render bare modifiers such as 'focal' or "
                "'possibly generalised'. If a Diagnosis heading says epilepsy is "
                "probable focal or possibly generalised, render 'focal epilepsy' or "
                "'generalised epilepsy' with the hedging in Certainty."
            ),
            (
                "Do not render non-epilepsy causes or contextual labels as Diagnosis, "
                "including brain tumours, nonepileptic events, and risk-counselling "
                "phrases such as convulsive seizures causing injury."
            ),
            (
                "Diagnosis categories: epilepsy syndromes/types use DiagCategory="
                "'Epilepsy'; one singular seizure event uses 'SingleSeizure'; "
                "plural named seizure types such as focal seizures or generalised "
                "tonic clonic seizures use 'MultipleSeizures'. Never write "
                "'tonic chronic'; use the source concept tonic clonic."
            ),
            (
                "If Diagnosis text ends with plural 'seizures' or names a plural "
                "seizure type, DiagCategory must be 'MultipleSeizures', not "
                "'Epilepsy'."
            ),
            (
                "For named seizure types, words such as 'without change in "
                "awareness' describe the seizure semiology, not diagnostic "
                "uncertainty. Use Certainty='5' unless the source says probable, "
                "possible, query, or similar hedging."
            ),
            (
                "SeizureFrequency: render only statements of current/historical "
                "frequency state: active count/rate, seizure-free/last-event anchor, "
                "unknown frequency, or qualitative change. Diagnosis-only mentions "
                "are not SF."
            ),
            (
                "SeizureFrequency anchor: use the specific seizure phrase named in "
                "the evidence; use generic 'seizures' only when the count/state is "
                "generic. Do not use bare 'events', 'these seizures', or a count "
                "phrase such as '2 to 3' as text."
            ),
            (
                "For SeizureFrequency active-rate mentions, text must be the "
                "seizure type or generic 'seizures', while attributes carry the "
                "count/date/cadence. Example: evidence '2 to 3 focal seizures in "
                "March' uses text='focal seizures', LowerNumberOfSeizures='2', "
                "UpperNumberOfSeizures='3', MonthDate='3'."
            ),
            (
                "Use numeric date attributes: January=1, February=2, March=3, "
                "April=4, May=5, June=6, July=7, August=8, September=9, "
                "October=10, November=11, December=12. Do not write MonthDate as "
                "a month name."
            ),
            (
                "Approximate count mapping for this benchmark surface: "
                "'several' means NumberOfSeizures='3'; 'a few' means "
                "NumberOfSeizures='2'."
            ),
            (
                "SeizureFrequency attributes: never emit an SF mention with empty "
                "attributes. Use NumberOfSeizures/TimePeriod for rates, "
                "NumberOfSeizures='0' plus Since/LastClinic/date for seizure-free "
                "or last-event statements, and Frequency='unknown' only when the "
                "letter explicitly says frequency is unknown."
            ),
            (
                "SeizureFrequency headings are high-value evidence. Keep heading "
                "counts such as 'several seizures since last clinic' unless a later "
                "statement is an explicit newer quantified correction."
            ),
            (
                "SeizureFrequency precision: reject risk/counselling statements, "
                "diagnostically vague episodes, loss-of-consciousness spells, and "
                "non-epileptic events even when they include a cadence."
            ),
            (
                "If a seizure-frequency heading names a plural seizure type followed "
                "only by a year or date, render one dated occurrence for that type: "
                "NumberOfSeizures='1', YearDate='2014', "
                "TimeSince_or_TimeOfEvent='During'."
            ),
            (
                "Investigations: render completed historical MRI/CT/EEG/telemetry "
                "or explicit no-test statements. Reject planned/requested/repeat/"
                "awaited tests unless a separate completed result is stated. Do not "
                "default plain EEG to EEG_Type='Standard'."
            ),
            (
                "Investigations attributes: do not default unrelated modalities to "
                "No. An EEG result should not include MRI_Performed='No' or "
                "CT_Performed='No'; a planned MR brain/EEG should emit no mention."
            ),
            (
                "Every rendered mention object must include both entity and text. "
                "Never emit projection-only CUI/CUIPhrase companion objects."
            ),
            (
                "Exhaustiveness pass before final JSON: reread Diagnosis, "
                "Impression, Seizure type and frequency, Current medication, "
                "and Investigations sections. Add every explicitly stated target "
                "fact as a model mention; do not rely on any later dictionary or "
                "residual repair to add missed target facts."
            ),
            (
                "Diagnosis residual concepts to emit when stated: secondary "
                "generalised seizures, generalised epilepsy, focal epilepsy, "
                "focal seizures with altered awareness, focal motor seizures, "
                "temporal/frontal/parietal/occipital lobe epilepsy or seizures, "
                "status epilepticus, drug refractory epilepsy, and nocturnal "
                "seizures. These are target diagnoses when they describe the "
                "patient, not projection companions."
            ),
            (
                "Named seizure types are usually both Diagnosis and "
                "SeizureFrequency when the same source clause names the type and "
                "gives a count/rate/date. Emit a Diagnosis mention for the seizure "
                "type with DiagCategory='MultipleSeizures', then emit the separate "
                "SeizureFrequency mention with the count/rate attributes."
            ),
            (
                "Never render anatomical qualifiers as bare modifiers: 'probable "
                "temporal' means 'temporal lobe epilepsy' or 'temporal lobe "
                "seizures' with Certainty='4'; 'focal onset' means 'focal "
                "seizures' when the seizure type is being diagnosed."
            ),
            (
                "SeizureFrequency residual facts to emit when stated: dated "
                "seizure-type headings such as '2 generalised tonic clonic "
                "seizures 2014', seizure-free clauses such as 'remains seizure "
                "free', interval rates such as 'every 3 to 4 weeks', clusters "
                "with counts, and qualitative changes such as returned/increased "
                "seizures."
            ),
            (
                "Investigation residual facts to emit when completed: MRI/CT/EEG "
                "clauses with normal or abnormal results, including terse forms "
                "such as 'MRI-normal', 'CT scan ... infarct', 'EEG ... slowing', "
                "or telemetry/video EEG results. Planned or awaited tests still "
                "emit no mention."
            ),
            (
                "Prescription residual facts to emit when current: brand names "
                "and short regimen lines such as Epilim/Episenta/Sodium Valproate, "
                "Keppra/Levetiracetam, Tegretol/Carbamazepine, Clobazam PRN or "
                "night doses, and bracketed regimen fragments like '200mg BD'."
            ),
            "Do not invent CUI values; omit CUI and CUIPhrase.",
            'If no requested findings are present, return {"clinical_events": []}.',
        ],
        "worked_examples": _qwen_compact_examples(),
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
