# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 140 / 140 letters

- JSONL: `experiments\exectv2_2call_no_sf_model_swap_qwen36_dev140_20260625_structured.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24_qwen_compact`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev140`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 1
- Parse/schema failures: 1
- Clinical events raw: 836
- Mentions raw: 848
- Mentions scored: 810
- Evidence-invalid dropped: 38
- Evidence validity rate: 0.9552

## Overall Scores

### semantic

- per-item: P=0.351 R=0.308 F1=0.328 (TP=284 FP=526 FN=638)
- per-letter: P=0.811 R=0.469 F1=0.594 (TP=197 FP=46 FN=223)

### benchmark

- per-item: P=0.333 R=0.293 F1=0.312 (TP=270 FP=540 FN=652)
- per-letter: P=0.805 R=0.452 F1=0.579 (TP=190 FP=46 FN=230)

### phrase_only

- per-item: P=0.484 R=0.425 F1=0.453 (TP=392 FP=418 FN=530)
- per-letter: P=0.853 R=0.633 F1=0.727 (TP=266 FP=46 FN=154)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.724 P=0.709 R=0.740

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.835 | 0.788 | 0.886 | 164 | 44 | 21 |
| Diagnosis | 0.80 | 0.719 | 0.702 | 0.736 | 212 | 84 | 76 |
| SeizureFrequency | 0.80 | 0.534 | 0.522 | 0.546 | 94 | 86 | 78 |
| Investigations | 0.80 | 0.835 | 0.876 | 0.798 | 99 | 14 | 25 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.730 | 632 | 178 | 290 | 0.701 (443/632) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.796 | 170 | 0.771 (131/170) |
| Diagnosis | 0.674 | 235 | 0.872 (205/235) |
| SeizureFrequency | 0.668 | 126 | 0.143 (18/126) |
| Investigations | 0.875 | 101 | 0.881 (89/101) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.201 | 0.432 |
| Diagnosis | 0.80 | 0.85 | 0.499 | 0.905 |
| SeizureFrequency | 0.80 | 0.66 | 0.096 | 0.225 |
| Investigations | 0.80 | 0.95 | 0.424 | 0.627 |