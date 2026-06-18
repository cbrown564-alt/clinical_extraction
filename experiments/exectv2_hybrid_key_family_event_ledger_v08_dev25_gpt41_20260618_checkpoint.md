# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 25 / 25 letters

- JSONL: `experiments\exectv2_hybrid_key_family_event_ledger_v08_dev25_gpt41_20260618.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.8`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `openai/gpt-4.1`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 125
- Mentions raw: 129
- Mentions scored: 129
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Overall Scores

### semantic

- per-item: P=0.426 R=0.377 F1=0.400 (TP=55 FP=74 FN=91)
- per-letter: P=0.911 R=0.578 F1=0.707 (TP=41 FP=4 FN=30)

### benchmark

- per-item: P=0.372 R=0.329 F1=0.349 (TP=48 FP=81 FN=98)
- per-letter: P=0.897 R=0.493 F1=0.636 (TP=35 FP=4 FN=36)

### phrase_only

- per-item: P=0.612 R=0.541 F1=0.575 (TP=79 FP=50 FN=67)
- per-letter: P=0.932 R=0.775 F1=0.846 (TP=55 FP=4 FN=16)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.974 | 0.950 | 1.000 | 38 | 2 | 0 |
| Diagnosis | 0.80 | 0.483 | 0.579 | 0.415 | 22 | 16 | 31 |
| SeizureFrequency | 0.80 | 0.677 | 0.677 | 0.677 | 21 | 10 | 10 |
| Investigations | 0.80 | 0.821 | 0.842 | 0.800 | 16 | 3 | 4 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.815 | 112 | 17 | 34 | 0.741 (83/112) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.938 | 38 | 0.895 (34/38) |
| Diagnosis | 0.688 | 32 | 0.562 (18/32) |
| SeizureFrequency | 0.774 | 24 | 0.625 (15/24) |
| Investigations | 0.923 | 18 | 0.889 (16/18) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.346 | 0.645 |
| Diagnosis | 0.80 | 0.85 | 0.366 | 0.842 |
| SeizureFrequency | 0.80 | 0.66 | 0.452 | 0.615 |
| Investigations | 0.80 | 0.95 | 0.513 | 0.667 |