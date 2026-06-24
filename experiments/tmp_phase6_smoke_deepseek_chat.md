# ExECTv2 Qwen LLM-Only Generation-Selection

- JSONL: `experiments\tmp_phase6_smoke_deepseek_chat.jsonl`
- Prompt version: `exectv2_llm_only_key_entities_generation_selection_v0.5`
- Prompt profile: `decision_table_sf_inv`
- Call strategy: `single_call_dedup_facts_per_family`
- Pipeline family: `exectv2_llm_only_key_entities_generation_selection`
- Component owner: `qwen_llm_only_generation_selection`
- Fact origin: `target_model_generated`
- Split: `dev`
- Model: `deepseek/deepseek-chat`
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
- Mentions raw final: 9
- Mentions scored: 9
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Protocol Surfaces

| Surface | P | R | F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| model_preserving_canonical | 0.111 | 0.100 | 0.105 | 1 | 8 | 9 |
| hybrid_full_stack | diagnostic-only/not-run |  |  |  |  |  |

## Overall Scores

### benchmark

- per-item: P=0.111 R=0.100 F1=0.105 (TP=1 FP=8 FN=9)
- per-letter: P=1.000 R=0.250 F1=0.400 (TP=1 FP=0 FN=3)

### semantic

- per-item: P=0.111 R=0.100 F1=0.105 (TP=1 FP=8 FN=9)
- per-letter: P=1.000 R=0.250 F1=0.400 (TP=1 FP=0 FN=3)

### phrase_only

- per-item: P=0.778 R=0.700 F1=0.737 (TP=7 FP=2 FN=3)
- per-letter: P=1.000 R=0.750 F1=0.857 (TP=3 FP=0 FN=1)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=1.000 P=1.000 R=1.000

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 1.000 | 1.000 | 1.000 | 2 | 0 | 0 |
| Diagnosis | 0.80 | 1.000 | 1.000 | 1.000 | 3 | 0 | 0 |
| SeizureFrequency | 0.80 | 1.000 | 1.000 | 1.000 | 2 | 0 | 0 |
| Investigations | 0.80 | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.947 | 9 | 0 | 1 | 0.333 (3/9) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 1.000 | 2 | 1.000 (2/2) |
| Diagnosis | 0.889 | 4 | 0.000 (0/4) |
| SeizureFrequency | 1.000 | 2 | 0.000 (0/2) |
| Investigations | 1.000 | 1 | 1.000 (1/1) |