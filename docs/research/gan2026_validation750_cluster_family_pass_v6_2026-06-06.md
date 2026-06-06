# Gan 2026 Validation750 Cluster Family Pass V6

Date: 2026-06-06

Status: validation-development read over the `context_repair_v6` reset
artifacts. This note inspects the cluster-family rows inside the 56-row
clinical/policy route surface defined in
`docs/research/gan2026_validation750_route_bucket_split_v6_2026-06-06.md`.

This is not a benchmark claim and does not authorize locked-test inspection or
LLM-verifier promotion.

## Surface

- Clinical/policy routed rows: `56`
- Cluster-routed subset: `22`
- Cluster-routed rendered rows: `4`
- Cluster-routed null-render rows: `18`
- Cluster-routed rows with provenance side-routes: `8`

Cluster route-family counts:

- `cluster_axis_ambiguity`: `13`
- `cyclic_window_without_event_count`: `5`
- `unresolved_cluster_cadence_with_per_cluster_burden`: `4`

## Main Read

The cluster surface is narrower and cleaner than a generic "cluster parser
gap" story.

The 4 rendered cluster routes are already the intended convention-supported
cases:

- `1317`
- `7141`
- `10189`
- `10200`

All 4 render `unknown, multiple per cluster` and route as
`unresolved_cluster_cadence_with_per_cluster_burden`. These are not silent
projection failures. They are explicit "burden seen, recurrence cadence not
owned" rows and should remain routed.

The remaining 18 cluster routes are true null-render cases, but they split into
distinct policy buckets rather than one missing regex family.

## Buckets

### 1. Cyclic window without event count: 5 rows

Rows:

- `3468`
- `3469`
- `3482`
- `3493`
- `10509`

Representative phrases:

- `perimenstrual only (days -2 to +2)`
- `the attacks cluster around her period`
- `clusters arising after nights of curtailed sleep`

Interpretation:

- These rows name timing windows or triggers, not a recurrence denominator.
- Keeping them null-routed is correct under the current reset contract.
- Any future recovery would need an explicit cyclic-window policy, not a parser
  tweak.

### 2. Vague cluster-day cadence with or without size: 3 rows

Rows:

- `1706`
- `10434`
- `10630`

Representative phrases:

- `cluster of short events on multiple days over the past month`
- `on several mornings each week`
- `several evenings per fortnight with roughly five short-lived spells per cluster`

Interpretation:

- These rows expose the current contract boundary most clearly.
- We can often parse the period window and sometimes the per-cluster burden.
- We still do not have an explicit reset-native representation for vague
  cluster-count cadence such as `multiple days`, `several mornings`, or
  `several evenings`.
- Rendering these rows today would require inventing a denominator convention
  that the current schema does not own.

Most important example:

- `10630` already carries `cluster_period=2 week` and `events_per_cluster=5`,
  but it still lacks a deterministic cluster-count value for `several`.
  Treating that as `multiple` or `1` would be a semantic policy addition, not a
  bug fix.

### 3. Event burst without recurrence rate: 4 rows

Rows:

- `10542`
- `10578`
- `16839`
- `16907`

Representative phrases:

- `two to four absences per cluster over approximately 1 hour`
- `three to four focal impaired-awareness seizures per cluster`
- `Clusters of 4 seizures in December and February`
- `run of six seizures within half an hour`

Interpretation:

- These rows describe cluster size or an isolated burst, but not a stable
  recurrence cadence.
- The current route behavior is correct. A scorer-facing label would require an
  explicit denominator or a new benchmark convention for dated bursts.

### 4. Broad cluster mention without stable cadence ownership: 6 rows

Rows:

- `6501`
- `9879`
- `9937`
- `15242`
- `15262`
- `16757`

Representative phrases:

- `brief episodes occurring over 2-3 days`
- `brief clusters of events over the past three months`
- `periodic bursts roughly every few weeks`
- `occasional clusters of myoclonic jerks persisting`
- `recent clusters of brief seizures`

Interpretation:

- These are genuinely under-specified for reset projection.
- Some mention duration-like windows (`over 2-3 days`), some mention loose
  recurrence (`every few weeks`), and some are only qualitative cluster claims.
- Broadly forcing them into rate labels would recreate the old hidden-fallback
  problem.

## What This Means

The cluster-family pass does not support a narrow deterministic recovery patch
today.

What looks tempting at first glance falls into three unsafe categories:

- vague cluster-count cadence with no owned numeric count
- isolated burst size with no recurrence denominator
- cyclic or trigger windows with no event-count policy

The current reset behavior is therefore directionally right:

- render the convention-supported `unknown, multiple per cluster` cases
- keep cyclic-window and axis-ownership cases null-routed
- avoid broad fallback that turns cluster mention into a guessed rate

## Recommended Next Contract Work

If cluster work is promoted later, the next changes should be explicit contract
extensions, not silent parser broadening:

1. Decide whether vague cluster-count cadence (`several mornings per week`,
   `multiple days per month`) gets a reset-native representation and route
   policy.
2. Decide whether dated multi-burst rows (`4 seizures in December and February`)
   belong to cluster projection, additive history, or verifier-only review.
3. Decide whether isolated burst-size phrases (`six seizures within half an
   hour`) should remain route-only forever or gain a named benchmark
   convention.

## Recommendation For The Current Thread

Treat the cluster-family pass as complete for `context_repair_v6`.

The next useful deterministic step is not more cluster regex work. It is to use
the now-cleaner route surface to define:

- the 56-row verifier-candidate report from the clinical/policy bucket only
- the null-render/action taxonomy across clinically unknown, abstain,
  human-review, missing upstream policy, and verifier-eligible ambiguity

## Resolution

The follow-on decision for the current thread is now recorded in
`docs/research/gan2026_validation750_vague_cluster_count_cadence_decision_v6_2026-06-06.md`.

Outcome:

- vague cluster-count cadence remains routed upstream policy debt for now;
- no reset-native projection/render contract is added for `multiple`/`several`
  cluster-count language in V6;
- future promotion requires an explicit schema contract plus ablation plan.
