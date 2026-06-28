# GEPA from-scratch (ExECTv2 de-dup facts) — exectv2_gepa_recall_dedup_gpt41mini_b2p0_20260628

Date: 2026-06-28

DSPy-native GEPA run. The optimizable surface is the signature instruction; the existing de-dup parse/evidence-gate/adapter and the canonical clinical_headline scorers are reused unchanged. Trained on a seeded sub-split of `dev` (optimizer-only); evaluated on the full `dev` split (development surface, NOT test). Attribution-clean LLM-only: the adapter performs representation mapping only, it adds no facts.

## Models

- Task model: `openai/gpt-4.1-mini` (temp 0.0, max_tokens 12000)
- Reflection (teacher) model: `deepseek/deepseek-reasoner`
- GEPA budget: auto=medium max_metric_calls=None (trainset 90, valset 50)

## Length penalty (prompt-bloat control)

- enabled: True
- instruction budget: 2000 tok (beta 0.25)
- demo budget: 800 tok (beta 0.25)
- output budget: 2000 tok (alpha 0.05)
- **final instruction length: 1992 tokens** (seed was 417 tokens)

## Final evaluation (dev, clinical-recovery surface)

- **Canonical clinical_headline overall F1: 0.721** (P=0.678 R=0.771, Diagnosis=concept_negation)
  - Diagnosis=0.700  SeizureFrequency=0.546  Prescription=0.859  Investigations=0.783
- Strict benchmark per-item F1 (diagnostic, NOT paper-cleared): 0.129
- Semantic (CUI-dropped) per-item F1: 0.139
- Letters: 140 (unscorable: 0); facts emitted 948, scored 927

## Comparators (dev140, from plan 13)

- Hand-tuned single-prompt de-dup plateau: GPT-4.1-mini 0.710, DeepSeek 0.745, Qwen 0.694
- v08 hybrid (multi-component) control: 0.9155

## Evolved instruction

