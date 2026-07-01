> **Superseded for navigation —** canonical summary: [`VALIDATION750_CANON.md`](../VALIDATION750_CANON.md). Full detail retained below.

# Gan 2026 Validation750 First Component Ablation Report Surface V6

Date: 2026-06-06

Scope: define the first reset-stage component-level ablation report surface for
the `context_repair_v6` validation-development replay.

This is a report-contract decision only. It does not authorize locked-test
inspection, benchmark-comparable claims, or silent promotion of verifier-facing
or scorer-facing behavior.

## Later Update: provenance residual changed after repair

This report-contract note remains valid, but one operational surface named
below is now historical rather than current.

At the time of writing, the candidate-trace replay still exposed a
`27`-row `selected_source_id_invalid` provenance tail. That residual has since
been repaired, and the current candidate-trace `selected_source_id_invalid`
tail is `0`.

What remains valid from this note:

- provenance route families stay visible in the component report
- provenance-only debt stays separate from the first verifier main
  success/failure table
- component accounting still needs provenance validity as an explicit column

What changed:

- the specific `27`-row residual provenance-tail count is no longer the current
  operational surface

## Purpose

The first component ablation report should answer a narrow reset question:

```text
For each named reset-owned family, what did the component recover, what new
route debt did it surface, what null debt remains, how valid is the
provenance/evidence trail, and what audit-only correctness movement appeared?
```

This keeps component accounting aligned with the reset architecture rather than
collapsing progress into a single rendered-row gain.

## Operational Surface

The report should use the replayed post-split surfaces already adopted for V6:

- verifier main success/failure table: `29` main ambiguity rows only
- non-provenance routed clinical/policy surface: `55` rows
- separate provenance follow-through tail:
  historical intermediate replay had `27` `selected_source_id_invalid` rows;
  current repaired candidate-trace replay has `0`
- provenance-only audit appendix:
  `220` rows kept out of the first verifier success/failure table

Component ablations should be read against those surfaces, not against the raw
`276` routed-row total alone.

## Included Families

The first component-level ablation report should cover all reset inventory
families that are either active deterministic behavior or active route families:

| Reset stage | New family | Status | Include in first ablation table | Why |
| --- | --- | --- | --- | --- |
| `normalize` | `selected_evidence_frequency_value_recovery` | `ported_v6` | `yes` | Direct recovery family with expected rendered-row gains. |
| `normalize` | `vague_period_frequency_value_recovery` | `ported_v6` | `yes` | Recovery family for explicit vague burden plus period. |
| `normalize` | `diary_date_list_frequency_recovery` | `ported_v6` | `yes` | Recovery family with Gan-specific portability caveat. |
| `normalize` | `seizure_free_duration_date_instrumentation` | `ported_v6` | `yes` | Large residual null family owner. |
| `project` | `current_summary_rate_priority` | `ported_v6` | `yes` | Projection policy family with rendered-row effects. |
| `project` | `previous_active_month_over_current_month_zero` | `ported_v6` | `yes` | Projection policy family with rendered-row effects. |
| `project` | `major_recent_relapse_over_background_frequency` | `ported_v6` | `yes` | Projection policy family that may alter ownership more than counts. |
| `verify` | `relative_only_trend` | `ported_route_family_v6` | `yes` | Route family defining abstain-style action debt. |
| `verify` | `conditional_only_trigger` | `ported_route_family_v6` | `yes` | Route family defining abstain-style action debt. |
| `verify` | `selected_evidence_missing_exact_trace` | `ported_route_family_v6` | `yes`, appendix-emphasized | Provenance route family; do not blend into main verifier score surface. |
| `verify` | `selected_source_id_invalid` | `ported_route_family_v6` | `yes`, appendix-emphasized | Historical residual provenance tail in the intermediate replay; current repaired candidate-trace surface is `0`, but the family stays reportable as provenance plumbing debt. |
| `verify` | `denominator_window_mismatch` | `ported_route_family_v6` | `yes` | Rendered-but-routed policy family. |
| `verify` | `unresolved_cluster_cadence_with_per_cluster_burden` | `ported_route_contract_v6` | `yes` | Rendered policy-sensitive route family. |

## Excluded Families

These families should stay visible in narrative notes but out of the first
per-family ablation score table:

| New family | Status | Why excluded from first table |
| --- | --- | --- |
| `named_comparator_preservation_action_policy` | `pending_policy_decision` | Not active reset behavior yet; including it would blur ablation versus proposal. |
| `audit_sidecars_only` | `retained_audit_only` | Audit instrumentation, not prediction-bearing or route-owning behavior. |
| `stage_owned_component_evidence_matrix` | `retained_audit_only` | Reporting substrate, not a row-changing family. |
| `do_not_port_broad_hybrid_fallback` | `retired_do_not_port` | Explicit negative control; mention only in retirement notes. |
| `do_not_port_broad_state_graph_projection` | `retired_do_not_port` | Explicit negative control; mention only in retirement notes. |

