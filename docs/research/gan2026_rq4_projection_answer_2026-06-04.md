# Gan 2026 RQ4 Projection Answer

Date: 2026-06-04

Status: Final answer for validation-development component mechanics.

## Answer

This report establishes the final projection answer for the validation-development split (`gan2026_split_v1`). By analyzing the follow-up panel and the first-failure attributions, we isolate the specific mechanisms that make projection successful and separate them from broad, regressive projection methods.

The final RQ4 answer is:
1. **Gated Projection Rules are Highly Precise**:
   - `boundary_state_priority` (unknown/unresolved-multiple graph states) achieved **17 W->C (Wrong to Correct) wins with exactly 0 C->W regressions**.
   - `graph_gated_month_bucket_duration` (seizure-free duration mapping) achieved **18 W->C wins with exactly 0 C->W regressions**.
   - Both components prove that gating projection under explicit conditions achieves 100% precision.
2. **Broad Graph Projection is Unsafe**:
   - Replacing the baseline projection logic with the general `state_graph_projection` caused **84 C->W regressions and 0 W->C wins** in the follow-up panel. 
   - General graph traversal lacks a reliable policy for sorting out stale, current, historical, and competing semiology nodes, causing it to over-select historical or inactive events.
3. **Projection Policy is the Core Bottleneck**:
   - The first-failure ownership analysis shows that **152 failures** are owned by `projection_policy` (lack of rule mapping for ambiguous clinical states) rather than candidate or evidence extraction components.
   - We resolved this bottleneck by implementing the **ACD-001 through ACD-010 decisions** in the ambiguous case log, defining explicit mappings for vague cadence, conditional triggers, relative trends, diary dates, non-epileptic symptoms, summary overrides, and multi-semiology relapses.

The practical pipeline recommendation is:
- **Lock the deterministic top candidate** as the primary projection substrate.
- **Deploy gated projection rules** (`boundary_state_priority` and `graph_gated_month_bucket_duration`) under strict metadata preconditions.
- **Utilize the ACD-001 through ACD-010 mapping rules** to resolve clinical ambiguities at the scorer-facing layer, keeping the underlying LLM representations source-near and clinically faithful.

## Supporting Evidence

The conclusions are backed by validation replay matrices and the **2026-06-04 follow-up panel** (654 panel rows over 371 source rows):
- [gan2026_component_projection_followup_panel_2026-06-04.md](file:///Users/cobro/code/clinical-extraction/experiments/gan2026_component_projection_followup_panel_2026-06-04.md)
- [gan2026_target_rows_inspection.md](file:///Users/cobro/code/clinical-extraction/docs/research/gan2026_target_rows_inspection.md)
- [gan2026_ambiguous_case_decision_log.md](file:///Users/cobro/code/clinical-extraction/docs/research/gan2026_ambiguous_case_decision_log.md)

### Component Outcomes

| Component | Panel rows | W->C | C->W | Exact evidence rate | Rationale |
| --- | ---: | ---: | ---: | ---: | --- |
| `boundary_state_priority` | 17 | 17 | 0 | 100% | Resolves unknown/unresolved-multiple graph states with 0 regressions. |
| `graph_gated_month_bucket_duration` | 250 | 18 | 0 | 100% | Corrects seizure-free duration mapping with 0 regressions. |
| `state_graph_projection` | 131 | 0 | 84 | 95.4% | Broad graph projection causes severe regressions. |

### Failure Owners and Hidden Families

The 152 `projection_policy` failures are distributed across several critical clinical hidden families:
- **`seizure_free_overreach` (38 rows owned by `projection_policy`)**: The model incorrectly projects seizure freedom. Fixed by **ACD-009** (previous month active rate priority) and **ACD-007** (non-epileptic symptoms exclusion).
- **`unknown_no_reference_boundary` (39 rows owned by `projection_policy`)**: The model incorrectly assumes a rate where the frequency is unquantified. Fixed by **ACD-004** (conditional-only triggers map to `unknown`).
- **`temporal_conflict` (39 rows owned by `projection_policy`)**: Blending current and historical events. Fixed by **ACD-010** (prioritizing major relapsed rates).

## Transfer Confidence

| Finding | Development confidence | Holdout-transfer confidence | Rationale |
| --- | --- | --- | --- |
| Gated projection rules achieve 100% precision. | High | Moderate-to-high | Preconditions (e.g. presence of duration or boundary nodes) are explicitly checked, minimizing overfit. |
| Broad state-graph projection causes regressions. | High | High | General graph traversal consistently picks stale/historical nodes over current ones. |
| Projection policy issues dominate overall errors. | High | High | The mismatch between messy clinical language and strict benchmark labels is a general challenge. |

## Decision

1. **Substrate**: Use the deterministic top candidate as the baseline.
2. **Selective Gates**: Retain `boundary_state_priority` and `graph_gated_month_bucket_duration` as gated projection modules under explicit graph metadata checks.
3. **ACD Normalization**: Standardise projection normalization using the **ACD-001 through ACD-010 mapping rules** to reconcile natural language ambiguity (e.g., vague count words, conditional-only, bimonthly) to the scorer surface.
4. **Next Component**: Move to RQ5 (deterministic compilation/rendering). With projection policies defined, the final task is ensuring the selected state translates cleanly into a Gan-compatible output.
