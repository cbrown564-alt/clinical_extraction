# Gan 2026 Agentic Boundary Audit Prompt V2 Hard50

Date: 2026-06-12

## Experiment Unit

- Work class: D1 validation hard50 boundary-audit prompt.
- Rows: 50
- Condition: `boundary_audit_prompt_v2`
- Reference condition: `single_self_consistency_temperature`
- Split: `validation`, manifest `gan2026_split_v1`.
- Surface: predeclared D1 `hard50`.
- Mode: `live`
- Model: `openai/gpt-4.1-mini`
- Prompt version: `gan2026_agentic_boundary_audit_prompt_v2`
- JSONL artifact: `experiments\gan2026_agentic_boundary_audit_prompt_v2_hard50_2026-06-12.jsonl`
- Parser context: disabled; fixed boundary-guide set used for every row.

## Summary

- Model calls attempted: 50
- Decision records: 50
- Call failures: 0
- Reused raw outputs: 0
- Parse/schema/label failures: 0
- Schema/label repair rows: 44
- Exact evidence substrings: 35
- Purist: 38/50
- Pragmatic: 38/50
- Wins vs reference: 8
- Losses vs reference: 2
- Changed labels vs reference: 22
- Changed-label precision: 0.3636
- Boundary demotions: 1
- E2 loss sentinel regressions: 0
- Cluster-burden preservation count: 5

## Gate

- Status: `reject_or_revise_after_hard50`
- Interpretation: Boundary audit prompt v2 did not satisfy the hard50 gate; do not escalate to validation250 or D3 from this condition.

## Claim Boundary

validation-development D1 hard50 only; parser candidates disabled as prompt context, no holdout use, no row-level test inspection, and no benchmark claim

## Rows

