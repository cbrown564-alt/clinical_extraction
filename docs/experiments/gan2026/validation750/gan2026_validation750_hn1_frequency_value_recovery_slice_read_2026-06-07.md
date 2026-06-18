# Gan 2026 Validation750 HN1 Frequency Value Recovery Slice Read

Date: 2026-06-07
Author: Codex

Scope: validation-development read of the first null-reduction execution item
from
``:
**HN1 source-near frequency value recovery**.

This document uses only the saved `validation750` reset-native baseline slice
artifacts. It is not a holdout-tuning artifact and it does not inspect locked
test rows.

---

## 1. Question

The synthesis memo ordered the next null-reduction program as:

1. HN1 source-near frequency value recovery
2. HN2 bounded vague-with-window rendering
3. HN3 seizure-free anchor completion

The immediate question for HN1 is:

```text
What exactly remains inside the validation750
frequency_rate_values_unparsed slice after the currently-ported
selected-evidence recovery, and which residual subfamilies are portable enough
to deserve implementation work?
```

---

## 2. Baseline Slice Read

Using
`experiments/gan2026_validation750_null_reduction_slices_baseline_2026-06-07.json`:

- HN1 proxy slice: `frequency_rate_values_unparsed`
- total rows: `71`
- rendered rows: `24`
- null rows: `47`
- Purist-correct rows: `23`
- Pragmatic-correct rows: `23`

### 2.1 Important first conclusion

HN1 is already partially real on validation, not only hypothetical.

All `24` rendered rows in this slice carry:

- `frequency_rate_values_repaired_from_primary_candidate`

Those rows are the existing proof that a source-near value recovery mechanism
can recover real null-prone frequency statements without broad semantic
fallback.

### 2.2 What remains null

The remaining `47 / 47` null rows in this slice still carry:

- `frequency_rate_values_incomplete`

That means the residual HN1 ceiling is no longer mainly "unparsed text that the
current repair can already see." It is mostly:

```text
selected current burden exists
-> source phrase is still frequency-like
-> but the reset pipeline still lacks a renderable count/window/state contract
```

So the next HN1 work should target **operand completion and bounded
window/anchor interpretation**, not another broad pass over the already-solved
primary-candidate repair family.

---

## 3. Residual Family Structure

Issue co-occurrence inside the `47` null rows is narrow:

- `42` rows: `frequency_rate_values_incomplete` only
- `4` rows: `additive_frequency_period_mismatch` plus
  `frequency_rate_values_incomplete`
- `1` row: `additive_frequency_count_unparsed` plus
  `frequency_rate_values_incomplete`

Interpretation:

- the dominant residual is a single-burden operand-completion problem;
- additive/multi-burden mixing exists, but it is a smaller secondary family;
- the next HN1 component should not be designed around additive rows first.

### 3.1 What the already-recovered rows look like

Representative successful HN1-style recoveries already on validation:

- diary/date-list aggregation:
  `Seizure events on 07-03, 07-07, 07-10, 07-18 ... -> 4 per month`
- selected evidence with explicit weekly cadence:
  `... approximately twice weekly -> 2 per week`
- explicit count over a bounded multi-month window:
  `... 5 events ... -> 5 per 2 month`

These rows support the core HN1 thesis:

- the selected fact was already right;
- value recovery, not label substitution, created the gain;
- the mechanism belongs to `Normalize`, not to verifier fallback.

### 3.2 What the remaining null rows look like

A manual validation-only scan shows five residual phrase families.

#### A. Qualitative or trigger-only frequency language with no safe rate operand

Examples:

- `sporadic epileptic spasms this year`
- `Recent breakthrough events predominantly following lapses in prescribed antiseizure medication`
- `intermittent morning myoclonic jerks day-to-day`
- `infrequent generalised seizures provoked by patterned or flickering visual stimuli`

Read:

- many of these rows are still true nulls or route-worthy unknowns;
- they should be used as **negative controls** for HN1;
- a good HN1 patch must not silently force these into numeric labels.

Primary owner:

- `Normalize` guardrails plus `Verify` route preservation

Portability:

- `clinical_epilepsy` plus `seizure_frequency`

#### B. Count present, but no denominator/window

Examples:

- `she has had two seizures`
- `five myoclonic jerks`
- `3 - 4 generalised tonic-clonic seizures`
- `one focal seizure on 21 December`

Read:

