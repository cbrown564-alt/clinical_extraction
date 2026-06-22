# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 23 / 25 letters

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v097_qwencompact_dev25_qwen36_35b_ollama_cuda11435_ctx12288_maxtok2500_dictrepair_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.7_qwen_compact`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 23

## Gate Summary

- Call failures: 0
- Parse/schema failures: 1
- Clinical events raw: 117
- Mentions raw: 124
- Mentions scored: 120
- Evidence-invalid dropped: 4
- Evidence validity rate: 0.9677

## Overall Scores

### semantic

- per-item: P=0.300 R=0.259 F1=0.278 (TP=36 FP=84 FN=103)
- per-letter: P=0.811 R=0.455 F1=0.583 (TP=30 FP=7 FN=36)

### benchmark

- per-item: P=0.292 R=0.252 F1=0.270 (TP=35 FP=85 FN=104)
- per-letter: P=0.806 R=0.439 F1=0.569 (TP=29 FP=7 FN=37)

### phrase_only

- per-item: P=0.483 R=0.417 F1=0.448 (TP=58 FP=62 FN=81)
- per-letter: P=0.854 R=0.621 F1=0.719 (TP=41 FP=7 FN=25)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.944 | 0.919 | 0.971 | 34 | 3 | 1 |
| Diagnosis | 0.80 | 0.658 | 0.714 | 0.610 | 25 | 10 | 16 |
| SeizureFrequency | 0.80 | 0.571 | 0.583 | 0.560 | 14 | 10 | 11 |
| Investigations | 0.80 | 0.800 | 0.667 | 1.000 | 18 | 9 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.764 | 99 | 21 | 40 | 0.687 (68/99) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.877 | 32 | 0.938 (30/32) |
| Diagnosis | 0.644 | 29 | 0.655 (19/29) |
| SeizureFrequency | 0.750 | 21 | 0.286 (6/21) |
| Investigations | 0.850 | 17 | 0.765 (13/17) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.247 | 0.593 |
| Diagnosis | 0.80 | 0.85 | 0.311 | 0.727 |
| SeizureFrequency | 0.80 | 0.66 | 0.214 | 0.364 |
| Investigations | 0.80 | 0.95 | 0.350 | 0.571 |