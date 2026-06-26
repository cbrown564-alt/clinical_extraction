# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 50 / 50 letters

- JSONL: `experiments\exectv2_2call_no_sf_self_consistency_hard50_temp0_r4_temp0p0_20260625_structured.jsonl`
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
- Mentions raw: 338
- Mentions scored: 333
- Evidence-invalid dropped: 5
- Evidence validity rate: 0.9852

## Overall Scores

### semantic

- per-item: P=0.471 R=0.476 F1=0.474 (TP=157 FP=176 FN=173)
- per-letter: P=0.893 R=0.667 F1=0.763 (TP=100 FP=12 FN=50)

### benchmark

- per-item: P=0.457 R=0.461 F1=0.459 (TP=152 FP=181 FN=178)
- per-letter: P=0.892 R=0.660 F1=0.759 (TP=99 FP=12 FN=51)

### phrase_only

- per-item: P=0.540 R=0.545 F1=0.543 (TP=180 FP=153 FN=150)
- per-letter: P=0.902 R=0.740 F1=0.813 (TP=111 FP=12 FN=39)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.793 P=0.777 R=0.811

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.885 | 0.859 | 0.912 | 73 | 12 | 7 |
| Diagnosis | 0.80 | 0.748 | 0.710 | 0.789 | 75 | 29 | 20 |
| SeizureFrequency | 0.80 | 0.608 | 0.620 | 0.596 | 31 | 19 | 21 |
| Investigations | 0.80 | 0.926 | 0.936 | 0.917 | 44 | 3 | 4 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.760 | 252 | 81 | 78 | 0.825 (208/252) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.720 | 72 | 0.792 (57/72) |
| Diagnosis | 0.737 | 94 | 0.936 (88/94) |
| SeizureFrequency | 0.726 | 41 | 0.512 (21/41) |
| Investigations | 0.947 | 45 | 0.933 (42/45) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.230 | 0.609 |
| Diagnosis | 0.80 | 0.85 | 0.635 | 0.945 |
| SeizureFrequency | 0.80 | 0.66 | 0.389 | 0.577 |
| Investigations | 0.80 | 0.95 | 0.653 | 0.840 |