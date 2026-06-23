# ExECTv2 Qwen LLM-Only Generation-Selection

- JSONL: `experiments\exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_phase3_v05_dev25_gpt41mini_20260623.jsonl`
- Prompt version: `exectv2_llm_only_key_entities_generation_selection_v0.5`
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
- Mentions raw final: 150
- Mentions scored: 144
- Evidence-invalid dropped: 6
- Evidence validity rate: 0.9600

## Protocol Surfaces

| Surface | P | R | F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| model_preserving_canonical | 0.160 | 0.158 | 0.159 | 23 | 121 | 123 |
| hybrid_full_stack | diagnostic-only/not-run |  |  |  |  |  |

## Overall Scores

### benchmark

- per-item: P=0.160 R=0.158 F1=0.159 (TP=23 FP=121 FN=123)
- per-letter: P=0.567 R=0.239 F1=0.337 (TP=17 FP=13 FN=54)

### semantic

- per-item: P=0.160 R=0.158 F1=0.159 (TP=23 FP=121 FN=123)
- per-letter: P=0.567 R=0.239 F1=0.337 (TP=17 FP=13 FN=54)

### phrase_only

- per-item: P=0.472 R=0.466 F1=0.469 (TP=68 FP=76 FN=78)
- per-letter: P=0.780 R=0.648 F1=0.708 (TP=46 FP=13 FN=25)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.800 P=0.752 R=0.856

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.949 | 0.925 | 0.974 | 37 | 3 | 1 |
| Diagnosis | 0.80 | 0.710 | 0.651 | 0.780 | 32 | 15 | 9 |
| SeizureFrequency | 0.80 | 0.643 | 0.600 | 0.692 | 18 | 12 | 8 |
| Investigations | 0.80 | 0.909 | 0.833 | 1.000 | 20 | 4 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.759 | 110 | 34 | 36 | 0.464 (51/110) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.916 | 38 | 0.816 (31/38) |
| Diagnosis | 0.614 | 31 | 0.000 (0/31) |
| SeizureFrequency | 0.677 | 21 | 0.048 (1/21) |
| Investigations | 0.909 | 20 | 0.950 (19/20) |