# ExECTv2 SeizureFrequency Candidate-Span State Adjudicator

- JSONL: `experiments\exectv2_section_timeline_ablation_dev140_sf_adjudicator_with_timeline.jsonl`
- Prompt version: `exectv2_hybrid_sf_state_adjudicator_v0.5`
- Pipeline family: `exectv2_hybrid_sf_state_adjudicator`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Draft SF mentions: 175
- Candidate spans: 414
- Mentions raw: 194
- Mentions scored: 194
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## SeizureFrequency Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.752 | 0.721 | 0.786 | 132 | 51 | 36 |

## Source-Near Diagnostic

- Overlap F1=0.793 R=0.807
