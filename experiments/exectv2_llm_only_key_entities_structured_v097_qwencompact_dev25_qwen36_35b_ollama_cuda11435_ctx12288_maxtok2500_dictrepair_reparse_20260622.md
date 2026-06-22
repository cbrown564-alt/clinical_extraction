# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v097_qwencompact_dev25_qwen36_35b_ollama_cuda11435_ctx12288_maxtok2500_dictrepair_reparse_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.9_qwen_compact`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `diagnostic-no-call-reparse`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 137
- Mentions raw: 138
- Mentions scored: 133
- Evidence-invalid dropped: 5
- Evidence validity rate: 0.9638

## Overall Scores

### semantic

- per-item: P=0.271 R=0.247 F1=0.258 (TP=36 FP=97 FN=110)
- per-letter: P=0.732 R=0.422 F1=0.536 (TP=30 FP=11 FN=41)

### benchmark

- per-item: P=0.263 R=0.240 F1=0.251 (TP=35 FP=98 FN=111)
- per-letter: P=0.725 R=0.408 F1=0.522 (TP=29 FP=11 FN=42)

### phrase_only

- per-item: P=0.444 R=0.404 F1=0.423 (TP=59 FP=74 FN=87)
- per-letter: P=0.792 R=0.592 F1=0.677 (TP=42 FP=11 FN=29)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.949 | 0.925 | 0.974 | 37 | 3 | 1 |
| Diagnosis | 0.80 | 0.642 | 0.667 | 0.619 | 26 | 13 | 16 |
| SeizureFrequency | 0.80 | 0.577 | 0.577 | 0.577 | 15 | 11 | 11 |
| Investigations | 0.80 | 0.784 | 0.645 | 1.000 | 20 | 11 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.760 | 106 | 27 | 40 | 0.698 (74/106) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.875 | 35 | 0.943 (33/35) |
| Diagnosis | 0.632 | 30 | 0.667 (20/30) |
| SeizureFrequency | 0.746 | 22 | 0.273 (6/22) |
| Investigations | 0.844 | 19 | 0.789 (15/19) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.225 | 0.533 |
| Diagnosis | 0.80 | 0.85 | 0.295 | 0.686 |
| SeizureFrequency | 0.80 | 0.66 | 0.203 | 0.333 |
| Investigations | 0.80 | 0.95 | 0.311 | 0.522 |