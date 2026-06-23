# ExECTv2 Qwen LLM-Only Generation-Selection

CHECKPOINT ONLY: processed 25 / 25 letters

- JSONL: `experiments\exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_phase3_v01_dev25_gpt41mini_20260623.jsonl`
- Prompt version: `exectv2_llm_only_key_entities_generation_selection_v0.1`
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
- Mentions raw final: 124
- Mentions scored: 122
- Evidence-invalid dropped: 2
- Evidence validity rate: 0.9839

## Protocol Surfaces

| Surface | P | R | F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| model_preserving_canonical | 0.189 | 0.158 | 0.172 | 23 | 99 | 123 |
| hybrid_full_stack | diagnostic-only/not-run |  |  |  |  |  |

## Overall Scores

### benchmark

- per-item: P=0.189 R=0.158 F1=0.172 (TP=23 FP=99 FN=123)
- per-letter: P=0.567 R=0.239 F1=0.337 (TP=17 FP=13 FN=54)

### semantic

- per-item: P=0.189 R=0.158 F1=0.172 (TP=23 FP=99 FN=123)
- per-letter: P=0.567 R=0.239 F1=0.337 (TP=17 FP=13 FN=54)

### phrase_only

- per-item: P=0.418 R=0.349 F1=0.381 (TP=51 FP=71 FN=95)
- per-letter: P=0.755 R=0.563 F1=0.645 (TP=40 FP=13 FN=31)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.743 P=0.719 R=0.768

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.974 | 0.974 | 0.974 | 37 | 1 | 1 |
| Diagnosis | 0.80 | 0.552 | 0.463 | 0.683 | 28 | 22 | 13 |
| SeizureFrequency | 0.80 | 0.588 | 0.600 | 0.577 | 15 | 10 | 11 |
| Investigations | 0.80 | 0.865 | 0.941 | 0.800 | 16 | 1 | 4 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.679 | 91 | 31 | 55 | 0.516 (47/91) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.871 | 37 | 0.838 (31/37) |
| Diagnosis | 0.467 | 21 | 0.000 (0/21) |
| SeizureFrequency | 0.607 | 17 | 0.059 (1/17) |
| Investigations | 0.865 | 16 | 0.938 (15/16) |