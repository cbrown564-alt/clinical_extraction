# Gan 2026 LLM-Heavy Clinical Frequency Reasoner V2 COMPACT

- JSONL: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v2_compact_2026-06-02.jsonl`
- Pipeline family: `llm_heavy_clinical_frequency_reasoner`
- Prompt version: `gan2026_llm_heavy_clinical_frequency_reasoner_v2_compact`
- Split: `validation` / `gan2026_split_v1`
- Rows: 25
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: LLM-heavy validation development result; deterministic selected-evidence arithmetic and benchmark-aligned layers are side-cars.
- Decision 0006 outcome: `reject`

## Smoke Summary

- Structured records: 25/25
- Parse/schema failures: 0
- Selected evidence valid: 22/25
- Rendering operands present: 24/25
- Arithmetic/rendering traces present: 24/25
- Event evidence valid: 35/37
- Selected-event trace mismatches: 0

## Score Layers

- `raw_llm`: scorable 23, Purist 22/25 (0.8800), Pragmatic 23/25 (0.9200)
- `format_only`: scorable 23, Purist 22/25 (0.8800), Pragmatic 23/25 (0.9200)
- `selected_evidence_arithmetic`: scorable 25, Purist 25/25 (1.0000), Pragmatic 25/25 (1.0000)
- `benchmark_aligned`: scorable 25, Purist 23/25 (0.9200), Pragmatic 24/25 (0.9600)
- `oracle_format_upper_bound`: scorable 23, Purist 22/25 (0.8800), Pragmatic 23/25 (0.9200)

## Decision 0006 Stop Rules

- Raw parser-compatible labels: 23/25
- Raw model-owned Purist: 22/25
- Deterministic selected-evidence arithmetic raw-wrong to correct: 3
- Deterministic selected-evidence arithmetic raw-correct to wrong: 0

## Row Review

- 182: side-car correction; gold `1 per 2 day`; raw `2 per 2 day`; selected-evidence arithmetic `1 per 2 day`; taxonomy `wrong arithmetic/rendering`
- 187: side-car correction; gold `1 per 7 to 9 day`; raw `2 per 63 day with 1 cluster per 7 to 9 day`; selected-evidence arithmetic `1 per 7 to 9 day`; taxonomy `wrong selected fact`
- 338: side-car correction; gold `multiple per month`; raw `many per month`; selected-evidence arithmetic `no seizure frequency reference`; taxonomy `parser/schema issue`

## Failure Taxonomy

- `no raw failure`: 20
- `parser/schema issue`: 1
- `wrong arithmetic/rendering`: 1
- `wrong selected fact`: 3

## Interpretation

The decision-0006 validation25 smoke fails at least one hard stop rule. Do not escalate this v2 prompt to validation50; revise the prompt/schema or keep selected-evidence arithmetic as an explicit deterministic component.
