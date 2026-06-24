# ExECTv2 SeizureFrequency Candidate-Span State Adjudicator

- JSONL: `experiments\exectv2_v08_full200_currentcode_sf_state_adjudicator_gpt41mini_20260624.jsonl`
- Prompt version: `exectv2_hybrid_sf_state_adjudicator_v0.5`
- Pipeline family: `exectv2_hybrid_sf_state_adjudicator`
- Split: `full_200_authorized`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 200

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Draft SF mentions: 284
- Candidate spans: 504
- Mentions raw: 291
- Mentions scored: 290
- Evidence-invalid dropped: 1
- Evidence validity rate: 0.9966

## SeizureFrequency Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.656 | 0.616 | 0.702 | 170 | 106 | 72 |

## Source-Near Diagnostic

- Overlap F1=0.720 R=0.757
