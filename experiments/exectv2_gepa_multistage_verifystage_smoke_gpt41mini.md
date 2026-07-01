# GEPA from-scratch (ExECTv2 de-dup facts) — exectv2_gepa_multistage_verifystage_smoke_gpt41mini

Date: 2026-07-01

DSPy-native GEPA run. The optimizable surface is the signature instruction; the existing de-dup parse/evidence-gate/adapter and the canonical clinical_headline scorers are reused unchanged. Trained on a seeded sub-split of `dev` (optimizer-only); evaluated on the full `dev` split (development surface, NOT test). Attribution-clean LLM-only: the adapter performs representation mapping only, it adds no facts.

## Models

- Task model: `openai/gpt-4.1-mini` (temp 0.0, max_tokens 8000)
- Reflection (teacher) model: `deepseek/deepseek-reasoner`
- GEPA budget: auto=None max_metric_calls=24 (trainset 8, valset 6)

## Length penalty (prompt-bloat control)

- enabled: True
- instruction budget: 4000 tok (beta 0.25)
- demo budget: 800 tok (beta 0.25)
- output budget: 2000 tok (alpha 0.05)
- **final instruction length: 2272 tokens** (seed was 2272 tokens)

## Final evaluation (dev, clinical-recovery surface)

- **Canonical clinical_headline overall F1: 0.709** (P=0.773 R=0.655, Diagnosis=concept_negation)
  - Diagnosis=0.421  SeizureFrequency=0.500  Prescription=1.000  Investigations=0.923
- **Producer evidence-recall (source_near): 0.553** (GEPA per-family baseline 0.694, v08 hybrid 0.883) — Dx=0.250 SF=0.556 Rx=1.000 Inv=0.857
- Strict benchmark per-item F1 (diagnostic, NOT paper-cleared): 0.102
- Semantic (CUI-dropped) per-item F1: 0.102
- Letters: 4 (unscorable: 0); facts emitted 21, scored 21

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
You audit a draft list of diagnosis facts against the clinical letter.

Keep facts that name an epilepsy syndrome or a named seizure-type diagnosis and
whose evidence is an exact substring of the letter. Drop comorbidities,
non-epileptic events, and duplicates. Add any clearly-stated epilepsy or
named-seizure-type diagnosis the draft missed, at a concise canonical
granularity (e.g. 'focal epilepsy', not a long qualified phrase). Set
negation=negated only if the diagnosis is explicitly excluded. Return exactly
one JSON object matching output_schema with a 'clinical_facts' list, no markdown.

=== verify.seizure_frequency ===
You audit a draft list of seizure-frequency facts against the clinical letter.

Keep a fact only when its evidence (an exact substring of the letter) names a
seizure type (or 'seizures') AND gives a concrete state: a count/rate
(active_rate), a stated seizure-free period (seizure_free), or an explicit
frequency change (changed). Drop bare 'unknown' states, facts inferred from
generic 'episodes'/'events'/'blackouts', and duplicates. Do not turn a
historical active count into seizure_free. Return exactly one JSON object
matching output_schema with a 'clinical_facts' list, no markdown.

=== verify.prescription ===
You audit a draft list of prescription facts against the clinical letter.

Keep only current regimens whose evidence (an exact substring of the letter)
states both a numeric dose and a dosing frequency. Drop past, planned-only, or
dose/frequency-less drugs and duplicates. Normalize dose_unit to mg or g and
frequency to 1/2/3/As_Required. Return exactly one JSON object matching
output_schema with a 'clinical_facts' list, no markdown.

=== verify.investigation ===
You audit a draft list of investigation facts against the clinical letter.

Keep only completed MRI/CT/EEG/telemetry investigations with a stated result
(normal or abnormal) whose evidence is an exact substring of the letter. Drop
requested/planned-only investigations and duplicates (de-duplicate by
modality+result). Return exactly one JSON object matching output_schema with a
'clinical_facts' list, no markdown.
```

## Provenance

`dev` is sub-split deterministically (seed 20260627) into an optimizer-only trainset and a selection valset; `test` is never touched. The full-dev headline is a superset of the valset, so it is mildly optimistic versus a disjoint split — a development-only number, NOT paper-comparable and NOT a test readout. The length penalty is part of the GEPA selection metric, so a shorter evolved instruction is a recorded optimization outcome.