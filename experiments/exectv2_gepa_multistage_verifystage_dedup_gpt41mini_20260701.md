# GEPA from-scratch (ExECTv2 de-dup facts) — exectv2_gepa_multistage_verifystage_dedup_gpt41mini_20260701

Date: 2026-07-01

DSPy-native GEPA run. The optimizable surface is the signature instruction; the existing de-dup parse/evidence-gate/adapter and the canonical clinical_headline scorers are reused unchanged. Trained on a seeded sub-split of `dev` (optimizer-only); evaluated on the full `dev` split (development surface, NOT test). Attribution-clean LLM-only: the adapter performs representation mapping only, it adds no facts.

## Models

- Task model: `openai/gpt-4.1-mini` (temp 0.0, max_tokens 12000)
- Reflection (teacher) model: `deepseek/deepseek-reasoner`
- GEPA budget: auto=medium max_metric_calls=None (trainset 90, valset 50)

## Length penalty (prompt-bloat control)

- enabled: True
- instruction budget: 4000 tok (beta 0.25)
- demo budget: 800 tok (beta 0.25)
- output budget: 2000 tok (alpha 0.05)
- **final instruction length: 4660 tokens** (seed was 2272 tokens)

## Final evaluation (dev, clinical-recovery surface)

- **Canonical clinical_headline overall F1: 0.760** (P=0.816 R=0.710, Diagnosis=concept_negation)
  - Diagnosis=0.719  SeizureFrequency=0.601  Prescription=0.886  Investigations=0.857
- **Producer evidence-recall (source_near): 0.643** (GEPA per-family baseline 0.694, v08 hybrid 0.883) — Dx=0.506 SF=0.599 Rx=0.859 Inv=0.787
- Strict benchmark per-item F1 (diagnostic, NOT paper-cleared): 0.129
- Semantic (CUI-dropped) per-item F1: 0.141
- Letters: 140 (unscorable: 0); facts emitted 675, scored 675

## Comparators (dev140, from plan 13)

- Hand-tuned single-prompt de-dup plateau: GPT-4.1-mini 0.710, DeepSeek 0.745, Qwen 0.694
- v08 hybrid (multi-component) control: 0.9155

## Evolved instruction

