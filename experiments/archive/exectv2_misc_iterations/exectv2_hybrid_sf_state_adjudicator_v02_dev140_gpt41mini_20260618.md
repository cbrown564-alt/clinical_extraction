# ExECTv2 SeizureFrequency Candidate-Span State Adjudicator

- JSONL: `experiments\exectv2_hybrid_sf_state_adjudicator_v02_dev140_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_hybrid_sf_state_adjudicator_v0.2`
- Pipeline family: `exectv2_hybrid_sf_state_adjudicator`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Draft SF mentions: 175
- Candidate spans: 412
- Mentions raw: 179
- Mentions scored: 179
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## SeizureFrequency Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.672 | 0.687 | 0.658 | 123 | 56 | 64 |

## Source-Near Diagnostic

- Overlap F1=0.760 R=0.743
