# ExECTv2 Qwen LLM-Only Generation-Selection

- JSONL: `experiments\exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_per_family_phase6_seq_decision_table_sf_inv_dev140_qwen36_side11435_20260624.jsonl`
- Prompt version: `exectv2_llm_only_key_entities_generation_selection_v0.5`
- Prompt profile: `decision_table_sf_inv`
- Call strategy: `single_call_dedup_facts_per_family`
- Pipeline family: `exectv2_llm_only_key_entities_generation_selection`
- Component owner: `qwen_llm_only_generation_selection`
- Fact origin: `target_model_generated`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
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
- Mentions raw final: 842
- Mentions scored: 793
- Evidence-invalid dropped: 49
- Evidence validity rate: 0.9418

## Protocol Surfaces

| Surface | P | R | F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| model_preserving_canonical | 0.139 | 0.118 | 0.127 | 110 | 683 | 824 |
| hybrid_full_stack | diagnostic-only/not-run |  |  |  |  |  |

## Overall Scores

### benchmark

- per-item: P=0.139 R=0.118 F1=0.127 (TP=110 FP=683 FN=824)
- per-letter: P=0.606 R=0.191 F1=0.290 (TP=80 FP=52 FN=340)

### semantic

- per-item: P=0.150 R=0.127 F1=0.138 (TP=119 FP=674 FN=815)
- per-letter: P=0.618 R=0.200 F1=0.302 (TP=84 FP=52 FN=336)

### phrase_only

- per-item: P=0.487 R=0.413 F1=0.447 (TP=386 FP=407 FN=548)
- per-letter: P=0.837 R=0.636 F1=0.723 (TP=267 FP=52 FN=153)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.694 P=0.680 R=0.708

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.795 | 0.759 | 0.834 | 161 | 51 | 32 |
| Diagnosis | 0.80 | 0.633 | 0.609 | 0.660 | 196 | 101 | 101 |
| SeizureFrequency | 0.80 | 0.562 | 0.548 | 0.577 | 97 | 80 | 71 |
| Investigations | 0.80 | 0.837 | 0.885 | 0.794 | 108 | 14 | 28 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.705 | 609 | 184 | 325 | 0.378 (230/609) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.835 | 177 | 0.712 (126/177) |
| Diagnosis | 0.580 | 195 | 0.000 (0/195) |
| SeizureFrequency | 0.681 | 127 | 0.008 (1/127) |
| Investigations | 0.853 | 110 | 0.936 (103/110) |