```text
=== generate.diagnosis ===
Read the clinical letter and extract all distinct diagnosis facts that are epilepsy-related. This includes: (1) the type of epilepsy (e.g., 'focal epilepsy', 'symptomatic structural focal epilepsy', 'Juvenile myoclonic epilepsy') and (2) any specific seizure types mentioned (e.g., 'generalised tonic clonic seizures', 'focal motor seizures', 'focal to bilateral convulsive seizures', 'focal seizures with altered awareness', 'generalised seizures', 'myoclonic jerks' if described as seizures). Do not include comorbid conditions (e.g., anxiety, learning difficulties, previous infections, meningioma, Trisomy 21, dementia), past medical history, or non-epileptic attacks (e.g., dissociative seizures). For each concept, provide an exact substring from the letter as evidence. Set "family" always to "diagnosis". Set "negation" to "affirmed" if the concept is present, or "negated" if explicitly excluded (e.g., 'no history of febrile seizures'). Deduplicate concepts. Return exactly one JSON object matching the schema {"clinical_facts": [{"concept": "short diagnosis concept", "evidence": "exact substring copied from the letter", "family": "diagnosis", "negation": "affirmed | negated"}]}. No markdown, just the JSON object.

=== generate.seizure_frequency ===
You read one clinical letter and extract seizure-frequency facts. For each distinct seizure type mentioned (use the exact name from the letter, or 'seizures' if generic), emit exactly one fact that captures the current state. Do not enumerate individual dated events. Ground each fact with an exact verbatim substring from the letter as evidence. Return a single JSON object with a 'clinical_facts' list, no markdown, following this schema:
{"clinical_facts": [{"evidence": "exact substring", "family": "seizure_frequency", "seizure_type": "named type or 'seizures'", "state": "active_rate | seizure_free | changed | unknown"}]}

Important rules:
- Only extract seizure-frequency facts. Do not output facts about diagnoses, prescriptions, investigations, comorbidities, or other clinical details.
- The state must be concrete:
  * "active_rate" when the letter gives an explicit current count or rate (e.g., "2 per year", "3 or 4 episodes", "occasional jerks", "1 per week", "every month"). The evidence must include a specific numerical or periodic frequency.
  * "seizure_free" when the letter states a clear period without seizures (e.g., "seven years without any tonic clonic", "last event was more than five years ago", "not had any for three years"). Do not use for absence of prior seizures (e.g., "he has not had any previous seizures" is not a freedom period after having seizures). If the letter says "has not had any more seizures" after a past event, treat current state as seizure_free.
  * "changed" only for explicit frequency comparison (e.g., "used to happen weekly but now less often", "seizures have increased"). Do not use for subjective statements like "helped", "improved", "under control".
  * "unknown" only if the letter mentions seizures but gives no count, rate, or freedom period. Prefer to omit such facts entirely; they will be dropped in scoring.
- For each seizure type, emit at most one fact. If the letter describes both a past seizure activity (e.g., a cluster) and a current freedom period, emit the current seizure_free state and do not also emit an active_rate for the past events.
- Do not emit facts for which you cannot provide a concrete state with an exact evidence substring. For example, "focal motor seizures where her arm twitches continually for up to 5 hours" does not give a frequency, so omit.
- Use the exact seizure type name from the letter. E.g., "absences" not "absence seizures"; "generalised tonic clonic seizures" not "GTCS". If no specific type is given, use "seizures".
- Evidence must be copied verbatim. Do not paraphrase.
- Output exactly a valid JSON object, no additional text.

=== generate.prescription ===
You read one clinical letter and list its current prescription facts.  

- Emit each distinct *current* drug regimen once as `drug` + `dose` (number only, as a string) + `dose_unit` (mg or g) + `frequency` (1 for once daily, 2 for twice daily, 3 for three times daily, As_Required for prn).  
- Only include a drug if the letter explicitly states both a numeric dose and a dosing frequency (e.g., bd, od, twice daily, nocte). If either is missing, omit that drug entirely.  
- Do **not** include:  
  - Past medications (e.g., “previously tried”)  
  - Planned‑only medications (e.g., “I suggest increasing to …” or a future titration schedule)  
  - Medications listed without dose and frequency (e.g., “simvastatin, Aspirin” without numbers)  
- If a drug has different doses at different times (e.g., “200 mg in the morning and 400 mg at night”), emit one fact per unique dose‑frequency combination.  
- The `evidence` field must be an exact substring copied from the letter that contains the drug name, dose, and frequency (e.g., “Levetiracetam 750mg bd”).  
- Return exactly one JSON object matching the schema:  
  `{"clinical_facts": [{"drug": "drug name", "dose": "number", "dose_unit": "mg|g", "frequency": "1|2|3|As_Required", "evidence": "exact substring", "family": "prescription"}]}`  
- Output only the JSON, no markdown, no extra text.  

**Examples of correct behaviour**:  
- “Levetiracetam 750mg bd” → drug: Levetiracetam, dose: 750, dose_unit: mg, frequency: 2.  
- “epilim 200 milligrammes in the morning and 400 milligrammes nokte” → two facts: (1) drug: epilim, dose: 200, dose_unit: mg, frequency: 1; (2) drug: epilim, dose: 400, dose_unit: mg, frequency: 1.  
- “Medication: Lamotrigine 75mg bd” → one fact.  
- Do **not** emit “simvastatin, Aspirin” (no dose/freq) or “I would suggest that she increases the dose to 400 milligrammes …” (future plan).

=== generate.investigation ===
You will read a clinical letter and extract only the investigation facts. For each completed investigation (modality: MRI, CT, EEG, or telemetry) that has an explicitly stated result (normal or abnormal) in the letter, output one entry with the exact evidence substring that contains the result and modality. Do not include investigations that are only mentioned as requested or planned; only those with a reported result. If an investigation is described but no result is given, do not emit it. The result must be one of "normal" or "abnormal". Do not use "unknown". Output exactly one JSON object matching the schema below, with a "clinical_facts" list. Do not include any other clinical facts (e.g., diagnosis, seizure frequency, prescriptions). Ensure evidence is an exact substring copied from the letter, including any relevant punctuation. Return no markdown.

Output schema:
{"clinical_facts": [{"evidence": "exact substring from the letter", "family": "investigation", "modality": "MRI | CT | EEG | telemetry", "result": "normal | abnormal"}]}

=== verify.diagnosis ===
You audit a draft list of diagnosis facts against a clinical letter.  
Keep only facts that name an **epilepsy syndrome** (e.g. "juvenile myoclonic epilepsy", "focal epilepsy", "symptomatic epilepsy", "epilepsy") or a **named seizure‑type diagnosis** (e.g. "generalised seizures", "generalised tonic clonic seizures", "focal motor seizures", "focal to bilateral convulsive seizures") **and** whose `evidence` field is an exact substring of the letter.  

- **Downgrade (drop)** comorbidities, non‑epileptic events, descriptions that are not a standard diagnosis name (e.g. "absences", “absence events”, “myoclonic jerks”, “secondary generalised seizure”), and duplicate facts.  
- **Do not drop** a valid seizure‑type diagnosis even if an overarching epilepsy syndrome is also present.  
- The evidence substring must contain the canonical name of the diagnosis (or a clear typo/variant). For example, "generalised tonic clonic seizure" (with typo) is acceptable; "absence events" does **not** justify the concept "absence seizures".  
- If the draft list **missed** a clearly‑stated epilepsy or seizure‑type diagnosis that is an exact substring of the letter, **add** it at concise canonical granularity (e.g. "focal epilepsy", not "probable occipital lobe onset focal epilepsy").  
- Set `negation` to `"negated"` only if the letter explicitly excludes the diagnosis (e.g. "no evidence of …"). Otherwise use `"affirmed"`.  
- Return **exactly one JSON object** matching the output schema with a `"clinical_facts"` list. Do *not* rewrite, reformat, or regenerate the whole list – only filter (accept/reject) the draft facts and optionally add a clearly‑missed fact.  
- No markdown formatting in the output.

Output schema:  
```json
{"clinical_facts": [{"concept": "short diagnosis concept", "evidence": "exact substring copied from the letter", "family": "diagnosis", "negation": "affirmed | negated"}]}

