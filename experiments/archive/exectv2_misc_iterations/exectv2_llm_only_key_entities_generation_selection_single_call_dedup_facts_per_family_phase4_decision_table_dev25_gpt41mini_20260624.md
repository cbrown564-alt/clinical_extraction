# ExECTv2 Qwen LLM-Only Generation-Selection

- JSONL: `experiments\exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_per_family_phase4_decision_table_dev25_gpt41mini_20260624.jsonl`
- Prompt version: `exectv2_llm_only_key_entities_generation_selection_v0.5`
- Prompt profile: `decision_table`
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
- Mentions raw final: 121
- Mentions scored: 116
- Evidence-invalid dropped: 5
- Evidence validity rate: 0.9587

## Protocol Surfaces

| Surface | P | R | F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| model_preserving_canonical | 0.172 | 0.137 | 0.153 | 20 | 96 | 126 |
| hybrid_full_stack | diagnostic-only/not-run |  |  |  |  |  |

## Overall Scores

### benchmark

- per-item: P=0.172 R=0.137 F1=0.153 (TP=20 FP=96 FN=126)
- per-letter: P=0.889 R=0.225 F1=0.360 (TP=16 FP=2 FN=55)

### semantic

- per-item: P=0.172 R=0.137 F1=0.153 (TP=20 FP=96 FN=126)
- per-letter: P=0.889 R=0.225 F1=0.360 (TP=16 FP=2 FN=55)

### phrase_only

- per-item: P=0.569 R=0.452 F1=0.504 (TP=66 FP=50 FN=80)
- per-letter: P=0.957 R=0.620 F1=0.752 (TP=44 FP=2 FN=27)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.785 P=0.812 R=0.760

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.849 | 1.000 | 0.737 | 28 | 0 | 10 |
| Diagnosis | 0.80 | 0.665 | 0.649 | 0.683 | 28 | 13 | 13 |
| SeizureFrequency | 0.80 | 0.717 | 0.704 | 0.731 | 19 | 8 | 7 |
| Investigations | 0.80 | 1.000 | 1.000 | 1.000 | 20 | 0 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.771 | 101 | 15 | 45 | 0.436 (44/101) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.806 | 27 | 0.889 (24/27) |
| Diagnosis | 0.611 | 29 | 0.000 (0/29) |
| SeizureFrequency | 0.833 | 25 | 0.040 (1/25) |
| Investigations | 1.000 | 20 | 0.950 (19/20) |