# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_hybrid_key_family_event_ledger_v06_dev25_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.6`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 136
- Mentions raw: 142
- Mentions scored: 142
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Overall Scores

### semantic

- per-item: P=0.317 R=0.308 F1=0.312 (TP=45 FP=97 FN=101)
- per-letter: P=0.881 R=0.521 F1=0.655 (TP=37 FP=5 FN=34)

### benchmark

- per-item: P=0.254 R=0.247 F1=0.250 (TP=36 FP=106 FN=110)
- per-letter: P=0.861 R=0.437 F1=0.579 (TP=31 FP=5 FN=40)

### phrase_only

- per-item: P=0.542 R=0.527 F1=0.535 (TP=77 FP=65 FN=69)
- per-letter: P=0.909 R=0.704 F1=0.794 (TP=50 FP=5 FN=21)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.872 | 0.850 | 0.895 | 34 | 6 | 4 |
| Diagnosis | 0.80 | 0.554 | 0.583 | 0.528 | 28 | 20 | 25 |
| SeizureFrequency | 0.80 | 0.507 | 0.472 | 0.548 | 17 | 19 | 14 |
| Investigations | 0.80 | 0.684 | 0.722 | 0.650 | 13 | 5 | 7 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.771 | 111 | 31 | 35 | 0.640 (71/111) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.864 | 35 | 0.886 (31/35) |
| Diagnosis | 0.667 | 34 | 0.529 (18/34) |
| SeizureFrequency | 0.776 | 26 | 0.346 (9/26) |
| Investigations | 0.842 | 16 | 0.812 (13/16) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.247 | 0.581 |
| Diagnosis | 0.80 | 0.85 | 0.353 | 0.811 |
| SeizureFrequency | 0.80 | 0.66 | 0.269 | 0.560 |
| Investigations | 0.80 | 0.95 | 0.421 | 0.600 |