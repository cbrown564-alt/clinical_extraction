# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 25 / 25 letters

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v0910_qwencompact_dev25_qwen36_35b_ollama_cuda11435_ctx12288_maxtok2500_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.10_qwen_compact`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 126
- Mentions raw: 127
- Mentions scored: 119
- Evidence-invalid dropped: 8
- Evidence validity rate: 0.9370

## Overall Scores

### semantic

- per-item: P=0.319 R=0.260 F1=0.287 (TP=38 FP=81 FN=108)
- per-letter: P=0.914 R=0.451 F1=0.604 (TP=32 FP=3 FN=39)

### benchmark

- per-item: P=0.311 R=0.253 F1=0.279 (TP=37 FP=82 FN=109)
- per-letter: P=0.912 R=0.437 F1=0.591 (TP=31 FP=3 FN=40)

### phrase_only

- per-item: P=0.513 R=0.418 F1=0.460 (TP=61 FP=58 FN=85)
- per-letter: P=0.935 R=0.606 F1=0.735 (TP=43 FP=3 FN=28)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.949 | 0.925 | 0.974 | 37 | 3 | 1 |
| Diagnosis | 0.80 | 0.648 | 0.793 | 0.548 | 23 | 6 | 19 |
| SeizureFrequency | 0.80 | 0.583 | 0.636 | 0.538 | 14 | 8 | 12 |
| Investigations | 0.80 | 0.927 | 0.905 | 0.950 | 19 | 2 | 1 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.785 | 104 | 15 | 42 | 0.702 (73/104) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.911 | 36 | 0.917 (33/36) |
| Diagnosis | 0.659 | 29 | 0.690 (20/29) |
| SeizureFrequency | 0.737 | 21 | 0.143 (3/21) |
| Investigations | 0.878 | 18 | 0.944 (17/18) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.203 | 0.500 |
| Diagnosis | 0.80 | 0.85 | 0.364 | 0.778 |
| SeizureFrequency | 0.80 | 0.66 | 0.105 | 0.300 |
| Investigations | 0.80 | 0.95 | 0.537 | 0.727 |