# ExECTv2 Investigations Verifier

- JSONL: `experiments\exectv2_section_timeline_ablation_dev140_inv_verifier_with_timeline.jsonl`
- Prompt version: `exectv2_llm_investigations_verifier_v0.1`
- Pipeline family: `exectv2_llm_investigations_verifier`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Draft Investigations mentions: 150
- Mentions raw: 141
- Mentions scored: 140
- Evidence-invalid dropped: 1
- Evidence validity rate: 0.9929

## Investigations Clinical-Recovery Headline

| Target F1 | F1 | P | R | TP | FP | FN |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.80 | 0.877 | 0.864 | 0.890 | 121 | 19 | 15 |
