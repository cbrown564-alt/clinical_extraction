# ExECTv2 SeizureFrequency Candidate-Span State Adjudicator

- JSONL: `experiments\exectv2_hybrid_sf_state_adjudicator_v03_dev140_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_hybrid_sf_state_adjudicator_v0.3`
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
- Mentions raw: 195
- Mentions scored: 195
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## SeizureFrequency Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.681 | 0.667 | 0.695 | 130 | 65 | 57 |

## Source-Near Diagnostic

- Overlap F1=0.770 R=0.786
