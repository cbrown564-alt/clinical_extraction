# GEPA from-scratch (ExECTv2 de-dup facts) — exectv2_gepa_dedup_gpt41mini_h2mb8_20260628

Date: 2026-06-28

DSPy-native GEPA run. The optimizable surface is the signature instruction; the existing de-dup parse/evidence-gate/adapter and the canonical clinical_headline scorers are reused unchanged. Trained on a seeded sub-split of `dev` (optimizer-only); evaluated on the full `dev` split (development surface, NOT test). Attribution-clean LLM-only: the adapter performs representation mapping only, it adds no facts.

## Models

- Task model: `openai/gpt-4.1-mini` (temp 0.0, max_tokens 12000)
- Reflection (teacher) model: `deepseek/deepseek-reasoner`
- GEPA budget: auto=None max_metric_calls=1400 (trainset 90, valset 50)

## Length penalty (prompt-bloat control)

- enabled: True
- instruction budget: 600 tok (beta 0.25)
- demo budget: 800 tok (beta 0.25)
- output budget: 2000 tok (alpha 0.05)
- **final instruction length: 490 tokens** (seed was 121 tokens)

## Final evaluation (dev, clinical-recovery surface)

- **Canonical clinical_headline overall F1: 0.719** (P=0.689 R=0.753, Diagnosis=concept_negation)
  - Diagnosis=0.662  SeizureFrequency=0.540  Prescription=0.850  Investigations=0.862
- Strict benchmark per-item F1 (diagnostic, NOT paper-cleared): 0.136
- Semantic (CUI-dropped) per-item F1: 0.146
- Letters: 140 (unscorable: 0); facts emitted 884, scored 866

## Comparators (dev140, from plan 13)

- Hand-tuned single-prompt de-dup plateau: GPT-4.1-mini 0.710, DeepSeek 0.745, Qwen 0.694
- v08 hybrid (multi-component) control: 0.9155

## Evolved instruction

```text
{
  "instruction": "Extract de‑duplicated clinical facts from the clinical letter into a single JSON object with a \"clinical_facts\" list. Each fact belongs to one of four families: diagnosis, seizure_frequency, prescription, investigation. Use the exact schemas below. Copy evidence as contiguous substrings from the letter. De‑duplicate: each unique concept (diagnosis), unique (seizure_type+state+number_of_seizures+frequency_change) combination, unique (drug+dose+frequency) combination, and unique investigation modality appears only once.\n\n1. **diagnosis** – Break compound diagnoses into individual seizure types and syndromes. Use lowercase hyphenated terms (e.g., generalised-tonic-clonic-seizures, absence-seizures, focal-to-bilateral-convulsive-seizures, secondary-generalised-seizures, epilepsy, focal-epilepsy). Preserve singular/plural as in the letter. Exclude non‑epilepsy conditions (e.g., migraine, depression) and non‑diagnostic findings (e.g., MRI/EEG results). Negation: \"affirmed\" or \"negated\".\n2. **seizure_frequency** – Only include current seizure status. State must be one of: \"active_rate\" (current count/rate given), \"seizure_free\" (explicitly seizure‑free), \"changed\" (improvement/worsening described), or \"unknown\" (no current pattern). Facts with state \"unknown\" are omitted. Set \"number_of_seizures\" to integer if a specific numeric count is given (ignore ranges). Set \"frequency_change\" as string if a change is mentioned (e.g., \"decreased\", \"increased\").\n3. **prescription** – Only include medications the patient is currently taking. Map \"bd\"→2, \"once daily\"→1, \"tds\"→3, \"nocte\"→1. Dose as number only (omit if not stated). Dose_unit: \"mg\" or \"g\".\n4. **investigation** – Only include performed investigations with a reported result. Modality: MRI, CT, EEG, telemetry. Result: \"normal\" or \"abnormal\". Exclude planned/requested.\n\nReturn one JSON object with no additional text."
}
```

## Provenance

`dev` is sub-split deterministically (seed 20260627) into an optimizer-only trainset and a selection valset; `test` is never touched. The full-dev headline is a superset of the valset, so it is mildly optimistic versus a disjoint split — a development-only number, NOT paper-comparable and NOT a test readout. The length penalty is part of the GEPA selection metric, so a shorter evolved instruction is a recorded optimization outcome.