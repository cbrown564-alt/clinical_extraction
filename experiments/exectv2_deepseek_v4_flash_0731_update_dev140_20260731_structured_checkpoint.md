# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 140 / 140 letters

- JSONL: `experiments\exectv2_deepseek_v4_flash_0731_update_dev140_20260731_structured.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev140`
- Model: `deepseek/deepseek-v4-flash`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Initial parse/schema failures: 0
- Format retries applied: 0
- Format retries rejected: 0
- Clinical events raw: 768
- Mentions raw: 843
- Mentions scored: 843
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Overall Scores

### semantic

- per-item: P=0.539 R=0.486 F1=0.511 (TP=454 FP=389 FN=480)
- per-letter: P=0.925 R=0.671 F1=0.778 (TP=282 FP=23 FN=138)

### benchmark

- per-item: P=0.517 R=0.467 F1=0.491 (TP=436 FP=407 FN=498)
- per-letter: P=0.923 R=0.655 F1=0.766 (TP=275 FP=23 FN=145)

### phrase_only

- per-item: P=0.612 R=0.552 F1=0.581 (TP=516 FP=327 FN=418)
- per-letter: P=0.932 R=0.750 F1=0.831 (TP=315 FP=23 FN=105)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.838 P=0.843 R=0.834

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.948 | 0.970 | 0.927 | 191 | 6 | 15 |
| Diagnosis | 0.80 | 0.743 | 0.733 | 0.754 | 224 | 81 | 73 |
| SeizureFrequency | 0.80 | 0.789 | 0.787 | 0.792 | 133 | 36 | 35 |
| Investigations | 0.80 | 0.951 | 0.984 | 0.919 | 125 | 2 | 11 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.826 | 734 | 109 | 200 | 0.804 (590/734) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.879 | 181 | 0.740 (134/181) |
| Diagnosis | 0.769 | 284 | 0.891 (253/284) |
| SeizureFrequency | 0.799 | 145 | 0.566 (82/145) |
| Investigations | 0.943 | 124 | 0.976 (121/124) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.257 | 0.541 |
| Diagnosis | 0.80 | 0.85 | 0.631 | 0.953 |
| SeizureFrequency | 0.80 | 0.66 | 0.441 | 0.674 |
| Investigations | 0.80 | 0.95 | 0.669 | 0.857 |