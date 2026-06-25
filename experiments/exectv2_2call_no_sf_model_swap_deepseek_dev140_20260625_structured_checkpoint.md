# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 140 / 140 letters

- JSONL: `experiments\exectv2_2call_no_sf_model_swap_deepseek_dev140_20260625_structured.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev140`
- Model: `deepseek/deepseek-chat`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 901
- Mentions raw: 912
- Mentions scored: 897
- Evidence-invalid dropped: 15
- Evidence validity rate: 0.9836

## Overall Scores

### semantic

- per-item: P=0.476 R=0.463 F1=0.469 (TP=427 FP=470 FN=495)
- per-letter: P=0.879 R=0.640 F1=0.741 (TP=269 FP=37 FN=151)

### benchmark

- per-item: P=0.458 R=0.446 F1=0.452 (TP=411 FP=486 FN=511)
- per-letter: P=0.877 R=0.629 F1=0.732 (TP=264 FP=37 FN=156)

### phrase_only

- per-item: P=0.576 R=0.561 F1=0.568 (TP=517 FP=380 FN=405)
- per-letter: P=0.896 R=0.759 F1=0.822 (TP=319 FP=37 FN=101)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.781 P=0.756 R=0.809

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.868 | 0.806 | 0.941 | 174 | 42 | 11 |
| Diagnosis | 0.80 | 0.750 | 0.734 | 0.767 | 221 | 78 | 67 |
| SeizureFrequency | 0.80 | 0.665 | 0.621 | 0.715 | 123 | 75 | 49 |
| Investigations | 0.80 | 0.897 | 0.963 | 0.839 | 104 | 4 | 20 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.789 | 718 | 179 | 204 | 0.776 (557/718) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.830 | 185 | 0.768 (142/185) |
| Diagnosis | 0.760 | 282 | 0.886 (250/282) |
| SeizureFrequency | 0.732 | 146 | 0.431 (63/146) |
| Investigations | 0.905 | 105 | 0.971 (102/105) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.278 | 0.568 |
| Diagnosis | 0.80 | 0.85 | 0.625 | 0.944 |
| SeizureFrequency | 0.80 | 0.66 | 0.306 | 0.563 |
| Investigations | 0.80 | 0.95 | 0.621 | 0.812 |