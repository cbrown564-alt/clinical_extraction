# ExECTv2 Key Entities Structured Events

CHECKPOINT ONLY: processed 140 / 140 letters

- JSONL: `experiments\exectv2_six_model_single_call_gemma4_26b_dev140_20260715_structured.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev140`
- Model: `ollama_chat/gemma4:26b`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 5
- Initial parse/schema failures: 5
- Format retries applied: 0
- Format retries rejected: 1
- Clinical events raw: 974
- Mentions raw: 948
- Mentions scored: 932
- Evidence-invalid dropped: 16
- Evidence validity rate: 0.9831

## Overall Scores

### semantic

- per-item: P=0.368 R=0.367 F1=0.368 (TP=343 FP=589 FN=591)
- per-letter: P=0.847 R=0.552 F1=0.669 (TP=232 FP=42 FN=188)

### benchmark

- per-item: P=0.352 R=0.351 F1=0.352 (TP=328 FP=604 FN=606)
- per-letter: P=0.843 R=0.536 F1=0.655 (TP=225 FP=42 FN=195)

### phrase_only

- per-item: P=0.494 R=0.492 F1=0.493 (TP=460 FP=472 FN=474)
- per-letter: P=0.876 R=0.705 F1=0.781 (TP=296 FP=42 FN=124)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.710 P=0.699 R=0.721

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.882 | 0.895 | 0.869 | 179 | 21 | 27 |
| Diagnosis | 0.80 | 0.640 | 0.618 | 0.663 | 197 | 99 | 100 |
| SeizureFrequency | 0.80 | 0.574 | 0.522 | 0.637 | 107 | 98 | 61 |
| Investigations | 0.80 | 0.786 | 0.853 | 0.728 | 99 | 17 | 37 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.702 | 655 | 277 | 279 | 0.695 (455/655) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.693 | 168 | 0.720 (121/168) |
| Diagnosis | 0.657 | 239 | 0.803 (192/239) |
| SeizureFrequency | 0.667 | 134 | 0.343 (46/134) |
| Investigations | 0.905 | 114 | 0.842 (96/114) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.198 | 0.475 |
| Diagnosis | 0.80 | 0.85 | 0.492 | 0.884 |
| SeizureFrequency | 0.80 | 0.66 | 0.204 | 0.444 |
| Investigations | 0.80 | 0.95 | 0.595 | 0.785 |