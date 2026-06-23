# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 1 / 1 letters

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v0923b_qwencompact_dev1_qwen36_35b_ollama_cuda11435_ctx12288_maxtok3000_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.23_qwen_compact`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 1

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 7
- Mentions raw: 10
- Mentions scored: 10
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Overall Scores

### semantic

- per-item: P=0.300 R=0.300 F1=0.300 (TP=3 FP=7 FN=7)
- per-letter: P=1.000 R=0.500 F1=0.667 (TP=2 FP=0 FN=2)

### benchmark

- per-item: P=0.300 R=0.300 F1=0.300 (TP=3 FP=7 FN=7)
- per-letter: P=1.000 R=0.500 F1=0.667 (TP=2 FP=0 FN=2)

### phrase_only

- per-item: P=0.500 R=0.500 F1=0.500 (TP=5 FP=5 FN=5)
- per-letter: P=1.000 R=0.500 F1=0.667 (TP=2 FP=0 FN=2)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 1.000 | 1.000 | 1.000 | 2 | 0 | 0 |
| Diagnosis | 0.80 | 0.857 | 0.750 | 1.000 | 3 | 1 | 0 |
| SeizureFrequency | 0.80 | 0.000 | 0.000 | 0.000 | 0 | 2 | 2 |
| Investigations | 0.80 | 1.000 | 1.000 | 1.000 | 1 | 0 | 0 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.800 | 8 | 2 | 2 | 0.625 (5/8) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 1.000 | 2 | 1.000 (2/2) |
| Diagnosis | 1.000 | 5 | 0.400 (2/5) |
| SeizureFrequency | 0.000 | 0 | 0.000 (0/0) |
| Investigations | 1.000 | 1 | 1.000 (1/1) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.500 | 1.000 |
| Diagnosis | 0.80 | 0.85 | 0.400 | 1.000 |
| SeizureFrequency | 0.80 | 0.66 | 0.000 | 0.000 |
| Investigations | 0.80 | 0.95 | 0.000 | 0.000 |