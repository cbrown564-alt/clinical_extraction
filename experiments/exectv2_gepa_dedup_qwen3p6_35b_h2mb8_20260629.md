# GEPA from-scratch (ExECTv2 de-dup facts) — exectv2_gepa_dedup_qwen3p6_35b_h2mb8_20260629

Date: 2026-06-29

DSPy-native GEPA run. The optimizable surface is the signature instruction; the existing de-dup parse/evidence-gate/adapter and the canonical clinical_headline scorers are reused unchanged. Trained on a seeded sub-split of `dev` (optimizer-only); evaluated on the full `dev` split (development surface, NOT test). Attribution-clean LLM-only: the adapter performs representation mapping only, it adds no facts.

## Models

- Task model: `ollama_chat/qwen3.6:35b` (temp 0.0, max_tokens 6000)
- Reflection (teacher) model: `deepseek/deepseek-reasoner`
- GEPA budget: auto=medium max_metric_calls=None (trainset 90, valset 50)

## Length penalty (prompt-bloat control)

- enabled: True
- instruction budget: 600 tok (beta 0.25)
- demo budget: 800 tok (beta 0.25)
- output budget: 2000 tok (alpha 0.05)
- **final instruction length: 247 tokens** (seed was 121 tokens)

## Final evaluation (dev, clinical-recovery surface)

- **Canonical clinical_headline overall F1: 0.607** (P=0.569 R=0.650, Diagnosis=concept_negation)
  - Diagnosis=0.530  SeizureFrequency=0.391  Prescription=0.759  Investigations=0.788
- **Producer evidence-recall (source_near): 0.599** (GEPA per-family baseline 0.694, v08 hybrid 0.883) — Dx=0.395 SF=0.604 Rx=0.806 Inv=0.882
- Strict benchmark per-item F1 (diagnostic, NOT paper-cleared): 0.121
- Semantic (CUI-dropped) per-item F1: 0.133
- Letters: 140 (unscorable: 0); facts emitted 863, scored 844

## Comparators (dev140, from plan 13)

- Hand-tuned single-prompt de-dup plateau: GPT-4.1-mini 0.710, DeepSeek 0.745, Qwen 0.694
- v08 hybrid (multi-component) control: 0.9155

## Evolved instruction

```text
{
  "clinical_facts": [
    {
      "concept": "short canonical diagnosis concept (e.g., 'focal epilepsy', 'generalised tonic-clonic seizures')",
      "evidence": "exact verbatim substring from the letter",
      "family": "diagnosis",
      "negation": "affirmed | negated"
    },
    {
      "evidence": "exact verbatim substring",
      "family": "seizure_frequency",
      "seizure_type": "named type from letter, or 'seizures' if not named",
      "state": "active_rate | seizure_free | changed | unknown"
    },
    {
      "drug": "generic drug name (e.g., 'sodium valproate', not brand)",
      "dose": "<numeric value only>",
      "dose_unit": "mg | g",
      "frequency": "1 | 2 | 3 | As_Required",
      "evidence": "exact verbatim substring",
      "family": "prescription"
    },
    {
      "evidence": "exact verbatim substring",
      "family": "investigation",
      "modality": "MRI | CT | EEG | telemetry",
      "result": "normal | abnormal | unknown"
    }
  ]
}
```

## Provenance

`dev` is sub-split deterministically (seed 20260627) into an optimizer-only trainset and a selection valset; `test` is never touched. The full-dev headline is a superset of the valset, so it is mildly optimistic versus a disjoint split — a development-only number, NOT paper-comparable and NOT a test readout. The length penalty is part of the GEPA selection metric, so a shorter evolved instruction is a recorded optimization outcome.