# ExECTv2 LLM-Only Per-Entity — BirthHistory

- JSONL: `experiments\exectv2_llm_only_per_entity_dev140_gpt41mini_20260617_birthhistory.jsonl`
- Prompt version: `exectv2_llm_only_per_entity_v0.4`
- Entity: `BirthHistory`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140
- Published per-item F1 target: 0.97

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 26
- Mentions scored (evidence-valid): 26
- Evidence-invalid dropped: 0
- Evidence validity rate: 1.0000

## Format Layers

| Layer | Item F1 | Item P | Item R | Letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.561 | 0.615 | 0.516 | 0.762 | 16 | 10 | 15 |
| semantic | 0.281 | 0.308 | 0.258 | 0.471 | 8 | 18 | 23 |
| benchmark | 0.246 | 0.269 | 0.226 | 0.424 | 7 | 19 | 24 |

## Source-Near Candidate Diagnostic (format-blind)

- Overlap recall: 0.806 (TP=25 FN=6)
- Overlap F1: 0.877
- Over-emission (overlap FP): 1
- Attribute agreement on overlaps: 0.480 (12/25)
