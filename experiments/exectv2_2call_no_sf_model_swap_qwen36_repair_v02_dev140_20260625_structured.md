# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_2call_no_sf_model_swap_qwen36_repair_v02_dev140_20260625_structured.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24_qwen_compact`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev140`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 817
- Mentions raw: 827
- Mentions scored: 824
- Evidence-invalid dropped: 3
- Evidence validity rate: 0.9964

## Overall Scores

### semantic

- per-item: P=0.392 R=0.350 F1=0.370 (TP=323 FP=501 FN=599)
- per-letter: P=0.827 R=0.548 F1=0.659 (TP=230 FP=48 FN=190)

### benchmark

- per-item: P=0.373 R=0.333 F1=0.352 (TP=307 FP=517 FN=615)
- per-letter: P=0.822 R=0.529 F1=0.643 (TP=222 FP=48 FN=198)

### phrase_only

- per-item: P=0.519 R=0.464 F1=0.490 (TP=428 FP=396 FN=494)
- per-letter: P=0.859 R=0.698 F1=0.770 (TP=293 FP=48 FN=127)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.758 P=0.732 R=0.787

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.878 | 0.815 | 0.951 | 176 | 40 | 9 |
| Diagnosis | 0.80 | 0.728 | 0.716 | 0.740 | 213 | 77 | 75 |
| SeizureFrequency | 0.80 | 0.593 | 0.566 | 0.622 | 107 | 82 | 65 |
| Investigations | 0.80 | 0.875 | 0.872 | 0.879 | 109 | 16 | 15 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.748 | 653 | 171 | 269 | 0.715 (467/653) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.822 | 180 | 0.789 (142/180) |
| Diagnosis | 0.671 | 230 | 0.891 (205/230) |
| SeizureFrequency | 0.693 | 134 | 0.187 (25/134) |
| Investigations | 0.924 | 109 | 0.872 (95/109) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.260 | 0.517 |
| Diagnosis | 0.80 | 0.85 | 0.502 | 0.914 |
| SeizureFrequency | 0.80 | 0.66 | 0.129 | 0.295 |
| Investigations | 0.80 | 0.95 | 0.585 | 0.785 |