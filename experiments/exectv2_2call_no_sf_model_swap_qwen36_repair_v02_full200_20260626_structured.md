# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_2call_no_sf_model_swap_qwen36_repair_v02_full200_20260626_structured.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24_qwen_compact`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `full200`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 200

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 1168
- Mentions raw: 1197
- Mentions scored: 1191
- Evidence-invalid dropped: 6
- Evidence validity rate: 0.9950

## Overall Scores

### semantic

- per-item: P=0.385 R=0.349 F1=0.366 (TP=458 FP=733 FN=854)
- per-letter: P=0.831 R=0.527 F1=0.645 (TP=319 FP=65 FN=286)

### benchmark

- per-item: P=0.364 R=0.330 F1=0.346 (TP=433 FP=758 FN=879)
- per-letter: P=0.825 R=0.507 F1=0.628 (TP=307 FP=65 FN=298)

### phrase_only

- per-item: P=0.514 R=0.467 F1=0.489 (TP=612 FP=579 FN=700)
- per-letter: P=0.865 R=0.689 F1=0.767 (TP=417 FP=65 FN=188)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.751 P=0.725 R=0.779

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.875 | 0.829 | 0.926 | 252 | 52 | 20 |
| Diagnosis | 0.80 | 0.710 | 0.700 | 0.721 | 303 | 121 | 117 |
| SeizureFrequency | 0.80 | 0.606 | 0.571 | 0.645 | 156 | 117 | 86 |
| Investigations | 0.80 | 0.850 | 0.833 | 0.869 | 159 | 32 | 24 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.767 | 960 | 231 | 352 | 0.698 (670/960) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.839 | 260 | 0.777 (202/260) |
| Diagnosis | 0.703 | 347 | 0.867 (301/347) |
| SeizureFrequency | 0.706 | 193 | 0.166 (32/193) |
| Investigations | 0.917 | 160 | 0.844 (135/160) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.245 | 0.477 |
| Diagnosis | 0.80 | 0.85 | 0.507 | 0.910 |
| SeizureFrequency | 0.80 | 0.66 | 0.113 | 0.258 |
| Investigations | 0.80 | 0.95 | 0.579 | 0.798 |