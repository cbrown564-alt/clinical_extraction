# Gan 2026 Agentic Direct Boundary Critic Rescue Panel

Date: 2026-06-12

## Experiment Unit

- Work class: D2 validation panel direct-plus-boundary-critic rescue-only.
- Hypothesis: boundary reasoning is useful as a constrained critic over a direct answer, not as a replacement labeler.
- Minimal change: one direct no-tool call plus one boundary critic call.
- Rows: 12
- Condition: `direct_boundary_critic_rescue`
- Reference condition: `single_self_consistency_temperature`
- Split: `validation`, manifest `gan2026_split_v1`.
- Surface: predeclared D2 `panel`.
- Mode: `live`
- Model: `openai/gpt-4.1-mini`
- Prompt version: `gan2026_agentic_direct_boundary_critic_rescue_v1`
- JSONL artifact: `experiments\gan2026_agentic_direct_boundary_critic_rescue_panel_2026-06-12.jsonl`
- Parser context: disabled; fixed boundary-guide set used by the critic.

## Summary

- Model calls attempted: 24
- Direct decision records: 12
- Critic decision records: 6
- Call failures: 0
- Reused raw outputs: 0
- Parse/schema/label failures: 6
- Schema/label repair rows: 8
- Exact evidence substrings: 18
- Direct Purist: 10/12
- Raw critic proposed-label Purist: 0/12
- Gated-final Purist: 10/12
- Gated-final Pragmatic: 10/12
- Wins vs reference: 2
- Losses vs reference: 0
- Changed labels vs reference: 5
- Changed-label precision: 0.4
- Accepted rescue correct: 0
- Accepted action regressions: 0
- Accepted boundary demotions: 0
- Fallback rate: 1.0
- Accepted action counts: `{'fallback': 12}`
- Blocked reasons: `{'fallback_action:keep': 6, 'no_critic_decision': 6}`

## Gate

- Status: `reject_or_revise_before_hard50`
- Interpretation: Direct plus boundary critic did not satisfy the micro-panel gate; do not run D2 hard50 without revising or stopping the live branch.

## Claim Boundary

validation-development D2 micro-panel only; direct no-tool answer plus boundary critic, parser candidates disabled as prompt context, no holdout use, no row-level test inspection, and no benchmark claim

## Rows

| Row | Direct | Critic proposed | Final | Accepted action | Reference | Gold | Purist | Direct Purist | Reference Purist | Notes |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 6368 | `3 per 6 week` | `None` | `3 per 6 week` | `fallback` | `3 per 6 week` | `unknown` | no | no | no | direct:final_label_repaired: 'three per six weeks' -> '3 per 6 week'; fallback_action:keep |
| 7615 | `no seizure frequency reference` | `None` | `no seizure frequency reference` | `fallback` | `2 per year` | `3 to 7 per month` | no | no | no | direct:final_label_repaired: 'multiple per cycle' -> 'no seizure frequency reference'; critic:schema_validation_error: Input should be a valid string; no_critic_decision; critic_evidence_not_exact |
| 10677 | `1 cluster per month, multiple per cluster` | `None` | `1 cluster per month, multiple per cluster` | `fallback` | `1 per month` | `1 cluster per month, multiple per cluster` | yes | yes | no | direct:final_label_repaired: 'brief bursts once a month' -> '1 cluster per month, multiple per cluster'; critic:schema_validation_error: Input should be a valid string; no_critic_decision; critic_evidence_not_exact |
| 10996 | `1 to 2 cluster per month, 4 per cluster` | `None` | `1 to 2 cluster per month, 4 per cluster` | `fallback` | `1 to 2 per month` | `1 to 2 cluster per month, 4 per cluster` | yes | yes | no | direct:final_label_repaired: 'one to two per month clusters with approximately four events over 90 min' -> '1 to 2 cluster per month, 4 per cluster'; critic:schema_validation_error: Input should be a valid string; no_critic_decision; critic_evidence_not_exact |
| 5534 | `multiple per month` | `None` | `multiple per month` | `fallback` | `1 per multiple month` | `1 per multiple month` | yes | yes | yes | fallback_action:keep |
| 6131 | `no seizure frequency reference` | `None` | `no seizure frequency reference` | `fallback` | `no seizure frequency reference` | `unknown` | yes | yes | yes | direct:final_label_repaired: 'infrequent generalised seizures' -> 'no seizure frequency reference'; critic:schema_validation_error: Input should be a valid string; no_critic_decision; critic_evidence_not_exact |
| 15193 | `multiple per month` | `None` | `multiple per month` | `fallback` | `no seizure frequency reference` | `multiple per 13 month` | yes | yes | yes | critic:schema_validation_error: Input should be a valid string; no_critic_decision; critic_evidence_not_exact |
| 15834 | `5 per week` | `None` | `5 per week` | `fallback` | `5 per week` | `5 per week` | yes | yes | yes | fallback_action:keep |
| 3356 | `multiple per month` | `None` | `multiple per month` | `fallback` | `multiple per month` | `unknown` | yes | yes | yes | fallback_action:keep |
| 4690 | `multiple per day` | `None` | `multiple per day` | `fallback` | `multiple per day` | `multiple per day` | yes | yes | yes | direct:final_label_repaired: 'unknown' -> 'multiple per day'; fallback_action:keep |
| 9955 | `1 cluster per month, multiple per cluster` | `None` | `1 cluster per month, multiple per cluster` | `fallback` | `1 cluster per month, multiple per cluster` | `1 cluster per month, multiple per cluster` | yes | yes | yes | direct:final_label_repaired: 'several per month' -> '1 cluster per month, multiple per cluster'; critic:schema_validation_error: Input should be a valid string; no_critic_decision; critic_evidence_not_exact |
| 12422 | `1 per day` | `None` | `1 per day` | `fallback` | `1 per day` | `1 per day` | yes | yes | yes | direct:final_label_repaired: 'nightly generalised convulsions and intermittent tonic seizures four times per year' -> '1 per day'; fallback_action:keep |
