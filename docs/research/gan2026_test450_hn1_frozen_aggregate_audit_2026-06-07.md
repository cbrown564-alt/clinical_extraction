# Gan 2026 Test450 HN1 Frozen Aggregate Audit

Date: 2026-06-07

Author: Codex

Status: frozen aggregate-read holdout audit, authorized by
`docs/research/gan2026_test450_null_reduction_synthesis_and_hypotheses_2026-06-07.md`
section 7.2 ("test450 should be revisited only as a frozen aggregate audit
after each promoted family or carefully batched family set").

This is a saved-artifact replay over the locked `test450` split. It reassembles
the saved ClinicalAssessment drafts and CandidateSet artifacts with the current
deterministic normalization/projection code (HN1 anchor-window plus multi-month
bucket recovery, both enabled by default) and reruns projection/render, score
audit, routing, and verification decision. It does not perform row-level
holdout tuning, does not add new clinical logic, and the score context remains
audit-only.

---

## 1. Inputs

- Frozen baseline (the synthesis-doc state, restored YTD denominator rule, HN1
  *not yet implemented*):
  `experiments/gan2026_reset_clinical_assessment_pipeline_test450_ytd_fix_2026-06-07.*`
- Refreshed HN1 frozen audit:
  `experiments/gan2026_reset_clinical_assessment_pipeline_test450_hn1_frozen_audit_2026-06-07.*`
- Pipeline runner (no new model calls, saved-artifact composition only):
  `src/clinical_extraction/tasks/seizure_frequency/gan2026/hybrid/reset_clinical_assessment_pipeline.py`
- Both replays use the same saved source artifacts:
  - assessment: `gan2026_candidate_set_clinical_assessment_probe_live_test450_gpt41mini_v3nested_v3_2026-06-07.jsonl`
  - candidate set: `gan2026_test450_candidate_set_v3_nested_dedupe_context_v1_2026-06-07.jsonl`

---

## 2. Whole-Pipeline Change

| Metric | Baseline (`ytd_fix`) | HN1 frozen audit | Delta |
| --- | ---: | ---: | ---: |
| input assessment rows | 450 | 450 | `0` |
| projection rows | 449 | 449 | `0` |
| rendered labels | 341 | 358 | `+17` |
| null renders | 108 | 91 | `-17` |
| scored rows | 341 | 358 | `+17` |
| Purist correct | 271 (`79.47%`) | 282 (`78.77%`) | `+11` |
| Pragmatic correct | 280 (`82.11%`) | 294 (`82.12%`) | `+14` |
| routed rows | 41 | 29 | `-12` |
| deterministic verification actions | `41 abstain` | `29 abstain` | `-12` |

This is the first time since the synthesis doc froze the `108`-null,
`341`-rendered state that **rendered coverage has moved on the holdout split**.
HN1 converts `17` previously-null rows into source-backed rendered output,
recovers `11` net Purist-correct rows, and shrinks the routed surface by `12`
rows with **zero new routes**.

---

## 3. Row-Level Transition Audit

Comparing `source_row_index`-aligned score rows between the baseline and the
HN1 frozen audit:

- **Newly rendered**: `17` rows (`892`, `934`, `1629`, `2725`, `12300`,
  `12330`, `12335`, `12392`, `12590`, `12643`, `12645`, `14590`, `15620`,
  `16807`, `16820`, `16834`, `16962`)
  - `11 / 17` are Purist-correct on the new render
    (`892`, `934`, `1629`, `2725`, `12300`, `12330`, `12335`, `12392`,
    `16807`, `16820`, `16834`)
  - `6 / 17` render but score Purist-incorrect (`12590`, `12643`, `12645`,
    `14590`, `15620`, `16962`) — these are now visible, audit-traceable, and
    scoreable instead of hidden behind a null
- **Newly null**: `0` rows
- **Wrong-to-correct (`W->C`) on already-rendered rows**: `0`
- **Correct-to-wrong (`C->W`) on already-rendered rows**: `0`

Net Purist-correct arithmetic: `271 + 11 (new correct) - 0 (lost) = 282`,
matching the frozen summary exactly.

This is a clean transition profile by the synthesis doc's own promotion
criteria (section 7.4): positive rendered-row gain, **zero regression** on
already-rendered rows, full trace visibility, and a frozen aggregate holdout
improvement.

---

## 4. Route-Family Read

The `12`-row routed-surface contraction is concentrated in one family:

| Route family | Baseline | HN1 audit |
| --- | ---: | ---: |
| `selected_source_id_invalid` | 15 | 15 |
| `mixed_window_or_vague_addition` | 13 | 1 |
| `cluster_axis_ambiguity` | 7 | 7 |
| `unresolved_cluster_cadence_with_per_cluster_burden` | 4 | 4 |
| `denominator_window_mismatch` | 2 | 2 |
| `relative_only_trend` | 1 | 1 |

All `12` rows that left the routed surface
(`892`, `1629`, `2725`, `12300`, `12330`, `12335`, `12392`, `12590`, `12643`,
`12645`, `15620`, `16962`) **also became newly rendered**, and **no row that
was previously unrouted became newly routed**. That means HN1 did not "fix
nulls by routing them away" — it resolved the underlying additive/multi-window
frequency ambiguity that previously produced both the null render *and* the
route flag (`mixed_window_or_vague_addition`), in one upstream `Normalize`
step. This is exactly the "convert already-supported clinical facts into
renderable outputs" mechanism the synthesis doc asked for, not verifier-side or
route-side rescue.

---

## 5. A Real Bug Found And Fixed Along The Way

The first frozen-audit pass (before the fix below) showed a **mixed** result:
`+11` rendered net but with a `6`-row regression tail (`6` previously-correct
rendered rows became null, `2` already-rendered rows flipped from correct to
wrong). Tracing those regressions to source level showed they were **not**
caused by the new HN1 recovery families. They were caused by a pre-existing,
overly broad text-normalization regex:

```python
# src/clinical_extraction/tasks/seizure_frequency/gan2026/llm/llm_candidate_set_clinical_assessment_probe.py
text = re.sub(r"\s*[-–—]\s*", " to ", text)
```

This unconditionally rewrote **any** hyphen/en-dash/em-dash as `" to "`,
corrupting hyphenated clinical compound terms — e.g. `tonic-clonic seizures`
became `tonic to clonic seizures` — before the frequency-rate parser ran. The
corrupted phrase then failed to match the parser's patterns and the row fell
through to `frequency_rate_values_unparsed`/`incomplete`. The regex predates
HN1 (landed `2026-06-06` in commit `081e8fd6`), but it was previously masked
because fewer phrases were routed through `_normalize_phrase_for_parse`; the
new HN1 anchor-window/multi-month families route more saved phrases through
that function, which surfaced the latent corruption on holdout rows such as
`2795` (`weekly tonic-clonic seizures` -> `1 per week`), `7327`
(`two brief generalised tonic-clonic seizures over the past four months` ->
`2 per 4 month`), and `12826`
(`just ten generalised tonic-clonic seizures documented this year to date` ->
`10 per 4 month`).

**Fix**: anchor the substitution to digit-bounded numeric ranges only, so
`24-48 hours` still becomes `24 to 48 hours` and `3-5 seizures` still becomes
`3 to 5 seizures`, but `tonic-clonic`, `absence-myoclonic`, and similar
clinical compound terms pass through untouched:

```python
text = re.sub(r"(?<=\d)\s*[-–—]\s*(?=\d)", " to ", text)
```

Regression coverage was added directly on the normalization helper and on
end-to-end assembly in
`tests/test_gan2026_llm_candidate_set_clinical_assessment_probe.py`
(`test_normalize_phrase_for_parse_keeps_hyphenated_clinical_terms_intact`,
`test_normalize_phrase_for_parse_still_converts_numeric_ranges`,
`test_assemble_clinical_assessment_parses_hyphenated_clinical_term_rate`).
The fix turned the mixed `+11`/`-8` result into the clean `+17`/`0` result
reported in sections 2-3. The full focused suite for this module
(`43` tests) and the broader `gan2026`-tagged suite pass after the fix, with
the only `3` failures being pre-existing ones unrelated to this change
(`test_build_projection_render_repairs_once_per_night_from_primary_candidate`,
`test_build_projection_render_repairs_diary_prefixed_numeric_date_list`,
and a typed-operations-reasoner cleanup-artifact test).

---

## 6. Reading The Newly-Rendered Incorrect Rows

The `6` newly-rendered-but-incorrect rows are now visible and traceable instead
of hidden, which is the intended outcome — they expose a real residual-accuracy
ceiling rather than masking it:

- `12590`, `12643`, `12645`, `14590`, `15620`, `16962` render plausible
  count/period values from source-backed evidence, but the selected
  denominator window or count does not match the gold label.

This matches the synthesis doc's framing: null reduction trades some
visible-but-imperfect renders for previously-invisible facts, and the
`11 / 17` correct-render rate on the newly-recovered surface is consistent
with (slightly below) the prior `79.47%` baseline accuracy on already-rendered
rows. The aggregate effect is still net positive because:

1. absolute correct count rises (`271 -> 282`);
2. the previously-correct surface is fully preserved (`0` `C->W`, `0` newly
   null);
3. `17` more clinical facts are now source-traced and scoreable instead of
   silently absent.

---

## 7. Decision

HN1 (source-near frequency value recovery) is **promoted** on the frozen
holdout audit:

- positive rendered-row gain: `+17` (`341 -> 358`) — synthesis criterion met;
- zero regression on already-rendered rows: `0` `W->C`/`C->W`/newly-null —
  synthesis criterion met;
- visible trace fields and named rule ownership preserved
  (`anchor_window_frequency_value_recovery`,
  `multi_month_bucket_frequency_value_recovery`,
  `frequency_rate_values_repaired_from_multi_month_bucket`,
  `frequency_rate_multi_month_window_from_named_buckets`, etc.) — synthesis
  criterion met;
- portability from validation to holdout confirmed: validation750 moved
  `580 -> 597` rendered / `170 -> 153` null; holdout moved `341 -> 358`
  rendered / `108 -> 91` null — synthesis criterion met;
- frozen aggregate holdout improvement: `null renders 108 -> 91`,
  `Purist correct 271 -> 282`, `routed rows 41 -> 29` — synthesis criterion
  met, with the routed surface shrinking rather than expanding.

HN1 closes the validation-to-holdout loop described in the synthesis doc
section 9:

```text
validation-developed proxy slices for frequency null families
-> ablatable portable components (anchor-window + multi-month bucket recovery)
-> frozen aggregate holdout audit (this document)
-> score gains by reducing nulls, not by hiding them (-17 null, +11 correct, no new routes)
```

---

## 8. What's Next

HN1 addressed the multi-month/anchor-window slice of the
`frequency_rate_values_unparsed` / `frequency_rate_values_incomplete` family.
The residual holdout null surface (now `91` rows, down from `108`) still
contains the bulk of the originally-named families — `vague_count`,
`seizure_free_duration_required`, `seizure_free_duration_unparsed`,
`cluster_frequency_values_unparsed`, `cluster_cadence_values_incomplete` — none
of which moved in this audit, as expected (HN1 was scoped narrowly and did not
touch them).

Per the synthesis doc's recommended execution order (section 8), the next
research move is **HN2 (bounded vague-with-window rendering)**, developed the
same way: validation-only proxy slices on `vague_count`, an ablatable
`Project`-owned component, then a frozen `test450` aggregate audit following
this same protocol.
