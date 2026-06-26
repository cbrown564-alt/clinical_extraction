"""Full and qwen_compact prompt builders for the structured-event extractor.

Pure relocation from ``llm_only_key_entities_structured``. No logic changes.
"""

from __future__ import annotations

import json

from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.data import (
    ExectLetter,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.constants import (
    PromptProfile,
    prompt_version_for,
)
from clinical_extraction.tasks.epilepsy_phenotyping.exectv2.llm.pipelines.key_entities_structured.prompt_content import (
    _attribute_vocabulary,
    _decision_procedure,
    _event_lane_guide,
    _family_guidance,
    _qwen_compact_examples,
    _worked_examples,
    candidate_evidence_ledger_for_letter,
    high_priority_evidence_ledger_for_letter,
)


def build_prompt_input(letter: ExectLetter, *, prompt_profile: PromptProfile = "full") -> str:
    """Build the single-prompt structured-event payload."""

    if prompt_profile == "qwen_compact":
        return _build_qwen_compact_prompt_input(letter)

    payload = {
        "prompt_version": prompt_version_for(prompt_profile),
        "task": (
            "Read the clinical letter once. Use the candidate_evidence_ledger as "
            "attention scaffolding, then build a compact list of source-near "
            "clinical events for medication, diagnosis, seizure frequency, and "
            "investigations. Each event may render one or more entity mentions when "
            "the same clinical fact validly belongs to more than one requested family."
        ),
        "architecture": {
            "name": "single hybrid key-family event ledger",
            "inspiration": (
                "Gan structured-events discipline: source-near candidate evidence, "
                "typed state lanes, exact evidence, then final mention renderings."
            ),
            "component_ownership": (
                "The deterministic ledger proposes possible evidence spans only. "
                "The model owns keep/reject/split/merge decisions and final rendered "
                "mentions. Deterministic code later validates evidence, strips illegal "
                "attributes, attaches finite ontology codes, and evaluates outputs."
            ),
        },
        "output_schema": {
            "clinical_events": [
                {
                    "family": "medication | diagnosis | seizure_frequency | investigation",
                    "anchor_text": (
                        "Short exact substring naming the clinical event. Use the "
                        "family guidance below."
                    ),
                    "evidence": (
                        "Exact clause or sentence copied from the letter that supports "
                        "the event and all rendered mentions."
                    ),
                    "event_state": (
                        "Source-near state for clinical reasoning, such as medication "
                        "dose/frequency, diagnostic assertion, seizure rate, or test "
                        "result. Values must be strings."
                    ),
                    "mentions": [
                        {
                            "entity": (
                                "One of Prescription, Diagnosis, SeizureFrequency, "
                                "Investigations."
                            ),
                            "text": "Short exact substring used for scoring this entity.",
                            "attributes": "Only attributes legal for that entity.",
                        }
                    ],
                    "confidence": "low | medium | high",
                    "rationale": "One brief sentence explaining the event.",
                }
            ]
        },
        "decision_procedure": _decision_procedure(),
        "candidate_evidence_ledger": candidate_evidence_ledger_for_letter(letter),
        "event_lane_guide": _event_lane_guide(),
        "family_guidance": _family_guidance(),
        "attribute_vocabulary": _attribute_vocabulary(),
        "worked_examples": _worked_examples(),
        "clinical_rules": [
            (
                "First classify each candidate_evidence_ledger item into an event "
                "lane: current_regimen, rescue_regimen, future_or_historical_medication, "
                "diagnosis_assertion, diagnosis_context_only, active_rate, "
                "seizure_free_anchor, qualitative_change, performed_investigation, "
                "planned_investigation, or reject."
            ),
            (
                "Candidate ledger rows are not predictions. Keep, reject, split, "
                "merge, or add events based only on the full letter and exact evidence."
            ),
            (
                "Return only final clinical_events. Do not return candidate IDs unless "
                "you copy them into event_state as trace strings."
            ),
            (
                "Write each rationale as one short final-justification sentence. "
                "Do not show step-by-step reasoning, self-questioning, alternative "
                "options, or quoted prompt rules inside rationale."
            ),
            "Use one event per medication, diagnostic concept, seizure-rate statement, or test.",
            "Both anchor_text and evidence must be exact substrings of the letter.",
            "Every rendered mention text must be an exact substring of the letter.",
            (
                "Named seizure types can render both Diagnosis and SeizureFrequency "
                "when the letter states both the type and a rate or seizure-free state."
            ),
            (
                "Do not force a single entity if the same fact belongs to more than "
                "one requested family; render each valid entity separately."
            ),
            (
                "For diagnosis, split compound seizure clauses into atomic diagnostic "
                "concepts when the letter names more than one seizure type."
            ),
            (
                "Every Diagnosis mention must include Certainty and Negation. Use "
                "Certainty='5' and Negation='Affirmed' for directly stated diagnoses "
                "or seizure types unless the letter explicitly says otherwise."
            ),
            (
                "For Diagnosis certainty, preserve diagnostic hedging: use "
                "Certainty='4' for probable or likely diagnoses, Certainty='3' for "
                "possible, suspected, query, or differential diagnoses, and "
                "Certainty='5' only for established or unqualified statements."
            ),
            (
                "For Diagnosis concepts, prefer the most specific epilepsy syndrome "
                "or seizure type stated in the letter, such as focal epilepsy, "
                "temporal lobe epilepsy, primary generalised epilepsy, or JME. "
                "When the letter explicitly states both a generic epilepsy diagnosis "
                "and a specific syndrome or seizure type, render both as separate "
                "Diagnosis mentions; do not collapse one into the other."
            ),
            (
                "When a Diagnosis heading or impression states an epilepsy subtype "
                "using the word epilepsy, such as 'Temporal lobe epilepsy' or "
                "'Symptomatic structural focal epilepsy', render the subtype and also "
                "render generic 'epilepsy' only when the source itself explicitly uses "
                "the word epilepsy as a diagnosis. Do not add generic epilepsy from "
                "family history, clinic names, medication labels, or weak context."
            ),
            (
                "Do not add a generic epilepsy companion to a specific epilepsy "
                "subtype unless the source separately asserts generic epilepsy as its "
                "own diagnosis or context says the patient has/has known epilepsy. "
                "For example, 'Diagnosis: symptomatic structural focal epilepsy' "
                "renders only 'symptomatic structural focal epilepsy'."
            ),
            (
                "When narrative says 'intractable epilepsy', keep the modifier in "
                "the Diagnosis text; do not shorten it to generic 'epilepsy'."
            ),
            (
                "In phrases like 'general and complex partial seizures', do not emit "
                "'general seizures'; render 'complex partial seizures' unless another "
                "explicit named generalised seizure type is present."
            ),
            (
                "Onset-history phrases such as 'epilepsy started at age 4' are not "
                "a separate Diagnosis mention when the same letter already provides "
                "the current diagnosis or named seizure types."
            ),
            (
                "For Diagnosis mention text, render only the core clinical concept "
                "span. Do not include section labels, dashes, hedging words "
                "('probable', 'possible', 'query'), qualifiers like 'single' or "
                "'alone', or surrounding explanation in the mention text; put "
                "uncertainty in Certainty instead."
            ),
            (
                "Do not render bare modifiers such as 'focal', 'generalised', "
                "'probable focal', or 'possibly generalised' as Diagnosis mentions. "
                "When such wording appears in a Diagnosis heading modifying "
                "epilepsy, render the implied concept, for example 'focal epilepsy' "
                "or 'generalised epilepsy'."
            ),
            (
                "When a Diagnosis heading combines an established epilepsy type "
                "with a probable anatomical qualifier, render two concepts with "
                "separate certainty: for example 'focal epilepsy-Probable temporal' "
                "means text 'focal epilepsy' with Certainty='5' and text "
                "'temporal lobe epilepsy' with Certainty='4'."
            ),
            (
                "When a Diagnosis heading states established epilepsy before a dash "
                "and an uncertain subtype after the dash, keep the generic epilepsy "
                "diagnosis at Certainty='5' and apply the lower certainty only to "
                "the subtype; for example 'Epilepsy - unclassified, possibly "
                "generalised' renders 'epilepsy' Certainty='5' and 'generalised "
                "epilepsy' Certainty='3'."
            ),
            (
                "For abbreviated syndromes, use the exact abbreviation as mention "
                "text when that is the source span, for example text 'JME' or 'jme' "
                "with Certainty from probable/possible context."
            ),
            (
                "Do not render vague symptoms, blackout/loss-of-consciousness "
                "descriptions, anxiety, or non-epileptic events as Diagnosis unless "
                "the same phrase is explicitly asserted as an epileptic seizure, "
                "epilepsy diagnosis, or named seizure type."
            ),
            (
                "Do not render negated resemblance statements as Diagnosis or "
                "SeizureFrequency. Phrases such as 'no events which resemble "
                "absences, myoclonus or focal seizures' are explicit absence of "
                "those events, not affirmed diagnoses or seizure-frequency states."
            ),
            (
                "Do not render isolated symptoms or aura features as Diagnosis, "
                "including myoclonic jerks, jerks, flashing lights, odd sensations, "
                "altered awareness by itself, or dizziness, unless the phrase is part "
                "of a named seizure type such as 'focal seizures with altered awareness'."
            ),
            (
                "For tonic-clonic seizure wording, preserve 'tonic clonic' or "
                "'tonic-clonic'. Never write 'tonic chronic'."
            ),
            (
                "For Diagnosis headings like 'generalised tonic clonic seizures with "
                "myoclonic jerks, possible JME', render the plural tonic-clonic "
                "seizure type as Diagnosis and render JME with lower certainty; do "
                "not render isolated 'myoclonic jerks' as a Diagnosis mention."
            ),
            (
                "For composite Diagnosis headings such as 'complex partial seizures "
                "with secondary generalised tonic clonic seizures', split the heading "
                "into separate Diagnosis mentions for the named seizure types instead "
                "of returning the whole clause as one text span."
            ),
            (
                "A problem-list or Diagnosis header is not enough by itself: still "
                "exclude anxiety, dissociative/non-epileptic events, blackouts, "
                "collapse, and loss of consciousness from the requested Diagnosis "
                "family unless the phrase is explicitly asserted as epileptic."
            ),
            (
                "For diagnosis, use DiagCategory='Epilepsy' for epilepsy syndromes or "
                "diagnoses. Use DiagCategory='SingleSeizure' for one singular named "
                "seizure event such as 'focal seizure'. Use "
                "DiagCategory='MultipleSeizures' for plural named seizure types such "
                "as 'focal seizures' or 'generalised tonic clonic seizures', and for "
                "phrases that represent multiple seizure types or recurrent seizures "
                "as a category."
            ),
            (
                "Keep plural seizure-type wording plural in Diagnosis text. Source "
                "phrases such as 'absence like seizures' or 'absence-like seizures' "
                "render as plural Diagnosis text with DiagCategory='MultipleSeizures', "
                "not singular 'absence like seizure'."
            ),
            (
                "For seizure frequency, mention text is only the seizure-type anchor; "
                "do not include counts, dates, or the words 'seizure frequency' in text. "
                "event_state and attributes carry counts, periods, dates, and changes."
            ),
            (
                "Never emit a SeizureFrequency mention with empty attributes, only "
                "Negation, or only CUI/CUIPhrase. A valid SeizureFrequency mention "
                "must include a frequency-state attribute such as NumberOfSeizures, "
                "LowerNumberOfSeizures, FrequencyChange, TimeSince_or_TimeOfEvent, "
                "PointInTime, DayDate, MonthDate, YearDate, AgeLower, or AgeUpper."
            ),
            (
                "For SeizureFrequency anchors, use the generic seizure phrase when "
                "the count refers to seizures generally; use a named seizure type only "
                "when the count explicitly belongs to that type."
            ),
            (
                "SF recall: Seizure type and frequency headings are high-value "
                "evidence. If a heading says 'seizures every 3 to 4 weeks', "
                "'several seizures since last clinic', '2 generalised tonic clonic "
                "seizures 2014', or a named seizure type plus a date, render a "
                "SeizureFrequency mention for that anchor even when the count is "
                "approximate or dated. Do not replace a heading frequency with a "
                "later vague narrative estimate unless the later statement is an "
                "explicit newer quantified correction."
            ),
            (
                "When a seizure-frequency heading names a plural seizure type "
                "followed only by a year or date, treat it as one dated occurrence "
                "of that named type unless another count is attached to that same "
                "type. For example, 'absence like seizures 2014' has "
                "NumberOfSeizures='1', YearDate='2014', and "
                "TimeSince_or_TimeOfEvent='During'."
            ),
            (
                "SF state choice: statements that seizures have returned or have "
                "been experienced since a triggering event are active seizure states, "
                "not unknown states. Use active-rate attributes when a count, cadence, "
                "date, or since-frame is present; use unknown only when the letter "
                "names current seizures but gives no count, cadence, change, or "
                "seizure-free time frame."
            ),
            (
                "For named seizure types, preserve clinically meaningful modifiers "
                "that are part of the exact phrase, including 'with altered awareness', "
                "'focal to bilateral', lobe qualifiers, convulsive, tonic clonic, "
                "absence-like, and myoclonic."
            ),
            (
                "When a named seizure-frequency row says 'focal seizures with altered "
                "awareness approximately 1 per fortnight', keep the full named anchor "
                "'focal seizures with altered awareness' rather than shortening it to "
                "'focal seizures'."
            ),
            (
                "Do not render SeizureFrequency for generic events, blackouts, "
                "collapse, anxiety attacks, or dissociative/non-epileptic events "
                "unless the same phrase is explicitly asserted as epileptic seizures."
            ),
            (
                "SF precision: reject generic spell anchors such as 'events', "
                "'episodes', 'episodes of loss of consciousness', 'minor seizures', "
                "and 'jerks' when the letter describes uncertain attacks, dizziness, "
                "loss of consciousness, shaking, or light-triggered jerks without "
                "explicitly asserting that the anchor itself is an epileptic seizure "
                "type."
            ),
            (
                "Do not render childhood febrile seizures, family-history seizures, "
                "risk discussion, or old previous-event context as current "
                "SeizureFrequency unless the sentence explicitly gives the patient's "
                "current frequency state."
            ),
            (
                "SF precision: do not render risk or counselling statements such as "
                "'risk of further seizures', 'at risk of further seizures', or "
                "'even though he has only had one seizure' as SeizureFrequency."
            ),
            (
                "SF precision: do not render non-epileptic or diagnostically vague "
                "episode descriptions as SeizureFrequency, even when they include a "
                "cadence, such as 'episodes around twice a week of an unusual thought'."
            ),
            (
                "SF precision: do not render old or contextual minor-seizure episode "
                "phrases such as 'the episodes occur 4 to 5 times a year' unless the "
                "sentence explicitly asserts a current scorable epileptic seizure type."
            ),
            (
                "Onset-history statements such as 'seizures since the age of 13' are "
                "not SeizureFrequency by themselves. Use them only as a seizure-free "
                "since-age anchor when the same sentence says the last seizures were "
                "in a past age range such as the teenage years."
            ),
            (
                "For seizure-frequency ranges, never write values like '2 to 3', "
                "'2-4', or '3 or 4' in NumberOfSeizures. Use LowerNumberOfSeizures "
                "and UpperNumberOfSeizures instead."
            ),
            (
                "For approximate count words without exact numbers, use conservative "
                "integer counts only when the letter clearly describes seizures: "
                "'couple'='2', 'few'='2', and 'several'='3'."
            ),
            (
                "For interval rates such as 'one every 3 to 4 weeks', set "
                "NumberOfSeizures='1', LowerNumberOfTimePeriods='3', "
                "UpperNumberOfTimePeriods='4', and TimePeriod='Week'. Do not convert "
                "the interval into 3 to 4 seizures."
            ),
            (
                "For cluster statements, keep the cluster as the clinical event when "
                "the note counts clusters, for example text 'cluster of seizures' with "
                "NumberOfSeizures='1' and the stated date or time frame."
            ),
            (
                "For frequency-change statements without an exact count, render a "
                "SeizureFrequency mention with FrequencyChange only, such as "
                "Frequent, Infrequent, Increased, Decreased, or Same."
            ),
            (
                "For dated counts such as '2 to 3 in March', use Lower/Upper count "
                "fields plus MonthDate or YearDate and TimeSince_or_TimeOfEvent='During'; "
                "do not invent TimePeriod='Month' unless the note says per month."
            ),
            (
                "For 'since last clinic', use TimeSince_or_TimeOfEvent='Since' and "
                "PointInTime='LastClinic'; do not put 'since last clinic' in TimePeriod."
            ),
            (
                "For last-event or seizure-free statements, use NumberOfSeizures='0' "
                "with TimeSince_or_TimeOfEvent='Since' and the stated MonthDate, "
                "YearDate, or PointInTime. Do not convert last-event dates into an "
                "annual recurring rate."
            ),
            (
                "Phrases like 'last seizure', 'last event', or 'has had none since' "
                "mean seizure-free since that anchor for the named seizure type; do "
                "not render them as one seizure during that date or as an active "
                "current-rate statement."
            ),
            (
                "Do not infer seizure-free from phrases like 'last seizure coincided "
                "with missing medication' or 'previous seizure was a year ago' unless "
                "the source also gives a clear no-further/since frame for the same "
                "seizure type."
            ),
            (
                "For seizure-free statements, anchor text to the underlying seizure "
                "phrase when it is present in the same sentence, such as 'seizures' or "
                "'focal seizures'; otherwise use the exact seizure-free phrase."
            ),
            (
                "SF precision: do not render safety-advice, conditional, or "
                "instructional statements as SeizureFrequency. Phrases such as 'if "
                "you have a seizure', 'in the event of a seizure', 'advised what to do "
                "if seizures occur', or general SUDEP/driving advice describe guidance, "
                "not a current rate."
            ),
            (
                "SF precision: do not emit a bare seizure-free or 'well controlled' "
                "SeizureFrequency mention unless it is tied to a seizure type, a count, "
                "or a temporal anchor (since/last/date). A standalone 'seizure free' "
                "with no seizure type and no time frame is not a scorable SF state."
            ),
            (
                "Phrases such as 'remains seizure free and is now driving' or "
                "'seizures were well controlled on medication' are not enough for a "
                "SeizureFrequency mention unless they name the seizure type and give "
                "a since/date/drug-change frame."
            ),
            (
                "SF precision: do not use an anaphoric anchor such as 'these seizures', "
                "'such episodes', or 'the events' as the SeizureFrequency text. Use the "
                "specific named seizure type stated earlier in the same context, or the "
                "generic 'seizures' when the count refers to seizures in general."
            ),
            (
                "SF precision: when a sentence names two seizure types joined by 'and' "
                "with a single shared count, render the count against the seizure type "
                "it actually belongs to, not a merged 'X and Y' anchor; only split into "
                "two SF mentions if the letter gives each type its own count or state."
            ),
            (
                "SF precision: emit at most one SeizureFrequency mention per distinct "
                "rate statement. Do not emit both a generic 'seizures' mention and a "
                "named-type mention for the same single count in the same clause."
            ),
            (
                "For medication, mention text is the medication name where possible; "
                "dose and frequency belong in attributes."
            ),
            (
                "Medication decision lane: current ordinary regimens and rescue "
                "as-required regimens render Prescription mentions; previous trials, "
                "stopped drugs, future starts, titration targets, options, and "
                "if-further-seizures plans are usually rejected."
            ),
            (
                "Medication current-list split dosing: if a current regimen gives "
                "unequal time-of-day doses such as 'Epilim 300 mg mane and 600 mg "
                "nocte' or 'Lamictal 100 mg in the morning, 175 mg in the afternoon', "
                "render separate Prescription mentions with Frequency='1'. Do not "
                "mark these current scheduled doses as As_Required."
            ),
            (
                "Medication plan boundary: future starts, requested dose increases, "
                "taper targets, or if-further-seizures instructions are not current "
                "Prescription mentions unless a separate current/taking/on-medication "
                "statement supports them."
            ),
            (
                "Medication frequency completion: when the selected current regimen "
                "says 'twice a day', 'twice daily', or 'bd', include Frequency='2'; "
                "when it says once daily, mane, nocte, morning, or evening, include "
                "Frequency='1'."
            ),
            (
                "For medication list entries that contain a compact regimen, render "
                "text as the exact medication item span including dose and frequency "
                "when those words are part of the same short line, for example "
                "'Topiramate 100 mg BD'."
            ),
            (
                "For investigations, use one event per modality such as EEG, MRI, or "
                "CT; put performed, result, and EEG type in attributes."
            ),
            (
                "ECG is not an ExECTv2 target investigation. Never map ECG to EEG, "
                "MRI, or CT, and do not emit an Investigations mention from ECG-only "
                "evidence."
            ),
            (
                "Investigation decision lane: completed historical tests and tests "
                "with results render Investigations mentions; planned/requested/repeat "
                "tests without a completed result are rejected."
            ),
            (
                "Do not render future planned, requested, repeat, or follow-up "
                "investigations as performed tests. Only render completed tests or "
                "tests with a stated result."
            ),
            (
                "Investigation pending-test cues are decisive: if the test sentence "
                "contains 'will', 'arrange', 'request', 'await'/'awaiting', "
                "'appointment', 'suggest', 'recommend', 'should update', 'chase', 'up "
                "to date', 'not yet performed/received', or 'planned', treat it as a "
                "pending test and do not emit an Investigations mention for it unless a "
                "separate completed result for the same modality is also stated."
            ),
            (
                "Never emit an Investigations mention whose only support is a pending "
                "cue with Performed='No' or an unknown result; a requested or awaited "
                "test is not a completed historical test."
            ),
            (
                "Do not render a bare modality-only investigation when the note gives "
                "no completion/result statement, and do not add a duplicate modality-only "
                "mention when a result-bearing mention for the same modality is already "
                "rendered."
            ),
            (
                "Phrases such as 'EEG did show temporal slowing', 'EEG has shown "
                "spike and wave', or 'MRI does show signal change' are completed "
                "abnormal investigation results."
            ),
            (
                "For investigation text, use the shortest exact modality phrase: "
                "'MRI scan' if those words occur together, otherwise 'MRI'; likewise "
                "'EEG' or 'CT'. Do not include dates or results in text."
            ),
            (
                "Only include EEG_Type when the letter explicitly says sleep-deprived "
                "EEG or video telemetry. Do not default a plain EEG to Standard."
            ),
            (
                "Every rendered mention object must include both entity and text. "
                "Do not emit projection-only companion mentions such as objects with "
                "only CUI/CUIPhrase attributes; omit CUI and CUIPhrase unless they "
                "are explicitly available in the source."
            ),
            "Do not invent CUI values. If a CUI is not explicitly available, omit it.",
            "If no requested findings are present, return {\"clinical_events\": []}.",
            "Return exactly one JSON object. No markdown code fences.",
        ],
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


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
                                "Prescription | Diagnosis | SeizureFrequency | "
                                "Investigations"
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
            "If no requested findings are present, return {\"clinical_events\": []}.",
        ],
        "worked_examples": _qwen_compact_examples(),
        "letter_id": letter.letter_id,
        "letter_text": letter.note_text,
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)
