# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 20 / 140 letters

- JSONL: `experiments\exectv2_six_model_deepseek_v4_flash_dev140_20260715_structured.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev140`
- Model: `deepseek/deepseek-v4-flash`
- Mode: `live`
- Letters: 20

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 102
- Mentions raw: 114
- Mentions scored: 114
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Overall Scores

### semantic

- per-item: P=0.623 R=0.534 F1=0.575 (TP=71 FP=43 FN=62)
- per-letter: P=0.959 R=0.723 F1=0.825 (TP=47 FP=2 FN=18)

### benchmark

- per-item: P=0.597 R=0.511 F1=0.551 (TP=68 FP=46 FN=65)
- per-letter: P=0.958 R=0.708 F1=0.814 (TP=46 FP=2 FN=19)

### phrase_only

- per-item: P=0.649 R=0.556 F1=0.599 (TP=74 FP=40 FN=59)
- per-letter: P=0.961 R=0.754 F1=0.845 (TP=49 FP=2 FN=16)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.888 P=0.900 R=0.876

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.986 | 1.000 | 0.971 | 34 | 0 | 1 |
| Diagnosis | 0.80 | 0.827 | 0.816 | 0.838 | 31 | 7 | 6 |
| SeizureFrequency | 0.80 | 0.792 | 0.864 | 0.731 | 19 | 3 | 7 |
| Investigations | 0.80 | 0.968 | 0.938 | 1.000 | 15 | 1 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.842 | 104 | 10 | 29 | 0.923 (96/104) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.870 | 30 | 0.867 (26/30) |
| Diagnosis | 0.817 | 38 | 0.921 (35/38) |
| SeizureFrequency | 0.778 | 21 | 0.952 (20/21) |
| Investigations | 0.968 | 15 | 1.000 (15/15) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.319 | 0.690 |
| Diagnosis | 0.80 | 0.85 | 0.710 | 0.947 |
| SeizureFrequency | 0.80 | 0.66 | 0.667 | 0.857 |
| Investigations | 0.80 | 0.95 | 0.581 | 0.737 |