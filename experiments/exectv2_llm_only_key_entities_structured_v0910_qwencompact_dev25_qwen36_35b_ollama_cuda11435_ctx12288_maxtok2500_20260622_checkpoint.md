# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 7 / 25 letters

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v0910_qwencompact_dev25_qwen36_35b_ollama_cuda11435_ctx12288_maxtok2500_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.10_qwen_compact`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 7

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 48
- Mentions raw: 49
- Mentions scored: 46
- Evidence-invalid dropped: 3
- Evidence validity rate: 0.9388

## Overall Scores

### semantic

- per-item: P=0.283 R=0.220 F1=0.248 (TP=13 FP=33 FN=46)
- per-letter: P=1.000 R=0.407 F1=0.579 (TP=11 FP=0 FN=16)

### benchmark

- per-item: P=0.261 R=0.203 F1=0.229 (TP=12 FP=34 FN=47)
- per-letter: P=1.000 R=0.370 F1=0.540 (TP=10 FP=0 FN=17)

### phrase_only

- per-item: P=0.500 R=0.390 F1=0.438 (TP=23 FP=23 FN=36)
- per-letter: P=1.000 R=0.556 F1=0.714 (TP=15 FP=0 FN=12)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.880 | 0.786 | 1.000 | 11 | 3 | 0 |
| Diagnosis | 0.80 | 0.476 | 0.714 | 0.357 | 5 | 2 | 9 |
| SeizureFrequency | 0.80 | 0.762 | 0.889 | 0.667 | 8 | 1 | 4 |
| Investigations | 0.80 | 0.889 | 0.889 | 0.889 | 8 | 1 | 1 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.800 | 42 | 4 | 17 | 0.714 (30/42) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.923 | 12 | 1.000 (12/12) |
| Diagnosis | 0.625 | 10 | 0.800 (8/10) |
| SeizureFrequency | 0.828 | 12 | 0.167 (2/12) |
| Investigations | 0.889 | 8 | 1.000 (8/8) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.154 | 0.444 |
| Diagnosis | 0.80 | 0.85 | 0.438 | 0.833 |
| SeizureFrequency | 0.80 | 0.66 | 0.138 | 0.444 |
| Investigations | 0.80 | 0.95 | 0.222 | 0.500 |