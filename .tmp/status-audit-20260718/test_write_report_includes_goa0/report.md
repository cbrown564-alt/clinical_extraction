# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 1 / 140 letters

- JSONL: `C:\Users\cbrow\Code\clinical_extraction\.tmp\status-audit-20260718\test_write_report_includes_goa0\rows.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `test-model`
- Mode: `prompt-only`
- Letters: 1

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Initial parse/schema failures: 0
- Format retries applied: 0
- Format retries rejected: 0
- Clinical events raw: 0
- Mentions raw: 0
- Mentions scored: 0
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Overall Scores

### semantic

- per-item: P=0.000 R=0.000 F1=0.000 (TP=0 FP=0 FN=0)
- per-letter: P=0.000 R=0.000 F1=0.000 (TP=0 FP=0 FN=0)

### benchmark

- per-item: P=0.000 R=0.000 F1=0.000 (TP=0 FP=0 FN=0)
- per-letter: P=0.000 R=0.000 F1=0.000 (TP=0 FP=0 FN=0)

### phrase_only

- per-item: P=0.000 R=0.000 F1=0.000 (TP=0 FP=0 FN=0)
- per-letter: P=0.000 R=0.000 F1=0.000 (TP=0 FP=0 FN=0)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.000 P=0.000 R=0.000

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.000 | 0.000 | 0.000 | 0 | 0 | 0 |
| Diagnosis | 0.80 | 0.000 | 0.000 | 0.000 | 0 | 0 | 0 |
| SeizureFrequency | 0.80 | 0.000 | 0.000 | 0.000 | 0 | 0 | 0 |
| Investigations | 0.80 | 0.000 | 0.000 | 0.000 | 0 | 0 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.000 | 0 | 0 | 0 | 0.000 (0/0) |

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