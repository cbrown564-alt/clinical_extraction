# Gan 2026 Test450 Null Reduction Synthesis And Hypotheses

Date: 2026-06-07
Author: Codex

Status: frozen aggregate-read synthesis after the authorized `test450` replay
with the restored YTD denominator rule. This document reframes the next
research objective around **substantially reducing holdout null renders** under
the reset-native ClinicalAssessment pipeline without reintroducing hidden repair
or holdout-tuned fallback.

This is a holdout-facing interpretation document. It does **not** authorize
test-row tuning or row-level holdout inspection. Any implementation work from
this synthesis must be developed on validation-only proxy slices and returned to
`test450` only as a frozen aggregate audit.

---

## 1. Executive Summary

The restored YTD denominator rule generalized:

- `test450` Purist-correct scored rows improved from `268 / 341` to
  `271 / 341` (`78.59% -> 79.47%`)
- Pragmatic stayed `280 / 341` (`82.11%`)
- Routed rows fell from `43` to `41`

But the central constraint did **not** move:

- rendered labels stayed `341`
- null renders stayed `108`

That means the next score ceiling is not mainly a routed-verifier problem and
not mainly a denominator-window problem. It is a **null-surface problem**.

The holdout pipeline is now accurate enough on rendered rows that future gains
must come from safely converting more currently-null rows into source-backed,
audit-visible rendered outputs. The dominant holdout null pressure is:

1. frequency value parsing/completeness;
2. seizure-free duration/date anchoring;
3. a smaller cluster/cyclic residual family.

The right next objective is therefore:

```text
Reduce test450 null renders by porting portable normalization/projection
mechanisms that are source-backed, ablatable, and validation-developed,
while preserving the reset-native generalization discipline.
```

---

## 2. What The Holdout Now Says

### 2.1 Current frozen aggregate state

Using
`experiments/gan2026_reset_clinical_assessment_pipeline_test450_ytd_fix_2026-06-07.json`:

- input assessment rows: `450`
- projection rows: `449`
- rendered labels: `341`
- null renders: `108`
- scored rows: `341`
- Purist correct: `271`
- Pragmatic correct: `280`
- routed rows: `41`
- deterministic verification actions: `41 abstain`

### 2.2 Immediate implication

The YTD fix improved correctness on already-renderable rows, but it did not
increase rendered coverage. So:

- the next improvement bottleneck is **not** the currently-routed surface;
- the next improvement bottleneck is **not** mainly label-format semantics;
- the next improvement bottleneck is the still-null projection surface.

### 2.3 Verification is not the main bottleneck

Only `41` rows are routed, while `108` rows remain null. The reset pipeline is
already exposing route-worthy policy debt separately from render failure.

So the next research move should **not** be "use a verifier to fill nulls."
That would blur stage ownership and risk rebuilding the old hidden repair
ladder.

The correct move is upstream:

- normalize more source-backed burden values;
- project more already-supported clinical states;
- leave true policy-sensitive or unsupported cases visible.

---

## 3. Holdout Null Ecology

Important caution: the issue counts below are **not additive**, because a single
row may carry multiple issues. They are a family-weight read, not a partition.

Using the current frozen holdout replay:

- `projection_semantics_missing`: `108`
- `frequency_rate_values_unparsed`: `73`
- `frequency_rate_values_incomplete`: `58`
- `vague_count`: `58`
- `seizure_free_duration_required`: `39`
- `seizure_free_duration_unparsed`: `32`
- `seizure_free_duration_instrumented_from_since_date`: `27`
- `seizure_free_anchor_year_inferred_from_reference_date`: `18`
- `cluster_frequency_values_unparsed`: `12`
- `seizure_free_since_date_anchor_unparsed`: `10`
- `cluster_cadence_values_incomplete`: `7`
- `cyclic_window_pattern_routed`: `4`
- `cluster_cadence_unknown_with_per_cluster_burden`: `4`

### 3.1 Family interpretation

#### A. Frequency value recovery is the largest opportunity

The holdout null surface is dominated by source-backed current frequency rows
whose values are still not renderable:

- `frequency_rate_values_unparsed = 73`
- `frequency_rate_values_incomplete = 58`
- `vague_count = 58`

This is stronger on `test450` than on the current validation post-surface as a
share of nulls:

- test: `frequency_rate_values_unparsed = 67.6% of null count`
- validation: `42.4%`

Interpretation:

- the holdout null problem is more frequency-parsing heavy than the validation
  null problem;
- that suggests the next high-value portable work is in normalization and
  source-near burden interpretation, not only seizure-free logic.

#### B. Seizure-free remains the second major family

Holdout still carries a substantial unresolved seizure-free tail:

- `seizure_free_duration_required = 39`
- `seizure_free_duration_unparsed = 32`
- `seizure_free_duration_instrumented_from_since_date = 27`
- `seizure_free_anchor_year_inferred_from_reference_date = 18`

Interpretation:

