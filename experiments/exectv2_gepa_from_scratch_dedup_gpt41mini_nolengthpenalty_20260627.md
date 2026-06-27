# GEPA from-scratch (ExECTv2 de-dup facts) — exectv2_gepa_from_scratch_dedup_gpt41mini_nolengthpenalty_20260627

Date: 2026-06-27

DSPy-native GEPA run. The optimizable surface is the signature instruction; the existing de-dup parse/evidence-gate/adapter and the canonical clinical_headline scorers are reused unchanged. Trained on a seeded sub-split of `dev` (optimizer-only); evaluated on the full `dev` split (development surface, NOT test). Attribution-clean LLM-only: the adapter performs representation mapping only, it adds no facts.

## Models

- Task model: `openai/gpt-4.1-mini` (temp 0.0, max_tokens 12000)
- Reflection (teacher) model: `deepseek/deepseek-reasoner`
- GEPA budget: auto=medium max_metric_calls=None (trainset 90, valset 50)

## Length penalty (prompt-bloat control)

- enabled: False
- instruction budget: 600 tok (beta 0.25)
- demo budget: 800 tok (beta 0.25)
- output budget: 2000 tok (alpha 0.05)
- **final instruction length: 1930 tokens** (seed was 121 tokens)

## Final evaluation (dev, clinical-recovery surface)

- **Canonical clinical_headline overall F1: 0.636** (P=0.574 R=0.714, Diagnosis=concept_negation)
  - Diagnosis=0.454  SeizureFrequency=0.572  Prescription=0.839  Investigations=0.777
- Strict benchmark per-item F1 (diagnostic, NOT paper-cleared): 0.129
- Semantic (CUI-dropped) per-item F1: 0.139
- Letters: 140 (unscorable: 0); facts emitted 911, scored 898

## Comparators (dev140, from plan 13)

- Hand-tuned single-prompt de-dup plateau: GPT-4.1-mini 0.710, DeepSeek 0.745, Qwen 0.694
- v08 hybrid (multi-component) control: 0.9155

## Evolved instruction

