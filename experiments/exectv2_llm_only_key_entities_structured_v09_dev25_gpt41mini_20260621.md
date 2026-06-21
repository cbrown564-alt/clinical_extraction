# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v09_dev25_gpt41mini_20260621.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 131
- Mentions raw: 140
- Mentions scored: 135
- Evidence-invalid dropped: 5
- Evidence validity rate: 0.9643

## Overall Scores

### semantic

- per-item: P=0.304 R=0.281 F1=0.292 (TP=41 FP=94 FN=105)
- per-letter: P=0.875 R=0.493 F1=0.631 (TP=35 FP=5 FN=36)

### benchmark

- per-item: P=0.296 R=0.274 F1=0.285 (TP=40 FP=95 FN=106)
- per-letter: P=0.872 R=0.479 F1=0.618 (TP=34 FP=5 FN=37)

### phrase_only

- per-item: P=0.533 R=0.493 F1=0.512 (TP=72 FP=63 FN=74)
- per-letter: P=0.906 R=0.676 F1=0.774 (TP=48 FP=5 FN=23)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.886 | 0.854 | 0.921 | 35 | 6 | 3 |
| Diagnosis | 0.80 | 0.667 | 0.667 | 0.667 | 28 | 14 | 14 |
| SeizureFrequency | 0.80 | 0.630 | 0.607 | 0.654 | 17 | 11 | 9 |
| Investigations | 0.80 | 0.850 | 0.850 | 0.850 | 17 | 3 | 3 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.776 | 109 | 26 | 37 | 0.661 (72/109) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.864 | 35 | 0.914 (32/35) |
| Diagnosis | 0.707 | 35 | 0.429 (15/35) |
| SeizureFrequency | 0.689 | 21 | 0.476 (10/21) |
| Investigations | 0.900 | 18 | 0.833 (15/18) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.247 | 0.581 |
| Diagnosis | 0.80 | 0.85 | 0.242 | 0.706 |
| SeizureFrequency | 0.80 | 0.66 | 0.295 | 0.560 |
| Investigations | 0.80 | 0.95 | 0.500 | 0.667 |