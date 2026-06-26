# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v05_dev140_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_llm_only_key_entities_structured_v0.5`
- Pipeline family: `exectv2_llm_only_key_entities_structured`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 925
- Mentions raw: 961
- Mentions scored: 919
- Evidence-invalid dropped: 42
- Evidence validity rate: 0.9563

## Overall Scores

### semantic

- per-item: P=0.292 R=0.287 F1=0.289 (TP=268 FP=651 FN=666)
- per-letter: P=0.781 R=0.493 F1=0.604 (TP=207 FP=58 FN=213)

### benchmark

- per-item: P=0.233 R=0.229 F1=0.231 (TP=214 FP=705 FN=720)
- per-letter: P=0.750 R=0.414 F1=0.534 (TP=174 FP=58 FN=246)

### phrase_only

- per-item: P=0.480 R=0.472 F1=0.476 (TP=441 FP=478 FN=493)
- per-letter: P=0.837 R=0.707 F1=0.766 (TP=297 FP=58 FN=123)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.777 | 0.768 | 0.788 | 152 | 46 | 41 |
| Diagnosis | 0.80 | 0.525 | 0.545 | 0.507 | 187 | 156 | 182 |
| SeizureFrequency | 0.80 | 0.558 | 0.577 | 0.540 | 101 | 74 | 86 |
| Investigations | 0.80 | 0.786 | 0.752 | 0.824 | 112 | 37 | 24 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.705 | 653 | 266 | 281 | 0.619 (404/653) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.720 | 171 | 0.749 (128/171) |
| Diagnosis | 0.652 | 238 | 0.508 (121/238) |
| SeizureFrequency | 0.685 | 124 | 0.363 (45/124) |
| Investigations | 0.839 | 120 | 0.917 (110/120) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.198 | 0.422 |
| Diagnosis | 0.80 | 0.85 | 0.269 | 0.756 |
| SeizureFrequency | 0.80 | 0.66 | 0.204 | 0.419 |
| Investigations | 0.80 | 0.95 | 0.601 | 0.766 |