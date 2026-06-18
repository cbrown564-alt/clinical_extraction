# ExECTv2 SeizureFrequency Verifier

- JSONL: `experiments\exectv2_llm_sf_verifier_v04_dev140_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_llm_sf_verifier_v0.4`
- Pipeline family: `exectv2_llm_sf_verifier`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Draft SF mentions: 175
- Mentions raw: 210
- Mentions scored: 208
- Evidence-invalid dropped: 2
- Evidence validity rate: 0.9905

## SeizureFrequency Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.623 | 0.591 | 0.658 | 123 | 85 | 64 |

## Source-Near Diagnostic

- Overlap F1=0.729 R=0.770
