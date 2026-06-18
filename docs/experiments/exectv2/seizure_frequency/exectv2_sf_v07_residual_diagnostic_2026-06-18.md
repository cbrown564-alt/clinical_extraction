# ExECTv2 SF v0.7 Residual Diagnostic

Date: 2026-06-18

## Scope

This note reviews the current SeizureFrequency route residual after the v0.6
state projection plus v0.7 unknown-suppression replay on dev140. It supersedes
the older routed-family snapshot for the immediate SF residual task: the
stale surface was SF `0.6321` with `77` wrong-detail selections and `65`
candidate misses; the current combined clinical-recovery ledger is SF `0.7824`
with `48` wrong-detail selections and `36` candidate misses.

Inputs:

- `experiments/exectv2_hybrid_sf_unknown_suppression_v07_dev140_20260618.jsonl`
- `experiments/exectv2_key_entities_clinical_error_ledger_v07sf_dev140_20260618.json`
- `experiments/exectv2_key_entities_clinical_error_ledger_v07sf_dev140_20260618.md`

No model calls, full-200 audit, or holdout/test row-level inspection were used.

## Current Residual Shape

The clinical-recovery ledger now emits these diagnostic fields for
SeizureFrequency:

| Diagnostic | Count |
| --- | ---: |
| candidate_miss | 36 |
| wrong_detail_selection | 48 |

Residual by state:

| Side | active-rate | seizure-free | unknown |
| --- | ---: | ---: | ---: |
| gold/candidate_miss | 17 | 11 | 8 |
| predicted/wrong_detail_selection | 19 | 17 | 12 |

Top miss and over-emission keys remain mixed:

- gold misses: generic active-rate `C0036572` (5), generic seizure-free
  `C0036572` (5), GTC active-rate `C0494475` (3), seizure-free concept
  `C1299590` (3), plus small named myoclonic/absence/focal buckets.
- predicted over-emissions: generic seizure-free `C0036572` (9), generic
  active-rate `C0036572` (5), generic unknown `C0036572` (5), seizure-free
  concept `C1299590` (5), and small named active/unknown buckets.

## Interpretation

No prediction-changing rule is predeclared-safe from this review. The remaining
surface is not one clean candidate-miss family:

- Some rows are state disagreements, such as generic active-rate gold versus
  predicted named active-rate or unknown-change state.
- Some rows are ownership disagreements, especially generic `seizure(s)` versus
  named seizure types.
- Some rows are benchmark-format convention disagreements, especially generic
  seizure-free `C0036572` versus seizure-free concept `C1299590`.
- Some spans are diagnosis/context or treatment-response language that previous
  v0.7 suppression intentionally handled only for high-precision unknown drops.

Adding another broad recovery or suppression regex would likely blend
`seizure_frequency` semantic rules with benchmark-format projection and would be
hard to attribute cleanly.

## Implemented Diagnostic

`clinical_recovery_error_ledger` now records:

- `residual_error_counts`: gold-side residuals as `candidate_miss` and
  predicted-side residuals as `wrong_detail_selection`.
- `residual_state_counts`: SeizureFrequency residuals split by side and state.

The v07sf JSON and markdown ledgers were regenerated from the same dev140 input
artifacts, adding a `Residual By State` table to the SeizureFrequency section.

## Next Action

Predeclare an SF v0.8 hard-slice diagnostic before changing predictions:

1. Build a dev140-only panel of letters whose SF residuals contain both sides
   of a state or ownership disagreement.
2. Label each pair as one of: `generic_named_ownership`, `state_swap`,
   `seizure_free_cui_convention`, `diagnosis_context_span`, or `true_candidate_gap`.
3. Only implement a rule if one bucket has an explicit non-gold feature, at
   least 5 possible fixes, and a stop rule that prevents active-rate or
   seizure-free recall regression.

Until that hard-slice exists, v0.7 should remain the promoted SF route layer and
the next code change should not modify prediction-bearing SF projection.
