# ExECTv2 Qwen LLM-Only Generation-Selection

- JSONL: `experiments\exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_per_family_phase6_seq_decision_table_sf_inv_dev140_deepseek_chat_20260624.jsonl`
- Prompt version: `exectv2_llm_only_key_entities_generation_selection_v0.5`
- Prompt profile: `decision_table_sf_inv`
- Call strategy: `single_call_dedup_facts_per_family`
- Pipeline family: `exectv2_llm_only_key_entities_generation_selection`
- Component owner: `qwen_llm_only_generation_selection`
- Fact origin: `target_model_generated`
- Split: `dev`
- Model: `deepseek/deepseek-chat`
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
- Mentions raw final: 913
- Mentions scored: 878
- Evidence-invalid dropped: 35
- Evidence validity rate: 0.9617

## Protocol Surfaces

| Surface | P | R | F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| model_preserving_canonical | 0.132 | 0.124 | 0.128 | 116 | 762 | 818 |
| hybrid_full_stack | diagnostic-only/not-run |  |  |  |  |  |

## Overall Scores

### benchmark

- per-item: P=0.132 R=0.124 F1=0.128 (TP=116 FP=762 FN=818)
- per-letter: P=0.675 R=0.202 F1=0.311 (TP=85 FP=41 FN=335)

### semantic

- per-item: P=0.142 R=0.134 F1=0.138 (TP=125 FP=753 FN=809)
- per-letter: P=0.685 R=0.212 F1=0.324 (TP=89 FP=41 FN=331)

### phrase_only

- per-item: P=0.518 R=0.487 F1=0.502 (TP=455 FP=423 FN=479)
- per-letter: P=0.878 R=0.705 F1=0.782 (TP=296 FP=41 FN=124)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.745 P=0.719 R=0.772

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.788 | 0.735 | 0.850 | 164 | 59 | 29 |
| Diagnosis | 0.80 | 0.689 | 0.659 | 0.721 | 214 | 109 | 83 |
| SeizureFrequency | 0.80 | 0.674 | 0.659 | 0.691 | 116 | 60 | 52 |
| Investigations | 0.80 | 0.898 | 0.922 | 0.875 | 119 | 10 | 17 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.774 | 701 | 177 | 233 | 0.354 (248/701) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.874 | 190 | 0.700 (133/190) |
| Diagnosis | 0.680 | 251 | 0.000 (0/251) |
| SeizureFrequency | 0.722 | 135 | 0.007 (1/135) |
| Investigations | 0.943 | 125 | 0.912 (114/125) |