# ExECTv2 Qwen LLM-Only Generation-Selection

- JSONL: `experiments\exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_per_family_phase4_decision_table_sf_inv_dev25_gpt41mini_20260624.jsonl`
- Prompt version: `exectv2_llm_only_key_entities_generation_selection_v0.5`
- Prompt profile: `decision_table_sf_inv`
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
- Mentions raw final: 133
- Mentions scored: 128
- Evidence-invalid dropped: 5
- Evidence validity rate: 0.9624

## Protocol Surfaces

| Surface | P | R | F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| model_preserving_canonical | 0.188 | 0.164 | 0.175 | 24 | 104 | 122 |
| hybrid_full_stack | diagnostic-only/not-run |  |  |  |  |  |

## Overall Scores

### benchmark

- per-item: P=0.188 R=0.164 F1=0.175 (TP=24 FP=104 FN=122)
- per-letter: P=0.857 R=0.254 F1=0.391 (TP=18 FP=3 FN=53)

### semantic

- per-item: P=0.188 R=0.164 F1=0.175 (TP=24 FP=104 FN=122)
- per-letter: P=0.857 R=0.254 F1=0.391 (TP=18 FP=3 FN=53)

### phrase_only

- per-item: P=0.516 R=0.452 F1=0.482 (TP=66 FP=62 FN=80)
- per-letter: P=0.938 R=0.634 F1=0.756 (TP=45 FP=3 FN=26)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.828 P=0.808 R=0.848

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.938 | 0.884 | 1.000 | 38 | 5 | 0 |
| Diagnosis | 0.80 | 0.686 | 0.667 | 0.707 | 29 | 10 | 12 |
| SeizureFrequency | 0.80 | 0.717 | 0.704 | 0.731 | 19 | 8 | 7 |
| Investigations | 0.80 | 1.000 | 1.000 | 1.000 | 20 | 0 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.774 | 106 | 22 | 40 | 0.491 (52/106) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.884 | 38 | 0.842 (32/38) |
| Diagnosis | 0.523 | 23 | 0.000 (0/23) |
| SeizureFrequency | 0.833 | 25 | 0.040 (1/25) |
| Investigations | 1.000 | 20 | 0.950 (19/20) |