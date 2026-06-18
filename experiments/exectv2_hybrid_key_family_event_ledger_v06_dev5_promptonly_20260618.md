# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_hybrid_key_family_event_ledger_v06_dev5_promptonly_20260618.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.6`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `prompt-only`
- Letters: 5

## Gate Summary

- Call failures: 0
- Parse/schema failures: 5
- Clinical events raw: 0
- Mentions raw: 0
- Mentions scored: 0
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Overall Scores

### semantic

- per-item: P=0.000 R=0.000 F1=0.000 (TP=0 FP=0 FN=47)
- per-letter: P=0.000 R=0.000 F1=0.000 (TP=0 FP=0 FN=20)

### benchmark

- per-item: P=0.000 R=0.000 F1=0.000 (TP=0 FP=0 FN=47)
- per-letter: P=0.000 R=0.000 F1=0.000 (TP=0 FP=0 FN=20)

### phrase_only

- per-item: P=0.000 R=0.000 F1=0.000 (TP=0 FP=0 FN=47)
- per-letter: P=0.000 R=0.000 F1=0.000 (TP=0 FP=0 FN=20)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.000 | 0.000 | 0.000 | 0 | 0 | 9 |
| Diagnosis | 0.80 | 0.000 | 0.000 | 0.000 | 0 | 0 | 16 |
| SeizureFrequency | 0.80 | 0.000 | 0.000 | 0.000 | 0 | 0 | 11 |
| Investigations | 0.80 | 0.000 | 0.000 | 0.000 | 0 | 0 | 8 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.000 | 0 | 0 | 47 | 0.000 (0/0) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.000 | 0 | 0.000 (0/0) |
| Diagnosis | 0.000 | 0 | 0.000 (0/0) |
| SeizureFrequency | 0.000 | 0 | 0.000 (0/0) |
| Investigations | 0.000 | 0 | 0.000 (0/0) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.000 | 0.000 |
| Diagnosis | 0.80 | 0.85 | 0.000 | 0.000 |
| SeizureFrequency | 0.80 | 0.66 | 0.000 | 0.000 |
| Investigations | 0.80 | 0.95 | 0.000 | 0.000 |