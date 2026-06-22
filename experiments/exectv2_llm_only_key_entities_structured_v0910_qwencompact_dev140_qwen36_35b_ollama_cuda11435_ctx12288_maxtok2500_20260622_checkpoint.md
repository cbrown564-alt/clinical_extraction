# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 140 / 140 letters

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v0910_qwencompact_dev140_qwen36_35b_ollama_cuda11435_ctx12288_maxtok2500_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.10_qwen_compact`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 10
- Clinical events raw: 799
- Mentions raw: 785
- Mentions scored: 749
- Evidence-invalid dropped: 36
- Evidence validity rate: 0.9541

## Overall Scores

### semantic

- per-item: P=0.263 R=0.211 F1=0.234 (TP=197 FP=552 FN=737)
- per-letter: P=0.790 R=0.376 F1=0.510 (TP=158 FP=42 FN=262)

### benchmark

- per-item: P=0.240 R=0.193 F1=0.214 (TP=180 FP=569 FN=754)
- per-letter: P=0.778 R=0.350 F1=0.483 (TP=147 FP=42 FN=273)

### phrase_only

- per-item: P=0.443 R=0.355 F1=0.395 (TP=332 FP=417 FN=602)
- per-letter: P=0.849 R=0.562 F1=0.676 (TP=236 FP=42 FN=184)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.879 | 0.876 | 0.881 | 170 | 24 | 23 |
| Diagnosis | 0.80 | 0.506 | 0.582 | 0.448 | 139 | 100 | 171 |
| SeizureFrequency | 0.80 | 0.494 | 0.473 | 0.518 | 87 | 97 | 81 |
| Investigations | 0.80 | 0.718 | 0.746 | 0.691 | 94 | 32 | 42 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.688 | 579 | 170 | 355 | 0.601 (348/579) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.813 | 167 | 0.820 (137/167) |
| Diagnosis | 0.574 | 185 | 0.605 (112/185) |
| SeizureFrequency | 0.668 | 127 | 0.142 (18/127) |
| Investigations | 0.810 | 100 | 0.810 (81/100) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.234 | 0.439 |
| Diagnosis | 0.80 | 0.85 | 0.254 | 0.712 |
| SeizureFrequency | 0.80 | 0.66 | 0.074 | 0.164 |
| Investigations | 0.80 | 0.95 | 0.429 | 0.634 |