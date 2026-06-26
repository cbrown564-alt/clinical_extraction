# ExECTv2 SeizureFrequency Verifier

- JSONL: `experiments\exectv2_llm_sf_verifier_v01_dev25_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_llm_sf_verifier_v0.1`
- Pipeline family: `exectv2_llm_sf_verifier`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Draft SF mentions: 29
- Mentions raw: 35
- Mentions scored: 35
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## SeizureFrequency Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.667 | 0.629 | 0.710 | 22 | 13 | 9 |

## Source-Near Diagnostic

- Overlap F1=0.727 R=0.774