- seizure-free is still a major ceiling;
- but on holdout it is less dominant than on validation, where
  `seizure_free_duration_required` was the largest named null family;
- this means the next null-reduction plan should put **frequency first,
  seizure-free second**, not the other way around.

#### C. Cluster and cyclic debt is real but smaller

The cluster/cyclic families are present, but they are no longer the dominant
global blocker:

- `cluster_frequency_values_unparsed = 12`
- `cluster_cadence_values_incomplete = 7`
- `cluster_cadence_unknown_with_per_cluster_burden = 4`
- `cyclic_window_pattern_routed = 4`

Interpretation:

- these families matter for completeness and failure taxonomy;
- they should not be the first null-reduction priority unless a targeted slice
  shows unusually high precision.

---

## 4. Validation vs Holdout Read

Comparing the current validation post-surface
(`validation750_ytd_fix_2026-06-07`) to the current holdout post-surface:

| Surface | Validation750 | Test450 |
| --- | ---: | ---: |
| rendered labels | 580 | 341 |
| null renders | 170 | 108 |
| Purist correct | 504 | 271 |
| routed rows | 68 | 41 |
| `frequency_rate_values_unparsed` | 72 | 73 |
| `frequency_rate_values_incomplete` | 70 | 58 |
| `seizure_free_duration_required` | 75 | 39 |
| `cluster_cadence_values_incomplete` | 13 | 7 |

Key observation:

- validation and test have similarly large **absolute** frequency-unparsed
  families despite different corpus sizes;
- therefore, a portable fix in that family has a real chance to generalize;
- by contrast, cluster and cyclic families are smaller and should be treated as
  secondary workstreams unless they prove unusually clean on validation slices.

---

## 5. Strategic Conclusion

The current holdout result does **not** suggest we need broader semantic rescue.
It suggests we need better **renderability of already-selected clinical facts**.

That means the next null-reduction program should favor:

1. source-backed normalization completion;
2. stage-owned projection for clinically supported but not yet renderable
   states;
3. portable date/context arithmetic;
4. explicit abstain/route preservation where evidence is still inadequate.

It should avoid:

1. verifier-written labels for null rows;
2. broad fallbacks from `unknown`, `no reference`, or seizure-free strings;
3. test-row-driven phrase maps;
4. hidden semantic replacement after the LLM-selected burden.

---

## 6. New Hypotheses For Null Reduction

These hypotheses are ordered by likely holdout leverage and portability.

### HN1: Source-Near Frequency Value Recovery

**Problem signal**

- `frequency_rate_values_unparsed = 73`
- `frequency_rate_values_incomplete = 58`
- `vague_count = 58`

**Hypothesis**

Many holdout nulls already contain the right current clinical fact, but the
reset normalization stage fails to carry that fact into renderable count/range
/period values. A narrow source-near value recovery layer could substantially
reduce nulls without changing the selected fact.

**Mechanism**

- recover parseable rate operands from selected evidence, selected source
  phrase, and same-fact candidate evidence when the current burden is already
  chosen;
- extend only format-preserving or fact-preserving recovery, not semantic
  reinterpretation;
- prioritize recurrent patterns that preserve event kind and temporality while
  filling missing count/range/period fields.

**Why it should generalize**

- the family is large on both validation and holdout;
- it attacks representation loss rather than label substitution;
- it stays in normalization/projection ownership.

**Primary owner**

- `Normalize` plus `rate_projection_policy`

**Portability**

- `general` plus `seizure_frequency`

### HN2: Bounded Vague-With-Window Rendering

**Problem signal**

- `vague_count = 58`
- `vague_frequency_with_explicit_time_period = 9`

**Hypothesis**

Some null rows describe a clinically usable burden with a vague count but an
explicit observation window. If the benchmark contract already supports bounded
vague categories in that setting, a narrower render policy can recover rows
without inventing exact counts.

**Mechanism**

- expand existing vague-with-explicit-period handling only where the source
  phrase and selected evidence already imply a supported vague benchmark class;
- keep unsupported vague phrases routed or null;
- forbid silent conversion of vague language into exact numeric counts.

**Why it should generalize**

- it targets a large family that is common on both surfaces;
- it is clinically plausible and benchmark-constrained;
- it can be stress-tested with paraphrase panels.

**Primary owner**

- `Project`

**Portability**

- `seizure_frequency` plus `benchmark_format`

### HN3: Seizure-Free Anchor Completion Beyond Prior Encounter

**Problem signal**

- `seizure_free_duration_required = 39`
- `seizure_free_duration_unparsed = 32`
- `seizure_free_duration_instrumented_from_since_date = 27`
- `seizure_free_anchor_year_inferred_from_reference_date = 18`

**Hypothesis**

The next seizure-free gain will not come mainly from prior-encounter linking.
It will come from broadening source-backed anchor resolution for explicit
event-date and since-date patterns that are already partially instrumented.

**Mechanism**

