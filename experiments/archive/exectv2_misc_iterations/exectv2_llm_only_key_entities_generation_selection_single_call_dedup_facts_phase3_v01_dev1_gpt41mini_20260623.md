# ExECTv2 Qwen LLM-Only Generation-Selection

- JSONL: `experiments\exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_phase3_v01_dev1_gpt41mini_20260623.jsonl`
- Prompt version: `exectv2_llm_only_key_entities_generation_selection_v0.1`
- Prompt profile: `compact`
- Call strategy: `single_call_dedup_facts`
- Pipeline family: `exectv2_llm_only_key_entities_generation_selection`
- Component owner: `qwen_llm_only_generation_selection`
- Fact origin: `target_model_generated`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 1
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
- Mentions raw final: 6
- Mentions scored: 6
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Protocol Surfaces

| Surface | P | R | F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| model_preserving_canonical | 0.167 | 0.100 | 0.125 | 1 | 5 | 9 |
| hybrid_full_stack | diagnostic-only/not-run |  |  |  |  |  |

## Overall Scores

### benchmark

- per-item: P=0.167 R=0.100 F1=0.125 (TP=1 FP=5 FN=9)
- per-letter: P=1.000 R=0.250 F1=0.400 (TP=1 FP=0 FN=3)

### semantic

- per-item: P=0.167 R=0.100 F1=0.125 (TP=1 FP=5 FN=9)
- per-letter: P=1.000 R=0.250 F1=0.400 (TP=1 FP=0 FN=3)

### phrase_only

- per-item: P=0.500 R=0.300 F1=0.375 (TP=3 FP=3 FN=7)
- per-letter: P=1.000 R=0.500 F1=0.667 (TP=2 FP=0 FN=2)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.854 P=0.833 R=0.875

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 1.000 | 1.000 | 1.000 | 2 | 0 | 0 |
| Diagnosis | 0.80 | 0.000 | 0.000 | 0.667 | 2 | 1 | 1 |
| SeizureFrequency | 0.80 | 1.000 | 1.000 | 1.000 | 2 | 0 | 0 |
| Investigations | 0.80 | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.750 | 6 | 0 | 4 | 0.500 (3/6) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 1.000 | 2 | 1.000 (2/2) |
| Diagnosis | 0.333 | 1 | 0.000 (0/1) |
| SeizureFrequency | 1.000 | 2 | 0.000 (0/2) |
| Investigations | 1.000 | 1 | 1.000 (1/1) |