# Gan 2026 LLM-Heavy Clinical Frequency Reasoner V1

- JSONL: `experiments/gan2026_llm_heavy_clinical_frequency_reasoner_validation50_gpt41mini_v1_2026-06-02.jsonl`
- Pipeline family: `llm_heavy_clinical_frequency_reasoner`
- Prompt version: `gan2026_llm_heavy_clinical_frequency_reasoner_v1`
- Split: `validation` / `gan2026_split_v1`
- Rows: 50
- Model: `openai/gpt-4.1-mini`
- Mode: `live`
- Claim language: LLM-heavy validation development result; benchmark-aligned layer is side-car.

## Smoke Summary

- Structured records: 50/50
- Parse/schema failures: 0
- Selected evidence valid: 48/50
- Event evidence valid: 120/125
- Selected-event trace mismatches: 1

## Score Layers

- `raw_llm`: scorable 45, Purist 41/50 (0.8200), Pragmatic 42/50 (0.8400)
- `format_only`: scorable 45, Purist 41/50 (0.8200), Pragmatic 42/50 (0.8400)
- `selected_evidence_arithmetic`: scorable 50, Purist 48/50 (0.9600), Pragmatic 49/50 (0.9800)
- `benchmark_aligned`: scorable 50, Purist 45/50 (0.9000), Pragmatic 46/50 (0.9200)
- `oracle_format_upper_bound`: scorable 45, Purist 41/50 (0.8200), Pragmatic 42/50 (0.8400)

## Interpretation

This v1 artifact is a schema/prompt smoke surface. It should not be promoted from diagnostic status until validation50 and hard-slice behavior show high schema validity, exact selected evidence, stable selected-event traces, and competitive raw or format-only layers.