```text
=== diagnosis ===
You are given a clinical letter. Your task is to extract all distinct diagnosis facts **directly related to epilepsy** from the letter. This includes:

- Epilepsy syndromes (e.g., "generalised epilepsy", "focal epilepsy", "juvenile myoclonic epilepsy", "temporal lobe epilepsy").
- Epilepsy types (e.g., "symptomatic structural focal epilepsy", "genetic generalised epilepsy", "drug‑refractory epilepsy").
- Specific seizure types **explicitly named using standard medical terminology** as occurring in the patient (e.g., "generalised tonic clonic seizures", "focal seizures with altered awareness", "focal motor seizures", "absence seizures", "tonic clonic seizures").  
  Do **NOT** infer seizure types from vague descriptions (e.g., "shakes", "jerks", "fall and generalised shakes"). Do **NOT** extract seizure types that are only part of a syndrome name (e.g., "absences" in "Juvenile absence epilepsy") unless they are also mentioned independently in the narrative.
- Underlying structural diagnoses or etiologies **only when they appear as part of an epilepsy diagnosis phrase** (e.g., "symptomatic structural epilepsy secondary to Tuberous sclerosis" → extract "symptomatic‑structural‑focal‑epilepsy", not the etiology alone).  

Do **NOT** include:
- Unrelated medical conditions (e.g., anxiety, depression, dissociative seizures, non‑epileptic attack disorder, migraine, diabetes, hypertension).
- Medications, investigations (e.g., MRI, EEG, ECG), or any seizure frequency/trend descriptions (e.g., "seizures per month", "increased frequency", "seizure‑free").

For each diagnosis fact, output a JSON object with:
- "concept": a short, canonical, lowercased‑with‑hyphens concept name (e.g., "absence‑seizures", "generalised‑tonic‑clonic‑seizures", "temporal‑lobe‑epilepsy", "epileptic‑seizures"). Break combined phrases into separate granular concepts when they are independent diagnoses (e.g., "Probable focal epilepsy and migraine" → only "focal‑epilepsy").
- "evidence": the exact substring from the letter that supports the diagnosis (including any negation marker if present).
- "family": always "diagnosis".
- "negation": "affirmed" if the diagnosis is present, "negated" if explicitly excluded (e.g., "no evidence of focal seizures").

Return exactly one JSON object matching the output schema below, with a `clinical_facts` list. Deduplicate identical concepts. Do not wrap in markdown.

Output schema:
{"clinical_facts": [{"concept": "short diagnosis concept", "evidence": "exact substring copied from the letter", "family": "diagnosis", "negation": "affirmed | negated"}]}

=== seizure_frequency ===
You extract seizure-frequency facts from a clinical letter.

Follow these rules:

1. **Only output facts for the "seizure_frequency" family.** Do not include diagnosis, medication, investigations, or any other information.

2. **For each distinct seizure type mentioned in the letter, emit one fact.**  
   - Use the exact named type as written (e.g., "generalised tonic clonic seizures", "complex partial seizures", "myoclonic jerks", "absences").  
   - If a description without a medical name is given, use that descriptive phrase (e.g., "staring episodes", "focal seizures left arm movement").  
   - Only use the generic term "seizures" when the letter refers to seizures with no specific type or description at all.

3. **Determine the correct state from these options:**  
   - `"active_rate"` – if a numerical rate or count is given (e.g., "occurs 4 to 5 times a year", "2 seizures", "cluster of 5 seizures").  
   - `"seizure_free"` – if the patient is explicitly stated to be seizure-free (e.g., "remains seizure free", "he has been seizure free since ...").  
   - `"changed"` – if improvement or change is mentioned without a specific rate (e.g., "seizures have improved", "seizures are well controlled").  
   - `"unknown"` – if no frequency information is provided at all.  
   **Never use "unknown" as a default;** if the letter contains any frequency information, use one of the other states.

4. **Ground each fact with an exact substring** copied verbatim from the letter as the evidence.

5. **Do not enumerate individual dated events** – only use the overall state (e.g., "She has had a few episodes" → do not list each date).

6. **De‑duplicate facts:** never emit two facts with the same `seizure_type` **and** the same `state`.

7. **Keep seizure type names concise** – use short canonical forms as written (e.g., "generalised tonic clonic seizures", not "generalised tonic clonic seizures with secondary generalisation").

Return exactly one JSON object matching this schema, with no markdown or extra text:

```json
{"clinical_facts": [{"evidence": "exact substring copied from the letter", "family": "seizure_frequency", "seizure_type": "named seizure type, or 'seizures' if generic", "state": "active_rate | seizure_free | changed | unknown"}]}
```

=== prescription ===
{
  "instruction": "Extract clinical facts from an epilepsy clinic letter. Output a single JSON object with a 'clinical_facts' list. Each fact must have a 'family' field (one of 'diagnosis', 'seizure_frequency', 'prescription', 'investigations'), an 'evidence' field (an exact substring copied verbatim from the letter including punctuation and spacing), and family‑specific fields as defined below.\n\nFamily‑specific rules:\n- **diagnosis**: 'concept' must be a short canonical string derived from the letter's diagnosis. Use hyphenated lowercase forms (e.g., 'frontal-lobe-epilepsy', 'juvenile-myoclonic-epilepsy', 'epilepsy-unclassified', 'drug-refractory-epilepsy', 'focal-epilepsy', 'dissociative-seizures'). Split composite diagnoses into separate facts (e.g., 'Drug refractory focal epilepsy' → facts for 'drug-refractory-epilepsy' and 'focal-epilepsy'). Do not include uncertain or negated statements. Evidence must be the exact substring containing the diagnosis.\n\n- **seizure_frequency**: 'concept' is always 'seizures' (do not create separate facts for subtypes like 'focal impaired awareness' or 'jerks'). 'state' must be one of: a number (integer count of seizures in a given period, e.g., '1' for 'once a week', '5' for 'cluster of 5 seizures within two days'), 'seizure-free', or a frequency change ('Same', 'Increased', 'Decreased'). Only emit a single seizure frequency fact per letter, choosing the most concrete numeric or change statement. Omit negated statements (e.g., 'no absences') and ambiguous descriptions (e.g., 'happen more frequently' without a specific change word).\n\n- **prescription**: Only include anti‑epileptic drugs (AEDs) that are **currently being taken**. Do **not** include past medications, planned future doses, or withdrawn medications. Use generic drug names (e.g., 'sodium valproate' not 'Epilim', 'levetiracetam' not 'Keppra'). Split different doses/times into separate facts (e.g., 100mg am and 200mg pm are two facts). Only emit if both dose and frequency are explicitly stated. Frequency must be one of '1', '2', '3', 'As_Required' (map 'od'/'on' to '1', 'bd' to '2', 'tds' to '3'). Dose_unit is 'mg' or 'g'.\n\n- **investigations**: Only include modalities explicitly mentioned as **performed** (past tense). Acceptable modalities: MRI, CT, EEG, telemetry. Do **not** include future arrangements (e.g., 'I will arrange an MRI') or tests not in the list (e.g., ECG). Evidence string must be the exact substring naming the modality.\n\nDeduplicate facts: same family and same core data (same concept, same state, same drug+dose+dose_unit+frequency, same modality).\n\nReturn the JSON without markdown formatting."
}

=== investigation ===
You read one clinical letter and list its investigation facts.

Emit each distinct completed modality once (MRI, CT, EEG, or telemetry) with a
result: normal, abnormal, or unknown. Ground each by an exact substring of the
letter as evidence. Return exactly one JSON object matching output_schema with a
'clinical_facts' list, no markdown.
```

## Provenance

`dev` is sub-split deterministically (seed 20260627) into an optimizer-only trainset and a selection valset; `test` is never touched. The full-dev headline is a superset of the valset, so it is mildly optimistic versus a disjoint split — a development-only number, NOT paper-comparable and NOT a test readout. The length penalty is part of the GEPA selection metric, so a shorter evolved instruction is a recorded optimization outcome.