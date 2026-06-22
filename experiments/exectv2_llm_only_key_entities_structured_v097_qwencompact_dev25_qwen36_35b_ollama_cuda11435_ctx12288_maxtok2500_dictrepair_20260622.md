# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v097_qwencompact_dev25_qwen36_35b_ollama_cuda11435_ctx12288_maxtok2500_dictrepair_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.7_qwen_compact`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 1
- Clinical events raw: 124
- Mentions raw: 131
- Mentions scored: 127
- Evidence-invalid dropped: 4
- Evidence validity rate: 0.9695

## Overall Scores

### semantic

- per-item: P=0.283 R=0.247 F1=0.264 (TP=36 FP=91 FN=110)
- per-letter: P=0.811 R=0.422 F1=0.556 (TP=30 FP=7 FN=41)

### benchmark

- per-item: P=0.276 R=0.240 F1=0.256 (TP=35 FP=92 FN=111)
- per-letter: P=0.806 R=0.408 F1=0.542 (TP=29 FP=7 FN=42)

### phrase_only

- per-item: P=0.465 R=0.404 F1=0.432 (TP=59 FP=68 FN=87)
- per-letter: P=0.857 R=0.592 F1=0.700 (TP=42 FP=7 FN=29)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.949 | 0.925 | 0.974 | 37 | 3 | 1 |
| Diagnosis | 0.80 | 0.667 | 0.722 | 0.619 | 26 | 10 | 16 |
| SeizureFrequency | 0.80 | 0.588 | 0.600 | 0.577 | 15 | 10 | 11 |
| Investigations | 0.80 | 0.816 | 0.690 | 1.000 | 20 | 9 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.777 | 106 | 21 | 40 | 0.698 (74/106) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.886 | 35 | 0.943 (33/35) |
| Diagnosis | 0.652 | 30 | 0.667 (20/30) |
| SeizureFrequency | 0.759 | 22 | 0.273 (6/22) |
| Investigations | 0.864 | 19 | 0.789 (15/19) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.228 | 0.552 |
| Diagnosis | 0.80 | 0.85 | 0.304 | 0.706 |
| SeizureFrequency | 0.80 | 0.66 | 0.207 | 0.348 |
| Investigations | 0.80 | 0.95 | 0.318 | 0.545 |