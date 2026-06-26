# ExECTv2 Qwen LLM-Only Generation-Selection

- JSONL: `experiments\exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_phase3_v05_dev140_gpt41mini_20260623.jsonl`
- Prompt version: `exectv2_llm_only_key_entities_generation_selection_v0.5`
- Prompt profile: `compact`
- Call strategy: `single_call_dedup_facts`
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
- Mentions raw final: 878
- Mentions scored: 844
- Evidence-invalid dropped: 34
- Evidence validity rate: 0.9613

## Protocol Surfaces

| Surface | P | R | F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| model_preserving_canonical | 0.133 | 0.120 | 0.126 | 112 | 732 | 822 |
| hybrid_full_stack | diagnostic-only/not-run |  |  |  |  |  |

## Overall Scores

### benchmark

- per-item: P=0.133 R=0.120 F1=0.126 (TP=112 FP=732 FN=822)
- per-letter: P=0.572 R=0.198 F1=0.294 (TP=83 FP=62 FN=337)

### semantic

- per-item: P=0.142 R=0.129 F1=0.135 (TP=120 FP=724 FN=814)
- per-letter: P=0.581 R=0.205 F1=0.303 (TP=86 FP=62 FN=334)

### phrase_only

- per-item: P=0.488 R=0.441 F1=0.463 (TP=412 FP=432 FN=522)
- per-letter: P=0.817 R=0.657 F1=0.728 (TP=276 FP=62 FN=144)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.710 P=0.691 R=0.729

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.814 | 0.764 | 0.871 | 168 | 52 | 25 |
| Diagnosis | 0.80 | 0.672 | 0.663 | 0.680 | 202 | 98 | 95 |
| SeizureFrequency | 0.80 | 0.558 | 0.535 | 0.583 | 98 | 85 | 70 |
| Investigations | 0.80 | 0.832 | 0.847 | 0.816 | 111 | 20 | 25 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.735 | 653 | 191 | 281 | 0.374 (244/653) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.876 | 190 | 0.716 (136/190) |
| Diagnosis | 0.638 | 223 | 0.000 (0/223) |
| SeizureFrequency | 0.667 | 126 | 0.008 (1/126) |
| Investigations | 0.854 | 114 | 0.939 (107/114) |