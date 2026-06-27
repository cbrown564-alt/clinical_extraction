# GEPA from-scratch (ExECTv2 de-dup facts) — exectv2_gepa_from_scratch_dedup_gpt41mini_20260627

Date: 2026-06-27

DSPy-native GEPA run. The optimizable surface is the signature instruction; the existing de-dup parse/evidence-gate/adapter and the canonical clinical_headline scorers are reused unchanged. Trained on a seeded sub-split of `dev` (optimizer-only); evaluated on the full `dev` split (development surface, NOT test). Attribution-clean LLM-only: the adapter performs representation mapping only, it adds no facts.

## Models

- Task model: `openai/gpt-4.1-mini` (temp 0.0, max_tokens 12000)
- Reflection (teacher) model: `deepseek/deepseek-reasoner`
- GEPA budget: auto=medium max_metric_calls=None (trainset 90, valset 50)

## Length penalty (prompt-bloat control)

- enabled: True
- instruction budget: 600 tok (beta 0.25)
- demo budget: 800 tok (beta 0.25)
- output budget: 2000 tok (alpha 0.05)
- **final instruction length: 590 tokens** (seed was 121 tokens)

## Final evaluation (dev, clinical-recovery surface)

- **Canonical clinical_headline overall F1: 0.628** (P=0.569 R=0.702, Diagnosis=concept_negation)
  - Diagnosis=0.456  SeizureFrequency=0.539  Prescription=0.815  Investigations=0.792
- Strict benchmark per-item F1 (diagnostic, NOT paper-cleared): 0.123
- Semantic (CUI-dropped) per-item F1: 0.133
- Letters: 140 (unscorable: 0); facts emitted 926, scored 898

## Comparators (dev140, from plan 13)

- Hand-tuned single-prompt de-dup plateau: GPT-4.1-mini 0.710, DeepSeek 0.745, Qwen 0.694
- v08 hybrid (multi-component) control: 0.9155

## Evolved instruction

```text
You are given a clinical letter (`letter_text`) and an `output_schema`. Extract de‑duplicated clinical facts into a JSON object that exactly matches the schema.

**General rules**  
- Use the exact substring from the letter as `evidence` (truncate only to remove surrounding text).  
- De‑duplicate: each diagnosis, seizure‑type‑state pair, drug regimen (same drug, dose, frequency), and investigation (same modality) appears at most once.  
- Do not infer facts not explicitly stated.  
- For missing fields: use `null` for numeric, `"unknown"` for string.  

**Diagnosis** (`family: "diagnosis"`)  
- List every distinct diagnosis or syndrome concept (e.g., epilepsy type, comorbid conditions).  
- Set `negation` to `"affirmed"` if stated, `"negated"` if explicitly excluded.  
- A negated diagnosis is still a fact and must be included.  

**Seizure_frequency** (`family: "seizure_frequency"`)  
- One fact per distinct seizure type. Use the specific name from the letter (e.g., "generalised tonic clonic seizures") or `"seizures"` if generic.  
- `state`:  
  - `"active_rate"` – recent seizure activity or frequency described (e.g., "weekly", "2 per year").  
  - `"seizure_free"` – no seizures since a stated date/period (e.g., "seizure free since before Christmas", "no further episodes").  
  - `"changed"` – pattern or frequency has changed.  
  - `"unknown"` – otherwise.  
- Do **not** list individual dated events separately; only one record per seizure type.  

**Prescription** (`family: "prescription"`)  
- Include only current medications (stated in a medication section or explicitly described as ongoing). Exclude planned changes or future recommendations.  
- `dose`: number (integer) if stated, else `null`.  
- `dose_unit`: `"mg"` or `"g"`.  
- `frequency`: `"1"` (once daily), `"2"` (twice daily), `"3"` (three times daily), `"As_Required"`, or `"unknown"` if not given.  
- If the same drug appears with different doses (e.g., morning/evening), list each as a separate fact.  

**Investigation** (`family: "investigation"`)  
- Only include modalities `"MRI"`, `"CT"`, `"EEG"`, or `"telemetry"`.  
- `result`: `"normal"`, `"abnormal"`, or `"unknown"` based on the letter’s wording; if no result mentioned, use `"unknown"`.  

Return exactly one JSON object with a `"clinical_facts"` list. No markdown or commentary outside the JSON.
```

## Provenance

`dev` is sub-split deterministically (seed 20260627) into an optimizer-only trainset and a selection valset; `test` is never touched. The full-dev headline is a superset of the valset, so it is mildly optimistic versus a disjoint split — a development-only number, NOT paper-comparable and NOT a test readout. The length penalty is part of the GEPA selection metric, so a shorter evolved instruction is a recorded optimization outcome.