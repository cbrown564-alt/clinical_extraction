# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 140 / 140 letters

- JSONL: `experiments\exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r4_temp1p0_20260625_structured.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `entropy_dev140_temps`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 981
- Mentions raw: 998
- Mentions scored: 974
- Evidence-invalid dropped: 24
- Evidence validity rate: 0.9760

## Overall Scores

### semantic

- per-item: P=0.399 R=0.422 F1=0.410 (TP=389 FP=585 FN=533)
- per-letter: P=0.847 R=0.605 F1=0.706 (TP=254 FP=46 FN=166)

### benchmark

- per-item: P=0.378 R=0.399 F1=0.388 (TP=368 FP=606 FN=554)
- per-letter: P=0.843 R=0.588 F1=0.693 (TP=247 FP=46 FN=173)

### phrase_only

- per-item: P=0.502 R=0.530 F1=0.516 (TP=489 FP=485 FN=433)
- per-letter: P=0.869 R=0.729 F1=0.793 (TP=306 FP=46 FN=114)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.725 P=0.712 R=0.739

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.823 | 0.794 | 0.854 | 158 | 41 | 27 |
| Diagnosis | 0.80 | 0.698 | 0.672 | 0.726 | 209 | 97 | 79 |
| SeizureFrequency | 0.80 | 0.602 | 0.589 | 0.616 | 106 | 74 | 66 |
| Investigations | 0.80 | 0.816 | 0.872 | 0.766 | 95 | 14 | 29 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.711 | 674 | 300 | 248 | 0.729 (491/674) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.655 | 174 | 0.713 (124/174) |
| Diagnosis | 0.717 | 270 | 0.870 (235/270) |
| SeizureFrequency | 0.686 | 130 | 0.300 (39/130) |
| Investigations | 0.858 | 100 | 0.930 (93/100) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.211 | 0.517 |
| Diagnosis | 0.80 | 0.85 | 0.582 | 0.933 |
| SeizureFrequency | 0.80 | 0.66 | 0.232 | 0.510 |
| Investigations | 0.80 | 0.95 | 0.601 | 0.758 |