# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 140 / 140 letters

- JSONL: `experiments\exectv2_2call_no_sf_model_swap_qwen36_repair_v02_dev140_20260625_structured.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24_qwen_compact`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev140`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 817
- Mentions raw: 827
- Mentions scored: 797
- Evidence-invalid dropped: 30
- Evidence validity rate: 0.9637

## Overall Scores

### semantic

- per-item: P=0.393 R=0.340 F1=0.364 (TP=313 FP=484 FN=609)
- per-letter: P=0.830 R=0.536 F1=0.651 (TP=225 FP=46 FN=195)

### benchmark

- per-item: P=0.374 R=0.323 F1=0.347 (TP=298 FP=499 FN=624)
- per-letter: P=0.825 R=0.517 F1=0.635 (TP=217 FP=46 FN=203)

### phrase_only

- per-item: P=0.518 R=0.448 F1=0.480 (TP=413 FP=384 FN=509)
- per-letter: P=0.863 R=0.688 F1=0.766 (TP=289 FP=46 FN=131)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.744 P=0.732 R=0.757

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.871 | 0.819 | 0.930 | 172 | 38 | 13 |
| Diagnosis | 0.80 | 0.719 | 0.719 | 0.719 | 207 | 75 | 81 |
| SeizureFrequency | 0.80 | 0.574 | 0.561 | 0.587 | 101 | 79 | 71 |
| Investigations | 0.80 | 0.843 | 0.864 | 0.823 | 102 | 16 | 22 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.735 | 632 | 165 | 290 | 0.720 (455/632) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.819 | 177 | 0.785 (139/177) |
| Diagnosis | 0.667 | 227 | 0.899 (204/227) |
| SeizureFrequency | 0.668 | 126 | 0.175 (22/126) |
| Investigations | 0.891 | 102 | 0.882 (90/102) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.264 | 0.517 |
| Diagnosis | 0.80 | 0.85 | 0.505 | 0.914 |
| SeizureFrequency | 0.80 | 0.66 | 0.117 | 0.264 |
| Investigations | 0.80 | 0.95 | 0.541 | 0.766 |