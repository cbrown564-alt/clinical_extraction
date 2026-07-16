# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 140 / 140 letters

- JSONL: `experiments\exectv2_six_model_single_call_deepseek_v4_flash_dev140_20260715_structured.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev140`
- Model: `deepseek/deepseek-v4-flash`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 728
- Mentions raw: 832
- Mentions scored: 828
- Evidence-invalid dropped: 4
- Evidence validity rate: 0.9952

## Overall Scores

### semantic

- per-item: P=0.523 R=0.464 F1=0.491 (TP=433 FP=395 FN=501)
- per-letter: P=0.921 R=0.667 F1=0.773 (TP=280 FP=24 FN=140)

### benchmark

- per-item: P=0.500 R=0.443 F1=0.470 (TP=414 FP=414 FN=520)
- per-letter: P=0.919 R=0.645 F1=0.758 (TP=271 FP=24 FN=149)

### phrase_only

- per-item: P=0.591 R=0.524 F1=0.555 (TP=489 FP=339 FN=445)
- per-letter: P=0.928 R=0.741 F1=0.824 (TP=311 FP=24 FN=109)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.815 P=0.830 R=0.800

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.938 | 0.959 | 0.917 | 189 | 8 | 17 |
| Diagnosis | 0.80 | 0.720 | 0.719 | 0.721 | 214 | 83 | 83 |
| SeizureFrequency | 0.80 | 0.736 | 0.759 | 0.714 | 120 | 38 | 48 |
| Investigations | 0.80 | 0.939 | 0.976 | 0.904 | 123 | 3 | 13 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.807 | 711 | 117 | 223 | 0.802 (570/711) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.893 | 183 | 0.743 (136/183) |
| Diagnosis | 0.738 | 273 | 0.886 (242/273) |
| SeizureFrequency | 0.749 | 131 | 0.557 (73/131) |
| Investigations | 0.947 | 124 | 0.960 (119/124) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.268 | 0.550 |
| Diagnosis | 0.80 | 0.85 | 0.592 | 0.957 |
| SeizureFrequency | 0.80 | 0.66 | 0.389 | 0.615 |
| Investigations | 0.80 | 0.95 | 0.695 | 0.887 |