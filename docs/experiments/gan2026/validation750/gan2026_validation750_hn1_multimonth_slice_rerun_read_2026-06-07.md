# Gan 2026 Validation750 HN1 Multi-Month Slice Rerun Read

Date: 2026-06-07
Author: Codex

Scope: validation-development follow-through on the work-board task to rerun the
`frequency_rate_values_unparsed` proxy slice after landing the narrow
`multi_month_bucket_frequency_value_recovery` Normalize family.

This is a saved-artifact replay only. It uses the existing validation750
ClinicalAssessment and CandidateSet artifacts, does not inspect locked test
rows, and does not authorize benchmark-comparable claims.

---

## 1. Question

After landing the multi-month-bucket HN1 component:

```text
What changed on validation750 overall, what changed on the
frequency_rate_values_unparsed proxy slice specifically, and do the remaining
single-month rows still look like true Normalize debt?
```

---

## 2. Inputs

Baseline comparison artifacts:

- `experiments/gan2026_validation750_null_reduction_slices_baseline_2026-06-07.json`
- `experiments/gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v0.json`

Fresh replay artifacts:

- `experiments/gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v0_hn1_multimonth_replay_2026-06-07.json`
- `experiments/gan2026_reset_clinical_assessment_pipeline_validation750_gpt41mini_v0_hn1_multimonth_replay_2026-06-07.score.jsonl`
- `experiments/gan2026_validation750_null_reduction_slices_after_hn1_multimonth_2026-06-07.json`
- ``

Saved source artifacts reused for the replay:

- `experiments/gan2026_candidate_set_clinical_assessment_probe_live_validation750_gpt41mini_v3nested_v3_2026-06-06.jsonl`
- `experiments/gan2026_validation750_candidate_set_v3_nested_dedupe_context_v1_2026-06-06.jsonl`

---

## 3. Whole-Pipeline Change

The fresh GPT-4.1-mini reset-native replay improved the saved validation750
surface overall:

- rendered rows: `580 -> 592` (`+12`)
- null renders: `170 -> 158` (`-12`)
- Purist-correct scored rows: `488 -> 494` (`+6`)
- routed rows: `73 -> 40` (`-33`)

So the new Normalize/projection state is not a no-op. It materially changes the
overall reset-native validation750 mechanics.

---

## 4. HN1 Proxy Slice Result

### 4.1 Raw slice counts look worse unless the row universe is held fixed

The named `frequency_rate_values_unparsed` slice changed from:

- baseline: `71` rows, `24` rendered, `47` null, `23` Purist-correct,
  `23` Pragmatic-correct

to:

- fresh replay: `85` rows, `26` rendered, `59` null, `21` Purist-correct,
  `25` Pragmatic-correct

This does **not** mean the new family simply made the slice worse. The row
universe itself expanded by `14` rows because additional validation rows now
carry `frequency_rate_values_unparsed`.

### 4.2 Stable-row comparison is the fairer read

On the original `71` baseline rows only, the fresh replay moves to:

- `25` rendered (`+1`)
- `46` null (`-1`)
- `21` Purist-correct (`-2`)
- `24` Pragmatic-correct (`+1`)

So the slice improvement is real but small, and it comes with a Purist
regression.

### 4.3 Newly rendered rows on the baseline row universe

Rows that were null at baseline and rendered on the fresh replay:

- `5551`
- `5791`
- `12192`
- `12236`
- `12751`
- `15129`

Important read:

- `15129` is the clean anchor-window recovery.
- The other newly rendered rows are mostly additive-fallback or adjacent
  behavior, not clear proof that the multi-month-bucket family hit its intended
  target examples.

### 4.4 New rows pulled into the slice

`14` additional rows now appear inside the
`frequency_rate_values_unparsed` slice; `13` of them are still null.

Representative new entrants:

- diary/date-list rows such as `4337`
- inter-seizure-interval rows such as `4562`, `4563`, `4574`, `4592`, `4597`
- year-to-date count rows such as `12788`, `12810`, `12877`, `12949`, `12979`

This means the slice is now mixing:

- intended HN1 month-bucket debt
- broader count/window completion debt
- rows newly exposed by the current normalization contract

---

## 5. Multi-Month Component-Specific Read

The new family fires explicitly on four validation rows:

- `16084`
- `16133`
- `16195`
- `16220`

These rows carry:

- `frequency_rate_values_repaired_from_multi_month_bucket`
- `frequency_rate_multi_month_window_from_named_buckets`

But this result is mixed:

- `16133` stays Purist-correct.
- `16084` changes from correct `8 per 4 month` to `8 per 3 month`.
- `16195` changes from correct `16 per 4 month` to incorrect `10 per 3 month`.
- `16220` changes from correct `11 per 4 month` to `11 per 3 month`.

So the current denominator-span contract is under-counting the inclusive month
window on at least three already-rendered rows.

This is the most important technical finding from the rerun:

```text
the family is live, but its current denominator/window behavior is not yet
stable enough to treat as a clean validated gain.
```

---

## 6. Residual Single-Month Debt

There are still `21` null rows in the refreshed
`frequency_rate_values_unparsed` slice that mention an explicit month or date.

They split into four practical groups.

### 6.1 True negatives or route-preservation rows

Examples:

- `11337`: `one seizure on 06-Nov after missed doses and sleep deprivation`
- `11389`: `one focal seizure on 21 December`
- `14335`: `three to four seizures around October`

These still look like boundary/route or insufficient-window cases, not clean
Normalize misses.

### 6.2 Anchor/date-window rows still better owned by anchor logic

Examples:

- `14092`
- `14146`
- `14965`
- `15094`
- `15108`
- `15127`

These remain explicit since-anchor / last-event-anchor problems, not generic
single-month parsing debt.

### 6.3 Single-month partial-burden rows

Examples:

- `14587`
- `14592`
- `15964`
- `15986`
- `15997`
- `16021`

These still look mostly like broader current-burden or same-note window debt.
They do **not** yet support a broad `count in month -> count per 1 month`
Normalize rescue.

### 6.4 Intended explicit multi-month positives that are still null

Examples:

- `16674`
- `16697`
- `16758`
- `16833`

These were the clean promotion examples from the prior evaluation memo, yet
they remain null on the fresh replay. That suggests the present family boundary
is still missing the intended target surface.

---

## 7. Decision

The updated slice read supports two concrete decisions.

### 7.1 Residual single-month rows are still mostly not the next Normalize target

The refreshed null surface still points to:

- selection/window debt
- anchor ownership debt
- route-preservation negatives

more than to a clean broad single-month Normalize family.

So the answer to the original work-board question is:

```text
No: the remaining single-month rows should not be promoted as broad new
Normalize debt on the basis of this rerun.
```

### 7.2 The new multi-month family needs contract tightening before further promotion

Because the rerun shows:

- denominator under-span regressions on already-correct rows, and
- missed recovery on the intended explicit multi-month target examples,

the next HN1 task should be:

```text
tighten the inclusive window/denominator contract for multi-month bucket
recovery, then rerun the same GPT-4.1-mini saved-artifact replay before using
the current state as the stable comparator for Qwen.
```

---

## 8. Bottom Line

The rerun did complete the requested slice audit and it clarified the plan:

- overall validation750 reset-native mechanics improved materially;
- the named HN1 proxy slice improved only slightly on a stable row universe;
- the current multi-month family is active but not yet stable;
- the residual single-month surface still looks mostly like selection/window or
  anchor debt, not a license for broad single-month Normalize rescue.

So the right next move is not broadening single-month handling. It is fixing
the current multi-month denominator/targeting contract first.