| Row | Final | Raw final | Reference | Gold | Purist | Reference Purist | Evidence exact | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| 3356 | `multiple per month` | `multiple per month` | `multiple per month` | `unknown` | yes | yes | yes |  |
| 3528 | `multiple per day` | `multiple per day` | `multiple per day` | `unknown` | yes | yes | yes | audit_field_shape_repaired:active_semiologies_and_burdens |
| 4690 | `multiple per day` | `multiple per hour` | `multiple per day` | `multiple per day` | yes | yes | yes | audit_field_shape_repaired:active_semiologies_and_burdens; final_label_repaired: 'multiple per hour' -> 'multiple per day' |
| 5534 | `multiple per month` | `less than one per month` | `1 per multiple month` | `1 per multiple month` | yes | yes | yes | audit_field_shape_repaired:active_semiologies_and_burdens; final_label_repaired: 'less than one per month' -> 'multiple per month' |
| 5974 | `multiple per month` | `multiple per month` | `seizure free for multiple year` | `unknown` | yes | no | no |  |
| 6077 | `1 per year` | `yearly` | `1 per year` | `unknown` | no | no | yes | final_label_repaired: 'yearly' -> '1 per year' |
| 6094 | `multiple per month` | `multiple per month` | `5 per month` | `3 per month` | no | no | yes | audit_field_shape_repaired:active_semiologies_and_burdens |
| 6131 | `no seizure frequency reference` | `infrequent` | `no seizure frequency reference` | `unknown` | yes | yes | yes | audit_field_shape_repaired:active_semiologies_and_burdens; final_label_repaired: 'infrequent' -> 'no seizure frequency reference' |
| 6153 | `9 per 4 week` | `multiple per month` | `9 per 4 week` | `9 per month` | yes | yes | no | audit_field_shape_repaired:active_semiologies_and_burdens; final_label_repaired: 'multiple per month' -> '9 per 4 week' |
| 6209 | `multiple per day` | `multiple per day` | `multiple per day` | `multiple per day` | yes | yes | yes | audit_field_shape_repaired:active_semiologies_and_burdens |
| 6244 | `1 per week` | `weekly` | `multiple per week` | `unknown` | no | yes | no | audit_field_shape_repaired:active_semiologies_and_burdens; final_label_repaired: 'weekly' -> '1 per week' |
| 6321 | `multiple per year` | `multiple per year` | `2 per year` | `unknown` | yes | no | yes | audit_field_shape_repaired:active_semiologies_and_burdens |
| 6368 | `multiple per day` | `multiple per month` | `3 per 6 week` | `unknown` | yes | no | yes | audit_field_shape_repaired:active_semiologies_and_burdens; final_label_repaired: 'multiple per month' -> 'multiple per day' |
| 6501 | `multiple per day` | `multiple per day` | `unknown` | `unknown` | yes | yes | no |  |
| 6571 | `seizure free for multiple year` | `seizure free` | `seizure free for 4 month` | `unknown` | no | no | no | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 6987 | `no seizure frequency reference` | `infrequent` | `no seizure frequency reference` | `unknown` | yes | yes | no | audit_field_shape_repaired:active_semiologies_and_burdens; final_label_repaired: 'infrequent' -> 'no seizure frequency reference' |
| 7168 | `multiple per month` | `multiple per month` | `2 per year` | `unknown` | yes | no | yes |  |
| 7615 | `no seizure frequency reference` | `3 to 6 per cycle` | `2 per year` | `3 to 7 per month` | no | no | no | audit_field_shape_repaired:active_semiologies_and_burdens; audit_field_shape_repaired:cluster_cadence_and_burden; final_label_repaired: '3 to 6 per cycle' -> 'no seizure frequency reference' |
| 9496 | `6 per 12 month` | `monthly or less` | `6 per 12 month` | `6 per 12 month` | yes | yes | yes | audit_field_shape_repaired:active_semiologies_and_burdens; final_label_repaired: 'monthly or less' -> '6 per 12 month' |
| 9888 | `unknown` | `unknown` | `no seizure frequency reference` | `unknown` | yes | yes | yes | audit_field_shape_repaired:active_semiologies_and_burdens |
| 9937 | `multiple per month` | `multiple per month` | `unknown` | `1 cluster per month, multiple per cluster` | no | no | yes | audit_field_shape_repaired:cluster_cadence_and_burden |
| 9943 | `1 per 4 to 5 week` | `multiple per month` | `unknown` | `1 cluster per 4 to 5 week, multiple per cluster` | no | no | no | audit_field_shape_repaired:cluster_cadence_and_burden; final_label_repaired: 'multiple per month' -> '1 per 4 to 5 week' |
| 9955 | `1 cluster per month, multiple per cluster` | `monthly` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | yes | yes | yes | final_label_repaired: 'monthly' -> '1 cluster per month, multiple per cluster' |
| 10266 | `unknown` | `unknown` | `unknown` | `unknown` | yes | yes | yes |  |
| 10618 | `multiple per day` | `multiple per day` | `multiple per day` | `unknown, 4 to 6 per cluster` | yes | yes | yes | audit_field_shape_repaired:active_semiologies_and_burdens |
| 10677 | `1 cluster per month, multiple per cluster` | `monthly` | `1 per month` | `1 cluster per month, multiple per cluster` | yes | no | no | final_label_repaired: 'monthly' -> '1 cluster per month, multiple per cluster' |
| 10996 | `1 to 2 cluster per month, 4 per cluster` | `one to two per month` | `1 to 2 per month` | `1 to 2 cluster per month, 4 per cluster` | yes | no | yes | audit_field_shape_repaired:cluster_cadence_and_burden; final_label_repaired: 'one to two per month' -> '1 to 2 cluster per month, 4 per cluster' |
| 12422 | `1 per day` | `multiple per day` | `1 per day` | `1 per day` | yes | yes | yes | audit_field_shape_repaired:active_semiologies_and_burdens; final_label_repaired: 'multiple per day' -> '1 per day' |
| 12438 | `1 per day` | `multiple per day` | `1 per day` | `1 per day` | yes | yes | yes | audit_field_shape_repaired:active_semiologies_and_burdens; final_label_repaired: 'multiple per day' -> '1 per day' |
| 12456 | `1 per day` | `multiple per day` | `1 per day` | `1 per day` | yes | yes | yes | audit_field_shape_repaired:active_semiologies_and_burdens; final_label_repaired: 'multiple per day' -> '1 per day' |
| 12460 | `1 per day` | `multiple per day` | `1 per day` | `1 per day` | yes | yes | yes | audit_field_shape_repaired:active_semiologies_and_burdens; final_label_repaired: 'multiple per day' -> '1 per day' |
| 12468 | `1 per day` | `multiple per day` | `1 per day` | `1 per day` | yes | yes | yes | audit_field_shape_repaired:active_semiologies_and_burdens; final_label_repaired: 'multiple per day' -> '1 per day' |
| 13843 | `seizure free for multiple year` | `unknown` | `unknown` | `seizure free for multiple month` | yes | no | no | audit_field_shape_repaired:active_semiologies_and_burdens; final_label_repaired: 'unknown' -> 'seizure free for multiple year' |
| 13858 | `unknown` | `unknown` | `unknown` | `seizure free for multiple month` | no | no | yes | audit_field_shape_repaired:active_semiologies_and_burdens |
| 13889 | `seizure free for multiple year` | `unknown` | `seizure free for multiple year` | `seizure free for multiple month` | yes | yes | no | audit_field_shape_repaired:active_semiologies_and_burdens; final_label_repaired: 'unknown' -> 'seizure free for multiple year' |
| 14025 | `multiple per month` | `multiple per month` | `2 per year` | `unknown` | yes | no | yes | audit_field_shape_repaired:active_semiologies_and_burdens |
| 14076 | `multiple per day` | `multiple per day` | `unknown` | `unknown` | yes | yes | no |  |
| 14810 | `seizure free for multiple year` | `seizure free` | `seizure free for multiple year` | `1 per month` | no | no | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 14821 | `seizure free for multiple year` | `seizure free` | `seizure free for multiple year` | `1 per month` | no | no | yes | final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
| 15168 | `multiple per month` | `occasional` | `no seizure frequency reference` | `multiple per 15 month` | yes | yes | no | audit_field_shape_repaired:active_semiologies_and_burdens; final_label_repaired: 'occasional' -> 'multiple per month' |
| 15193 | `multiple per month` | `multiple per month` | `no seizure frequency reference` | `multiple per 13 month` | yes | yes | yes | audit_field_shape_repaired:active_semiologies_and_burdens |
| 15593 | `1 cluster per 5 day, 2 to 4 per cluster` | `two to four per week` | `1 cluster per 5 day, 2 to 4 per cluster` | `1 cluster per 5 day, 2 to 4 per cluster` | yes | yes | yes | audit_field_shape_repaired:cluster_cadence_and_burden; final_label_repaired: 'two to four per week' -> '1 cluster per 5 day, 2 to 4 per cluster' |
| 15672 | `1 per day` | `multiple per day` | `1 per day` | `1 per day` | yes | yes | no | audit_field_shape_repaired:active_semiologies_and_burdens; audit_field_shape_repaired:cluster_cadence_and_burden; final_label_repaired: 'multiple per day' -> '1 per day' |
| 15834 | `multiple per week` | `multiple per week` | `5 per week` | `5 per week` | no | yes | yes | audit_field_shape_repaired:active_semiologies_and_burdens |
| 2748 | `1 per month` | `monthly` | `1 per month` | `1 per month` | yes | yes | yes | audit_field_shape_repaired:active_semiologies_and_burdens; final_label_repaired: 'monthly' -> '1 per month' |
| 4368 | `5 per 2 month` | `multiple per month` | `5 per 2 month` | `5 per 2 month` | yes | yes | yes | final_label_repaired: 'multiple per month' -> '5 per 2 month' |
| 5921 | `1 per 6 to 8 week` | `once every 6 to 8 weeks` | `1 per 6 to 8 week` | `1 per 6 to 8 week` | yes | yes | yes | audit_field_shape_repaired:cluster_cadence_and_burden; final_label_repaired: 'once every 6 to 8 weeks' -> '1 per 6 to 8 week' |
| 6889 | `multiple per week` | `multiple per week` | `multiple per week` | `multiple per week` | yes | yes | yes | audit_field_shape_repaired:active_semiologies_and_burdens |
| 10386 | `1 cluster per week, 2 to 3 per cluster` | `weekly` | `1 cluster per week, 2 to 3 per cluster` | `1 cluster per week, 2 to 3 per cluster` | yes | yes | yes | audit_field_shape_repaired:cluster_cadence_and_burden; final_label_repaired: 'weekly' -> '1 cluster per week, 2 to 3 per cluster' |
| 11216 | `seizure free for multiple year` | `seizure free` | `seizure free for 4 month` | `unknown` | no | no | no | audit_field_shape_repaired:active_semiologies_and_burdens; final_label_repaired: 'seizure free' -> 'seizure free for multiple year' |
