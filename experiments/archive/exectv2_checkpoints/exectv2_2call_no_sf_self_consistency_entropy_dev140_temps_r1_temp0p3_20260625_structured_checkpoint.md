# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 140 / 140 letters

- JSONL: `experiments\exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r1_temp0p3_20260625_structured.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `entropy_dev140_temps`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 963
- Mentions raw: 973
- Mentions scored: 954
- Evidence-invalid dropped: 19
- Evidence validity rate: 0.9805

## Overall Scores

### semantic

- per-item: P=0.407 R=0.421 F1=0.414 (TP=388 FP=566 FN=534)
- per-letter: P=0.851 R=0.610 F1=0.710 (TP=256 FP=45 FN=164)

### benchmark

- per-item: P=0.388 R=0.401 F1=0.395 (TP=370 FP=584 FN=552)
- per-letter: P=0.847 R=0.593 F1=0.698 (TP=249 FP=45 FN=171)

### phrase_only

- per-item: P=0.513 R=0.530 F1=0.521 (TP=489 FP=465 FN=433)
- per-letter: P=0.873 R=0.733 F1=0.797 (TP=308 FP=45 FN=112)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.730 P=0.715 R=0.746

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.804 | 0.768 | 0.843 | 156 | 47 | 29 |
| Diagnosis | 0.80 | 0.715 | 0.702 | 0.729 | 210 | 87 | 78 |
| SeizureFrequency | 0.80 | 0.603 | 0.585 | 0.622 | 107 | 76 | 65 |
| Investigations | 0.80 | 0.835 | 0.856 | 0.815 | 101 | 17 | 23 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.715 | 671 | 283 | 251 | 0.741 (497/671) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.670 | 173 | 0.740 (128/173) |
| Diagnosis | 0.725 | 267 | 0.865 (231/267) |
| SeizureFrequency | 0.656 | 125 | 0.312 (39/125) |
| Investigations | 0.876 | 106 | 0.934 (99/106) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.225 | 0.533 |
| Diagnosis | 0.80 | 0.85 | 0.575 | 0.932 |
| SeizureFrequency | 0.80 | 0.66 | 0.231 | 0.490 |
| Investigations | 0.80 | 0.95 | 0.612 | 0.785 |