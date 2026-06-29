# ADR 0037: SeizureFrequency state_profile is the primary clinical metric

Date: 2026-06-29

## Status

Accepted.

## Decision

The 4-way change-aware `state_profile` (`frequency_state_faithful`: seizure-free /
active-rate / changed / unknown) is the primary clinical SF metric for all future
ExECTv2 GEPA and single-model experiments. The legacy count-only
`clinical_headline` (`_frequency_state`: seizure-free / active-rate / unknown) is
retained as a convention-strict companion for benchmark continuity but is no longer
the number experiment conclusions are drawn from.

## Context

`_frequency_state` (`scoring/seizure_frequency.py:218-234`) is count-only and
**`FrequencyChange`-blind** by design: any SF fact whose only signal is a
qualitative change descriptor (FrequencyChange = Increased / Decreased / Frequent /
Infrequent / Same) is re-bucketed to `unknown`. The change-aware
`frequency_state_faithful` (`scoring/seizure_frequency.py:237-259`) credits
FrequencyChange as its own `changed` state.

Phase 3b (`exectv2_phase3b_sf_deterministic_projection.py`, 2026-06-29) made the
cost of using the wrong metric concrete. The deterministic SF projection added 18
recall-additive `changed` facts across 15 letters, lifting state_profile
**0.710 → 0.779** (+0.069). But on `clinical_headline` the same 18 facts are
**invisible** (they score as `unknown`), so the clinical_headline lift
(0.580 → 0.650) came entirely from the filter/repair sub-operation, understating
the projection's effect by ~50%. A metric that silently zeroes an entire clinical
state cannot be the one experiments are optimized or concluded against.

This was already flagged in
`docs/research/exectv2_sf_representation_not_recall_2026-06-28.md` (P1, §1) which
showed the strict key under-credits SF by ~0.12 overall and the 0.592 "plateau"
was partly a measurement artifact. Phase 3b confirms the live cost.

## What this changes

- **Experiment headlines, gate criteria, and kill-criteria** for SF report
  `state_profile` as the primary number, with `clinical_headline` as a companion.
- **GEPA optimization objectives** for SF programs (P2, Phase 4 successors) optimize
  against `state_profile`, not `clinical_headline`.
- **Comparisons to the hybrid** use the hybrid's `state_profile` (0.930) as the
  target, not its `clinical_headline` (0.926).
- `clinical_headline` is NOT deprecated or removed — it remains the frozen
  benchmark key for legacy comparability and for families where the change class is
  not in play (Dx, Rx, Inv). It is demoted from *primary SF clinical metric* to
  *convention-strict companion*.

## What this does not change

- The `clinical_headline` field on `FrequencyStateScores` is unchanged in code.
- Other entity families (Diagnosis, Prescription, Investigations) continue to use
  their existing headline metrics as primary.
- The frozen benchmark F1 reported for regulatory/benchmark comparability may still
  cite `clinical_headline`, but experiment-internal conclusions (gate passage,
  kill-criteria, headline results) cite `state_profile` for SF.
