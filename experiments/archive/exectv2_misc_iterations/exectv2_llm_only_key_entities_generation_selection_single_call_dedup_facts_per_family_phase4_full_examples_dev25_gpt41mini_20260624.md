# ExECTv2 Qwen LLM-Only Generation-Selection

- JSONL: `experiments\exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_per_family_phase4_full_examples_dev25_gpt41mini_20260624.jsonl`
- Prompt version: `exectv2_llm_only_key_entities_generation_selection_v0.5`
- Prompt profile: `full_examples`
- Call strategy: `single_call_dedup_facts_per_family`
- Pipeline family: `exectv2_llm_only_key_entities_generation_selection`
- Component owner: `qwen_llm_only_generation_selection`
- Fact origin: `target_model_generated`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25
- Pool letters: not-used
- Pool mentions total: not-used

## Model-Call And Gate Summary

- Generation call failures: 0
- Selection call failures: 0
- Inventory call failures: 0
- Generation parse/schema failures: 0
- Selection parse/schema failures: 0
- Inventory parse/schema failures: 0
- Clinical events generation: 0
- Clinical events final: 0
- Mentions raw final: 137
- Mentions scored: 131
- Evidence-invalid dropped: 6
- Evidence validity rate: 0.9562

## Protocol Surfaces

| Surface | P | R | F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| model_preserving_canonical | 0.183 | 0.164 | 0.173 | 24 | 107 | 122 |
| hybrid_full_stack | diagnostic-only/not-run |  |  |  |  |  |

## Overall Scores

### benchmark

- per-item: P=0.183 R=0.164 F1=0.173 (TP=24 FP=107 FN=122)
- per-letter: P=0.720 R=0.254 F1=0.375 (TP=18 FP=7 FN=53)

### semantic

- per-item: P=0.183 R=0.164 F1=0.173 (TP=24 FP=107 FN=122)
- per-letter: P=0.720 R=0.254 F1=0.375 (TP=18 FP=7 FN=53)

### phrase_only

- per-item: P=0.496 R=0.445 F1=0.469 (TP=65 FP=66 FN=81)
- per-letter: P=0.870 R=0.662 F1=0.752 (TP=47 FP=7 FN=24)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.782 P=0.758 R=0.808

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.900 | 0.857 | 0.947 | 36 | 6 | 2 |
| Diagnosis | 0.80 | 0.701 | 0.694 | 0.707 | 29 | 11 | 12 |
| SeizureFrequency | 0.80 | 0.593 | 0.571 | 0.615 | 16 | 12 | 10 |
| Investigations | 0.80 | 0.952 | 0.909 | 1.000 | 20 | 2 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.765 | 106 | 25 | 40 | 0.481 (51/106) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.914 | 37 | 0.838 (31/37) |
| Diagnosis | 0.617 | 29 | 0.000 (0/29) |
| SeizureFrequency | 0.667 | 20 | 0.050 (1/20) |
| Investigations | 0.952 | 20 | 0.950 (19/20) |