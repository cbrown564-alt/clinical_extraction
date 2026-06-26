# Gan 2026 Typed Adapter Reasoner Validation50 Error Analysis

- Source JSONL: `experiments/gan2026_llm_only_typed_adapter_reasoner_validation50_gpt41mini_v0_diagnostic_2026-06-02.jsonl`
- CSV: `experiments/gan2026_llm_only_typed_adapter_reasoner_validation50_error_analysis_2026-06-02.csv`
- JSON: `experiments/gan2026_llm_only_typed_adapter_reasoner_validation50_error_analysis_2026-06-02.json`
- Surface: first 50 validation rows under `gan2026_split_v1`.
- Run status: user-approved diagnostic escalation after rejected validation25 gate; not a promotion artifact.
- Claim language: typed-adapter LLM-only architecture diagnostic; deterministic arithmetic is a side-car.

## Headline

The validation50 diagnostic confirms that scoped `JSONAdapter` and typed DSPy fields solve adapter/schema parseability but do not yet solve LLM-owned final-label rendering or evidence copying. The clean decision is reject-for-promotion, revise-for-architecture.

## Metrics

- Structured typed outputs: 50/50
- Adapter parse failures: 0
- Call failures: 0
- Raw parser-compatible labels: 45/50
- Raw model-owned Purist: 42/50
- Format-only Purist: 45/50
- Selected-evidence arithmetic Purist: 49/50
- Benchmark-aligned Purist: 43/50
- Selected evidence exact: 45/50
- Event evidence exact: 79/85
- Selected-event trace mismatches: 0/50
- Rendering operands present: 49/50
- Arithmetic traces present: 38/50

## Failure Families

- `clean_raw_correct`: 29
- `evidence_copying_failure`: 5
- `llm_rendering_or_arithmetic_gap`: 2
- `parser_ready_label_failure`: 3
- `selected_fact_or_semantic_gap`: 1
- `trace_contract_gap`: 10

## Issue Tags

- `benchmark_adapter_changed_label`: 8
- `clean_raw_correct`: 28
- `event_evidence_not_exact`: 5
- `evidence_exactness_failure`: 5
- `format_only_changed_label`: 7
- `missing_arithmetic_trace`: 12
- `missing_rendering_operands`: 1
- `raw_label_not_parser_compatible`: 5
- `raw_label_wrong_purist`: 3
- `selected_evidence_not_exact`: 5
- `sidecar_rescue`: 7

## Rows Needing Review

