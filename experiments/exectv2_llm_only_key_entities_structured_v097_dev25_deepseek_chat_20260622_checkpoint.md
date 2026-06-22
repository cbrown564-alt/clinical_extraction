# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 25 / 25 letters

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v097_dev25_deepseek_chat_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.7`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `deepseek/deepseek-chat`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 136
- Mentions raw: 146
- Mentions scored: 145
- Evidence-invalid dropped: 1
- Evidence validity rate: 0.9932

## Overall Scores

### semantic

- per-item: P=0.386 R=0.384 F1=0.385 (TP=56 FP=89 FN=90)
- per-letter: P=0.915 R=0.606 F1=0.729 (TP=43 FP=4 FN=28)

### benchmark

- per-item: P=0.372 R=0.370 F1=0.371 (TP=54 FP=91 FN=92)
- per-letter: P=0.911 R=0.578 F1=0.707 (TP=41 FP=4 FN=30)

### phrase_only

- per-item: P=0.572 R=0.569 F1=0.570 (TP=83 FP=62 FN=63)
- per-letter: P=0.930 R=0.747 F1=0.828 (TP=53 FP=4 FN=18)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.961 | 0.949 | 0.974 | 37 | 2 | 1 |
| Diagnosis | 0.80 | 0.767 | 0.750 | 0.786 | 33 | 11 | 9 |
| SeizureFrequency | 0.80 | 0.759 | 0.688 | 0.846 | 22 | 10 | 4 |
| Investigations | 0.80 | 0.909 | 0.833 | 1.000 | 20 | 4 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.839 | 122 | 23 | 24 | 0.730 (89/122) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.937 | 37 | 0.892 (33/37) |
| Diagnosis | 0.762 | 40 | 0.575 (23/40) |
| SeizureFrequency | 0.800 | 26 | 0.577 (15/26) |
| Investigations | 0.905 | 19 | 0.947 (18/19) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.228 | 0.552 |
| Diagnosis | 0.80 | 0.85 | 0.362 | 0.842 |
| SeizureFrequency | 0.80 | 0.66 | 0.492 | 0.714 |
| Investigations | 0.80 | 0.95 | 0.571 | 0.783 |