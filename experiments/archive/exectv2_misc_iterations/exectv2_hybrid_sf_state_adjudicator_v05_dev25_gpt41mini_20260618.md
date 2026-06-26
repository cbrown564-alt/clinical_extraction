# ExECTv2 SeizureFrequency Candidate-Span State Adjudicator

- JSONL: `experiments\exectv2_hybrid_sf_state_adjudicator_v05_dev25_gpt41mini_20260618.jsonl`
- Prompt version: `exectv2_hybrid_sf_state_adjudicator_v0.5`
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
| 0.80 | 0.918 | 0.933 | 0.903 | 28 | 2 | 3 |

## Source-Near Diagnostic

- Overlap F1=0.918 R=0.903
