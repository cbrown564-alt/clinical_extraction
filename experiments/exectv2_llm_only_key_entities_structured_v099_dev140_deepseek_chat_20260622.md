# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v099_dev140_deepseek_chat_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.10`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `deepseek/deepseek-chat`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 896
- Mentions raw: 921
- Mentions scored: 910
- Evidence-invalid dropped: 11
- Evidence validity rate: 0.9881

## Overall Scores

### semantic

- per-item: P=0.370 R=0.361 F1=0.365 (TP=337 FP=573 FN=597)
- per-letter: P=0.868 R=0.593 F1=0.704 (TP=249 FP=38 FN=171)

### benchmark

- per-item: P=0.352 R=0.343 F1=0.347 (TP=320 FP=590 FN=614)
- per-letter: P=0.863 R=0.571 F1=0.688 (TP=240 FP=38 FN=180)

### phrase_only

- per-item: P=0.567 R=0.552 F1=0.560 (TP=516 FP=394 FN=418)
- per-letter: P=0.892 R=0.745 F1=0.812 (TP=313 FP=38 FN=107)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.885 | 0.825 | 0.953 | 184 | 39 | 9 |
| Diagnosis | 0.80 | 0.686 | 0.678 | 0.694 | 215 | 102 | 95 |
| SeizureFrequency | 0.80 | 0.726 | 0.684 | 0.774 | 130 | 60 | 38 |
| Investigations | 0.80 | 0.910 | 0.967 | 0.860 | 117 | 4 | 19 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.805 | 742 | 168 | 192 | 0.668 (496/742) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.860 | 191 | 0.843 (161/191) |
| Diagnosis | 0.759 | 285 | 0.516 (147/285) |
| SeizureFrequency | 0.755 | 148 | 0.493 (73/148) |
| Investigations | 0.918 | 118 | 0.975 (115/118) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.284 | 0.532 |
| Diagnosis | 0.80 | 0.85 | 0.322 | 0.818 |
| SeizureFrequency | 0.80 | 0.66 | 0.347 | 0.593 |
| Investigations | 0.80 | 0.95 | 0.661 | 0.865 |