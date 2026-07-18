# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_six_model_single_call_gemma4_26b_dev140_20260715_structured.jsonl`
- Prompt version: `exectv2_hybrid_key_family_event_ledger_v0.9.24`
- Pipeline family: `exectv2_hybrid_key_family_event_ledger`
- Split: `dev140`
- Model: `ollama_chat/gemma4:26b`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 2
- Initial parse/schema failures: 5
- Format retries applied: 0
- Format retries rejected: 1
- Clinical events raw: 1002
- Mentions raw: 978
- Mentions scored: 961
- Evidence-invalid dropped: 17
- Evidence validity rate: 0.9826

## Overall Scores

### semantic

- per-item: P=0.368 R=0.379 F1=0.374 (TP=354 FP=607 FN=580)
- per-letter: P=0.850 R=0.564 F1=0.678 (TP=237 FP=42 FN=183)

### benchmark

- per-item: P=0.352 R=0.362 F1=0.357 (TP=338 FP=623 FN=596)
- per-letter: P=0.846 R=0.548 F1=0.665 (TP=230 FP=42 FN=190)

### phrase_only

- per-item: P=0.492 R=0.506 F1=0.499 (TP=473 FP=488 FN=461)
- per-letter: P=0.878 R=0.719 F1=0.791 (TP=302 FP=42 FN=118)


## Key Clinical-Recovery Headlines

- Canonical overall (`clinical_headline`, Diagnosis=`concept_negation`): F1=0.721 P=0.700 R=0.744

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.888 | 0.892 | 0.883 | 182 | 22 | 24 |
| Diagnosis | 0.80 | 0.650 | 0.619 | 0.683 | 203 | 102 | 94 |
| SeizureFrequency | 0.80 | 0.590 | 0.528 | 0.667 | 112 | 100 | 56 |
| Investigations | 0.80 | 0.805 | 0.858 | 0.757 | 103 | 17 | 33 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.716 | 678 | 283 | 256 | 0.692 (469/678) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.695 | 171 | 0.714 (122/171) |
| Diagnosis | 0.673 | 248 | 0.806 (200/248) |
| SeizureFrequency | 0.688 | 141 | 0.333 (47/141) |
| Investigations | 0.922 | 118 | 0.848 (100/118) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.195 | 0.475 |
| Diagnosis | 0.80 | 0.85 | 0.505 | 0.898 |
| SeizureFrequency | 0.80 | 0.66 | 0.200 | 0.444 |
| Investigations | 0.80 | 0.95 | 0.617 | 0.803 |