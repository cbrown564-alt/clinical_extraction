# Gan 2026 LLM-Heavy Clinical Frequency Reasoner V0

- JSONL: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation25_gpt41mini_v0_2026-06-02.jsonl`
- Pipeline family: `llm_heavy_clinical_frequency_reasoner`
- Prompt version: `gan2026_llm_heavy_clinical_frequency_reasoner_v0`
- Split: `validation` / `gan2026_split_v1`
- Rows: 25
- Model: `openai/gpt-4.1-mini`
- Mode: `saved-output-schema-replay`
- Claim language: LLM-heavy validation development result; benchmark-aligned layer is side-car.

## Smoke Summary

- Structured records: 24/25
- Parse/schema failures: 1
- Selected evidence valid: 18/25
- Event evidence valid: 42/47
- Selected-event trace mismatches: 0

## Score Layers

- `raw_llm`: scorable 0, Purist 0/25 (0.0000), Pragmatic 0/25 (0.0000)
- `format_only`: scorable 11, Purist 10/25 (0.4000), Pragmatic 10/25 (0.4000)
- `selected_evidence_arithmetic`: scorable 24, Purist 23/25 (0.9200), Pragmatic 23/25 (0.9200)
- `benchmark_aligned`: scorable 24, Purist 13/25 (0.5200), Pragmatic 13/25 (0.5200)
- `oracle_format_upper_bound`: scorable 11, Purist 10/25 (0.4000), Pragmatic 10/25 (0.4000)

## Interpretation

This v0 artifact is a schema/prompt smoke surface. It should not be promoted from diagnostic status until validation50 and hard-slice behavior show high schema validity, exact selected evidence, stable selected-event traces, and competitive raw or format-only layers.
