# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_six_model_single_call_gpt56luna_dev140_20260715_structured.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev140`
- Model: `openai/gpt-5.6-luna`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 727
- Mentions raw: 813
- Mentions scored: 813
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Overall Scores

### semantic

- per-item: P=0.541 R=0.471 F1=0.504 (TP=440 FP=373 FN=494)
- per-letter: P=0.937 R=0.676 F1=0.786 (TP=284 FP=19 FN=136)

### benchmark

- per-item: P=0.518 R=0.451 F1=0.482 (TP=421 FP=392 FN=513)
- per-letter: P=0.936 R=0.659 F1=0.774 (TP=277 FP=19 FN=143)

### phrase_only

- per-item: P=0.628 R=0.547 F1=0.585 (TP=511 FP=302 FN=423)
- per-letter: P=0.944 R=0.764 F1=0.845 (TP=321 FP=19 FN=99)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.829 P=0.848 R=0.812

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.948 | 0.970 | 0.927 | 191 | 6 | 15 |
| Diagnosis | 0.80 | 0.735 | 0.754 | 0.717 | 213 | 68 | 84 |
| SeizureFrequency | 0.80 | 0.776 | 0.778 | 0.774 | 130 | 37 | 38 |
| Investigations | 0.80 | 0.920 | 0.953 | 0.890 | 121 | 6 | 15 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.820 | 716 | 97 | 218 | 0.797 (571/716) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.877 | 182 | 0.753 (137/182) |
| Diagnosis | 0.755 | 267 | 0.895 (239/267) |
| SeizureFrequency | 0.790 | 143 | 0.545 (78/143) |
| Investigations | 0.943 | 124 | 0.944 (117/124) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.270 | 0.547 |
| Diagnosis | 0.80 | 0.85 | 0.634 | 0.961 |
| SeizureFrequency | 0.80 | 0.66 | 0.392 | 0.679 |
| Investigations | 0.80 | 0.95 | 0.677 | 0.871 |