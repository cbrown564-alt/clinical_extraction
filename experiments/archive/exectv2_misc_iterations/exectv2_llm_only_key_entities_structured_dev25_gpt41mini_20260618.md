# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_dev25_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_llm_only_key_entities_structured_v0.1`
- Pipeline family: `exectv2_llm_only_key_entities_structured`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 146
- Mentions raw: 152
- Mentions scored: 145
- Evidence-invalid dropped: 7
- Evidence validity rate: 0.9539

## Overall Scores

### semantic

- per-item: P=0.207 R=0.205 F1=0.206 (TP=30 FP=115 FN=116)
- per-letter: P=0.667 R=0.338 F1=0.449 (TP=24 FP=12 FN=47)

### benchmark

- per-item: P=0.159 R=0.158 F1=0.158 (TP=23 FP=122 FN=123)
- per-letter: P=0.625 R=0.282 F1=0.388 (TP=20 FP=12 FN=51)

### phrase_only

- per-item: P=0.386 R=0.384 F1=0.385 (TP=56 FP=89 FN=90)
- per-letter: P=0.778 R=0.592 F1=0.672 (TP=42 FP=12 FN=29)


## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.722 | 105 | 40 | 41 | 0.591 (62/105) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.791 | 36 | 0.861 (31/36) |
| Diagnosis | 0.653 | 32 | 0.469 (15/32) |
| SeizureFrequency | 0.667 | 19 | 0.210 (4/19) |
| Investigations | 0.800 | 18 | 0.667 (12/18) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.264 | 0.562 |
| Diagnosis | 0.80 | 0.85 | 0.204 | 0.452 |
| SeizureFrequency | 0.80 | 0.66 | 0.070 | 0.191 |
| Investigations | 0.80 | 0.95 | 0.267 | 0.522 |