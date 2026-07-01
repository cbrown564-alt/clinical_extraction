> **Superseded for navigation —** canonical summary: [`VALIDATION750_CANON.md`](../VALIDATION750_CANON.md). Full detail retained below.

# Gan 2026 Validation750 HN1 Month-Bucket Frequency Recovery Evaluation

Date: 2026-06-07
Author: Codex

Scope: validation-development follow-through on the next item recorded in
`PROJECT_STATUS.md` after the first HN1 anchor-window component:
evaluate whether **explicit month-bucket aggregation** should become the next
narrow null-reduction family on the `frequency_rate_values_unparsed` proxy
slice.

This is a validation-only read. It does not inspect locked-test rows and it
does not authorize holdout-tuned implementation.

---

## 1. Question

After the first HN1 anchor-window recovery, should the next Normalize-owned
null-reduction component be a month-bucket family?

More precisely:

```text
Is the residual month/date-heavy HN1 surface mostly a clean
count-plus-month aggregation problem, or is much of it actually selection debt,
anchor debt, or true unknown/guardrail debt?
```

---

## 2. Source Surface

Primary source:

- `experiments/gan2026_validation750_null_reduction_slices_baseline_2026-06-07.json`

Working slice:

- `frequency_rate_values_unparsed`

Month/date-filtered subset inside that slice:

- `34` rows mention an explicit calendar month or date token
- `14` are already rendered by existing recovery families
- `20` remain null on the saved baseline slice

Important caution:

- this saved slice predates the newly landed anchor-window HN1 component, so
  several date-anchored null rows are no longer the right target for a
  month-bucket decision;
- the purpose here is not to restate the whole HN1 surface, but to isolate what
  should come **after** the anchor-window family.

---

## 3. Residual Month/Date Null Families

The `20` null rows with explicit month/date language split into four practical
families.

### 3.1 Not month-bucket targets: explicit single-event or trigger-only negatives

Rows such as:

- `6077`: `one breakthrough seizure on 12/09/2025`
- `11337`: `one seizure on 06-Nov after missed doses and sleep deprivation`
- `11389`: `one focal seizure on 21 December`

Read:

- these rows name an event date, but they do not establish a safe observation
  denominator;
- they look like true unknowns or route-preservation cases, not month-bucket
  aggregation misses.

Conclusion:

- keep them as guardrail negatives for HN1 month-bucket work.

### 3.2 Already-better-owned elsewhere: anchor/date-window rows

Rows such as:

- `14092`: `5 myoclonic jerks since last clinic appointment, last on 7 April`
- `14146`: `3 generalised tonic-clonic seizures since starting Clobazam, most recent on 13 October`
- `14965`: `last seizure episode on 20 May, stable since`
- `15094`: `3 morning jerks since last tonic-clonic seizure in Apr 2022`
- `15108`: `2 to 3 morning jerks since last tonic-clonic seizure in January 2024`
- `15127`: `4 morning jerks since last tonic-clonic seizure in Feb 2020`

Read:

- these are explicit anchor/window problems, not bucket aggregation problems;
- they belong to the now-landed anchor-window HN1 family or adjacent seizure-free
  / boundary-style anchor work.

Conclusion:

- exclude them from the month-bucket promotion decision.

### 3.3 True month-bucket-like rows that are still high risk

Rows such as:

- `14592`: `Two seizures in June 2024 during sleep` with gold `3 per 5 month`
- `15964`: `3 seizures in sleep and 3 while awake in May` with gold
  `11 per 3 month`
- `15986`: `In May she had no seizures during sleep and one while awake` with
  gold `11 per 3 month`
- `15997`: `Six seizures in January, including five nocturnal and one daytime`
  with gold `10 per 3 month`
- `16021`: `five seizures in sleep in April, none while awake` with gold
  `9 per 3 month`
- `16704`: `seven myoclonic jerks documented in September over three months`
  with gold `9 per 6 month`
- `14335`: `three to four seizures around October` with gold
  `3 to 4 per 2 month`

