# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 25 / 25 letters

- JSONL: `experiments\exectv2_hybrid_key_family_event_ledger_v07_dev25_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.7`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 133
- Mentions raw: 144
- Mentions scored: 143
- Evidence-invalid dropped: 1
- Evidence validity rate: 0.9931

## Overall Scores

### semantic

- per-item: P=0.322 R=0.315 F1=0.318 (TP=46 FP=97 FN=100)
- per-letter: P=0.897 R=0.493 F1=0.636 (TP=35 FP=4 FN=36)

### benchmark

- per-item: P=0.238 R=0.233 F1=0.235 (TP=34 FP=109 FN=112)
- per-letter: P=0.879 R=0.408 F1=0.558 (TP=29 FP=4 FN=42)

### phrase_only

- per-item: P=0.545 R=0.534 F1=0.540 (TP=78 FP=65 FN=68)
- per-letter: P=0.924 R=0.690 F1=0.790 (TP=49 FP=4 FN=22)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.883 | 0.872 | 0.895 | 34 | 5 | 4 |
| Diagnosis | 0.80 | 0.600 | 0.638 | 0.566 | 30 | 17 | 23 |
| SeizureFrequency | 0.80 | 0.523 | 0.500 | 0.548 | 17 | 17 | 14 |
| Investigations | 0.80 | 0.780 | 0.762 | 0.800 | 16 | 5 | 4 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.782 | 113 | 30 | 33 | 0.646 (73/113) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.805 | 33 | 0.879 (29/33) |
| Diagnosis | 0.733 | 37 | 0.595 (22/37) |
| SeizureFrequency | 0.769 | 25 | 0.280 (7/25) |
| Investigations | 0.878 | 18 | 0.833 (15/18) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.195 | 0.483 |
| Diagnosis | 0.80 | 0.85 | 0.416 | 0.811 |
| SeizureFrequency | 0.80 | 0.66 | 0.215 | 0.522 |
| Investigations | 0.80 | 0.95 | 0.488 | 0.667 |