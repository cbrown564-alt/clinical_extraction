# ExECTv2 Deduplicated Clinical Facts Phase 4 Fallback Readout

Date: 2026-06-24

## Scope

Phase 4 tested the first fallback rung after the single-prompt Phase 3 plateau:
lean per-family LLM-only prompts for direct de-duplicated `clinical_facts`.
Each letter used four model-owned calls, one each for Diagnosis,
SeizureFrequency, Prescription, and Investigation. Deterministic code only
combined the model-emitted facts, validated evidence, mapped representation
fields one-to-one, and scored on canonical `clinical_headline`.

All runs used the dev split only, `openai/gpt-4.1-mini`, temperature 0, and no
holdout/full-200 inspection.

## Phase 4 Implementation

Added `single_call_dedup_facts_per_family` to the existing LLM-only
generation-selection runner. The route:

- builds a family-gated prompt payload with `target_family`;
- filters the output schema and worked examples to that family;
- runs four independent model calls per letter;
- concatenates only model-emitted `clinical_facts`;
- reuses the Phase 2 attribution-clean adapter without deterministic additions,
  selection, state completion, ontology expansion, or de-duplication.

Focused tests cover the family-gated prompt and prompt-only row/report behavior
in `tests/test_exectv2_dedup_facts_route.py`.

## Dev25 Gate Results

| Variant | Split | Clinical-recovery F1 | P | R | Evidence validity | Call/schema failures |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Phase 3 `single_call_dedup_facts` v0.5 | dev25 | 0.800 | 0.752 | 0.856 | 0.9600 | 0 |
| Phase 4 per-family compact | dev25 | 0.796 | 0.784 | 0.808 | 0.9609 | 0 |
| Phase 4 per-family full examples | dev25 | 0.782 | 0.758 | 0.808 | 0.9562 | 0 |

Primary artifacts:

- `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_per_family_phase4_dev25_gpt41mini_20260624.{jsonl,md}`
- `experiments/exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_per_family_phase4_full_examples_dev25_gpt41mini_20260624.{jsonl,md}`

## Best Phase 4 Gate: Compact Per-Family

Canonical `clinical_headline` overall on dev25:
F1 `0.796`, precision `0.784`, recall `0.808`.

| Entity | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.873 | 0.939 | 0.816 | 31 | 2 | 7 |
| Diagnosis | 0.698 | 0.667 | 0.732 | 30 | 10 | 11 |
| SeizureFrequency | 0.690 | 0.625 | 0.769 | 20 | 12 | 6 |
| Investigations | 0.976 | 0.952 | 1.000 | 20 | 1 | 0 |

Strict `model_preserving_canonical` remains diagnostic only for this route:
F1 `0.141`, precision `0.154`, recall `0.130`.

## Interpretation

The per-family split helped Investigation and kept evidence/call hygiene clean,
but it did not improve over the Phase 3 dev25 gate and did not approach the
`>0.900` clinical-recovery target. Adding the larger worked-example set reduced
overall F1 and SeizureFrequency F1.

The remaining gap is still localized to Diagnosis and SeizureFrequency. On the
best Phase 4 gate, those families were `0.698` and `0.690`, respectively, while
Prescription and Investigations were substantially stronger. Because neither
Phase 4 variant beat the Phase 3 dev25 gate, no dev140 promotion was run.

## Phase 4 Closeout

Phase 4 is closed as a fallback plateau:

- the attribution-clean per-family route exists and is tested;
- dev25 compact and full-example gates had zero call failures and zero
  parse/schema failures;
- evidence validity stayed near the Phase 3 level;
- neither fallback variant cleared the dev25 promotion gate or approached
  `>0.900`;
- no winning configuration exists for Phase 5 DeepSeek/Qwen rollout.

The Satellite 13 finding is now conservative: direct de-duplicated
clinical-fact LLM-only prompting, including single-prompt and per-family
fallbacks, plateaus well below the v08 hybrid clinical-recovery control, with
the persistent gap concentrated in Diagnosis and SeizureFrequency.
