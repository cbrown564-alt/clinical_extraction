# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 5 / 5 letters

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v0923c_qwencompact_dev5_qwen36_35b_ollama_cuda11435_ctx12288_maxtok3000_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.23_qwen_compact`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 5

## Gate Summary

- Call failures: 0
- Parse/schema failures: 1
- Clinical events raw: 30
- Mentions raw: 32
- Mentions scored: 32
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Overall Scores

### semantic

- per-item: P=0.188 R=0.128 F1=0.152 (TP=6 FP=26 FN=41)
- per-letter: P=1.000 R=0.250 F1=0.400 (TP=5 FP=0 FN=15)

### benchmark

- per-item: P=0.188 R=0.128 F1=0.152 (TP=6 FP=26 FN=41)
- per-letter: P=1.000 R=0.250 F1=0.400 (TP=5 FP=0 FN=15)

### phrase_only

- per-item: P=0.469 R=0.319 F1=0.380 (TP=15 FP=17 FN=32)
- per-letter: P=1.000 R=0.450 F1=0.621 (TP=9 FP=0 FN=11)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.941 | 1.000 | 0.889 | 8 | 0 | 1 |
| Diagnosis | 0.80 | 0.600 | 0.667 | 0.545 | 6 | 3 | 5 |
| SeizureFrequency | 0.80 | 0.625 | 0.625 | 0.625 | 5 | 3 | 3 |
| Investigations | 0.80 | 0.857 | 1.000 | 0.750 | 6 | 0 | 2 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.785 | 31 | 1 | 16 | 0.613 (19/31) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.941 | 8 | 1.000 (8/8) |
| Diagnosis | 0.621 | 9 | 0.444 (4/9) |
| SeizureFrequency | 0.842 | 8 | 0.125 (1/8) |
| Investigations | 0.857 | 6 | 1.000 (6/6) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.118 | 0.333 |
| Diagnosis | 0.80 | 0.85 | 0.207 | 0.571 |
| SeizureFrequency | 0.80 | 0.66 | 0.105 | 0.333 |
| Investigations | 0.80 | 0.95 | 0.143 | 0.333 |