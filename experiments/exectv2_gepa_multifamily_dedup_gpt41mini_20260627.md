# GEPA from-scratch (ExECTv2 de-dup facts) — exectv2_gepa_multifamily_dedup_gpt41mini_20260627

Date: 2026-06-27

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
- **final instruction length: 1902 tokens** (seed was 417 tokens)

## Final evaluation (dev, clinical-recovery surface)

- **Canonical clinical_headline overall F1: 0.631** (P=0.565 R=0.715, Diagnosis=concept_negation)
  - Diagnosis=0.425  SeizureFrequency=0.523  Prescription=0.890  Investigations=0.800
- Strict benchmark per-item F1 (diagnostic, NOT paper-cleared): 0.135
- Semantic (CUI-dropped) per-item F1: 0.145
- Letters: 140 (unscorable: 0); facts emitted 966, scored 884

## Comparators (dev140, from plan 13)

- Hand-tuned single-prompt de-dup plateau: GPT-4.1-mini 0.710, DeepSeek 0.745, Qwen 0.694
- v08 hybrid (multi-component) control: 0.9155

## Evolved instruction

```text
=== diagnosis ===
You are given a clinical letter as input. Your task is to extract all clinically relevant facts from the letter and return them as a single JSON object with a key `clinical_facts` containing a list of fact objects.

Each fact object must have the following fields:
- `concept`: a short, canonical description of the fact (e.g., diagnosis name, seizure type with state, medication regimen, test name with result).
- `evidence`: an exact substring copied from the letter that supports the fact.
- `family`: one of `"diagnosis"`, `"seizure_frequency"`, `"prescription"`, or `"investigations"`.
- `negation`: (only for `family: "diagnosis"`) either `"affirmed"` if the diagnosis is present, or `"negated"` if the diagnosis is explicitly excluded (a negated diagnosis is still a valid fact).
- `state`: (only for `family: "seizure_frequency"`) a coarse state value: `"active_rate"` (if a current frequency is given), `"seizure_free"` (if the patient has had no seizures for a period, including phrases like “no seizures since”), `"changed"` (if frequency has changed but no specific rate), or `"unknown"` (if seizure status is not mentioned).

Follow these rules:

1. **Diagnosis family**  
   - List every distinct epilepsy type or syndrome and every distinct comorbid condition (e.g., focal cortical dysplasia, depression).  
   - Include negated diagnoses (e.g., “no photosensitivity” becomes a negated fact).  
   - Omit symptoms or seizure types (those go under seizure_frequency).  
   - Each concept appears only once.

2. **Seizure frequency family**  
   - For each distinct seizure type mentioned (e.g., focal seizures with altered awareness, tonic‑clonic seizures), emit one fact with the coarse state derived from the letter.  
   - Do **not** enumerate individual dated events. For example, “had one in 2014 and one in 2015” becomes `state: "changed"` or `"unknown"` – not two separate facts.  
   - If the letter says “no seizures since X”, the state is `"seizure_free"`.  
   - If a current frequency is given (e.g., “1 per week”), state is `"active_rate"` and include the rate in the concept (e.g., “focal seizures with altered awareness: 1 per week”).

3. **Prescription family**  
   - Emit one fact for each current medication (name + dose) mentioned in the letter.  
   - Include only medications that are currently being taken (not previously tried and stopped, unless they are part of a current regimen).  
   - Evidence should be the exact line that states the medication and dose.

4. **Investigations family**  
   - Emit one fact for each diagnostic test (e.g., EEG, MRI) that is mentioned, including the result (if given).  
   - Use a short concept like “EEG: generalized spike and wave, no photosensitivity” or “MRI brain: normal”.  
   - Include tests that were done in the past and are still relevant; do not include future planned tests.

**General principles:**  
- **Deduplicate**: The same fact must not appear more than once.  
- **Ground all facts** with an exact substring copied from the letter.  
- **Only emit facts that are clearly supported by the current letter** – avoid inferring or extrapolating.  
- **Be concise** – prefer a few general principles over many special‑case rules.  
- **Output exactly one JSON object** with the structure above, no markdown or extra text.

=== seizure_frequency ===
You are an AI assistant tasked with extracting seizure-frequency facts from a single clinical letter. Your output must be a valid JSON object conforming to the following schema, with no markdown formatting:

{"clinical_facts": [{"evidence": "exact substring copied from the letter", "family": "seizure_frequency", "seizure_type": "named seizure type, or 'seizures' if generic", "state": "active_rate | seizure_free | changed | unknown"}]}

Rules:
- **Emit exactly one fact per distinct seizure type.** For each seizure type named in the letter (e.g., "generalised tonic-clonic seizures", "absence seizures"), output a single fact. If no specific type is named, use the generic "seizures". Do not output multiple facts for the same type even if multiple pieces of evidence exist.
- **Choose the coarse state using this priority:**
  1. **"active_rate"** – when a current frequency is explicitly stated (e.g., "4 to 5 episodes a month", "cluster of 5 seizures within two days"). This overrides other possible states for that type.
  2. **"seizure_free"** – if the letter explicitly says the patient has had no seizures (e.g., "no seizures since", "last seizure was two years ago").
  3. **"changed"** – if there is explicit mention of a change in seizure frequency (e.g., "this is unusual as before this her seizures have been relatively well controlled") and no current active_rate or seizure_free is directly stated for that type.
  4. **"unknown"** – if no clear frequency, freedom, or change can be determined.
- **Ground each fact with an exact substring** from the letter that directly supports the chosen state and seizure type. Do not paraphrase or combine multiple phrases.
- **De-duplicate aggressively.** If multiple pieces of evidence refer to the same seizure type and state, output only one fact (the one with the clearest evidence). Drop any fact that is not clearly current and directly supported.
- **Ignore families other than "seizure_frequency".** The "family" field must always be exactly "seizure_frequency".
- **Do not enumerate individual dated events.** For example, "cluster of 5 seizures within two days" is treated as a single active_rate fact, not multiple facts.
- **If the letter contains no information about seizure frequency**, output an empty list: {"clinical_facts": []}.

Output only the JSON object. Do not include explanations, markdown code blocks, or any additional text.

=== prescription ===
You will be given a clinical letter and an output schema. Your task is to extract all current prescription facts from the letter and output them as a JSON object with a "clinical_facts" list. Follow these rules strictly:

- Only include medications that are currently prescribed (e.g., "currently taking", "current medication"). Omit past medications (e.g., "previously tried") and planned-only changes (e.g., "suggests increasing").
- Each distinct drug regimen (drug + dose + dose_unit + frequency) should appear exactly once.
- For each fact, provide:
  - "drug": the drug name exactly as written in the letter (generic or brand name).
  - "dose": the numeric dose only (e.g., "75", "1000"). If no dose stated, omit the entire fact.
  - "dose_unit": "mg" or "g" only, as given in the letter.
  - "frequency": use numeric codes: "1" for once daily (od, mane, etc.), "2" for twice daily (bd, bid), "3" for three times daily (tds, tid), "As_Required" for prn.
  - "evidence": an exact substring copied verbatim from the letter that contains the drug name, dose, dose_unit, and frequency (e.g., "Lamotrigine 75mg bd").
  - "family": always "prescription".
- Output only the JSON object, no markdown, no extra text. Ensure the JSON is valid and matches the schema.

Examples of evidence: "Current medication:       Lamictal 100mg BD" → drug: "Lamictal", dose: "100", dose_unit: "mg", frequency: "2", evidence: "Current medication:       Lamictal 100mg BD"

=== investigation ===
You read one clinical letter and list its investigation facts.

Emit each distinct completed modality once (MRI, CT, EEG, or telemetry) with a
result: normal, abnormal, or unknown. Ground each by an exact substring of the
letter as evidence. Return exactly one JSON object matching output_schema with a
'clinical_facts' list, no markdown.
```

## Provenance

`dev` is sub-split deterministically (seed 20260627) into an optimizer-only trainset and a selection valset; `test` is never touched. The full-dev headline is a superset of the valset, so it is mildly optimistic versus a disjoint split — a development-only number, NOT paper-comparable and NOT a test readout. The length penalty is part of the GEPA selection metric, so a shorter evolved instruction is a recorded optimization outcome.