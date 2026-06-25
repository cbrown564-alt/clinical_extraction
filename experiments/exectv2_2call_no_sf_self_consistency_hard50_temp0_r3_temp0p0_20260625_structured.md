# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_2call_no_sf_self_consistency_hard50_temp0_r3_temp0p0_20260625_structured.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `hard50_temp0`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 50

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 324
- Mentions raw: 323
- Mentions scored: 316
- Evidence-invalid dropped: 7
- Evidence validity rate: 0.9783

## Overall Scores

### semantic

- per-item: P=0.468 R=0.449 F1=0.458 (TP=148 FP=168 FN=182)
- per-letter: P=0.890 R=0.647 F1=0.749 (TP=97 FP=12 FN=53)

### benchmark

- per-item: P=0.453 R=0.433 F1=0.443 (TP=143 FP=173 FN=187)
- per-letter: P=0.889 R=0.640 F1=0.744 (TP=96 FP=12 FN=54)

### phrase_only

- per-item: P=0.541 R=0.518 F1=0.529 (TP=171 FP=145 FN=159)
- per-letter: P=0.901 R=0.727 F1=0.804 (TP=109 FP=12 FN=41)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.790 P=0.787 R=0.793

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.896 | 0.879 | 0.912 | 73 | 10 | 7 |
| Diagnosis | 0.80 | 0.755 | 0.732 | 0.779 | 74 | 26 | 21 |
| SeizureFrequency | 0.80 | 0.571 | 0.609 | 0.538 | 28 | 18 | 24 |
| Investigations | 0.80 | 0.905 | 0.915 | 0.896 | 43 | 4 | 5 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.755 | 244 | 72 | 86 | 0.824 (201/244) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.746 | 72 | 0.792 (57/72) |
| Diagnosis | 0.733 | 92 | 0.935 (86/92) |
| SeizureFrequency | 0.673 | 36 | 0.472 (17/36) |
| Investigations | 0.926 | 44 | 0.932 (41/44) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.249 | 0.638 |
| Diagnosis | 0.80 | 0.85 | 0.622 | 0.945 |
| SeizureFrequency | 0.80 | 0.66 | 0.318 | 0.490 |
| Investigations | 0.80 | 0.95 | 0.611 | 0.800 |