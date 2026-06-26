# ExECTv2 Qwen LLM-Only Generation-Selection

CHECKPOINT ONLY: processed 5 / 140 letters

- JSONL: `experiments\exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_per_family_phase6_seq_decision_table_sf_inv_dev140_qwen36_20260624.jsonl`
- Prompt version: `exectv2_llm_only_key_entities_generation_selection_v0.5`
- Prompt profile: `decision_table_sf_inv`
- Call strategy: `single_call_dedup_facts_per_family`
- Pipeline family: `exectv2_llm_only_key_entities_generation_selection`
- Component owner: `qwen_llm_only_generation_selection`
- Fact origin: `target_model_generated`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 5
- Pool letters: not-used
- Pool mentions total: not-used

## Model-Call And Gate Summary

- Generation call failures: 5
- Selection call failures: 5
- Inventory call failures: 5
- Generation parse/schema failures: 0
- Selection parse/schema failures: 0
- Inventory parse/schema failures: 0
- Clinical events generation: 0
- Clinical events final: 0
- Mentions raw final: 0
- Mentions scored: 0
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Protocol Surfaces

| Surface | P | R | F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| model_preserving_canonical | 0.000 | 0.000 | 0.000 | 0 | 0 | 47 |
| hybrid_full_stack | diagnostic-only/not-run |  |  |  |  |  |

## Overall Scores

### benchmark

- per-item: P=0.000 R=0.000 F1=0.000 (TP=0 FP=0 FN=47)
- per-letter: P=0.000 R=0.000 F1=0.000 (TP=0 FP=0 FN=20)

### semantic

- per-item: P=0.000 R=0.000 F1=0.000 (TP=0 FP=0 FN=47)
- per-letter: P=0.000 R=0.000 F1=0.000 (TP=0 FP=0 FN=20)

### phrase_only

- per-item: P=0.000 R=0.000 F1=0.000 (TP=0 FP=0 FN=47)
- per-letter: P=0.000 R=0.000 F1=0.000 (TP=0 FP=0 FN=20)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.000 P=0.000 R=0.000

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.000 | 0.000 | 0.000 | 0 | 0 | 9 |
| Diagnosis | 0.80 | 0.000 | 0.000 | 0.000 | 0 | 0 | 10 |
| SeizureFrequency | 0.80 | 0.000 | 0.000 | 0.000 | 0 | 0 | 8 |
| Investigations | 0.80 | 0.000 | 0.000 | 0.000 | 0 | 0 | 8 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.000 | 0 | 0 | 47 | 0.000 (0/0) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.000 | 0 | 0.000 (0/0) |
| Diagnosis | 0.000 | 0 | 0.000 (0/0) |
| SeizureFrequency | 0.000 | 0 | 0.000 (0/0) |
| Investigations | 0.000 | 0 | 0.000 (0/0) |