# ExECTv2 Qwen LLM-Only Generation-Selection

- JSONL: `experiments\exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_replay_clean_render_ids_dev140_qwen36_20260623.jsonl`
- Prompt version: `exectv2_llm_only_key_entities_generation_selection_v0.1`
- Prompt profile: `replay`
- Call strategy: `single_call_dedup_facts`
- Pipeline family: `exectv2_llm_only_key_entities_generation_selection`
- Component owner: `qwen_llm_only_generation_selection`
- Fact origin: `target_model_generated`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b/no-call-clean-render-replay`
- Mode: `replay`
- Letters: 140
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
- Mentions raw final: 867
- Mentions scored: 867
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Protocol Surfaces

| Surface | P | R | F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| model_preserving_canonical | 0.352 | 0.327 | 0.339 | 305 | 562 | 629 |
| hybrid_full_stack | diagnostic-only/not-run |  |  |  |  |  |

## Overall Scores

### benchmark

- per-item: P=0.352 R=0.327 F1=0.339 (TP=305 FP=562 FN=629)
- per-letter: P=0.813 R=0.498 F1=0.617 (TP=209 FP=48 FN=211)

### semantic

- per-item: P=0.375 R=0.348 F1=0.361 (TP=325 FP=542 FN=609)
- per-letter: P=0.821 R=0.524 F1=0.639 (TP=220 FP=48 FN=200)

### phrase_only

- per-item: P=0.464 R=0.430 F1=0.446 (TP=402 FP=465 FN=532)
- per-letter: P=0.846 R=0.626 F1=0.720 (TP=263 FP=48 FN=157)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.722 P=0.704 R=0.741

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.839 | 0.784 | 0.902 | 174 | 48 | 19 |
| Diagnosis | 0.80 | 0.673 | 0.647 | 0.700 | 208 | 102 | 89 |
| SeizureFrequency | 0.80 | 0.512 | 0.506 | 0.518 | 87 | 85 | 81 |
| Investigations | 0.80 | 0.919 | 0.968 | 0.875 | 119 | 4 | 17 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.716 | 645 | 222 | 289 | 0.730 (471/645) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.715 | 162 | 0.741 (120/162) |
| Diagnosis | 0.657 | 236 | 0.869 (205/236) |
| SeizureFrequency | 0.690 | 128 | 0.242 (31/128) |
| Investigations | 0.919 | 119 | 0.966 (115/119) |