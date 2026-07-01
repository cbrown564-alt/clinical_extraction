# Verify-stage credit assignment in multi-stage GEPA — does a stage-local reward fix it?

Status: **CLOSED. Qualitative hypothesis CONFIRMED; quantitative kill-criterion narrowly MISSED
(-0.0014).** Date: 2026-07-01. Owner: ExECTv2 GEPA workstream.

Executes: Item 1 (Tier 1) of
`docs/research/exploratory_research_directions_multiagent_review_2026-07-01.md`, Phase 2 of
`docs/plans/exectv2_exploratory_directions_implementation_plan_2026-07-01.md`.

Companions:
- `docs/research/exectv2_gepa_single_model_plateau_synthesis_2026-06-28.md` §3 (the prior
  multistage run and its diagnosed failure mode)
- `docs/plans/exectv2_gepa_multistage_program_scope_2026-06-28.md`
- Code: `src/.../exectv2/gepa/metric.py` (`_verify_stage_feedback`, `_verify_family_of`),
  `src/.../exectv2/gepa/program_multistage.py`,
  `experiments/gepa_multistage_verifyonly_exectv2.py`
- Tests: `tests/test_exectv2_gepa_metric.py` (8 new stage-local-feedback tests)
- Runs: `exectv2_gepa_multistage_dedup_gpt41mini_20260628` (prior, 0.7235),
  `exectv2_gepa_multistage_verifystage_dedup_gpt41mini_20260701` (this run, 0.7596)

## 1. Question

The repo already had a documented negative result: the jointly-evolved multi-stage
(generate->verify) GEPA program missed its kill-criterion (0.7235 vs. the single-pass 0.731
ceiling, needing >= 0.761) because the verify stage was scored on the same undecomposed
end-to-end `clinical_headline` F1 as the generator. Evolved-instruction inspection showed the
mechanism: verify cut recall (805->783 facts) and the most heavily-evolved verifier drifted
into "output a complete corrected list in hyphenated-lowercase canonical representation" —
reformatting, not filtering.