Read:

- these rows mention a month bucket, but the gold labels usually reflect a
  broader current burden than the month phrase alone;
- that means a naive `count in month -> count per 1 month` repair would often
  under-render the selected clinical state;
- several of these rows look more like selected-phrase incompleteness,
  broader same-note window debt, or clinical selection debt than pure
  normalization loss.

Conclusion:

- do **not** promote a broad single-month-bucket recovery family as the next
  HN1 component.

### 3.4 Cleanest month-bucket promotion candidates: explicit multi-month lists

The strongest remaining rows are:

- `16674`: `four short absences in a cluster in April, two brief absences in July, and one in September`
- `16697`: `Three seizures recorded over six months: September, November, and February`
- `16758`: `3 brief absences in Dec, 5 drop attacks in Mar, and 1 tonic seizure in Apr`
- `16833`: `5 drop attacks in October, 2 myoclonic jerks in December, and a prolonged event in July`

Read:

- these rows already present explicit count-bearing month buckets;
- the intended denominator is plausibly the inclusive span across the named
  month buckets or the source-stated multi-month window;
- unlike the risky single-month rows, these examples look like true
  representation loss inside `Normalize`, not obviously broader current-burden
  debt.

Important guardrail:

- `16674` still contains cluster language, so any promoted family must preserve
  visibility when month summation would flatten a clinically important cluster
  axis.

Conclusion:

- if month-bucket work is promoted next, it should be a **multi-month explicit
  bucket aggregation** family, not a generic month-name parser.

---

## 4. Decision

The answer is:

```text
Yes, but only in a narrower form than "month-bucket aggregation" suggests.
```

What should be promoted next is:

```text
normalize_frequency_multi_month_bucket_value_recovery_v0
```

Not:

```text
render any count-with-month phrase as count per 1 month
```

Reason:

1. the cleanest positive cases are explicit multi-month bucket lists, not
   single-month snippets;
2. many single-month rows appear to be partial burden views whose gold labels
   span longer windows;
3. broad month-bucket rescue would risk turning selection debt into false
   normalization confidence.

---

## 5. Recommended Component Boundary

The next family should allow only:

1. explicit numeric counts attached to named calendar months;
2. aggregation across two or more explicit month buckets, or one month bucket
   plus an explicit source-stated multi-month window;
3. inspectable denominator construction from:
   - inclusive month span across named buckets, or
   - an explicit stated window already present in the source phrase.

It should forbid, at least in `v0`:

1. single dated breakthrough-event rescue;
2. single-month bucket rescue without a broader source-backed window;
3. trigger-only or provoked-event rescue;
4. silent flattening of cluster-bearing rows into plain frequency labels when
   cluster structure appears clinically relevant;
5. additive rescue that requires re-choosing the clinical fact across multiple
   competing semiologies.

Suggested ownership:

- stage: `Normalize`
- portability: `general` plus `seizure_frequency`

Suggested success condition:

- newly rendered rows should come mainly from the explicit multi-month bucket
  list rows, not from the risky single-month partial-burden rows.

---

## 6. Execution Consequence

The clean next implementation step is:

```text
Build a validation-only HN1 multi-month bucket recovery component restricted to
explicit month-list aggregation and explicit source-stated multi-month windows,
then ablate it on the frequency_rate_values_unparsed slice.
```

The next follow-up question after that ablation should be:

```text
Are the remaining single-month bucket rows actually normalization debt,
or are they mostly selection / same-note window debt that should not be solved
inside Normalize?
```

---

## 7. Bottom Line

Month-bucket work does deserve promotion, but only after narrowing the family.

The validation read does **not** support:

- broad single-month rescue;
- date-token rescue in general;
- conflating anchor-window and month-bucket work.

It **does** support:

- a small explicit multi-month bucket aggregation family;
- a validation-only ablation targeted at rows like `16674`, `16697`, `16758`,
  and `16833`;
- keeping single-month and trigger/date rows visible until a different contract
  justifies them.