## Required Per-Family Columns

Every included family should report the same top-level columns:

| Column | Meaning |
| --- | --- |
| `family` | Reset-native family name from the inventory. |
| `stage` | `normalize`, `project`, or `verify`. |
| `portability` | `general`, `clinical_epilepsy`, `seizure_frequency`, `gan2026_specific`, or `benchmark_format`. |
| `ablation_switch` | Named switch used to disable the family. |
| `family_status` | Inventory status such as `ported_v6` or `ported_route_family_v6`. |
| `recovered_rows` | Rows newly rendered or newly made policy-owned because the family is on. |
| `newly_routed_rows` | Rows newly routed because the family surfaced ambiguity or provenance debt explicitly. |
| `remaining_null_rows` | Rows still null-rendered in the family-owned residual surface after the port. |
| `provenance_validity` | Exact-trace and source-id validity read for the family-owned surface. |
| `audit_only_w_to_c` | Audit-only wrong-to-correct movement versus comparator/gold context. |
| `audit_only_c_to_w` | Audit-only correct-to-wrong movement versus comparator/gold context. |
| `notes` | One-line interpretation of what the family changed or exposed. |

## Metric Definitions

To keep later tables comparable, the first report should freeze the meanings of
the key columns:

### `recovered_rows`

Count rows where enabling the family causes one of the following relative to the
off-state:

- a prior null render becomes a rendered label
- a less-owned projected state becomes an explicitly policy-owned rendered state

Do not count mere wording changes that preserve the same route/render outcome.

### `newly_routed_rows`

Count rows where enabling the family adds an explicit verification route that
was absent in the off-state.

For provenance families, this is expected and should not be treated as a
negative by default; the interpretation belongs in `notes`.

### `remaining_null_rows`

Count rows still null-rendered within the family-owned residual slice after the
family is enabled.

This is a residual debt measure, not a failure count. A high-value family can
still leave hard residuals.

### `provenance_validity`

Report this as a compact sub-read, not a single scalar:

- exact-trace valid rows
- source-id valid rows
- invalid or unresolved source-id rows

For non-provenance families, this is still useful because a family can recover a
row while degrading trace quality.

### `audit_only_w_to_c` and `audit_only_c_to_w`

These are audit-only movement counts against comparator/gold context.

Rules:

- never mix these counts into scorer-facing success rates
- never use them as verifier-visible hints
- always report them together
- `C->W` must remain visible even when rendered/null counts improve

## Recommended Report Slices

The first report should present the ablation results in three slices:

### 1. Recovery families

Use for:

- normalization and projection ports
- rendered-row gains
- residual null debt reads

Primary families:

- `selected_evidence_frequency_value_recovery`
- `vague_period_frequency_value_recovery`
- `diary_date_list_frequency_recovery`
- `seizure_free_duration_date_instrumentation`
- `current_summary_rate_priority`
- `previous_active_month_over_current_month_zero`
- `major_recent_relapse_over_background_frequency`

### 2. Clinical/policy route families

Use for:

- explicit ambiguity surfacing
- abstain/human-review boundary work
- rendered-but-routed policy-sensitive rows

Primary families:

- `relative_only_trend`
- `conditional_only_trigger`
- `denominator_window_mismatch`
- `unresolved_cluster_cadence_with_per_cluster_burden`

### 3. Provenance route appendix

Use for:

- provenance-only debt
- mixed clinical/provenance sidecars
- residual invalid-source tail

Primary families:

- `selected_evidence_missing_exact_trace`
- `selected_source_id_invalid`

This appendix should stay separate from the first verifier main success/failure
table even though the route families belong in the component report.

## Minimum Narrative Read Per Family

Each family row should be followed by a one- or two-sentence read answering:

1. Did this family recover ordinary deterministic debt or surface new review
   debt?
2. Did it change the clinical/policy surface, the provenance surface, or both?
3. Did it introduce any audit-only `C->W` risk that blocks promotion?

## Decision Summary

The first reset-stage component ablation report for `context_repair_v6` should:

1. use the reset inventory as the family list
2. report per-family `recovered_rows`, `newly_routed_rows`,
   `remaining_null_rows`, `provenance_validity`, and audit-only
   `W->C` / `C->W`
3. keep provenance route families in the component report but out of the first
   verifier main success/failure table
4. keep pending, audit-only, and retired families out of the first per-family
   score table
5. treat component progress as a joint read over recovery, route surfacing,
   trace validity, and audit-only correctness movement
