# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v0924_qwencompact_schemarepair_dev25_qwen36_35b_ollama_cuda11435_ctx12288_maxtok3000_20260622.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24_qwen_compact`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `schema-reparse`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 142
- Mentions raw: 137
- Mentions scored: 132
- Evidence-invalid dropped: 5
- Evidence validity rate: 0.9635

## Overall Scores

### semantic

- per-item: P=0.295 R=0.267 F1=0.281 (TP=39 FP=93 FN=107)
- per-letter: P=0.914 R=0.451 F1=0.604 (TP=32 FP=3 FN=39)

### benchmark

- per-item: P=0.288 R=0.260 F1=0.273 (TP=38 FP=94 FN=108)
- per-letter: P=0.912 R=0.437 F1=0.591 (TP=31 FP=3 FN=40)

### phrase_only

- per-item: P=0.523 R=0.473 F1=0.496 (TP=69 FP=63 FN=77)
- per-letter: P=0.939 R=0.648 F1=0.767 (TP=46 FP=3 FN=25)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.974 | 0.950 | 1.000 | 38 | 2 | 0 |
| Diagnosis | 0.80 | 0.790 | 0.821 | 0.762 | 32 | 7 | 10 |
| SeizureFrequency | 0.80 | 0.667 | 0.680 | 0.654 | 17 | 8 | 9 |
| Investigations | 0.80 | 0.864 | 0.792 | 0.950 | 19 | 5 | 1 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.835 | 116 | 16 | 30 | 0.672 (78/116) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.914 | 37 | 0.919 (34/37) |
| Diagnosis | 0.796 | 39 | 0.513 (20/39) |
| SeizureFrequency | 0.772 | 22 | 0.318 (7/22) |
| Investigations | 0.857 | 18 | 0.944 (17/18) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.198 | 0.483 |
| Diagnosis | 0.80 | 0.85 | 0.245 | 0.667 |
| SeizureFrequency | 0.80 | 0.66 | 0.246 | 0.545 |
| Investigations | 0.80 | 0.95 | 0.571 | 0.727 |