- strengthen parsing of last-event dates, explicit since-dates, month/year-only
  anchors, and same-note temporal antecedents;
- maintain a strict rule that bare unsupported relative anchors remain null;
- preserve explicit trace fields for anchor source and arithmetic basis.

**Why it should generalize**

- this is portable date/context logic rather than Gan-specific rescue;
- holdout already shows partial instrumentation families, meaning the substrate
  exists.

**Primary owner**

- `Normalize` plus `boundary_projection_policy`

**Portability**

- `general` plus `seizure_frequency`

### HN4: Cluster Operand Completion Before Cluster Policy Expansion

**Problem signal**

- `cluster_frequency_values_unparsed = 12`
- `cluster_cadence_values_incomplete = 7`
- `cluster_cadence_unknown_with_per_cluster_burden = 4`

**Hypothesis**

The next cluster gain is more likely to come from operand completion than from
new convention rendering. The cluster-default multiple-per-cluster rule already
exists; the residual ceiling is now missing or unparsed cluster operands.

**Mechanism**

- recover cluster count, cadence period, and events-per-cluster fields from
  already-selected source-backed cluster statements;
- keep unresolved axis-ownership cases routed;
- avoid broad cyclic-window-to-cluster conversion.

**Why it should generalize**

- it preserves the new cluster contract rather than broadening semantics;
- the family is smaller, but likely high-precision.

**Primary owner**

- `Normalize` plus `cluster_projection_policy`

**Portability**

- `seizure_frequency`

### HN5: Route-Only Cyclic And Sleep Precision

**Problem signal**

- `cyclic_window_pattern_routed = 4`
- cluster/cyclic debt remains visible but non-dominant

**Hypothesis**

For the next phase, cyclic and sleep patterns should mostly improve taxonomy,
not aggressively reduce nulls. Better route precision may still matter because
it prevents the null-reduction program from smuggling unsupported numeric
cadence through the frequency family.

**Mechanism**

- preserve explicit route-only handling for unsupported cyclic/sleep patterns;
- allow rendering only where explicit count and period operands already exist;
- use route-family precision as a guardrail against overreach in HN1/HN2/HN4.

**Primary owner**

- `Verify / Route`

**Portability**

- `clinical_epilepsy` plus `seizure_frequency`

---

## 7. Research Program For Null Reduction

### 7.1 Controlling objective

The next milestone is not "increase score however possible." It is:

```text
Reduce holdout null renders by converting already-supported clinical facts into
renderable outputs, while preserving stage ownership, traceability, and the
validation-to-test gap discipline.
```

### 7.2 Development rule

Because holdout row-level tuning remains prohibited:

- all implementation work must be developed on validation-only proxy slices;
- the proxy slices should be defined by the **same issue families now dominant
  on test450**;
- test450 should be revisited only as a frozen aggregate audit after each
  promoted family or carefully batched family set.

### 7.3 Required proxy slices

Create validation slices for:

1. `frequency_rate_values_unparsed`
2. `frequency_rate_values_incomplete`
3. `vague_count`
4. `seizure_free_duration_required`
5. `seizure_free_duration_unparsed`
6. `cluster_frequency_values_unparsed`
7. `cluster_cadence_values_incomplete`

Each slice should report:

- row count;
- rendered/null/routed counts;
- wrong-to-correct and correct-to-wrong transitions;
- newly rendered rows;
- newly null rows;
- evidence-validity and trace-validity checks.

### 7.4 Promotion metrics

Each null-reduction component should be promoted only if it shows:

- positive rendered-row gain on the targeted validation slice;
- acceptable or zero regression on already-rendered validation rows;
- visible trace fields and named rule ownership;
- a plausible portability argument from validation to holdout;
- frozen aggregate holdout improvement or at minimum no harmful expansion of the
  validation-test gap when audited.

---

## 8. Recommended Execution Order

The most rigorous order is:

1. **HN1 source-near frequency value recovery**
   - largest likely portable yield
   - strongest overlap between validation and holdout
2. **HN2 bounded vague-with-window rendering**
   - likely high leverage within the same frequency-heavy null surface
3. **HN3 seizure-free anchor completion beyond prior encounter**
   - still important, but second-order on current holdout
4. **HN4 cluster operand completion**
   - smaller but potentially precise
5. **HN5 cyclic/sleep route precision**
   - guardrail and taxonomy work, not primary aggregate lever

---

## 9. Bottom Line

The holdout now says something specific and useful:

- the reset-native pipeline is no longer primarily failing through overfit
  rendered semantics;
- it is now primarily failing through **non-rendered but potentially
  recoverable clinical state**.

The next research phase should therefore be a **null-reduction program**, not a
verifier-first program and not a fallback-expansion program.

If we stay disciplined, the best path is:

```text
validation-developed proxy slices for frequency and seizure-free null families
-> ablatable portable components
-> frozen aggregate holdout audits
-> score gains by reducing nulls, not by hiding them
```
