# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 25 / 25 letters

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v099_dev25_deepseek_chat_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.9`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `deepseek/deepseek-chat`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 124
- Mentions raw: 136
- Mentions scored: 136
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Overall Scores

### semantic

- per-item: P=0.426 R=0.397 F1=0.411 (TP=58 FP=78 FN=88)
- per-letter: P=0.938 R=0.634 F1=0.756 (TP=45 FP=3 FN=26)

### benchmark

- per-item: P=0.412 R=0.384 F1=0.397 (TP=56 FP=80 FN=90)
- per-letter: P=0.935 R=0.606 F1=0.735 (TP=43 FP=3 FN=28)

### phrase_only

- per-item: P=0.640 R=0.596 F1=0.617 (TP=87 FP=49 FN=59)
- per-letter: P=0.946 R=0.747 F1=0.835 (TP=53 FP=3 FN=18)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.974 | 0.950 | 1.000 | 38 | 2 | 0 |
| Diagnosis | 0.80 | 0.843 | 0.854 | 0.833 | 35 | 6 | 7 |
| SeizureFrequency | 0.80 | 0.792 | 0.778 | 0.808 | 21 | 6 | 5 |
| Investigations | 0.80 | 0.976 | 0.952 | 1.000 | 20 | 1 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.858 | 121 | 15 | 25 | 0.727 (88/121) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.925 | 37 | 0.919 (34/37) |
| Diagnosis | 0.804 | 41 | 0.537 (22/41) |
| SeizureFrequency | 0.814 | 24 | 0.583 (14/24) |
| Investigations | 0.927 | 19 | 0.947 (18/19) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.275 | 0.645 |
| Diagnosis | 0.80 | 0.85 | 0.392 | 0.872 |
| SeizureFrequency | 0.80 | 0.66 | 0.508 | 0.692 |
| Investigations | 0.80 | 0.95 | 0.585 | 0.783 |