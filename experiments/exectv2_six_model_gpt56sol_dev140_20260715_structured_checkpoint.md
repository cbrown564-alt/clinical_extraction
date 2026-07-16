# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 50 / 140 letters

- JSONL: `experiments\exectv2_six_model_gpt56sol_dev140_20260715_structured.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev140`
- Model: `openai/gpt-5.6-sol`
- Mode: `live`
- Letters: 50

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 253
- Mentions raw: 290
- Mentions scored: 290
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Overall Scores

### semantic

- per-item: P=0.586 R=0.515 F1=0.548 (TP=170 FP=120 FN=160)
- per-letter: P=0.965 R=0.733 F1=0.833 (TP=110 FP=4 FN=40)

### benchmark

- per-item: P=0.569 R=0.500 F1=0.532 (TP=165 FP=125 FN=165)
- per-letter: P=0.965 R=0.727 F1=0.829 (TP=109 FP=4 FN=41)

### phrase_only

- per-item: P=0.662 R=0.582 F1=0.619 (TP=192 FP=98 FN=138)
- per-letter: P=0.968 R=0.793 F1=0.872 (TP=119 FP=4 FN=31)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.852 P=0.847 R=0.856

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.944 | 0.974 | 0.916 | 76 | 2 | 7 |
| Diagnosis | 0.80 | 0.756 | 0.717 | 0.800 | 76 | 30 | 19 |
| SeizureFrequency | 0.80 | 0.816 | 0.824 | 0.808 | 42 | 9 | 10 |
| Investigations | 0.80 | 0.936 | 0.957 | 0.917 | 44 | 2 | 4 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.829 | 257 | 33 | 73 | 0.833 (214/257) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.901 | 73 | 0.767 (56/73) |
| Diagnosis | 0.746 | 94 | 0.894 (84/94) |
| SeizureFrequency | 0.821 | 46 | 0.696 (32/46) |
| Investigations | 0.936 | 44 | 0.955 (42/44) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.346 | 0.716 |
| Diagnosis | 0.80 | 0.85 | 0.651 | 0.956 |
| SeizureFrequency | 0.80 | 0.66 | 0.571 | 0.807 |
| Investigations | 0.80 | 0.95 | 0.596 | 0.800 |