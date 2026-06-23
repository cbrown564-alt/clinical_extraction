# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 5 / 5 letters

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v0923d_qwencompact_dev5_qwen36_35b_ollama_cuda11435_ctx12288_maxtok3000_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.23_qwen_compact`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 5

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 38
- Mentions raw: 41
- Mentions scored: 41
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Overall Scores

### semantic

- per-item: P=0.342 R=0.298 F1=0.318 (TP=14 FP=27 FN=33)
- per-letter: P=1.000 R=0.450 F1=0.621 (TP=9 FP=0 FN=11)

### benchmark

- per-item: P=0.342 R=0.298 F1=0.318 (TP=14 FP=27 FN=33)
- per-letter: P=1.000 R=0.450 F1=0.621 (TP=9 FP=0 FN=11)

### phrase_only

- per-item: P=0.561 R=0.489 F1=0.523 (TP=23 FP=18 FN=24)
- per-letter: P=1.000 R=0.600 F1=0.750 (TP=12 FP=0 FN=8)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 1.000 | 1.000 | 1.000 | 9 | 0 | 0 |
| Diagnosis | 0.80 | 0.696 | 0.667 | 0.727 | 8 | 4 | 3 |
| SeizureFrequency | 0.80 | 0.941 | 0.889 | 1.000 | 8 | 1 | 0 |
| Investigations | 0.80 | 0.800 | 0.667 | 1.000 | 8 | 4 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.886 | 39 | 2 | 8 | 0.692 (27/39) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 1.000 | 9 | 1.000 (9/9) |
| Diagnosis | 0.727 | 12 | 0.667 (8/12) |
| SeizureFrequency | 0.952 | 10 | 0.500 (5/10) |
| Investigations | 1.000 | 8 | 0.625 (5/8) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.111 | 0.333 |
| Diagnosis | 0.80 | 0.85 | 0.424 | 0.750 |
| SeizureFrequency | 0.80 | 0.66 | 0.476 | 0.889 |
| Investigations | 0.80 | 0.95 | 0.125 | 0.333 |