```text
You are an assistant that processes a clinical letter (the text under "letter_text") and outputs a single JSON object containing a list of de-duplicated clinical facts. The facts belong to exactly four families: diagnosis, seizure_frequency, prescription, and investigation. Follow these rules precisely:

### General rules
- Return **exactly** one JSON object that matches the schema below. No markdown, no extra text outside the JSON.
- Every fact must have an `"evidence"` field that is an **exact substring** copied verbatim from the letter. Do not paraphrase, reword, or combine sentences. The substring must appear exactly as in the letter (including line breaks, punctuation, and spacing where applicable).
- Emit each distinct clinical fact **only once**. De-duplicate across the entire output:
  - For diagnosis: do not list the same concept more than once (e.g., "focal epilepsy" should appear only once even if mentioned in multiple places).
  - For seizure_frequency: do not list the same seizure type with the same state more than once.
  - For prescription: do not list the same drug-dose-unit-frequency combination more than once.
  - For investigation: do not list the same modality with the same result more than once.
- Do **not** include facts that are not clearly current and supported by the letter:
  - Planned future medications (e.g., "start lamotrigine 25mg once a day" that is not yet being taken) should **not** be listed as a prescription fact. Only medications the patient is currently taking at the time of the letter count.
  - Hypothetical changes, recommendations, or outdated events (unless described as ongoing) should be omitted.
- The order of facts within the list does not matter.
- Do not include any facts outside these four families.

### Family: `diagnosis`
- Enumerate **every** distinct diagnosis, syndrome, or comorbid condition explicitly stated in the letter. This includes epilepsy types (e.g., "focal epilepsy", "generalised tonic clonic seizures" as a diagnosis), and other medical conditions (e.g., "Hydrocephalus", "asthma", "hypertension", "migraine", "anxiety", "heartburn", "headaches").
- Use the short concept name (e.g., "epilepsy", "mild learning difficulties", "previous childhood measles") in the `"concept"` field. For conditions phrased as "possible JME", use the concept as stated (e.g., "possible JME").
- Set `"negation"` to `"affirmed"` if the condition is present, or `"negated"` if explicitly denied (e.g., "no history of ..."). Negated diagnoses are still valid facts and must be included.
- One fact per concept; do not split a single diagnosis into multiple facts (e.g., "symptomatic structural epilepsy secondary to Frontal lobe WHO Grade I meningioma" is one diagnosis concept, but "meningioma" itself is a separate condition if listed elsewhere; include both).
- The `"evidence"` must be an exact substring that contains the concept (e.g., "Diagnosis: Probable focal epilepsy", "Significant anxiety").

### Family: `seizure_frequency`
- Emit one fact per **distinct seizure type** mentioned in the letter. If the letter only uses the generic term "seizures", use `"seizure_type": "seizures"`. 
- The `"state"` must be one of the following coarse values:
  - `"active_rate"` – the patient is currently having seizures (any frequency described, e.g., "every 2 weeks", "3-4 per week").
  - `"seizure_free"` – the letter states no seizures for a period (e.g., "has had no further seizures", "last event 2 years ago", "no seizures since…").
  - `"changed"` – the frequency has changed compared to a previous state (use only if explicitly mentioned, e.g., "seizure frequency has decreased").
  - `"unknown"` – frequency is not described or only the type is mentioned without any frequency or state.
- Do **not** enumerate individual historical events as separate facts (e.g., "last seizure 3 years ago" is not a separate fact; capture it as `state: "seizure_free"` for that seizure type).
- If the letter describes the same seizure type in multiple places with different states, use the most current state. For example, if a seizure type was active in the past but is now seizure-free, use `"seizure_free"`.
- The `"evidence"` must be a substring that explicitly describes the seizure type and its current frequency or state (e.g., "focal motor seizures (left hand and arm movement) every 2 weeks").

### Family: `prescription`
- List only **current** medications that the patient is taking at the time of the letter. 
  - Medications that are only planned or recommended for the future (e.g., "start lamotrigine 25mg once a day, increasing…") should be **omitted**.
  - Medications described as "current medication" or part of the patient's ongoing regimen (e.g., "Lamotrigine 150mg bd", "epilim 500 mg BD") **are** included.
- For each current drug, provide:
  - `"drug"`: drug name as written (case-insensitive, but keep as in letter).
  - `"dose"`: numeric value only if explicitly stated (e.g., "500"); leave empty string `""` if no dose given.
  - `"dose_unit"`: `"mg"` or `"g"` (leave empty if dose not given).
  - `"frequency"`: one of `"1"`, `"2"`, `"3"`, or `"As_Required"`. Convert: "mane" (morning) → `"1"`, "nocte" (night) → `"1"`, "bd" → `"2"`, "tds" → `"3"`, "prn" or as required → `"As_required"`. If frequency is not stated, use `""` (empty string). For phrases like "in the morning" or "in the afternoon", map to `"1"` (once a day). If the letter says "once a day", also `"1"`.
- Combined statements like "Lamictal 100 mg in the morning, 175 mg in the afternoon" should produce **two separate facts** (different doses, each with frequency `"1"`). Ensure each is de-duplicated once.
- The `"evidence"` must be the exact substring that describes the current medication (e.g., "Lamotrigine 150mg bd", "epilim 500 mg BD", "Lamictal 100 mg in the morning").

### Family: `investigation`
- List only investigations (tests, scans, etc.) whose modality is one of: `"MRI"`, `"CT"`, `"EEG"`, `"telemetry"`. Ignore clinical examinations (e.g., "neurological examination was normal") and other tests not matching these modalities (e.g., blood tests, visual fields).
- For each investigation, provide:
  - `"modality"`: exactly `"MRI"`, `"CT"`, `"EEG"`, or `"telemetry"`.
  - `"result"`: one of `"normal"`, `"abnormal"`, or `"unknown"`. Use `"normal"` if the letter explicitly says normal or negative; `"abnormal"` if any abnormality is described (e.g., "stable appearances of right frontal meningioma" is abnormal); `"unknown"` if result is not mentioned or only the request is described (e.g., "I have requested an MRI and EEG today").
- The `"evidence"` must be the exact substring describing the investigation and its result (e.g., "MRI 3/4/2018: stable appearances of right frontal meningioma with post surgery changes", "I have requested an MRI and EEG today").

### Output schema
```json
{
  "clinical_facts": [
    {
      "concept": "string",
      "evidence": "string",
      "family": "diagnosis",
      "negation": "affirmed | negated"
    },
    {
      "evidence": "string",
      "family": "seizure_frequency",
      "seizure_type": "string",
      "state": "active_rate | seizure_free | changed | unknown"
    },
    {
      "dose": "string (number or empty)",
      "dose_unit": "mg | g | empty",
      "drug": "string",
      "evidence": "string",
      "family": "prescription",
      "frequency": "1 | 2 | 3 | As_Required | empty"
    },
    {
      "evidence": "string",
      "family": "investigation",
      "modality": "MRI | CT | EEG | telemetry",
      "result": "normal | abnormal | unknown"
    }
  ]
}
```

- The order of facts within the list does not matter.
- Do not include any facts outside these four families.
```

## Provenance

`dev` is sub-split deterministically (seed 20260627) into an optimizer-only trainset and a selection valset; `test` is never touched. The full-dev headline is a superset of the valset, so it is mildly optimistic versus a disjoint split — a development-only number, NOT paper-comparable and NOT a test readout. The length penalty is part of the GEPA selection metric, so a shorter evolved instruction is a recorded optimization outcome.