# ExECTv2 Qwen LLM-Only Generation-Selection

CHECKPOINT ONLY: processed 25 / 25 letters

- JSONL: `experiments\exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_phase3_v02_dev25_gpt41mini_20260623.jsonl`
- Prompt version: `exectv2_llm_only_key_entities_generation_selection_v0.2`
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
- Mentions raw final: 157
- Mentions scored: 148
- Evidence-invalid dropped: 9
- Evidence validity rate: 0.9427

## Protocol Surfaces

| Surface | P | R | F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| model_preserving_canonical | 0.155 | 0.158 | 0.157 | 23 | 125 | 123 |
| hybrid_full_stack | diagnostic-only/not-run |  |  |  |  |  |

## Overall Scores

### benchmark

- per-item: P=0.155 R=0.158 F1=0.157 (TP=23 FP=125 FN=123)
- per-letter: P=0.607 R=0.239 F1=0.343 (TP=17 FP=11 FN=54)

### semantic

- per-item: P=0.155 R=0.158 F1=0.157 (TP=23 FP=125 FN=123)
- per-letter: P=0.607 R=0.239 F1=0.343 (TP=17 FP=11 FN=54)

### phrase_only

- per-item: P=0.453 R=0.459 F1=0.456 (TP=67 FP=81 FN=79)
- per-letter: P=0.807 R=0.648 F1=0.719 (TP=46 FP=11 FN=25)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.772 P=0.733 R=0.816

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.933 | 0.946 | 0.921 | 35 | 2 | 3 |
| Diagnosis | 0.80 | 0.691 | 0.636 | 0.756 | 31 | 16 | 10 |
| SeizureFrequency | 0.80 | 0.607 | 0.567 | 0.654 | 17 | 13 | 9 |
| Investigations | 0.80 | 0.864 | 0.792 | 0.950 | 19 | 5 | 1 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.728 | 107 | 41 | 39 | 0.458 (49/107) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.878 | 36 | 0.833 (30/36) |
| Diagnosis | 0.547 | 29 | 0.000 (0/29) |
| SeizureFrequency | 0.710 | 22 | 0.045 (1/22) |
| Investigations | 0.909 | 20 | 0.900 (18/20) |