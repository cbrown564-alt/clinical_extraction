# ExECTv2 Qwen LLM-Only Generation-Selection

- JSONL: `experiments\exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_per_family_phase4_decision_table_sf_inv_dev140_gpt41mini_20260624.jsonl`
- Prompt version: `exectv2_llm_only_key_entities_generation_selection_v0.5`
- Prompt profile: `decision_table_sf_inv`
- Call strategy: `single_call_dedup_facts_per_family`
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
- Mentions raw final: 751
- Mentions scored: 728
- Evidence-invalid dropped: 23
- Evidence validity rate: 0.9694

## Protocol Surfaces

| Surface | P | R | F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| model_preserving_canonical | 0.148 | 0.116 | 0.130 | 108 | 620 | 826 |
| hybrid_full_stack | diagnostic-only/not-run |  |  |  |  |  |

## Overall Scores

### benchmark

- per-item: P=0.148 R=0.116 F1=0.130 (TP=108 FP=620 FN=826)
- per-letter: P=0.743 R=0.193 F1=0.306 (TP=81 FP=28 FN=339)

### semantic

- per-item: P=0.161 R=0.125 F1=0.141 (TP=117 FP=611 FN=817)
- per-letter: P=0.752 R=0.202 F1=0.319 (TP=85 FP=28 FN=335)

### phrase_only

- per-item: P=0.508 R=0.396 F1=0.445 (TP=370 FP=358 FN=564)
- per-letter: P=0.902 R=0.617 F1=0.733 (TP=259 FP=28 FN=161)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.729 P=0.753 R=0.707

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.851 | 0.858 | 0.845 | 163 | 27 | 30 |
| Diagnosis | 0.80 | 0.681 | 0.711 | 0.653 | 194 | 65 | 103 |
| SeizureFrequency | 0.80 | 0.556 | 0.546 | 0.566 | 95 | 79 | 73 |
| Investigations | 0.80 | 0.883 | 0.982 | 0.801 | 109 | 2 | 27 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.721 | 599 | 129 | 335 | 0.392 (235/599) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.863 | 173 | 0.751 (130/173) |
| Diagnosis | 0.580 | 185 | 0.000 (0/185) |
| SeizureFrequency | 0.697 | 131 | 0.008 (1/131) |
| Investigations | 0.891 | 110 | 0.946 (104/110) |