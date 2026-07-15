# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 50 / 140 letters

- JSONL: `experiments\exectv2_six_model_gpt41mini_dev140_20260715_structured.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev140`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 50

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 338
- Mentions raw: 332
- Mentions scored: 328
- Evidence-invalid dropped: 4
- Evidence validity rate: 0.9880

## Overall Scores

### semantic

- per-item: P=0.467 R=0.464 F1=0.465 (TP=153 FP=175 FN=177)
- per-letter: P=0.900 R=0.660 F1=0.761 (TP=99 FP=11 FN=51)

### benchmark

- per-item: P=0.448 R=0.446 F1=0.447 (TP=147 FP=181 FN=183)
- per-letter: P=0.899 R=0.653 F1=0.757 (TP=98 FP=11 FN=52)

### phrase_only

- per-item: P=0.527 R=0.524 F1=0.526 (TP=173 FP=155 FN=157)
- per-letter: P=0.908 R=0.727 F1=0.807 (TP=109 FP=11 FN=41)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.792 P=0.778 R=0.806

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.905 | 0.894 | 0.916 | 76 | 9 | 7 |
| Diagnosis | 0.80 | 0.739 | 0.703 | 0.779 | 74 | 30 | 21 |
| SeizureFrequency | 0.80 | 0.577 | 0.577 | 0.577 | 30 | 22 | 22 |
| Investigations | 0.80 | 0.936 | 0.957 | 0.917 | 44 | 2 | 4 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.760 | 250 | 78 | 80 | 0.844 (211/250) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.753 | 73 | 0.781 (57/73) |
| Diagnosis | 0.734 | 94 | 0.936 (88/94) |
| SeizureFrequency | 0.667 | 38 | 0.632 (24/38) |
| Investigations | 0.957 | 45 | 0.933 (42/45) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.237 | 0.627 |
| Diagnosis | 0.80 | 0.85 | 0.602 | 0.933 |
| SeizureFrequency | 0.80 | 0.66 | 0.404 | 0.593 |
| Investigations | 0.80 | 0.95 | 0.638 | 0.816 |