| Row | Primary family | Gold | Raw | Format-only | Side-car | Tags |
| --- | --- | --- | --- | --- | --- | --- |
| 10 | `parser_ready_label_failure` | `4 per day` | `up to 4 per day` | `4 per day` | `4 per day` | `raw_label_not_parser_compatible`, `sidecar_rescue`, `format_only_changed_label`, `benchmark_adapter_changed_label` |
| 40 | `evidence_copying_failure` | `4 per week` | `up to 4 per week` | `4 per week` | `4 per week` | `evidence_exactness_failure`, `raw_label_not_parser_compatible`, `sidecar_rescue`, `format_only_changed_label`, `benchmark_adapter_changed_label`, `selected_evidence_not_exact`, `event_evidence_not_exact` |
| 79 | `evidence_copying_failure` | `6 to 7 per year` | `6 to 7 per year` | `6 to 7 per year` | `6 to 7 per year` | `evidence_exactness_failure`, `selected_evidence_not_exact`, `event_evidence_not_exact` |
| 103 | `evidence_copying_failure` | `2 to 4 per year` | `2 to 4 per year` | `2 to 4 per year` | `2 to 4 per year` | `evidence_exactness_failure`, `selected_evidence_not_exact`, `event_evidence_not_exact` |
| 128 | `trace_contract_gap` | `17 per month` | `17 per month` | `17 per month` | `17 per month` | `missing_arithmetic_trace` |
| 187 | `trace_contract_gap` | `1 per 7 to 9 day` | `1 per 7 to 9 day` | `1 per 7 to 9 day` | `1 per 7 to 9 day` | `missing_arithmetic_trace` |
| 190 | `parser_ready_label_failure` | `1 per 4 week` | `1 cluster per 4 weeks lasting 1-2 days` | `1 cluster per 4 week lasting 1 to 2 day` | `1 per 4 week` | `raw_label_not_parser_compatible`, `sidecar_rescue`, `format_only_changed_label`, `benchmark_adapter_changed_label` |
| 278 | `trace_contract_gap` | `multiple per week` | `multiple per week` | `multiple per week` | `multiple per week` | `missing_arithmetic_trace` |
| 280 | `trace_contract_gap` | `multiple per day` | `multiple per day` | `multiple per day` | `multiple per day` | `missing_arithmetic_trace` |
| 338 | `trace_contract_gap` | `multiple per month` | `multiple per month` | `multiple per month` | `multiple per month` | `missing_arithmetic_trace` |
| 409 | `evidence_copying_failure` | `1 per month` | `1 per month` | `1 per month` | `1 per month` | `evidence_exactness_failure`, `selected_evidence_not_exact`, `event_evidence_not_exact` |
| 446 | `evidence_copying_failure` | `2 per week` | `up to 2 per week` | `2 per week` | `2 per week` | `evidence_exactness_failure`, `raw_label_not_parser_compatible`, `sidecar_rescue`, `format_only_changed_label`, `benchmark_adapter_changed_label`, `selected_evidence_not_exact`, `event_evidence_not_exact` |
| 467 | `trace_contract_gap` | `9 per month` | `9 per month` | `9 per month` | `9 per month` | `missing_arithmetic_trace` |
| 531 | `trace_contract_gap` | `12 to 30 per 3 month` | `12 to 30 per 3 month` | `12 to 30 per 3 month` | `12 to 30 per 3 month` | `missing_arithmetic_trace` |
| 743 | `parser_ready_label_failure` | `multiple per week` | `frequent per shift` | `frequent per shift` | `no seizure frequency reference` | `raw_label_not_parser_compatible`, `sidecar_rescue`, `benchmark_adapter_changed_label`, `missing_rendering_operands`, `missing_arithmetic_trace` |
| 744 | `trace_contract_gap` | `multiple per week` | `multiple per week` | `multiple per week` | `multiple per week` | `missing_arithmetic_trace` |
| 891 | `trace_contract_gap` | `1 per 2 day` | `1 per 2 day` | `1 per 2 day` | `1 per 2 day` | `missing_arithmetic_trace` |
| 960 | `llm_rendering_or_arithmetic_gap` | `1 per 2 month` | `2 per 1 to 2 month` | `2 per 1 to 2 month` | `1 per 2 month` | `raw_label_wrong_purist`, `sidecar_rescue` |
| 987 | `llm_rendering_or_arithmetic_gap` | `1 per 2 month` | `2 per 1 month` | `2 per month` | `1 per 2 month` | `raw_label_wrong_purist`, `sidecar_rescue`, `format_only_changed_label`, `benchmark_adapter_changed_label` |
| 1094 | `trace_contract_gap` | `3 to 5 per week` | `3 to 5 per week` | `3 to 5 per week` | `3 to 5 per week` | `missing_arithmetic_trace` |
| 1165 | `selected_fact_or_semantic_gap` | `5 to 7 per 3 week` | `seizure free for 6 weeks` | `seizure free for multiple year` | `seizure free for multiple year` | `raw_label_wrong_purist`, `format_only_changed_label`, `benchmark_adapter_changed_label`, `missing_arithmetic_trace` |

## Side-Car Rescue Rows

- Row 10: raw `up to 4 per day` -> selected-evidence arithmetic `4 per day`; gold `4 per day`.
- Row 40: raw `up to 4 per week` -> selected-evidence arithmetic `4 per week`; gold `4 per week`.
- Row 190: raw `1 cluster per 4 weeks lasting 1-2 days` -> selected-evidence arithmetic `1 per 4 week`; gold `1 per 4 week`.
- Row 446: raw `up to 2 per week` -> selected-evidence arithmetic `2 per week`; gold `2 per week`.
- Row 743: raw `frequent per shift` -> selected-evidence arithmetic `no seizure frequency reference`; gold `multiple per week`.
- Row 960: raw `2 per 1 to 2 month` -> selected-evidence arithmetic `1 per 2 month`; gold `1 per 2 month`.
- Row 987: raw `2 per 1 month` -> selected-evidence arithmetic `1 per 2 month`; gold `1 per 2 month`.

## Decision

Reject validation50 promotion. The typed adapter is worth keeping as a scaffold because adapter/schema reliability is excellent, but the result is not clean LLM-only evidence: raw model-owned Purist is 42/50, raw parser compatibility is 45/50, selected evidence exactness is 45/50, and deterministic selected-evidence arithmetic corrects seven raw-wrong rows. The next useful revision should target parser-ready final labels, exact evidence copying, and mandatory compact arithmetic traces before any larger surface.
