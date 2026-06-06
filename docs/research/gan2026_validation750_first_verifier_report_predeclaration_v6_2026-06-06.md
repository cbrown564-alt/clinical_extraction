# Gan 2026 Validation750 First Verifier Report Predeclaration V6

Date: 2026-06-06

Scope: predeclare the first verifier-facing report layout for the
`context_repair_v6` validation-development surface.

This is a report-shape and evaluation-surface decision only. It does not
authorize locked-test inspection, benchmark-comparable language, or live
verifier promotion.

## Later Update: report shape held, provenance tail did not

This predeclaration still correctly defined the first verifier report shape:

- main ambiguity score table
- abstain appendix
- upstream-policy appendix
- rendered policy-sensitive appendix
- provenance-only audit appendix

Later work changed one provenance detail:

- the original intermediate candidate-trace
  `selected_source_id_invalid` residual is no longer active after the later
  source-id repair

Later execution also fixed the verifier policy direction:

- the primary verifier policy is now `action_only`
- forced choice remains diagnostic only

So this note should be read as the correct pre-run bucket contract, with later
policy and provenance updates layered on top.

## Purpose

The first verifier report should answer a narrow question:

```text
Given reset-owned routed rows, can a verifier make action decisions on the
clinically/policy-relevant surface without being judged on provenance-only
audit debt?
```

This predeclaration fixes the report intake and bucket layout before verifier
execution.

## Included Surfaces

### 1. Main ambiguity set

- `29` rows
- bucket:
  `verifier_eligible_ambiguity`
- family:
  `mixed_window_or_vague_addition`

Use:

- primary verifier success/failure table
- main action comparison surface

### 2. Abstain exemplars

- `4` rows
- families:
  - `relative_only_trend`
  - `conditional_only_trigger`
  - `seizure_free_proxy_evidence_overreach`

Use:

- negative-boundary appendix
- prompt exemplars for "decline label/action escalation" behavior

### 3. Upstream-policy appendix

- `18` rows
- families:
  - `cluster_axis_ambiguity`
  - `cyclic_window_without_event_count`

Use:

- separate appendix
- visible during verifier analysis, but excluded from the main verifier success
  criterion

Rationale:

- these rows are mostly contract-boundary debt rather than the cleanest first
  verifier benchmark

### 4. Rendered policy-sensitive appendix

- `5` rows
- families:
  - `unresolved_cluster_cadence_with_per_cluster_burden`
  - `rendered_label_supported_but_policy_sensitive`

Use:

- appendix for already-rendered routed states
- useful for `affirm` versus `abstain` versus `human_review` behavior on
  rendered labels

### 5. Provenance-only audit appendix

- `220` rows
- families:
  - `selected_evidence_missing_exact_trace`
  - `selected_source_id_invalid`
  - provenance-only combinations of those families

Use:

- keep fully visible as audit/instrumentation debt
- exclude from the first verifier score table

## Provenance-Sidecar Policy

For the 56 clinical/policy rows:

- provenance sidecars remain visible to the first verifier prompt when present
- these sidecars are secondary audit context, not the primary route target

Counts:

- mixed clinical/policy rows with provenance sidecars: `39`
- mixed clinical/policy rows without provenance sidecars: `17`

Visible sidecar fields should include:

- provenance-sidecar present or absent
- `selected_evidence_missing_exact_trace` when present
- `selected_source_id_invalid` when present

These fields may inform caution or abstention, but the primary evaluation axis
remains the non-provenance action family and bucket.

## Main Report Columns

The first verifier report should expose at least:

- source row id
- route bucket
- non-provenance route family
- provenance sidecar present or absent
- provenance sidecar family or families
- rendered label
- normalized source phrase
- projection basis
- score status
- verifier action
- verifier rationale summary

## Main Score Table

The first verifier score table should use only the 29-row main ambiguity set.

Optional side analyses may separately summarize:

- abstain exemplars
- upstream-policy appendix
- rendered policy-sensitive appendix

But those should not be blended into the main success/failure rate.

## Decision Summary

The first verifier report is therefore predeclared as:

1. main ambiguity score table: `29`
2. abstain appendix: `4`
3. upstream-policy appendix: `18`
4. rendered policy-sensitive appendix: `5`
5. provenance-only audit appendix: `220`

This keeps the verifier focused on genuine action ambiguity while still making
provenance debt and contract-boundary rows visible.
