# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 140 / 140 letters

- JSONL: `experiments\exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r3_temp0p7_20260625_structured.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `entropy_dev140_temps`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 960
- Mentions raw: 967
- Mentions scored: 951
- Evidence-invalid dropped: 16
- Evidence validity rate: 0.9835

## Overall Scores

### semantic

- per-item: P=0.418 R=0.432 F1=0.425 (TP=398 FP=553 FN=524)
- per-letter: P=0.863 R=0.617 F1=0.719 (TP=259 FP=41 FN=161)

### benchmark

- per-item: P=0.399 R=0.411 F1=0.405 (TP=379 FP=572 FN=543)
- per-letter: P=0.860 R=0.600 F1=0.707 (TP=252 FP=41 FN=168)

### phrase_only

- per-item: P=0.529 R=0.546 F1=0.537 (TP=503 FP=448 FN=419)
- per-letter: P=0.884 R=0.748 F1=0.810 (TP=314 FP=41 FN=106)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.734 P=0.723 R=0.745

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.812 | 0.774 | 0.854 | 158 | 46 | 27 |
| Diagnosis | 0.80 | 0.717 | 0.708 | 0.726 | 209 | 84 | 79 |
| SeizureFrequency | 0.80 | 0.610 | 0.593 | 0.628 | 108 | 74 | 64 |
| Investigations | 0.80 | 0.831 | 0.875 | 0.790 | 98 | 14 | 26 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.733 | 686 | 265 | 236 | 0.725 (497/686) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.686 | 178 | 0.708 (126/178) |
| Diagnosis | 0.742 | 274 | 0.869 (238/274) |
| SeizureFrequency | 0.686 | 130 | 0.285 (37/130) |
| Investigations | 0.881 | 104 | 0.923 (96/104) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.220 | 0.526 |
| Diagnosis | 0.80 | 0.85 | 0.606 | 0.949 |
| SeizureFrequency | 0.80 | 0.66 | 0.237 | 0.506 |
| Investigations | 0.80 | 0.95 | 0.610 | 0.791 |