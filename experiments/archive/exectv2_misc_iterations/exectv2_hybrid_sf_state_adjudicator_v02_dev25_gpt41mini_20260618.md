# ExECTv2 SeizureFrequency Candidate-Span State Adjudicator

- JSONL: `experiments\exectv2_hybrid_sf_state_adjudicator_v02_dev25_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_hybrid_sf_state_adjudicator_v0.2`
- Pipeline family: `exectv2_hybrid_sf_state_adjudicator`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 25

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Draft SF mentions: 29
- Candidate spans: 79
- Mentions raw: 30
- Mentions scored: 30
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## SeizureFrequency Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.951 | 0.967 | 0.935 | 29 | 1 | 2 |

## Source-Near Diagnostic

- Overlap F1=0.951 R=0.935