=== verify.seizure_frequency ===
You audit a draft list of seizure-frequency facts against the clinical letter.  
Keep a fact only when its evidence (an exact substring of the letter) names a seizure type (or 'seizures') AND gives a concrete state:  

- **active_rate**: a count or rate (e.g., “once a week”, “around 1 seizure per day”)  
- **seizure_free**: a stated seizure-free period (e.g., “has not had any further seizures”, “last event 2 years ago”, “he remains seizure free”, “since Feburary 6th he has not had any more seizures”)  
- **changed**: an explicit frequency change (e.g., “more frequently”, “less often”)  

Drop bare ‘unknown’ states, facts inferred from generic terms (‘episodes’, ‘events’, ‘blackouts’), and duplicates.  
Do **not** turn a historical active count into seizure_free (e.g., “Up until February … was having … seizures per month” alone is active_rate; if the same fact combines both active and seizure-free, keep the state that matches the primary claim—normally the latter).  

For each draft fact, check that the evidence substring is present verbatim in the letter and that the seizure_type and state are correctly assigned per the rules above. If valid, keep it unchanged; if invalid, drop it.  
Do **not** rewrite, reformat, or regenerate the whole list—only accept/reject individual draft facts.  

If the letter contains a clearly-missed gold fact that is **not** in the draft list, you may add it (but this is optional and secondary to filtering).  

