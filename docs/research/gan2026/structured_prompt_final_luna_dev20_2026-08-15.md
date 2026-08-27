# Luna `dev20` test of the Gan `final` prompt

Date: 2026-08-15
Status: complete
Protocol: [final Luna `dev20` protocol](structured_prompt_final_protocol_2026-08-15.md)
Decision: [0053](../../decisions/0053-gan-structured-events-final-prompt.md)
Model: `openai/gpt-5.6-luna`
Sample: frozen 20 rows from Gan `dev750`; `test450` not touched

## Verdict

**no large drop.** A predeclared Luna `dev750` protocol is allowed. This does not authorize `test450` or the other five models.

This is not a promotion and not a selected-fill rewrite.

## Frozen sample

Lowest `source_row_index` in each gold-kind pool. Not chosen by `v0.5` error.

- **cluster:** 1317, 1694, 1706, 3224
- **frequency:** 10, 40, 79, 103, 128, 156, 180, 182
- **no_reference:** 11400, 11405
- **seizure_free:** 2907, 2932, 2938, 2965
- **unknown:** 2149, 2166

Indices: 10, 40, 79, 103, 128, 156, 180, 182, 1317, 1694, 1706, 2149, 2166, 2907, 2932, 2938, 2965, 3224, 11400, 11405

## Conditions

| Item | Value |
| :--- | :--- |
| Control | `live` `gan2026_hybrid_structured_events_v0.5` |
| Control source | `live v0.5 (sidecar absent)` |
| Candidate | live Luna, `gan2026_hybrid_structured_events_final` |
| Repair | `hybrid_full_stack` |
| Scorer | Gan Purist primary; Pragmatic secondary |
| Gold at prompt-build time | forbidden |
| Holdout | not touched |
| `final` contract SHA-256 | `171d15bc6d3c2fb178e5ba0d713e75d008d31aceabe25d0163e0c8457a9ebb1d` |

## Counts on the 20-row pool

| Surface | v0.5 | final | delta |
| :--- | ---: | ---: | ---: |
| raw Purist | 19/20 | 19/20 | +0 |
| raw Pragmatic | 19/20 | 19/20 | +0 |
| hybrid Purist | 19/20 | 19/20 | +0 |
| hybrid Pragmatic | 19/20 | 19/20 | +0 |

Call failures: v0.5 0, final 0.
Parse failures: v0.5 0, final 1.

## Hybrid Purist flips

- `180` (frequency): v0.5 True → final False
- `2907` (seizure_free): v0.5 False → final True

## Boundary

Not `test450`. Not a selected prompt. Decision 0043 / 0050 fills stay on `v0.5`. Only the model-facing envelope changed on the `final` arm.
