# ExECTv2 LLM-Only Per-Entity — Prescription

- JSONL: `experiments\exectv2_llm_only_per_entity_dev140_gpt41mini_20260617_prescription.jsonl`
- Prompt version: `exectv2_llm_only_per_entity_v0.4`
- Entity: `Prescription`
- Split: `dev`
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Letters: 140
- Published per-item F1 target: 0.87

## Gate Summary

- Call failures: 0
- Parse/schema failures: 0
- Mentions raw: 235
- Mentions scored (evidence-valid): 232
- Evidence-invalid dropped: 3
- Evidence validity rate: 0.9872

## Format Layers

| Layer | Item F1 | Item P | Item R | Letter F1 | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| phrase_only | 0.297 | 0.280 | 0.316 | 0.568 | 65 | 167 | 141 |
| semantic | 0.173 | 0.164 | 0.184 | 0.385 | 38 | 194 | 168 |
| benchmark | 0.173 | 0.164 | 0.184 | 0.385 | 38 | 194 | 168 |

## Source-Near Candidate Diagnostic (format-blind)

- Overlap recall: 0.903 (TP=186 FN=20)
- Overlap F1: 0.849
- Over-emission (overlap FP): 46
- Attribute agreement on overlaps: 0.801 (149/186)
