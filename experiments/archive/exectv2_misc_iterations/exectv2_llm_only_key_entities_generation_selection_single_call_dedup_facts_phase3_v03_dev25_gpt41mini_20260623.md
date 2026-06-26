# ExECTv2 Qwen LLM-Only Generation-Selection

- JSONL: `experiments\exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_phase3_v03_dev25_gpt41mini_20260623.jsonl`
- Prompt version: `exectv2_llm_only_key_entities_generation_selection_v0.3`
- Prompt profile: `compact`
- Call strategy: `single_call_dedup_facts`
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
- Mentions scored: 135
- Evidence-invalid dropped: 2
- Evidence validity rate: 0.9854

## Protocol Surfaces

| Surface | P | R | F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| model_preserving_canonical | 0.156 | 0.144 | 0.149 | 21 | 114 | 125 |
| hybrid_full_stack | diagnostic-only/not-run |  |  |  |  |  |

## Overall Scores

### benchmark

- per-item: P=0.156 R=0.144 F1=0.149 (TP=21 FP=114 FN=125)
- per-letter: P=0.630 R=0.239 F1=0.347 (TP=17 FP=10 FN=54)

### semantic

- per-item: P=0.156 R=0.144 F1=0.149 (TP=21 FP=114 FN=125)
- per-letter: P=0.630 R=0.239 F1=0.347 (TP=17 FP=10 FN=54)

### phrase_only

- per-item: P=0.489 R=0.452 F1=0.470 (TP=66 FP=69 FN=80)
- per-letter: P=0.821 R=0.648 F1=0.724 (TP=46 FP=10 FN=25)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.792 P=0.763 R=0.824

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.933 | 0.946 | 0.921 | 35 | 2 | 3 |
| Diagnosis | 0.80 | 0.724 | 0.674 | 0.780 | 32 | 14 | 9 |
| SeizureFrequency | 0.80 | 0.593 | 0.571 | 0.615 | 16 | 12 | 10 |
| Investigations | 0.80 | 0.930 | 0.870 | 1.000 | 20 | 3 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.762 | 107 | 28 | 39 | 0.458 (49/107) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.921 | 35 | 0.829 (29/35) |
| Diagnosis | 0.614 | 31 | 0.000 (0/31) |
| SeizureFrequency | 0.689 | 21 | 0.048 (1/21) |
| Investigations | 0.930 | 20 | 0.950 (19/20) |