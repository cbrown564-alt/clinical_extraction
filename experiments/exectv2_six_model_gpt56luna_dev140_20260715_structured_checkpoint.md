# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 140 / 140 letters

- JSONL: `experiments\exectv2_six_model_gpt56luna_dev140_20260715_structured.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev140`
- Model: `openai/gpt-5.6-luna`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 695
- Mentions raw: 783
- Mentions scored: 783
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Overall Scores

### semantic

- per-item: P=0.571 R=0.485 F1=0.524 (TP=447 FP=336 FN=475)
- per-letter: P=0.940 R=0.674 F1=0.785 (TP=283 FP=18 FN=137)

### benchmark

- per-item: P=0.545 R=0.463 F1=0.501 (TP=427 FP=356 FN=495)
- per-letter: P=0.939 R=0.657 F1=0.773 (TP=276 FP=18 FN=144)

### phrase_only

- per-item: P=0.656 R=0.557 F1=0.603 (TP=514 FP=269 FN=408)
- per-letter: P=0.947 R=0.759 F1=0.843 (TP=319 FP=18 FN=101)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.834 P=0.857 R=0.812

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.948 | 0.965 | 0.931 | 190 | 7 | 14 |
| Diagnosis | 0.80 | 0.777 | 0.794 | 0.760 | 219 | 56 | 69 |
| SeizureFrequency | 0.80 | 0.725 | 0.755 | 0.698 | 120 | 39 | 52 |
| Investigations | 0.80 | 0.929 | 0.965 | 0.895 | 111 | 4 | 13 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.807 | 688 | 95 | 234 | 0.796 (548/688) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.852 | 176 | 0.761 (134/176) |
| Diagnosis | 0.765 | 268 | 0.899 (241/268) |
| SeizureFrequency | 0.744 | 131 | 0.504 (66/131) |
| Investigations | 0.946 | 113 | 0.947 (107/113) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.305 | 0.587 |
| Diagnosis | 0.80 | 0.85 | 0.670 | 0.973 |
| SeizureFrequency | 0.80 | 0.66 | 0.398 | 0.671 |
| Investigations | 0.80 | 0.95 | 0.661 | 0.818 |