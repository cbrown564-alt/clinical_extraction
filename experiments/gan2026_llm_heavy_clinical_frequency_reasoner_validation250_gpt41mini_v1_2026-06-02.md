# Gan 2026 LLM-Heavy Clinical Frequency Reasoner V1

- JSONL: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation250_gpt41mini_v1_2026-06-02.jsonl`
- Pipeline family: `llm_heavy_clinical_frequency_reasoner`
- Prompt version: `gan2026_llm_heavy_clinical_frequency_reasoner_v1`
- Split: `validation` / `gan2026_split_v1`
- Rows: 250
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: LLM-heavy validation development result; benchmark-aligned layer is side-car.

## Smoke Summary

- Structured records: 237/250
- Parse/schema failures: 13
- Selected evidence valid: 230/250
- Event evidence valid: 508/535
- Selected-event trace mismatches: 9

## Score Layers

- `raw_llm`: scorable 213, Purist 188/250 (0.7520), Pragmatic 195/250 (0.7800)
- `format_only`: scorable 213, Purist 188/250 (0.7520), Pragmatic 195/250 (0.7800)
- `selected_evidence_arithmetic`: scorable 237, Purist 219/250 (0.8760), Pragmatic 225/250 (0.9000)
- `benchmark_aligned`: scorable 237, Purist 204/250 (0.8160), Pragmatic 213/250 (0.8520)
- `oracle_format_upper_bound`: scorable 213, Purist 188/250 (0.7520), Pragmatic 195/250 (0.7800)

## Interpretation

This v1 artifact is a schema/prompt smoke surface. It should not be promoted from diagnostic status until validation50 and hard-slice behavior show high schema validity, exact selected evidence, stable selected-event traces, and competitive raw or format-only layers.
