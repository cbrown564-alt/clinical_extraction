# Gan 2026 Agentic Boundary Audit Prompt V2 Panel

Date: 2026-06-12

## Experiment Unit

- Work class: D1 validation panel boundary-audit prompt.
- Rows: 12
- Condition: `boundary_audit_prompt_v2`
- Reference condition: `single_self_consistency_temperature`
- Split: `validation`, manifest `gan2026_split_v1`.
- Surface: predeclared D1 `panel`.
- Mode: `reuse`
- Model: `openai/gpt-4.1-mini`
- Prompt version: `gan2026_agentic_boundary_audit_prompt_v2`
- JSONL artifact: `experiments\gan2026_agentic_boundary_audit_prompt_v2_panel_2026-06-12.jsonl`
- Parser context: disabled; fixed boundary-guide set used for every row.

## Summary

- Model calls attempted: 12
- Decision records: 12
- Call failures: 0
- Reused raw outputs: 12
- Parse/schema/label failures: 0
- Schema/label repair rows: 11
- Exact evidence substrings: 10
- Purist: 10/12
- Pragmatic: 10/12
- Wins vs reference: 3
- Losses vs reference: 1
- Changed labels vs reference: 7
- Changed-label precision: 0.4286
- Boundary demotions: 1
- E2 loss sentinel regressions: 0
- Cluster-burden preservation count: 3

## Gate

- Status: `pass_panel_gate`
- Interpretation: Boundary audit prompt v2 passed the predeclared micro-panel gate; hard50 is permitted as the next D1 surface.

## Claim Boundary

validation-development D1 micro-panel only; parser candidates disabled as prompt context, no holdout use, no row-level test inspection, and no benchmark claim

## Rows

| Row | Final | Raw final | Reference | Gold | Purist | Reference Purist | Evidence exact | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| 6368 | `multiple per day` | `multiple per month` | `3 per 6 week` | `unknown` | yes | no | yes | audit_field_shape_repaired:active_semiologies_and_burdens; final_label_repaired: 'multiple per month' -> 'multiple per day' |
| 7615 | `no seizure frequency reference` | `3 to 6 per cycle` | `2 per year` | `3 to 7 per month` | no | no | no | audit_field_shape_repaired:active_semiologies_and_burdens; audit_field_shape_repaired:cluster_cadence_and_burden; final_label_repaired: '3 to 6 per cycle' -> 'no seizure frequency reference' |
| 10677 | `1 cluster per month, multiple per cluster` | `monthly` | `1 per month` | `1 cluster per month, multiple per cluster` | yes | no | no | final_label_repaired: 'monthly' -> '1 cluster per month, multiple per cluster' |
| 10996 | `1 to 2 cluster per month, 4 per cluster` | `one to two per month` | `1 to 2 per month` | `1 to 2 cluster per month, 4 per cluster` | yes | no | yes | audit_field_shape_repaired:cluster_cadence_and_burden; final_label_repaired: 'one to two per month' -> '1 to 2 cluster per month, 4 per cluster' |
| 5534 | `multiple per month` | `less than one per month` | `1 per multiple month` | `1 per multiple month` | yes | yes | yes | audit_field_shape_repaired:active_semiologies_and_burdens; final_label_repaired: 'less than one per month' -> 'multiple per month' |
| 6131 | `no seizure frequency reference` | `infrequent` | `no seizure frequency reference` | `unknown` | yes | yes | yes | audit_field_shape_repaired:active_semiologies_and_burdens; final_label_repaired: 'infrequent' -> 'no seizure frequency reference' |
| 15193 | `multiple per month` | `multiple per month` | `no seizure frequency reference` | `multiple per 13 month` | yes | yes | yes | audit_field_shape_repaired:active_semiologies_and_burdens |
| 15834 | `multiple per week` | `multiple per week` | `5 per week` | `5 per week` | no | yes | yes | audit_field_shape_repaired:active_semiologies_and_burdens |
| 3356 | `multiple per month` | `multiple per month` | `multiple per month` | `unknown` | yes | yes | yes |  |
| 4690 | `multiple per day` | `multiple per hour` | `multiple per day` | `multiple per day` | yes | yes | yes | audit_field_shape_repaired:active_semiologies_and_burdens; final_label_repaired: 'multiple per hour' -> 'multiple per day' |
| 9955 | `1 cluster per month, multiple per cluster` | `monthly` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | yes | yes | yes | final_label_repaired: 'monthly' -> '1 cluster per month, multiple per cluster' |
| 12422 | `1 per day` | `multiple per day` | `1 per day` | `1 per day` | yes | yes | yes | audit_field_shape_repaired:active_semiologies_and_burdens; final_label_repaired: 'multiple per day' -> '1 per day' |
