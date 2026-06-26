# ExECTv2 Key Entities Structured Events

- JSONL: `experiments\exectv2_llm_only_key_entities_structured_v04_dev25_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_llm_only_key_entities_structured_v0.4`
- Pipeline family: `exectv2_llm_only_key_entities_structured`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Clinical events raw: 153
- Mentions raw: 164
- Mentions scored: 159
- Evidence-invalid dropped: 5
- Evidence validity rate: 0.9695

## Overall Scores

### semantic

- per-item: P=0.283 R=0.308 F1=0.295 (TP=45 FP=114 FN=101)
- per-letter: P=0.795 R=0.493 F1=0.609 (TP=35 FP=9 FN=36)

### benchmark

- per-item: P=0.245 R=0.267 F1=0.256 (TP=39 FP=120 FN=107)
- per-letter: P=0.769 R=0.422 F1=0.545 (TP=30 FP=9 FN=41)

### phrase_only

- per-item: P=0.428 R=0.466 F1=0.446 (TP=68 FP=91 FN=78)
- per-letter: P=0.833 R=0.634 F1=0.720 (TP=45 FP=9 FN=26)


## Key Clinical-Recovery Headlines

| Entity | Target headline F1 | F1 | P | R | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.900 | 0.857 | 0.947 | 36 | 6 | 2 |
| Diagnosis | 0.80 | 0.460 | 0.433 | 0.491 | 26 | 34 | 27 |
| SeizureFrequency | 0.80 | 0.644 | 0.679 | 0.613 | 19 | 9 | 12 |
| Investigations | 0.80 | 0.837 | 0.783 | 0.900 | 18 | 5 | 2 |

## Diagnostic Scoring Ladder

| Layer | Item F1 | TP | FP | FN | Attribute agreement |
| --- | ---: | ---: | ---: | ---: | ---: |
| source_near | 0.728 | 111 | 48 | 35 | 0.694 (77/111) |

| Entity | Source-near F1 | Overlap TP | Attribute agreement |
| --- | ---: | ---: | ---: |
| Prescription | 0.681 | 32 | 0.906 (29/32) |
| Diagnosis | 0.697 | 38 | 0.447 (17/38) |
| SeizureFrequency | 0.746 | 22 | 0.591 (13/22) |
| Investigations | 0.884 | 19 | 0.947 (18/19) |

## Per-Entity Semantic F1

| Entity | Goal item F1 | Published item F1 | Item F1 | Letter F1 |
| --- | ---: | ---: | ---: | ---: |
| Prescription | 0.80 | 0.87 | 0.192 | 0.516 |
| Diagnosis | 0.80 | 0.85 | 0.202 | 0.606 |
| SeizureFrequency | 0.80 | 0.66 | 0.441 | 0.667 |
| Investigations | 0.80 | 0.95 | 0.558 | 0.667 |