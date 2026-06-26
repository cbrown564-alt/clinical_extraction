# Gan 2026 Staged Hybrid Validation750 No-Call Assembly

This report assembles saved validation750 component artifacts only. It makes no live model calls and does not authorize locked-test inspection, whole-pipeline promotion, verifier full-validation effect estimates, or benchmark-comparable language.

## Coverage

The joined assembly has 750 source rows. Reasoner replay, safety-floor gate, and selective router cover 750, 750, and 750 rows respectively.

## Selective Routing

The router predicts on 716 rows, abstains on 26, and routes 8 to human review.

## Claim Boundary

Validation750 staged assembly over saved component artifacts only. No new model calls, locked-test inspection, whole-pipeline promotion, verifier full-validation effect estimate, or benchmark-comparable claim.

## Artifacts

- Assembly JSONL: `experiments/gan2026_staged_hybrid_assembly_validation750_no_call_2026-06-04.jsonl`
- Summary JSON: `experiments/gan2026_staged_hybrid_assembly_validation750_no_call_2026-06-04.json`

## Metrics

| Metric | Value |
| --- | ---: |
| assembly rows | 750 |
| reasoner rows | 750 |
| safety floor rows | 750 |
| router rows | 750 |
| assembly rows with reasoner | 750 |
| assembly rows with safety floor | 750 |
| assembly rows with router | 750 |
| router predict rows | 716 |
| router abstain rows | 26 |
| router human review rows | 8 |
| safety floor selected evidence exact rows | 750 |
| safety floor selected source ids exist rows | 750 |

## Component Outputs

| Component | Owner | Rows |
| --- | --- | ---: |
| `hybrid_reasoner_replay` | `hybrid_reasoner_replay` | 750 |
| `selective_safety_floor_gate_v0` | `selective_safety_floor_gate_v0` | 750 |
| `rq9_selective_action_router_v3` | `rq9_selective_action_router_v3` | 750 |

## Missing Inputs Kept Out Of This Replay

| Component | Status |
| --- | --- |
| `rich_selected_state_fact_carrier` | not materialized at validation750 in the current component shape |
| `boundary_v3_selected_state_candidates` | hard-panel artifact exists; validation750 component input not identified |
| `promoted_binary_selective_verifier` | saved slice exists; full-validation use needs predeclared calls or gating |

## Prompt Payload Boundary

Historical reasoner prompt payload strings remain in the original saved artifact rows, but are omitted from this assembly artifact. The assembly rows keep compact status, candidate, scoring, gate, and router records only.

## Next Assembly Action

Add the explicit prediction-bearing decision layer over the assembled validation750 component rows, keeping verifier slice evidence separate until a full-validation verifier protocol exists.
