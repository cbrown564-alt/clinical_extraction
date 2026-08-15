"""Clinical rules corpus for the full structured-event prompt profile."""

from __future__ import annotations


def _clinical_rules() -> list[str | tuple[str, ...]]:
    return [
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
            "Never emit a SeizureFrequency mention with empty attributes or only "
            "Negation. A valid SeizureFrequency mention "
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
            "Every rendered mention object must include both entity and text."
        ),
        'If no requested findings are present, return {"clinical_events": []}.',
        "Return exactly one JSON object. No markdown code fences.",
    ]
