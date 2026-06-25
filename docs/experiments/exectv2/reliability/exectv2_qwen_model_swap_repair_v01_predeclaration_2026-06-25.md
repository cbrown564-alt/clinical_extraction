# ExECTv2 Qwen Same-Core Repair v01 Predeclaration

- Predeclared: `2026-06-25`
- Candidate id: `exectv2_2call_no_sf_adjudicator_qwen36_repair_v01_dev140`
- Baseline comparator: `exectv2_2call_no_sf_adjudicator_qwen36_dev140`
- Model/runtime: `ollama_chat/qwen3.6:35b` / `ollama_chat_think_false`
- Architecture core: `exectv2_2call_no_sf_adjudicator_model_swap`
- Split/scope: dev140 only
- Row inspection boundary: dev140 row-level inspection allowed; no full-200 or holdout row-level inspection
- Frozen-core rule: live model-owned components remain `structured_key_family_event_ledger` and `diagnosis_decomposer`; deterministic SF projection/unknown suppression/union, Prescription repair, lenses, views, scorer, row count, and gold loader remain unchanged.

## Repair Under Test

This is a Qwen-specific output-contract repair, not a clinical architecture
change:

1. Diagnosis decomposer parser repair may accept format-preserving JSON dialect
   drift already accepted by the structured producer: Python-literal dict/list
   syntax, literal control characters inside strings, and a top-level list of
   mention objects coerced to `{"mentions": [...]}`.
2. The model-facing Diagnosis prompt may add a Qwen compact output-contract
   reminder that the final answer must be one object with only the `mentions`
   key and no analysis text.
3. Runtime-adapter handling may be adjusted only to recover a Qwen response that
   already contains the expected clinical JSON payload but is rejected because
   of output-field wrapping. Any such recovery must be recorded in
   `parse_errors`/metadata as adapter repair.

The repair may not introduce or remove clinical facts beyond parsing the
model-selected JSON payload, evidence validation, existing attribute repair, and
the already frozen deterministic components.

## Promotion Gates

The repaired Qwen dev140 row passes for operational inclusion only if all gates
hold:

- Architecture parity: same frozen core and component graph as the baseline
  model-swap configs.
- Operational stability: `0` call failures and `0` blocking parse/schema
  failures across the completed dev140 assembly row.
- Evidence validity: minimum exact evidence rate remains `>=0.99`.
- Clinical non-regression: overall clinical-headline F1 is at least the
  baseline Qwen `0.8018`, and SeizureFrequency F1 is at least baseline `0.6919`.

If operational stability passes but clinical-headline or SeizureFrequency falls
below baseline, keep the repaired row diagnostic only. If operational stability
fails, keep Qwen diagnostic-only and do not include it in the next full-200
candidate set.

## Reporting

Report:

- call failures and blocking parse/schema failures before and after repair
- parser/adapter repair notes separately from clinical metrics
- overall and family clinical-headline F1
- whether Qwen is eligible for the next same-core full-200 aggregate-only
  predeclaration

