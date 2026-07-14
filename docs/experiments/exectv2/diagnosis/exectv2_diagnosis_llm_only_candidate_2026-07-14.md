# ExECTv2 Diagnosis Heading/Narrative Decomposer

- JSONL: `experiments\exectv2_diagnosis_llm_only_candidate_dev140_20260714.jsonl`
- Prompt version: `exectv2_hybrid_diagnosis_decomposer_v0.2`
- Pipeline family: `exectv2_hybrid_diagnosis_decomposer`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Draft Diagnosis mentions: 0
- Diagnosis spans: 606
- Mentions raw: 300
- Mentions scored: 300
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Diagnosis Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.465 | 0.548 | 0.403 | 125 | 103 | 185 |

## Source-Near Diagnostic

- Overlap F1=0.650 R=0.565
