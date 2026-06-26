# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_2call_no_sf_self_consistency_hard50_temp0_r1_temp0p0_20260625_structured.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `hard50_temp0`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 50

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 333
- Mentions raw: 343
- Mentions scored: 338
- Evidence-invalid dropped: 5
- Evidence validity rate: 0.9854

## Overall Scores

### semantic

- per-item: P=0.444 R=0.455 F1=0.449 (TP=150 FP=188 FN=180)
- per-letter: P=0.882 R=0.647 F1=0.746 (TP=97 FP=13 FN=53)

### benchmark

- per-item: P=0.429 R=0.439 F1=0.434 (TP=145 FP=193 FN=185)
- per-letter: P=0.880 R=0.633 F1=0.736 (TP=95 FP=13 FN=55)

### phrase_only

- per-item: P=0.518 R=0.530 F1=0.524 (TP=175 FP=163 FN=155)
- per-letter: P=0.894 R=0.733 F1=0.806 (TP=110 FP=13 FN=40)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.772 P=0.749 R=0.796

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.878 | 0.857 | 0.900 | 72 | 12 | 8 |
| Diagnosis | 0.80 | 0.740 | 0.696 | 0.789 | 75 | 31 | 20 |
| SeizureFrequency | 0.80 | 0.569 | 0.544 | 0.596 | 31 | 26 | 21 |
| Investigations | 0.80 | 0.891 | 0.932 | 0.854 | 41 | 3 | 7 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.737 | 246 | 92 | 84 | 0.813 (200/246) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.710 | 71 | 0.775 (55/71) |
| Diagnosis | 0.724 | 93 | 0.935 (87/93) |
| SeizureFrequency | 0.672 | 40 | 0.475 (19/40) |
| Investigations | 0.913 | 42 | 0.929 (39/42) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.230 | 0.609 |
| Diagnosis | 0.80 | 0.85 | 0.623 | 0.945 |
| SeizureFrequency | 0.80 | 0.66 | 0.336 | 0.538 |
| Investigations | 0.80 | 0.95 | 0.587 | 0.792 |