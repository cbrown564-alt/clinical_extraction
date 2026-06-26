# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 1 / 1 letters

- JSONL: `experiments\exectv2_2call_no_sf_self_consistency_smoke1_temp0_r1_temp0p0_20260625_structured.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `smoke1_temp0`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 1

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 8
- Mentions raw: 5
- Mentions scored: 5
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Overall Scores

### semantic

- per-item: P=0.600 R=0.429 F1=0.500 (TP=3 FP=2 FN=4)
- per-letter: P=1.000 R=0.750 F1=0.857 (TP=3 FP=0 FN=1)

### benchmark

- per-item: P=0.600 R=0.429 F1=0.500 (TP=3 FP=2 FN=4)
- per-letter: P=1.000 R=0.750 F1=0.857 (TP=3 FP=0 FN=1)

### phrase_only

- per-item: P=0.600 R=0.429 F1=0.500 (TP=3 FP=2 FN=4)
- per-letter: P=1.000 R=0.750 F1=0.857 (TP=3 FP=0 FN=1)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.500 P=0.500 R=0.500

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 |
| Diagnosis | 0.80 | 0.333 | 0.333 | 0.333 | 1 | 2 | 2 |
| SeizureFrequency | 0.80 | 0.000 | 0.000 | 0.000 | 0 | 1 | 1 |
| Investigations | 0.80 | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.833 | 5 | 0 | 2 | 0.800 (4/5) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 1.000 | 1 | 1.000 (1/1) |
| Diagnosis | 0.667 | 2 | 1.000 (2/2) |
| SeizureFrequency | 1.000 | 1 | 0.000 (0/1) |
| Investigations | 1.000 | 1 | 1.000 (1/1) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 1.000 | 1.000 |
| Diagnosis | 0.80 | 0.85 | 0.333 | 1.000 |
| SeizureFrequency | 0.80 | 0.66 | 0.000 | 0.000 |
| Investigations | 0.80 | 0.95 | 1.000 | 1.000 |