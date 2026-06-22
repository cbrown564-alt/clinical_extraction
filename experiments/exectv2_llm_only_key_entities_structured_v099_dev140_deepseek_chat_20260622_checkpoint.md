# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 60 / 140 letters

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v099_dev140_deepseek_chat_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.9`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `deepseek/deepseek-chat`
- Mode: `live`
- Letters: 60

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 346
- Mentions raw: 369
- Mentions scored: 365
- Evidence-invalid dropped: 4
- Evidence validity rate: 0.9892

## Overall Scores

### semantic

- per-item: P=0.436 R=0.411 F1=0.423 (TP=159 FP=206 FN=228)
- per-letter: P=0.885 R=0.670 F1=0.763 (TP=116 FP=15 FN=57)

### benchmark

- per-item: P=0.414 R=0.390 F1=0.402 (TP=151 FP=214 FN=236)
- per-letter: P=0.882 R=0.647 F1=0.747 (TP=112 FP=15 FN=61)

### phrase_only

- per-item: P=0.611 R=0.576 F1=0.593 (TP=223 FP=142 FN=164)
- per-letter: P=0.899 R=0.775 F1=0.832 (TP=134 FP=15 FN=39)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.927 | 0.865 | 1.000 | 83 | 13 | 0 |
| Diagnosis | 0.80 | 0.748 | 0.748 | 0.748 | 89 | 30 | 30 |
| SeizureFrequency | 0.80 | 0.763 | 0.725 | 0.806 | 58 | 22 | 14 |
| Investigations | 0.80 | 0.926 | 0.980 | 0.877 | 50 | 1 | 7 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.800 | 301 | 64 | 86 | 0.748 (225/301) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.865 | 80 | 0.950 (76/80) |
| Diagnosis | 0.747 | 109 | 0.569 (62/109) |
| SeizureFrequency | 0.754 | 63 | 0.619 (39/63) |
| Investigations | 0.907 | 49 | 0.980 (48/49) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.357 | 0.658 |
| Diagnosis | 0.80 | 0.85 | 0.349 | 0.860 |
| SeizureFrequency | 0.80 | 0.66 | 0.455 | 0.676 |
| Investigations | 0.80 | 0.95 | 0.685 | 0.853 |