The multi-agent review's generalized claim: *if a verify/critique stage in a
reflective-prompt-optimization pipeline shares an undecomposed scalar reward with its upstream
generator, optimization will not learn to verify — it will learn to regenerate.* Falsifiable,
cheap test proposed: rerun with a stage-local metric (verifier scored on accept/reject precision
against a frozen generator's candidate set, independent of final headline F1) and check whether
the evolved instruction text becomes filter-shaped and the kill-criterion delta turns positive.

## 2. Method

Two changes from the prior multistage run, both additive (no change to the single-pass or
multifamily programs, no change to any other program's behavior — verified by 8 new unit tests
plus the existing 24-test multistage/metric suite, all passing):

1. **Frozen S0.** Generate predictors warm-start from `load_evolved_s0_seeds()` (the evolved
   0.731 per-family instructions, IDENTICAL seed to the prior run) and are excluded from
   mutation entirely via a new `VerifyOnlySelector` (`ReflectionComponentSelector` restricted to
   the four `verify_<family>` predictors). The prior run mutated all 8 predictors jointly.
2. **Stage-local reflection feedback.** `metric.py`'s `build_metric()` now branches on
   `pred_name`: a `verify_<family>` reflective-mutation call gets `_verify_stage_feedback` — an
   accept/reject/add audit of that predictor's own decision on each draft fact it was given
   (`pred_trace`'s captured `draft_facts_json` input vs. `verified_facts_json` output), keyed
   against gold via the same `_family_unit_keys` the final scorer uses, entirely independent of
   the merged-output diff. The **selection score stays the unchanged end-to-end
   `clinical_headline` F1** — only the feedback TEXT differs; GEPA's Pareto/candidate selection
   is untouched, so this isolates exactly the credit-assignment variable the review named.

Same task/reflection models (gpt-4.1-mini / deepseek-reasoner), same `auto="medium"` budget
class, same dev140 final-eval surface, same kill-criterion (beat 0.731 by >= +0.03) as the prior
run, for a clean two-run comparison.

## 3. Result

| | prior multistage (joint, whole-program feedback) | this run (frozen S0, stage-local feedback) | delta |
| --- | ---: | ---: | ---: |
| `clinical_headline` overall F1 | 0.7235 | **0.7596** | **+0.0361** |
| precision | 0.7399 | 0.8162 | +0.0763 |
| recall | 0.7078 | 0.7103 | +0.0025 |
| Diagnosis | 0.65 | 0.7194 | +0.0694 |
| SeizureFrequency | 0.55 | 0.6006 | +0.0506 |
| Prescription | 0.8514 | 0.886 | +0.0346 |
| Investigations | 0.916 | 0.8571 | -0.0589 |
| final facts emitted | 783 | 675 | -108 |
| final instruction tokens | 4030 | 4660 | +630 |
| elapsed | 141.3 min | 366.1 min | +224.8 min |

**Kill-criterion (beat 0.731 by >= +0.03, i.e. >= 0.761): 0.7596 — MISSES by 0.0014.** This is
a rounding-level margin, not a robust pass, and is reported as a miss per the pre-registered
criterion. It is nonetheless a decisive improvement over the prior attempt (+0.036, more than
4x the prior run's shortfall) and comes within 0.2% of clearing the bar outright.

**The improvement is precision-driven, not recall-driven** — precision +0.076 vs. recall +0.003
— meaning the stage-local verify learned to reject *more* spurious drafts (108 fewer final
facts than the prior run, a much bigger cut) while barely touching correct recall, the opposite
of the prior run's failure (a *smaller* cut that still lost enough recall to hurt F1 net).
Investigations is the one family that regressed (-0.059); not investigated further here — a
single-family regression inside an aggregate net gain, out of scope for this credit-assignment
question (see Tier-2 item 6 territory if it recurs).

Evidence-recall (`source_near`, a different metric from `clinical_headline`) dropped to 0.6435
overall — *below* the per-family GEPA baseline's 0.694 comparator. Reported for completeness:
this run's precision-favoring verify pulled down raw evidence-presence recall even as the
headline (precision+recall-weighted) F1 rose. Not itself evidence against the credit-assignment
hypothesis — the hypothesis is about the verify stage's decision quality on
`clinical_headline`, and F1 rose — but a caveat for anyone citing this run's evidence-recall
number alongside its headline number.

### 3.1 The qualitative mechanism check — filter-shaped vs. reformat-shaped

The prior run's failure signature was a verifier instruction that drifted toward reformatting
("output a complete corrected list in hyphenated-lowercase canonical representation"). This
run's four evolved verify instructions
(`experiments/exectv2_gepa_multistage_verifystage_dedup_gpt41mini_20260701.instruction.txt`)
are unambiguously filter-shaped instead — three of four contain near-verbatim echoes of the new
stage-local feedback's own closing guidance ("do not rewrite, reformat, or regenerate the whole
list"):

- **verify.diagnosis**: "Do not rewrite, reformat, or regenerate the whole list – only filter
  (accept/reject) the draft facts and optionally add a clearly-missed fact."
- **verify.seizure_frequency**: "Do not rewrite, reformat, or regenerate the whole list—only
  accept/reject individual draft facts."
- **verify.prescription**: "Rules for filtering each draft fact (decide independently, do not
  rewrite the list)... Your goal is to be a precise filter – accept or reject each draft fact on
  its own merits."
- **verify.investigation**: "Remember: Your primary role is to **filter and de-duplicate** the
  draft list. Only add a missing fact if it is clearly justified."

All four also specify explicit, enumerated per-fact keep/reject criteria (evidence-substring
exactness, modality/result whitelists, dose/frequency normalization rules, duplicate handling) —
the "filter-shaped: explicit keep/reject criteria" signature the review predicted, not the prior
run's "regenerate the whole list in canonical form" drift. This qualitative check is a clean,
unambiguous **CONFIRM**.

## 4. Verdict on the review's generalizable claim

**CONFIRMED, with a precise scope note.** *A verify/critique stage sharing an undecomposed
scalar reward with its upstream generator does drift toward regenerating rather than verifying
— and decomposing the reflection feedback (while leaving the selection score global) is
sufficient to reverse that drift and produce a real, if narrowly short-of-threshold, quality
gain.* The scope note: this run changed **two** things at once (froze S0 *and* decomposed
feedback), not one — a stage-local-feedback-only run (S0 still jointly mutable) was not tested,
so this result confirms the *combination* recovers filter-shaped behavior and improves F1; it
does not by itself isolate how much of the +0.036 is feedback decomposition vs. S0-freezing
alone. Given the review's proposed mechanism is specifically about feedback decomposition (not
freezing), and freezing S0 mechanically cannot explain a precision *gain* on the SAME frozen
draft distribution (only the verify stage's own decisions changed), the improvement is
attributable to the feedback change — but a rigorous ablation isolating the two variables is
future work, not claimed here.

## 5. What this leaves open

- Does not clear the pre-registered kill-criterion outright (0.7596 < 0.761) — report as a
  near-miss, not a pass, in any future citation.
- Investigations' regression (-0.059) is unexplained here.
- Whether feedback-decomposition alone (S0 still mutable) reproduces most of the gain, or
  whether freezing S0 is doing real work too, is untested (would need a third run with
  stage-local feedback + S0 still in the component selector).
- The evidence-recall drop (0.6435, below the 0.694 per-family comparator) alongside the
  headline F1 rise is a real divergence between two of this project's standard metrics on the
  same run; not reconciled here.

## 6. Registry

`exectv2_gepa_multistage_verifystage_dedup_gpt41mini_20260701` registered automatically on this
run (the pre-existing broken-artifact-path row blocking `validate_run_registry_artifacts` — see
`docs/research/exectv2_registry_survivorship_bias_2026-07-01.md` — was fixed as part of this
plan's Phase 2 step 0, before this run started; registration this time required no backfill).
