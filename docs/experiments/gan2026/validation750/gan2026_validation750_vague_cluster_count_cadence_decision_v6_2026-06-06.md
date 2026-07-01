> **Superseded for navigation —** canonical summary: [`VALIDATION750_CANON.md`](../VALIDATION750_CANON.md). Full detail retained below.

# Gan 2026 Validation750 Vague Cluster-Count Cadence Decision V6

Date: 2026-06-06

Status: validation-development policy decision over the
`context_repair_v6` cluster-family read. This note resolves the open question
from `PROJECT_STATUS.md` and
``
about whether vague cluster-count cadence should gain a reset-native contract
now.

This is not a benchmark claim and does not authorize locked-test inspection,
LLM-verifier promotion, or broad cluster fallback.

## Decision

Vague cluster-count cadence should remain routed policy debt for the current
reset thread. We are not adding a reset-native projection/render contract for
phrases such as:

- `multiple days over the past month`
- `several mornings each week`
- `several evenings per fortnight`

These rows remain upstream policy debt inside the current cluster route surface
until a future contract explicitly defines:

1. what quantity is being represented;
2. whether vague cluster-count words are allowed to map to benchmark-facing
   cadence semantics;
3. how that mapping would be reported, ablated, and separated from general
   clinical parsing.

## Why

The dedicated cluster-family pass already shows that the tempting rows are not
missing a narrow parser patch. They are missing an owned semantic contract.

For the three clearest examples (`1706`, `10434`, `10630`):

- the period window is often parseable;
- per-cluster burden may also be parseable;
- the cluster-count value itself remains vague (`multiple`, `several`);
- projecting a scorer-facing cadence would require inventing a denominator
  convention that the reset schema does not currently own.

That would violate the current reset objective:

```text
Extract -> Select / Clinical Assessment -> Normalize -> Project -> Verify -> Render / Score
```

The reset is supposed to make policy ownership explicit. Turning vague
cluster-count language into a benchmark-facing rate now would recreate the old
hidden-fallback problem under a cleaner name.

## Research-Framing Read

This decision protects the current research claims:

- Transparency: the system keeps these rows visibly routed instead of silently
  guessing a count.
- Deterministic rules as controlled variables: no new semantic repair family is
  introduced without a named contract and future ablation.
- Generalisation discipline: vague cluster-count mapping looks
  benchmark-convention-specific today, not like general epilepsy logic.

Portability classification for any future contract would therefore begin at
`benchmark_format` or `gan2026_specific`, not `general`.

## Current Operational Policy

For `context_repair_v6` and the first verifier-candidate reporting thread:

- keep explicit `unresolved_cluster_cadence_with_per_cluster_burden` rendered
  route rows as they are today;
- keep vague cluster-count cadence rows null-rendered and routed under the
  existing cluster ambiguity surface;
- treat them as upstream policy debt, not verifier-success/failure evidence;
- do not broaden parser or projection logic to coerce `several`/`multiple`
  into owned numeric cadence.

## What Would Need To Be True Before Revisiting

A future reset-native contract should be considered only if all of the
following are made explicit first:

1. A schema field or route-owned representation for vague cluster-count cadence.
2. A predeclared policy for when vague cluster-count language may become a
   rendered benchmark label versus remain route-only.
3. An ablation/report plan showing:
   - newly rendered rows;
   - newly routed rows;
   - remaining nulls;
   - evidence validity;
   - audit-only W->C/C->W.

Until then, the right next work is to keep the first verifier surface narrow
and to separate clinical/policy ambiguity from provenance-only routing.
