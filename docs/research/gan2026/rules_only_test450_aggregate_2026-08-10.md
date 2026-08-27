# Gan 2026 Rules-Only test450 Aggregate (Gate B)

Date: 2026-08-11
Status: complete; Gate B of the test450 aggregate protocol
Row policy: aggregate-only
Model calls: zero

Protocol: [docs/research/gan2026/rules_only_test450_aggregate_protocol_2026-08-10.md](rules_only_test450_aggregate_protocol_2026-08-10.md)
Gate A: [rules_only_validation750_gate_a_2026-08-10.md](rules_only_validation750_gate_a_2026-08-10.md)

Machine artifact: [JSON](../../experiments/gan2026_rules_only_test450_20260810.json)

## Question

What is the Purist accuracy of the Gan rules-only pipeline (no model calls) on the locked `test450` split?

## Result

Aggregate-only. No row text, row index, label, diagnostic, or failure case is reported. Sealed row-level predictions remain under ignored `scratch/holdout/`.

| Measure | Of rendered | Of all 450 rows |
| --- | ---: | ---: |
| Purist correct | 329/450 (0.7311) | 329/450 (0.7311) |
| Pragmatic correct | 341/450 (0.7578) | 341/450 (0.7578) |

Rendered rows (`final_label != "unknown"`): 450
Null rows (`unknown`): 0
Evidence-valid rows: 450

`rendered` uses the rules lane's own convention (`final_label != "unknown"`); the LLM lanes use a different convention (non-null `comparison` block). See `rules_only_reference_refresh_2026-08-10.md`.

## Method

- Pipeline: `deterministic_canonical_pipeline` (`runners/split.py:run_split` -> `_run_deterministic_split`).
- Ablation config: default — all rule groups and portability classes enabled, `disabled_rule_ids` empty.
- Split: `test450` (locked), `gan2026_split_v1` manifest.
- Models: none. Zero LLM calls.

## Claim boundary

Standalone Gan rules-only test450 holdout figure (deterministic pipeline, zero model calls). Not ruleset-matched to the llm_with_rules test450 row (that row replays the 2026-07-31 ruleset through LLM-produced structured events; rules-only has no such repair stages and never did). Not a stage-contribution or leave-one-stage-out measurement. Aggregate-only; no row text, row index, label, diagnostic, or failure case from test450 is included in this artifact.

## Predeclared reporting

Per the protocol, this number is reported as-is with no threshold and no pass/fail criterion.
