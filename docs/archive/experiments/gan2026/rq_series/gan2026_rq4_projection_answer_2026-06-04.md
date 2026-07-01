> **Superseded for navigation —** canonical summary: [`COMPONENT_MECHANICS_CANON.md`](../COMPONENT_MECHANICS_CANON.md). Full detail retained below.

# Gan 2026 RQ4 Projection Answer

Date: 2026-06-04

Status: final validation-development answer for LLM component mechanics. This is
not a holdout-transfer, production, or benchmark-comparable claim.

## Answer

RQ4 is answered for saved validation-development replay:

```text
Projection works when it is narrow, gated, and metadata-explicit. Broad graph
projection and unconstrained LLM label projection are negative results.
```

The 2026-06-04 follow-up panel is decisive. Two gated projection policies show
high-precision selective value:

- `boundary_state_priority`: 17 panel rows, 17 W->C, 0 C->W, 17 exact-evidence
  rows.
- `graph_gated_month_bucket_duration`: 250 panel rows, 18 W->C target
  corrections, 0 C->W, 250 exact-evidence rows, and 0 changed labels across
  its 232-row regression panel.

Broad replacement policies fail the component question:

- `state_graph_projection`: 131 panel rows, 0 W->C, 84 C->W.
- `hybrid_adjudicator_raw`: 61 panel rows, 0 W->C, 8 C->W.
- `llm_candidate_selector_raw`: 61 panel rows, 7 W->C, 49 C->W.

Projection policy is the largest remaining first-failure owner in the panel:
152 rows, including 93 `current_vs_historical`, 74 `competing_semiologies`, 55
`rate_bucket_or_denominator`, 49 `benchmark_format_convention`, 43
`seizure_free_duration`, 42 `cluster_burden`, 41 `uncertainty_or_ambiguity`, 39
`unknown_no_reference_boundary`, and 38 `unknown_boundary` rows.

## Claim Boundary

Supporting artifacts:

- ``
- ``
- `experiments/gan2026_component_projection_followup_panel_2026-06-04.md`
- ``
- ``
- `experiments/gan2026_rq4_projection_decision_matrix_2026-06-03.jsonl`

All evidence comes from saved validation artifacts under `gan2026_split_v1`.
Locked holdout rows were not used for this answer. The ACD projection policies
are validation-development policy decisions; future holdout-facing use still
requires a frozen predeclared audit.

## LLM/Projection Component Trade-Offs

| Component | Panel rows | W->C | C->W | Exact evidence | Interpretation |
| --- | ---: | ---: | ---: | ---: | --- |
| `boundary_state_priority` | 17 | 17 | 0 | 17 | Strong narrow projection gate for boundary/unresolved states. |
| `graph_gated_month_bucket_duration` | 250 | 18 | 0 | 250 | Strong narrow duration gate with regression panel. |
| `competing_frequency_uncertainty` | 1 | 1 | 0 | 1 | Promising but too small for a broad claim. |
| `claim_table_final_query` | 38 | 0 | 0 | 38 | Diagnostic selected-state surface. |
| `llm_heavy_selected_fact` | 95 | 0 | 0 | 94 | Diagnostic selected-fact surface. |
| `hybrid_adjudicator_raw` | 61 | 0 | 8 | 61 | Exact evidence but unsafe label projection. |
| `llm_candidate_selector_raw` | 61 | 7 | 49 | 61 | Selective rescues overwhelmed by regressions. |
| `state_graph_projection` | 131 | 0 | 84 | 125 | Negative broad replacement result. |

## Deterministic Baseline Role

The deterministic top candidate remains the safety floor and regression-risk
reference. The RQ4 answer is not that deterministic projection is the research
solution; it is that LLM/graph projection should only spend the safety floor
under explicit metadata gates with exact evidence and changed-row accounting.

## Row-Level Mechanism Examples

`source_row_index=278`, gold `multiple per week`: boundary-state priority
correctly projects active recurring seizure burden instead of stale
seizure-free overreach. Projection owns the conversion from source-near
"multiple times per week" to Gan-compatible syntax.

`source_row_index=338`, gold `multiple per month`: the policy selects the
active cluster/frequency state rather than treating competing context as
non-decisive.

`source_row_index=744`, gold `multiple per week`: the gated projection chooses
the most-weekday absence pattern over a lower or stale frequency node.

`source_row_index=3118`, `3137`, `4839`, `4842`, and `4951`: the
month-bucket-duration gate maps seizure-free duration states to `seizure free
for multiple month` without changing the 232-row regression panel.

`source_row_index=1695`, gold `multiple per month`: the LLM selected exact
zero-current-month evidence, but projection policy must prioritize the previous
month's active burden over a short current-month zero window. This is captured
by ACD-009.

`source_row_index=1363`, gold `3 per day`: multi-semiology projection must
prioritize recent major relapsed events over minor baseline auras. This is
captured by ACD-010.

## Hidden-Family Readout

Projection policy is most visible in these families:

- `current_vs_historical`: 93 projection-policy rows.
- `competing_semiologies`: 74 projection-policy rows.
- `rate_bucket_or_denominator`: 55 projection-policy rows.
- `benchmark_format_convention`: 49 projection-policy rows.
- `cluster_or_diary`: 46 projection-policy rows.
- `seizure_free_duration`: 43 projection-policy rows.
- `cluster_burden`: 42 projection-policy rows.
- `uncertainty_or_ambiguity`: 41 projection-policy rows.
- `temporal_conflict`: 39 projection-policy rows.
- `unknown_no_reference_boundary`: 39 projection-policy rows.
- `unknown_boundary`: 38 projection-policy rows.
- `seizure_free_overreach`: 38 projection-policy rows.

The ACD decision log now records stable interpretation rules for the recurring
projection ambiguities. ACD-001 and ACD-002 classify projection-compatible
phrases such as `multiple times per week` and `multiple per shift`. The
predeclared production projection-policy scope covers ACD-003 through ACD-010:
vague count adjectives, conditional-only triggers, relative-only trends, diary
date lists, non-epileptic events, qualitative summary overrides,
previous-month/current-month aggregation, and multi-semiology severity
prioritization.

## Transfer Confidence

| Finding | Development confidence | Holdout-transfer confidence | Reason |
| --- | --- | --- | --- |
| Gated projection policies have high precision on target validation slices. | High | Moderate | Gates are explicit, but target rows come from validation-cycle diagnostics. |
| Broad state-graph projection is unsafe. | High | Moderate-to-high | Regressions are severe and mechanistically plausible. |
| Projection policy is the dominant remaining bottleneck. | High | Moderate | The hidden-family pattern is broad, but still validation-derived. |

## Metadata/Instrumentation Gaps

- Gated policies act only when the relevant graph node or selected state already
  exists; missing-node construction belongs to RQ1/RQ3.
- ACD policies need changed-row exact-evidence and deterministic-correct
  regression accounting before any holdout-facing use.
- Claim-table and selected-fact projection surfaces need same-row validation750
  source-id instrumentation before promotion.
- Rendering of a fixed selected state remains RQ5.

## Decision

RQ4 is answered for validation development:

- Accept `boundary_state_priority` and `graph_gated_month_bucket_duration` as
  high-precision gated projection mechanisms for their named slices.
- Reject broad `state_graph_projection` and unconstrained LLM label projection
  as replacement projection policies.
- Treat ACD-003 through ACD-010 as predeclared validation-development projection
  policies, not benchmark claims.

## Next Action

Move to RQ5: deterministic compilation/rendering from fixed selected states and
explicit projection-policy decisions into Gan-compatible labels, with semantic
drift checks and ablatable ACD policy accounting.
