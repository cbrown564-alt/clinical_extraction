# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_hybrid_key_family_event_ledger_v08_dev25_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.8`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 1
- Clinical events raw: 137
- Mentions raw: 145
- Mentions scored: 142
- Evidence-invalid dropped: 3
- Evidence validity rate: 0.9793

## Overall Scores

### semantic

- per-item: P=0.380 R=0.370 F1=0.375 (TP=54 FP=88 FN=92)
- per-letter: P=0.872 R=0.578 F1=0.695 (TP=41 FP=6 FN=30)

### benchmark

- per-item: P=0.289 R=0.281 F1=0.285 (TP=41 FP=101 FN=105)
- per-letter: P=0.850 R=0.479 F1=0.613 (TP=34 FP=6 FN=37)

### phrase_only

- per-item: P=0.528 R=0.514 F1=0.521 (TP=75 FP=67 FN=71)
- per-letter: P=0.889 R=0.676 F1=0.768 (TP=48 FP=6 FN=23)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.831 | 0.821 | 0.842 | 32 | 7 | 6 |
| Diagnosis | 0.80 | 0.540 | 0.575 | 0.509 | 27 | 20 | 26 |
| SeizureFrequency | 0.80 | 0.562 | 0.545 | 0.581 | 18 | 15 | 13 |
| Investigations | 0.80 | 0.800 | 0.800 | 0.800 | 16 | 4 | 4 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.757 | 109 | 33 | 37 | 0.725 (79/109) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.795 | 33 | 0.909 (30/33) |
| Diagnosis | 0.673 | 34 | 0.676 (23/34) |
| SeizureFrequency | 0.750 | 24 | 0.417 (10/24) |
| Investigations | 0.900 | 18 | 0.889 (16/18) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.217 | 0.533 |
| Diagnosis | 0.80 | 0.85 | 0.436 | 0.821 |
| SeizureFrequency | 0.80 | 0.66 | 0.375 | 0.667 |
| Investigations | 0.80 | 0.95 | 0.550 | 0.727 |