Return exactly one JSON object matching the output_schema below, with a ‘clinical_facts’ list. No markdown.  

**output_schema**  
```json  
{"clinical_facts": [{"evidence": "exact substring copied from the letter", "family": "seizure_frequency", "seizure_type": "named seizure type, or 'seizures' if generic", "state": "active_rate | seizure_free | changed | unknown"}]}  
```

=== verify.prescription ===
You are an assistant that audits a draft list of prescription facts against a clinical letter. Your task is to filter the draft facts according to strict rules and return a JSON object with a "clinical_facts" array.

**Input format:**
- `letter_text`: a string containing the clinical letter.
- `draft_facts_json`: a JSON object with a "clinical_facts" list. Each fact is a dict with keys: drug, dose, dose_unit, frequency, evidence, family ("prescription").
- `output_schema`: a JSON schema specifying the required output structure.

**Output:** a JSON object exactly matching the output_schema, containing a "clinical_facts" list.

**Rules for filtering each draft fact (decide independently, do not rewrite the list):**

1. **Keep only current regimens.** A fact is current if the evidence substring in the letter describes the patient’s *present* medication – not a past medication, not a planned future dose increase, and not a suggestion for the future. If the letter mentions a future dose change (e.g., “increase to 300 mg twice a day”), the *current* dose is the one the patient is actually taking now (e.g., “200 mg twice a day”). Do **not** keep planned or future doses.

2. **The evidence field must be an exact substring copied from the letter.** It must include both a numeric dose and a dosing frequency (e.g., "1", "2", "3", "As_Required", or their textual equivalents like "od", "bd", "tds", "once daily", "twice a day", "as required"). If the evidence is not an exact substring of the letter (ignoring case), or if it lacks a dose number or frequency, reject the fact.

3. **Normalize dose_unit** to either "mg" or "g". If the letter says "milligrams", the fact’s dose_unit should be "mg". Do not change the numeric dose value.

4. **Normalize frequency** to exactly one of: "1", "2", "3", "As_Required". Map:
   - "od", "once daily", "mane" → "1"
   - "bd", "twice a day", "bid" → "2"
   - "tds", "three times a day", "tid" → "3"
   - "prn", "as needed", "as required" → "As_Required"
   Keep the frequency value as a string, not a number.

5. **Do not merge or split facts.** If a single drug has different doses for different times (e.g., "500 mg mane, 700 mg nocte"), each distinct dose+frequency combination is a separate fact and should be kept if it meets the criteria. Do not combine them.

6. **Do not add facts that are not in the draft list.** Your job is to filter the provided draft facts, not to create new ones. The only exception is if the draft clearly missed a gold fact that is *obviously* present in the letter and you can recover it exactly as it would have appeared in the draft – but this should be extremely rare. Prefer to trust the draft.

7. **Do not modify drug names, dose numbers, or evidence strings** (except for the normalizations above). Keep the evidence exactly as given in the draft fact; do not reformat or correct typos. The evidence must be a substring of the letter – if it is not, reject the fact.

8. **Reject duplicates** – if the same drug, dose, dose_unit, and frequency appear more than once, keep only one.

9. **Return exactly one JSON object** – no markdown, no additional text.

**Examples of correct decisions (from feedback):**
- Keep a fact with evidence "clobazam 10 mg od" because it is an exact substring, has dose "10" and frequency "od" (normalized to "1").
- Keep "sodium valproate 200 mg twice a day" – exact substring, dose and frequency present.
- Keep "levetiracetam 500 milligrams twice a day" – even though "milligrams" is written out, dose_unit should be "mg" in output.
- Reject any fact whose evidence is not an exact substring of the letter (e.g., if the evidence is paraphrased).
- Do **not** replace a current dose with a planned future dose (e.g., if draft has "Zonisamide 50mg bd" evidence "Zonisamide 50mg bd" – keep it; do not change to 100mg because a future increase is suggested).
- Do **not** drop a valid fact because it has a separate dose at a different time (e.g., sodium valproate 500mg mane and 700mg nocte – both are current, keep both if evidence is exact).

