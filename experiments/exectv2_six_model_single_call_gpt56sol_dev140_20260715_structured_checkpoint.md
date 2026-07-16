# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 140 / 140 letters

- JSONL: `experiments\exectv2_six_model_single_call_gpt56sol_dev140_20260715_structured.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev140`
- Model: `openai/gpt-5.6-sol`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 736
- Mentions raw: 842
- Mentions scored: 842
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Overall Scores

### semantic

- per-item: P=0.531 R=0.479 F1=0.503 (TP=447 FP=395 FN=487)
- per-letter: P=0.947 R=0.679 F1=0.791 (TP=285 FP=16 FN=135)

### benchmark

- per-item: P=0.511 R=0.460 F1=0.484 (TP=430 FP=412 FN=504)
- per-letter: P=0.946 R=0.664 F1=0.780 (TP=279 FP=16 FN=141)

### phrase_only

- per-item: P=0.622 R=0.561 F1=0.590 (TP=524 FP=318 FN=410)
- per-letter: P=0.953 R=0.774 F1=0.854 (TP=325 FP=16 FN=95)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.823 P=0.825 R=0.822

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.953 | 0.970 | 0.937 | 193 | 6 | 13 |
| Diagnosis | 0.80 | 0.706 | 0.693 | 0.721 | 214 | 94 | 83 |
| SeizureFrequency | 0.80 | 0.788 | 0.790 | 0.786 | 132 | 35 | 36 |
| Investigations | 0.80 | 0.936 | 0.961 | 0.912 | 124 | 5 | 12 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.826 | 733 | 109 | 201 | 0.783 (574/733) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.901 | 186 | 0.742 (138/186) |
| Diagnosis | 0.751 | 275 | 0.869 (239/275) |
| SeizureFrequency | 0.798 | 146 | 0.527 (77/146) |
| Investigations | 0.951 | 126 | 0.952 (120/126) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.320 | 0.602 |
| Diagnosis | 0.80 | 0.85 | 0.604 | 0.952 |
| SeizureFrequency | 0.80 | 0.66 | 0.410 | 0.683 |
| Investigations | 0.80 | 0.95 | 0.641 | 0.849 |