- these are source-backed current burden statements with missing observation
  windows;
- some should remain `unknown`;
- some may become renderable only if a bounded same-note or reference-date
  window can be justified without changing the selected fact.

Primary owner:

- `Normalize`

Portability:

- `seizure_frequency`

#### C. Count plus since-anchor or last-event anchor

Examples:

- `3 generalised tonic-clonic seizures since starting Clobazam, most recent on 13 October`
- `3 morning jerks since last tonic-clonic seizure in Apr 2022`
- `four brief morning jerks since 3/2015`
- `last seizure episode on 20 May, stable since`

Read:

- this is the clearest bridge between HN1 and HN3;
- the phrase already contains count-like burden plus a temporal anchor;
- the missing piece is bounded date arithmetic and explicit anchor ownership.

Primary owner:

- `Normalize`

Portability:

- `general` plus `seizure_frequency`

#### D. Date-bucket and month-list aggregation

Examples:

- `Two seizures in June 2024 during sleep`
- `Six seizures in January, including five nocturnal and one daytime`
- `four short absences in a cluster in April, two brief absences in July, and one in September`
- `3 brief absences in Dec, 5 drop attacks in Mar, and 1 tonic seizure in Apr`

Read:

- these rows are promising because they already look like explicit count-plus-
  time evidence;
- they may support a narrow month-bucket aggregation family;
- any such component must keep cluster-bearing or multi-semiology rows visible
  when summation would change the selected clinical fact.

Primary owner:

- `Normalize`

Portability:

- `general` plus `seizure_frequency`

#### E. Additive or multi-semiology mixtures

Examples:

- `several episodes per day ... with occasional generalised breakthroughs approximately once weekly`
- `daily absence seizures and occasional generalised tonic-clonic seizures`
- `focal clonic occur 4 per day; generalised tonic-clonic seizures twice monthly; drop attacks clustering every month`

Read:

- this is a real family, but it is not the dominant HN1 lever on validation;
- it is higher risk because value completion and clinical selection are tightly
  entangled;
- it should stay secondary until the simpler single-burden families are tested.

Primary owner:

- `Normalize` plus existing additive selection policy

Portability:

- `seizure_frequency`

---

## 4. Development Implications

### 4.1 What HN1 should try first

The best next HN1 development order on validation is:

1. bounded date-bucket and explicit month-list aggregation;
2. count-plus-anchor completion where the anchor is explicit and arithmetic is
   inspectable;
3. narrow count-with-window completion from same-note bounded context;
4. only then review additive/multi-semiology residuals.

### 4.2 What HN1 should explicitly not try first

HN1 should not begin with:

1. trigger-only or provoked-event frequency rescue;
2. vague qualitative terms such as `sporadic`, `infrequent`, or `less frequent`
   being forced into numeric labels;
3. broad additive fusion across multiple semiologies;
4. verifier-written replacement labels for null rows.

---

## 5. Promotion Contract For The First HN1 Component

The first HN1 component should be promoted only if a validation-only slice
ablation shows:

- increased rendered rows on `frequency_rate_values_unparsed`;
- visible reduction in `frequency_rate_values_incomplete` on the targeted rows;
- acceptable or zero regression on already-rendered validation rows;
- explicit trace fields showing the source phrase and anchor/window basis;
- no broad conversion of qualitative-trigger rows into exact counts.

Recommended first component framing:

```text
normalize_frequency_date_bucket_value_recovery_v0
```

Suggested ownership:

- stage: `Normalize`
- portability: `general` plus `seizure_frequency`
- targeted residual family:
  explicit dated/month-bucket frequency evidence that already contains a bounded
  count

Recommended comparator:

- current validation750 baseline slice
- plus one-family-off or one-family-on slice audit against the same saved rows

---

## 6. Bottom Line

The first HN1 validation read says something specific:

- HN1 already has a proven portable core: `24` rows are rendered through
  source-near primary-candidate recovery.
- The remaining HN1 null surface is mostly **not** another version of that same
  solved family.
- The next real lever is a narrower operand-completion program centered on
  explicit date-bucket and count-plus-anchor frequency statements.
- Qualitative-trigger rows should stay as guardrail negatives, not as the first
  target for rescue.

So the clean next implementation task is:

```text
Build and ablate a narrow Normalize-owned date-bucket / explicit-anchor
frequency value recovery component on validation-only slices before touching
additive or verifier behavior.
```
