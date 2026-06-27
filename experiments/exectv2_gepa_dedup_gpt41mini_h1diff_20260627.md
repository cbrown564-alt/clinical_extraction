# GEPA from-scratch (ExECTv2 de-dup facts) — exectv2_gepa_dedup_gpt41mini_h1diff_20260627

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
- **final instruction length: 576 tokens** (seed was 121 tokens)

## Final evaluation (dev, clinical-recovery surface)

- **Canonical clinical_headline overall F1: 0.702** (P=0.752 R=0.659, Diagnosis=concept_negation)
  - Diagnosis=0.569  SeizureFrequency=0.597  Prescription=0.836  Investigations=0.864
- Strict benchmark per-item F1 (diagnostic, NOT paper-cleared): 0.135
- Semantic (CUI-dropped) per-item F1: 0.146
- Letters: 140 (unscorable: 0); facts emitted 720, scored 693

## Comparators (dev140, from plan 13)

- Hand-tuned single-prompt de-dup plateau: GPT-4.1-mini 0.710, DeepSeek 0.745, Qwen 0.694
- v08 hybrid (multi-component) control: 0.9155

## Evolved instruction

```text
{
  "instruction": "Extract de‑duplicated clinical facts from a clinical letter into four families: diagnosis, seizure_frequency, prescription, investigation. Return exactly one JSON object matching the output schema. Follow these rules:\n\n- Evidence: every fact must have an 'evidence' field that is an exact substring copied verbatim from the letter. Do not repeat a fact already listed (same concept, same family, same evidence).\n\n- Diagnosis: Only include **epileptic seizure types** and **epilepsy syndromes** (e.g., 'temporal-lobe-epilepsy', 'secondary-generalised-seizures', 'focal-epilepsy', 'drug-refractory-epilepsy'). Do **not** include non‑epileptic conditions, comorbidities (e.g., hypertension, depression, anxiety), or historical non‑epileptic diagnoses (e.g., sub‑arachnoid haemorrhage). Use short canonical concepts (hyphenated, lowercase). Negation: 'affirmed' if present, 'negated' if ruled out.\n\n- Seizure_frequency: Only current frequency. Include only if an **explicit numeric rate** is given (e.g., 'every month', 'twice a day', '2 per year'), or if 'seizure_free' is explicitly stated, or if 'increased'/'decreased' is explicitly mentioned. Do **not** infer from vague terms like 'most days', 'occasional', 'sometimes'. 'seizure_type': use the exact named type from the letter if specified (e.g., 'partial-motor-seizures'), otherwise 'seizures'. 'state': one of 'active_rate' (for numeric), 'seizure_free', 'changed' (for explicit increase/decrease), or 'unknown' only if no other option.\n\n- Prescription: Only current medications (do not include planned future changes). For each drug: 'drug' exact name as written; 'dose' number only when stated (omit field if no dose); 'dose_unit' 'mg' or 'g' when dose present; 'frequency' one of '1', '2', '3', 'As_Required', or 'unknown' if not specified. Separate entries for different dose‑frequency combinations.\n\n- Investigation: Only investigations that have been performed **and** have an **explicitly stated result** of 'normal' or 'abnormal'. Do **not** emit if the result is only implied (e.g., 'confirmed', 'showed changes'). Modality: one of MRI, CT, EEG, telemetry. Result: 'normal' or 'abnormal' only. Deduplicate by modality (keep the first occurrence).\n\nReturn only the JSON object, no markdown or extra text."
}
```

## Provenance

`dev` is sub-split deterministically (seed 20260627) into an optimizer-only trainset and a selection valset; `test` is never touched. The full-dev headline is a superset of the valset, so it is mildly optimistic versus a disjoint split — a development-only number, NOT paper-comparable and NOT a test readout. The length penalty is part of the GEPA selection metric, so a shorter evolved instruction is a recorded optimization outcome.