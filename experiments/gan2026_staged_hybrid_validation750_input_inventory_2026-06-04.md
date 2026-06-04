# Gan 2026 Staged Hybrid Validation750 Input Inventory

Inventory of saved validation750 component surfaces for staged assembly. This artifact makes no new model calls and does not authorize locked-test inspection, whole-pipeline promotion, or benchmark-comparable claims.

## Available Components

| Component | Rows | Unique source rows | Ready | Assembly role |
| --- | ---: | ---: | --- | --- |
| `hybrid_reasoner_replay` | 750 | 750 | yes | historical full-validation source candidate replay |
| `selective_safety_floor_gate_v0` | 750 | 750 | yes | full-validation safety floor and rescue gate replay |
| `rq9_selective_action_router_v3` | 750 | 750 | yes | full-validation selective predict/abstain/review policy |

## Missing Inputs

| Component | Needed for | Status |
| --- | --- | --- |
| `rich_selected_state_fact_carrier` | new selected-state union assembly contract | not materialized at validation750 in the current component shape |
| `boundary_v3_selected_state_candidates` | validation750 selected-state union replay | hard-panel artifact exists; validation750 component input not identified |
| `promoted_binary_selective_verifier` | full-validation verifier effect estimate | saved slice exists; full-validation use needs predeclared calls or gating |

## Next Assembly Action

Adapt the available validation750 source-candidate, safety-floor, and router surfaces into assembly rows first; keep the verifier slice separate until a full-validation verifier protocol exists.

## Artifact

- Summary JSON: `experiments/gan2026_staged_hybrid_validation750_input_inventory_2026-06-04.json`
