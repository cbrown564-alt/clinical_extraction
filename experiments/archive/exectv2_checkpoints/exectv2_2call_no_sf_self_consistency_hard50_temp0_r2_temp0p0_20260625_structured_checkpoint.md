# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 50 / 50 letters

- JSONL: `experiments\exectv2_2call_no_sf_self_consistency_hard50_temp0_r2_temp0p0_20260625_structured.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `hard50_temp0`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 50

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 327
- Mentions raw: 335
- Mentions scored: 329
- Evidence-invalid dropped: 6
- Evidence validity rate: 0.9821

## Overall Scores

### semantic

- per-item: P=0.453 R=0.452 F1=0.452 (TP=149 FP=180 FN=181)
- per-letter: P=0.900 R=0.660 F1=0.761 (TP=99 FP=11 FN=51)

### benchmark

- per-item: P=0.438 R=0.436 F1=0.437 (TP=144 FP=185 FN=186)
- per-letter: P=0.899 R=0.653 F1=0.757 (TP=98 FP=11 FN=52)

### phrase_only

- per-item: P=0.532 R=0.530 F1=0.531 (TP=175 FP=154 FN=155)
- per-letter: P=0.911 R=0.747 F1=0.821 (TP=112 FP=11 FN=38)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.787 P=0.768 R=0.807

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.885 | 0.859 | 0.912 | 73 | 12 | 7 |
| Diagnosis | 0.80 | 0.741 | 0.707 | 0.779 | 74 | 29 | 21 |
| SeizureFrequency | 0.80 | 0.585 | 0.574 | 0.596 | 31 | 23 | 21 |
| Investigations | 0.80 | 0.936 | 0.957 | 0.917 | 44 | 2 | 4 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.747 | 246 | 83 | 84 | 0.813 (200/246) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.727 | 72 | 0.778 (56/72) |
| Diagnosis | 0.720 | 90 | 0.933 (84/90) |
| SeizureFrequency | 0.667 | 39 | 0.462 (18/39) |
| Investigations | 0.957 | 45 | 0.933 (42/45) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.242 | 0.638 |
| Diagnosis | 0.80 | 0.85 | 0.600 | 0.933 |
| SeizureFrequency | 0.80 | 0.66 | 0.325 | 0.549 |
| Investigations | 0.80 | 0.95 | 0.660 | 0.840 |