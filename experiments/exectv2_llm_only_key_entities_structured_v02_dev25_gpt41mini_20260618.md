# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v02_dev25_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_llm_only_key_entities_structured_v0.2`
- Pipeline family: `exectv2_llm_only_key_entities_structured`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 159
- Mentions raw: 167
- Mentions scored: 163
- Evidence-invalid dropped: 4
- Evidence validity rate: 0.9760

## Overall Scores

### semantic

- per-item: P=0.258 R=0.288 F1=0.272 (TP=42 FP=121 FN=104)
- per-letter: P=0.786 R=0.465 F1=0.584 (TP=33 FP=9 FN=38)

### benchmark

- per-item: P=0.209 R=0.233 F1=0.220 (TP=34 FP=129 FN=112)
- per-letter: P=0.750 R=0.380 F1=0.505 (TP=27 FP=9 FN=44)

### phrase_only

- per-item: P=0.387 R=0.431 F1=0.408 (TP=63 FP=100 FN=83)
- per-letter: P=0.824 R=0.592 F1=0.689 (TP=42 FP=9 FN=29)


## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.680 | 105 | 58 | 41 | 0.657 (69/105) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.688 | 32 | 0.875 (28/32) |
| Diagnosis | 0.655 | 37 | 0.513 (19/37) |
| SeizureFrequency | 0.632 | 18 | 0.278 (5/18) |
| Investigations | 0.783 | 18 | 0.944 (17/18) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.172 | 0.467 |
| Diagnosis | 0.80 | 0.85 | 0.283 | 0.737 |
| SeizureFrequency | 0.80 | 0.66 | 0.210 | 0.381 |
| Investigations | 0.80 | 0.95 | 0.522 | 0.667 |