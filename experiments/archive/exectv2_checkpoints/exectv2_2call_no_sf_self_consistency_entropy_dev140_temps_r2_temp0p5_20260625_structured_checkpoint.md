# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 140 / 140 letters

- JSONL: `experiments\exectv2_2call_no_sf_self_consistency_entropy_dev140_temps_r2_temp0p5_20260625_structured.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `entropy_dev140_temps`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 977
- Mentions raw: 991
- Mentions scored: 973
- Evidence-invalid dropped: 18
- Evidence validity rate: 0.9818

## Overall Scores

### semantic

- per-item: P=0.397 R=0.419 F1=0.407 (TP=386 FP=587 FN=536)
- per-letter: P=0.853 R=0.607 F1=0.709 (TP=255 FP=44 FN=165)

### benchmark

- per-item: P=0.377 R=0.398 F1=0.387 (TP=367 FP=606 FN=555)
- per-letter: P=0.849 R=0.588 F1=0.695 (TP=247 FP=44 FN=173)

### phrase_only

- per-item: P=0.499 R=0.527 F1=0.513 (TP=486 FP=487 FN=436)
- per-letter: P=0.875 R=0.731 F1=0.796 (TP=307 FP=44 FN=113)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.736 P=0.721 R=0.752

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.824 | 0.782 | 0.870 | 161 | 45 | 24 |
| Diagnosis | 0.80 | 0.719 | 0.706 | 0.733 | 211 | 85 | 77 |
| SeizureFrequency | 0.80 | 0.592 | 0.574 | 0.611 | 105 | 78 | 67 |
| Investigations | 0.80 | 0.849 | 0.886 | 0.815 | 101 | 13 | 23 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.711 | 674 | 299 | 248 | 0.740 (499/674) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.646 | 174 | 0.747 (130/174) |
| Diagnosis | 0.729 | 268 | 0.881 (236/268) |
| SeizureFrequency | 0.663 | 127 | 0.268 (34/127) |
| Investigations | 0.882 | 105 | 0.943 (99/105) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.211 | 0.517 |
| Diagnosis | 0.80 | 0.85 | 0.585 | 0.945 |
| SeizureFrequency | 0.80 | 0.66 | 0.214 | 0.480 |
| Investigations | 0.80 | 0.95 | 0.613 | 0.782 |