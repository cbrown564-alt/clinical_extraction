# Gan 2026 LLM-Heavy Clinical Frequency Reasoner V2 COMPACT

- JSONL: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation50_gpt41mini_v2_compact_2026-06-03.jsonl`
- Pipeline family: `llm_heavy_clinical_frequency_reasoner`
- Prompt version: `gan2026_llm_heavy_clinical_frequency_reasoner_v2_compact`
- Split: `validation` / `gan2026_split_v1`
- Rows: 50
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: LLM-heavy validation development result; deterministic selected-evidence arithmetic and benchmark-aligned layers are side-cars.
- Decision 0006 outcome: `reject`

## Smoke Summary

- Structured records: 50/50
- Parse/schema failures: 0
- Selected evidence valid: 45/50
- Rendering operands present: 49/50
- Arithmetic/rendering traces present: 49/50
- Event evidence valid: 71/76
- Selected-event trace mismatches: 0

## Score Layers

- `raw_llm`: scorable 46, Purist 42/50 (0.8400), Pragmatic 44/50 (0.8800)
- `format_only`: scorable 47, Purist 43/50 (0.8600), Pragmatic 45/50 (0.9000)
- `selected_evidence_arithmetic`: scorable 50, Purist 50/50 (1.0000), Pragmatic 50/50 (1.0000)
- `benchmark_aligned`: scorable 50, Purist 44/50 (0.8800), Pragmatic 46/50 (0.9200)
- `oracle_format_upper_bound`: scorable 47, Purist 43/50 (0.8600), Pragmatic 45/50 (0.9000)

## Decision 0006 Stop Rules

- Raw parser-compatible labels: 46/50
- Raw model-owned Purist: 42/50
- Deterministic selected-evidence arithmetic raw-wrong to correct: 8
- Deterministic selected-evidence arithmetic raw-correct to wrong: 0

## Row Review

- 182: side-car correction; gold `1 per 2 day`; raw `2 per 2 day`; selected-evidence arithmetic `1 per 2 day`; taxonomy `wrong arithmetic/rendering`
- 187: side-car correction; gold `1 per 7 to 9 day`; raw `2 per 63 day with 1 cluster per 7 to 9 day`; selected-evidence arithmetic `1 per 7 to 9 day`; taxonomy `wrong selected fact`
- 338: side-car correction; gold `multiple per month`; raw `many per month`; selected-evidence arithmetic `multiple per month`; taxonomy `parser/schema issue`
- 678: side-car correction; gold `2 per 4 month`; raw `2 per 4 month with 3 to 6 per 1 day`; selected-evidence arithmetic `2 per 4 month`; taxonomy `parser/schema issue`
- 869: side-car correction; gold `multiple per month`; raw `several per month`; selected-evidence arithmetic `multiple per month`; taxonomy `wrong selected fact`
- 959: side-car correction; gold `1 per 2 month`; raw `2 per 1 month`; selected-evidence arithmetic `1 per 2 month`; taxonomy `wrong arithmetic/rendering`
- 960: side-car correction; gold `1 per 2 month`; raw `2 per month`; selected-evidence arithmetic `1 per 2 month`; taxonomy `wrong arithmetic/rendering`
- 987: side-car correction; gold `1 per 2 month`; raw `2 per 8 week`; selected-evidence arithmetic `1 per 2 month`; taxonomy `wrong arithmetic/rendering`

## Failure Taxonomy

- `no raw failure`: 39
- `parser/schema issue`: 2
- `wrong arithmetic/rendering`: 4
- `wrong selected fact`: 5

## Interpretation

The decision-0006 validation25 smoke fails at least one hard stop rule. Do not escalate this v2 prompt to validation50; revise the prompt/schema or keep selected-evidence arithmetic as an explicit deterministic component.