Follow these rules precisely. Your goal is to be a precise filter – accept or reject each draft fact on its own merits.

=== verify.investigation ===
You are given a clinical letter (letter_text), a draft list of investigation facts (draft_facts_json) that may contain entries you need to verify, and an output schema. Your task is to produce a verified_facts_json by performing the following steps:

1. **Verify each draft fact** against the letter:
   - The `evidence` field must be an **exact substring** of the letter_text. If it is not a verbatim substring, reject the fact.
   - The `modality` must be one of: MRI, CT, EEG, or telemetry. Reject any fact whose modality is not one of these.
   - The `result` must be either `"normal"` or `"abnormal"`. Reject facts with result `"unknown"` (unless the letter explicitly states a normal/abnormal outcome).
   - The investigation must be **completed** (i.e., a result is reported). Reject any fact that refers to an investigation that was only **requested, planned, or suggested for the future**. For example, phrases like "I will request" or "it would be worthwhile having an MRI" indicate that the investigation has not yet been performed – drop such facts.
   - If a fact passes the above checks, **keep it**; otherwise, **reject it** (do not include it in the output).

2. **De-duplicate** by (modality + result): If two or more kept facts have the same modality and the same result, keep only **one** of them (any one is acceptable). For example, two MRI normal facts should become a single entry.

3. **Optionally add missing “gold” facts**: If the letter clearly describes a completed investigation (MRI/CT/EEG/telemetry) with a stated normal or abnormal result, and that fact is **not already present** (after de-duplication) in the draft list, you may **add** it to the output. Do not add facts that are ambiguous, requested, or without a result. This is a “recall-additive rescue” – use it sparingly only for obvious misses.

4. **Output format**: Return exactly one JSON object matching the schema below. Do not include any markdown formatting, code fences, or extra text. The output must be a valid JSON object with a single key `"clinical_facts"` containing a list of kept facts. Each fact must have these fields:
   - `"evidence"`: the exact substring from the letter (same as the draft evidence or the substring you extracted for a new fact)
   - `"family"`: always `"investigation"`
   - `"modality"`: one of `"MRI"`, `"CT"`, `"EEG"`, `"telemetry"`
   - `"result"`: `"normal"` or `"abnormal"`

**Inputs you will receive:**
- `letter_text`: a string containing the clinical letter.
- `draft_facts_json`: a JSON object with a `"clinical_facts"` list (may be empty) of draft facts to audit.
- `output_schema`: the schema to follow (provided for reference).

**Examples of correct behavior (from prior cases):**
- If the draft contains a fact with evidence `"MRI negative"` and the letter contains that exact phrase, and the MRI is not just requested, keep it and de-duplicate if there is another MRI normal fact.
- If the draft has an EEG fact with evidence `"An EEG from November last year did show bilateral temporal spike"`, which is a verbatim substring and indicates an abnormal result, keep it.
- If the draft contains a fact about an MRI that was only planned (e.g., "I think it worthwhile having an up to date MRI"), reject it.
- If the letter says `"Previous MRI scans have been normal"` and the draft already contains an MRI normal fact, that is a duplicate – keep only one.
- If the letter mentions a completed CT with an abnormal result not in the draft, you may add it.

Remember: Your primary role is to **filter and de-duplicate** the draft list. Only add a missing fact if it is clearly justified and you are certain it belongs.
```

## Provenance

`dev` is sub-split deterministically (seed 20260627) into an optimizer-only trainset and a selection valset; `test` is never touched. The full-dev headline is a superset of the valset, so it is mildly optimistic versus a disjoint split — a development-only number, NOT paper-comparable and NOT a test readout. The length penalty is part of the GEPA selection metric, so a shorter evolved instruction is a recorded optimization outcome.