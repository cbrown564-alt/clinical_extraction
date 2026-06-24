# ExECTv2 Qwen LLM-Only Generation-Selection

- JSONL: `experiments\exectv2_llm_only_key_entities_generation_selection_single_call_dedup_facts_per_family_phase6_seq_decision_table_sf_inv_dev140_deepseek_v4_flash_20260624.jsonl`
- Prompt version: `exectv2_llm_only_key_entities_generation_selection_v0.5`
- Prompt profile: `decision_table_sf_inv`
- Call strategy: `single_call_dedup_facts_per_family`
- Pipeline family: `exectv2_llm_only_key_entities_generation_selection`
- Component owner: `qwen_llm_only_generation_selection`
- Fact origin: `target_model_generated`
- Split: `dev`
- Model: `deepseek/deepseek-v4-flash`
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
- Mentions raw final: 816
- Mentions scored: 791
- Evidence-invalid dropped: 25
- Evidence validity rate: 0.9694

## Protocol Surfaces

| Surface | P | R | F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| model_preserving_canonical | 0.152 | 0.129 | 0.139 | 120 | 671 | 814 |
| hybrid_full_stack | diagnostic-only/not-run |  |  |  |  |  |

## Overall Scores

### benchmark

- per-item: P=0.152 R=0.129 F1=0.139 (TP=120 FP=671 FN=814)
- per-letter: P=0.772 R=0.209 F1=0.330 (TP=88 FP=26 FN=332)

### semantic

- per-item: P=0.163 R=0.138 F1=0.150 (TP=129 FP=662 FN=805)
- per-letter: P=0.780 R=0.219 F1=0.342 (TP=92 FP=26 FN=328)

### phrase_only

- per-item: P=0.551 R=0.467 F1=0.505 (TP=436 FP=355 FN=498)
- per-letter: P=0.917 R=0.686 F1=0.785 (TP=288 FP=26 FN=132)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.783 P=0.786 R=0.780

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.917 | 0.913 | 0.922 | 178 | 17 | 15 |
| Diagnosis | 0.80 | 0.712 | 0.710 | 0.714 | 212 | 86 | 85 |
| SeizureFrequency | 0.80 | 0.647 | 0.651 | 0.643 | 108 | 58 | 60 |
| Investigations | 0.80 | 0.917 | 0.945 | 0.890 | 121 | 7 | 15 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.780 | 673 | 118 | 261 | 0.382 (257/673) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.923 | 185 | 0.757 (140/185) |
| Diagnosis | 0.672 | 237 | 0.000 (0/237) |
| SeizureFrequency | 0.710 | 126 | 0.008 (1/126) |
| Investigations | 0.947 | 125 | 0.928 (116/125) |