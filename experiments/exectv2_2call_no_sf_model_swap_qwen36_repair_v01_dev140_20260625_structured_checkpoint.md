# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 50 / 140 letters

- JSONL: `experiments\exectv2_2call_no_sf_model_swap_qwen36_repair_v01_dev140_20260625_structured.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24_qwen_compact`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev140`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 50

## Gate Summary

- Call failures: 0
- Parse/schema failures: 2
- Clinical events raw: 288
- Mentions raw: 277
- Mentions scored: 267
- Evidence-invalid dropped: 10
- Evidence validity rate: 0.9639

## Overall Scores

### semantic

- per-item: P=0.352 R=0.285 F1=0.315 (TP=94 FP=173 FN=236)
- per-letter: P=0.842 R=0.460 F1=0.595 (TP=69 FP=13 FN=81)

### benchmark

- per-item: P=0.341 R=0.276 F1=0.305 (TP=91 FP=176 FN=239)
- per-letter: P=0.842 R=0.460 F1=0.595 (TP=69 FP=13 FN=81)

### phrase_only

- per-item: P=0.472 R=0.382 F1=0.422 (TP=126 FP=141 FN=204)
- per-letter: P=0.871 R=0.587 F1=0.701 (TP=88 FP=13 FN=62)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.788 P=0.795 R=0.782

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.897 | 0.921 | 0.875 | 70 | 6 | 10 |
| Diagnosis | 0.80 | 0.787 | 0.784 | 0.789 | 75 | 19 | 20 |
| SeizureFrequency | 0.80 | 0.566 | 0.556 | 0.577 | 30 | 24 | 22 |
| Investigations | 0.80 | 0.860 | 0.889 | 0.833 | 40 | 5 | 8 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.724 | 216 | 51 | 114 | 0.745 (161/216) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.822 | 67 | 0.776 (52/67) |
| Diagnosis | 0.646 | 74 | 0.892 (66/74) |
| SeizureFrequency | 0.626 | 36 | 0.250 (9/36) |
| Investigations | 0.867 | 39 | 0.872 (34/39) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.184 | 0.492 |
| Diagnosis | 0.80 | 0.85 | 0.437 | 0.825 |
| SeizureFrequency | 0.80 | 0.66 | 0.122 | 0.261 |
| Investigations | 0.80 | 0.95 | 0.489 | 0.667 |