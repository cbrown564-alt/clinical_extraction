# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_six_model_single_call_qwen36_35b_dev140_20260715_structured.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev140`
- Model: `ollama_chat/qwen3.6:35b`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 813
- Mentions raw: 875
- Mentions scored: 873
- Evidence-invalid dropped: 2
- Evidence validity rate: 0.9977

## Overall Scores

### semantic

- per-item: P=0.440 R=0.411 F1=0.425 (TP=384 FP=489 FN=550)
- per-letter: P=0.837 R=0.598 F1=0.697 (TP=251 FP=49 FN=169)

### benchmark

- per-item: P=0.417 R=0.390 F1=0.403 (TP=364 FP=509 FN=570)
- per-letter: P=0.833 R=0.583 F1=0.686 (TP=245 FP=49 FN=175)

### phrase_only

- per-item: P=0.530 R=0.496 F1=0.512 (TP=463 FP=410 FN=471)
- per-letter: P=0.860 R=0.714 F1=0.780 (TP=300 FP=49 FN=120)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.780 P=0.769 R=0.791

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.898 | 0.858 | 0.942 | 194 | 32 | 12 |
| Diagnosis | 0.80 | 0.701 | 0.701 | 0.700 | 208 | 88 | 89 |
| SeizureFrequency | 0.80 | 0.672 | 0.640 | 0.708 | 119 | 67 | 49 |
| Investigations | 0.80 | 0.910 | 0.967 | 0.860 | 117 | 4 | 19 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.775 | 700 | 173 | 234 | 0.769 (538/700) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.841 | 188 | 0.761 (143/188) |
| Diagnosis | 0.715 | 258 | 0.864 (223/258) |
| SeizureFrequency | 0.709 | 135 | 0.444 (60/135) |
| Investigations | 0.926 | 119 | 0.941 (112/119) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.228 | 0.470 |
| Diagnosis | 0.80 | 0.85 | 0.557 | 0.916 |
| SeizureFrequency | 0.80 | 0.66 | 0.252 | 0.485 |
| Investigations | 0.80 | 0.95 | 0.654 | 0.838 |