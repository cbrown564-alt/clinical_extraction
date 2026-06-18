# ExECTv2 SeizureFrequency Verifier

- JSONL: `experiments\exectv2_llm_sf_verifier_v03_dev140_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_llm_sf_verifier_v0.3`
- Pipeline family: `exectv2_llm_sf_verifier`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Draft SF mentions: 175
- Mentions raw: 196
- Mentions scored: 192
- Evidence-invalid dropped: 4
- Evidence validity rate: 0.9796

## SeizureFrequency Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.602 | 0.594 | 0.610 | 114 | 78 | 73 |

## Source-Near Diagnostic

- Overlap F1=0.702 R=0.711
