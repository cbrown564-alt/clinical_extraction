# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 140 / 140 letters

- JSONL: `experiments\exectv2_six_model_single_call_gpt41mini_dev140_20260715_structured.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev140`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 963
- Mentions raw: 973
- Mentions scored: 968
- Evidence-invalid dropped: 5
- Evidence validity rate: 0.9949

## Overall Scores

### semantic

- per-item: P=0.396 R=0.410 F1=0.403 (TP=383 FP=585 FN=551)
- per-letter: P=0.831 R=0.586 F1=0.687 (TP=246 FP=50 FN=174)

### benchmark

- per-item: P=0.379 R=0.393 F1=0.386 (TP=367 FP=601 FN=567)
- per-letter: P=0.828 R=0.574 F1=0.678 (TP=241 FP=50 FN=179)

### phrase_only

- per-item: P=0.490 R=0.507 F1=0.498 (TP=474 FP=494 FN=460)
- per-letter: P=0.855 R=0.700 F1=0.770 (TP=294 FP=50 FN=126)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.730 P=0.715 R=0.745

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.853 | 0.847 | 0.859 | 177 | 32 | 29 |
| Diagnosis | 0.80 | 0.639 | 0.622 | 0.657 | 195 | 115 | 102 |
| SeizureFrequency | 0.80 | 0.650 | 0.605 | 0.702 | 118 | 77 | 50 |
| Investigations | 0.80 | 0.854 | 0.895 | 0.816 | 111 | 13 | 25 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.730 | 694 | 274 | 240 | 0.749 (520/694) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.707 | 181 | 0.724 (131/181) |
| Diagnosis | 0.716 | 263 | 0.875 (230/263) |
| SeizureFrequency | 0.682 | 134 | 0.388 (52/134) |
| Investigations | 0.885 | 116 | 0.922 (107/116) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.184 | 0.455 |
| Diagnosis | 0.80 | 0.85 | 0.536 | 0.893 |
| SeizureFrequency | 0.80 | 0.66 | 0.280 | 0.530 |
| Investigations | 0.80 | 0.95 | 0.641 | 0.791 |