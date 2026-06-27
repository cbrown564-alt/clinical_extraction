# GEPA from-scratch (ExECTv2 de-dup facts) — exectv2_gepa_from_scratch_dedup_deepseek_reasoner_20260627

Date: 2026-06-27

DSPy-native GEPA run. The optimizable surface is the signature instruction; the existing de-dup parse/evidence-gate/adapter and the canonical clinical_headline scorers are reused unchanged. Trained on a seeded sub-split of `dev` (optimizer-only); evaluated on the full `dev` split (development surface, NOT test). Attribution-clean LLM-only: the adapter performs representation mapping only, it adds no facts.

## Models

- Task model: `deepseek/deepseek-reasoner` (temp 0.0, max_tokens 12000)
- Reflection (teacher) model: `deepseek/deepseek-reasoner`
- GEPA budget: auto=medium max_metric_calls=None (trainset 90, valset 50)

## Length penalty (prompt-bloat control)

- enabled: True
- instruction budget: 600 tok (beta 0.25)
- demo budget: 800 tok (beta 0.25)
- output budget: 2000 tok (alpha 0.05)
- **final instruction length: 555 tokens** (seed was 121 tokens)

## Final evaluation (dev, clinical-recovery surface)

- **Canonical clinical_headline overall F1: 0.636** (P=0.574 R=0.714, Diagnosis=concept_negation)
  - Diagnosis=0.435  SeizureFrequency=0.524  Prescription=0.892  Investigations=0.825
- Strict benchmark per-item F1 (diagnostic, NOT paper-cleared): 0.136
- Semantic (CUI-dropped) per-item F1: 0.146
- Letters: 140 (unscorable: 0); facts emitted 894, scored 871

## Comparators (dev140, from plan 13)

- Hand-tuned single-prompt de-dup plateau: GPT-4.1-mini 0.710, DeepSeek 0.745, Qwen 0.694
- v08 hybrid (multi-component) control: 0.9155

## Evolved instruction

```text
Extract de‑duplicated clinical facts from the given clinical letter. Return exactly one JSON object matching the schema below. The object must contain a 'clinical_facts' list. No text outside the JSON.

Four families of facts, each with required keys:
1. **diagnosis** – one fact per distinct concept (epilepsy type, comorbidities). Include both affirmed and negated. Evidence: exact verbatim substring. Keys: concept, evidence, family="diagnosis", negation="affirmed"|"negated".
2. **seizure_frequency** – one fact per distinct seizure type (use 'seizures' if generic). State must be: "active_rate" (rate described), "seizure_free" (explicitly free since a point), "changed" (pattern changed), "unknown". Do not list individual events. "No seizures since…" → seizure_free. Keys: evidence, family="seizure_frequency", seizure_type, state.
3. **prescription** – only current anti‑seizure medications (AEDs). Provide drug name as written, dose number and unit (if stated, else empty strings), frequency as "1","2","3","As_Required". Evidence must be exact substring containing drug and dose. Do not include non‑AEDs. Keys: dose, dose_unit, drug, evidence, family="prescription", frequency.
4. **investigation** – only modalities "MRI","CT","EEG","telemetry". Result: "normal","abnormal","unknown". Evidence exact substring. Keys: evidence, family="investigation", modality, result.

De‑duplication: Do not repeat the same concept (diagnosis), same seizure type+state, same drug+dosage, or same modality+result. Every 'evidence' must appear verbatim in the letter. If a fact lacks sufficient textual support, drop it.

Output schema (use exactly these keys per fact):
- diagnosis: {"concept": "...", "evidence": "...", "family": "diagnosis", "negation": "affirmed|negated"}
- seizure_frequency: {"evidence": "...", "family": "seizure_frequency", "seizure_type": "...", "state": "active_rate|seizure_free|changed|unknown"}
- prescription: {"dose": "number or ''", "dose_unit": "mg|g or ''", "drug": "...", "evidence": "...", "family": "prescription", "frequency": "1|2|3|As_Required"}
- investigation: {"evidence": "...", "family": "investigation", "modality": "MRI|CT|EEG|telemetry", "result": "normal|abnormal|unknown"}
```

## Provenance

`dev` is sub-split deterministically (seed 20260627) into an optimizer-only trainset and a selection valset; `test` is never touched. The full-dev headline is a superset of the valset, so it is mildly optimistic versus a disjoint split — a development-only number, NOT paper-comparable and NOT a test readout. The length penalty is part of the GEPA selection metric, so a shorter evolved instruction is a recorded optimization outcome.