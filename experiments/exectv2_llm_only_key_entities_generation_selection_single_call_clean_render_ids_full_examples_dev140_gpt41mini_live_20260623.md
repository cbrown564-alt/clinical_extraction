# ExECTv2 Qwen LLM-Only Generation-Selection

- JSONL: `experiments\exectv2_llm_only_key_entities_generation_selection_single_call_clean_render_ids_full_examples_dev140_gpt41mini_live_20260623.jsonl`
- Prompt version: `exectv2_llm_only_key_entities_generation_selection_v0.1`
- Prompt profile: `full_examples`
- Call strategy: `single_call_clean_render_ids`
- Pipeline family: `exectv2_llm_only_key_entities_generation_selection`
- Component owner: `qwen_llm_only_generation_selection`
- Fact origin: `target_model_generated`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
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
- Mentions raw final: 941
- Mentions scored: 904
- Evidence-invalid dropped: 37
- Evidence validity rate: 0.9607

## Protocol Surfaces

| Surface | P | R | F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| model_preserving_canonical | 0.340 | 0.329 | 0.334 | 307 | 597 | 627 |
| hybrid_full_stack | diagnostic-only/not-run |  |  |  |  |  |

## Overall Scores

### benchmark

- per-item: P=0.340 R=0.329 F1=0.334 (TP=307 FP=597 FN=627)
- per-letter: P=0.821 R=0.512 F1=0.630 (TP=215 FP=47 FN=205)

### semantic

- per-item: P=0.359 R=0.348 F1=0.354 (TP=325 FP=579 FN=609)
- per-letter: P=0.827 R=0.536 F1=0.650 (TP=225 FP=47 FN=195)

### phrase_only

- per-item: P=0.455 R=0.440 F1=0.447 (TP=411 FP=493 FN=523)
- per-letter: P=0.854 R=0.655 F1=0.741 (TP=275 FP=47 FN=145)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.846 | 0.838 | 0.855 | 165 | 32 | 28 |
| Diagnosis | 0.80 | 0.580 | 0.571 | 0.590 | 183 | 137 | 127 |
| SeizureFrequency | 0.80 | 0.551 | 0.537 | 0.566 | 95 | 82 | 73 |
| Investigations | 0.80 | 0.863 | 0.924 | 0.809 | 110 | 9 | 26 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.712 | 654 | 250 | 280 | 0.717 (469/654) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.772 | 181 | 0.718 (130/181) |
| Diagnosis | 0.636 | 235 | 0.838 (197/235) |
| SeizureFrequency | 0.668 | 126 | 0.318 (40/126) |
| Investigations | 0.885 | 112 | 0.911 (102/112) |