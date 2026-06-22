# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v098_dev25_deepseek_chat_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.8`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `deepseek/deepseek-chat`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 129
- Mentions raw: 143
- Mentions scored: 143
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Overall Scores

### semantic

- per-item: P=0.420 R=0.411 F1=0.415 (TP=60 FP=83 FN=86)
- per-letter: P=0.900 R=0.634 F1=0.744 (TP=45 FP=5 FN=26)

### benchmark

- per-item: P=0.406 R=0.397 F1=0.401 (TP=58 FP=85 FN=88)
- per-letter: P=0.898 R=0.620 F1=0.733 (TP=44 FP=5 FN=27)

### phrase_only

- per-item: P=0.594 R=0.582 F1=0.588 (TP=85 FP=58 FN=61)
- per-letter: P=0.912 R=0.732 F1=0.812 (TP=52 FP=5 FN=19)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.962 | 0.927 | 1.000 | 38 | 3 | 0 |
| Diagnosis | 0.80 | 0.762 | 0.762 | 0.762 | 32 | 10 | 10 |
| SeizureFrequency | 0.80 | 0.750 | 0.700 | 0.808 | 21 | 9 | 5 |
| Investigations | 0.80 | 0.976 | 0.952 | 1.000 | 20 | 1 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.844 | 122 | 21 | 24 | 0.746 (91/122) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.925 | 37 | 0.919 (34/37) |
| Diagnosis | 0.792 | 42 | 0.571 (24/42) |
| SeizureFrequency | 0.774 | 24 | 0.625 (15/24) |
| Investigations | 0.927 | 19 | 0.947 (18/19) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.275 | 0.645 |
| Diagnosis | 0.80 | 0.85 | 0.396 | 0.842 |
| SeizureFrequency | 0.80 | 0.66 | 0.516 | 0.690 |
| Investigations | 0.80 | 0.95 | 0.585 | 0.783 |