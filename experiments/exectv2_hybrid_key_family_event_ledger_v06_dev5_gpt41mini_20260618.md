# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_hybrid_key_family_event_ledger_v06_dev5_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.6`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 5

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 36
- Mentions raw: 38
- Mentions scored: 38
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Overall Scores

### semantic

- per-item: P=0.342 R=0.277 F1=0.306 (TP=13 FP=25 FN=34)
- per-letter: P=1.000 R=0.550 F1=0.710 (TP=11 FP=0 FN=9)

### benchmark

- per-item: P=0.263 R=0.213 F1=0.235 (TP=10 FP=28 FN=37)
- per-letter: P=1.000 R=0.450 F1=0.621 (TP=9 FP=0 FN=11)

### phrase_only

- per-item: P=0.579 R=0.468 F1=0.518 (TP=22 FP=16 FN=25)
- per-letter: P=1.000 R=0.700 F1=0.824 (TP=14 FP=0 FN=6)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 1.000 | 1.000 | 1.000 | 9 | 0 | 0 |
| Diagnosis | 0.80 | 0.357 | 0.417 | 0.312 | 5 | 7 | 11 |
| SeizureFrequency | 0.80 | 0.667 | 0.700 | 0.636 | 7 | 3 | 4 |
| Investigations | 0.80 | 0.800 | 0.857 | 0.750 | 6 | 1 | 2 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.800 | 34 | 4 | 13 | 0.676 (23/34) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 1.000 | 9 | 1.000 (9/9) |
| Diagnosis | 0.581 | 9 | 0.333 (3/9) |
| SeizureFrequency | 0.857 | 9 | 0.556 (5/9) |
| Investigations | 0.933 | 7 | 0.857 (6/7) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.222 | 0.571 |
| Diagnosis | 0.80 | 0.85 | 0.258 | 0.750 |
| SeizureFrequency | 0.80 | 0.66 | 0.476 | 0.889 |
| Investigations | 0.80 | 0.95 | 0.267 | 0.571 |