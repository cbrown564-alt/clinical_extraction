# ExECTv2 Qwen LLM-Only Generation-Selection

- JSONL: `experiments\exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_phase3_v04_dev25_gpt41mini_20260623.jsonl`
- Prompt version: `exectv2_llm_only_key_entities_generation_selection_v0.4`
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
- Mentions raw final: 148
- Mentions scored: 139
- Evidence-invalid dropped: 9
- Evidence validity rate: 0.9392

## Protocol Surfaces

| Surface | P | R | F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| model_preserving_canonical | 0.151 | 0.144 | 0.147 | 21 | 118 | 125 |
| hybrid_full_stack | diagnostic-only/not-run |  |  |  |  |  |

## Overall Scores

### benchmark

- per-item: P=0.151 R=0.144 F1=0.147 (TP=21 FP=118 FN=125)
- per-letter: P=0.607 R=0.239 F1=0.343 (TP=17 FP=11 FN=54)

### semantic

- per-item: P=0.151 R=0.144 F1=0.147 (TP=21 FP=118 FN=125)
- per-letter: P=0.607 R=0.239 F1=0.343 (TP=17 FP=11 FN=54)

### phrase_only

- per-item: P=0.482 R=0.459 F1=0.470 (TP=67 FP=72 FN=79)
- per-letter: P=0.817 R=0.690 F1=0.748 (TP=49 FP=11 FN=22)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.798 P=0.767 R=0.832

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.933 | 0.946 | 0.921 | 35 | 2 | 3 |
| Diagnosis | 0.80 | 0.742 | 0.689 | 0.805 | 33 | 14 | 8 |
| SeizureFrequency | 0.80 | 0.654 | 0.621 | 0.692 | 18 | 11 | 8 |
| Investigations | 0.80 | 0.857 | 0.818 | 0.900 | 18 | 4 | 2 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.751 | 107 | 32 | 39 | 0.439 (47/107) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.875 | 35 | 0.829 (29/35) |
| Diagnosis | 0.627 | 32 | 0.000 (0/32) |
| SeizureFrequency | 0.689 | 21 | 0.048 (1/21) |
| Investigations | 0.905 | 19 | 0.895 (17/19) |