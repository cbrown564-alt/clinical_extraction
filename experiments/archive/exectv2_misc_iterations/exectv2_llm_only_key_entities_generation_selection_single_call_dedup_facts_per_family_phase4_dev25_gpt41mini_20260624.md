# ExECTv2 Qwen LLM-Only Generation-Selection

- JSONL: `experiments\exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_per_family_phase4_dev25_gpt41mini_20260624.jsonl`
- Prompt version: `exectv2_llm_only_key_entities_generation_selection_v0.5`
- Prompt profile: `compact`
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
- Mentions raw final: 128
- Mentions scored: 123
- Evidence-invalid dropped: 5
- Evidence validity rate: 0.9609

## Protocol Surfaces

| Surface | P | R | F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| model_preserving_canonical | 0.154 | 0.130 | 0.141 | 19 | 104 | 127 |
| hybrid_full_stack | diagnostic-only/not-run |  |  |  |  |  |

## Overall Scores

### benchmark

- per-item: P=0.154 R=0.130 F1=0.141 (TP=19 FP=104 FN=127)
- per-letter: P=0.667 R=0.225 F1=0.337 (TP=16 FP=8 FN=55)

### semantic

- per-item: P=0.154 R=0.130 F1=0.141 (TP=19 FP=104 FN=127)
- per-letter: P=0.667 R=0.225 F1=0.337 (TP=16 FP=8 FN=55)

### phrase_only

- per-item: P=0.480 R=0.404 F1=0.439 (TP=59 FP=64 FN=87)
- per-letter: P=0.843 R=0.606 F1=0.705 (TP=43 FP=8 FN=28)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.796 P=0.784 R=0.808

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.873 | 0.939 | 0.816 | 31 | 2 | 7 |
| Diagnosis | 0.80 | 0.698 | 0.667 | 0.732 | 30 | 10 | 11 |
| SeizureFrequency | 0.80 | 0.690 | 0.625 | 0.769 | 20 | 12 | 6 |
| Investigations | 0.80 | 0.976 | 0.952 | 1.000 | 20 | 1 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.714 | 96 | 27 | 50 | 0.469 (45/96) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.789 | 30 | 0.833 (25/30) |
| Diagnosis | 0.523 | 23 | 0.000 (0/23) |
| SeizureFrequency | 0.719 | 23 | 0.043 (1/23) |
| Investigations | 0.976 | 20 | 0.950 (19/20) |