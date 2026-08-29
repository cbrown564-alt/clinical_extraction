# Gan rules-only three-stage Phase D: aggregate-only `test450`

Date: 2026-08-29
Status: complete; verdict `promotion_accepted`
Protocol: [Phase D protocol](gan_rules_only_three_stage_phase_d_protocol_2026-08-29.md)
Phase C: [select keeps](gan_rules_only_three_stage_phase_c_2026-08-29.md)
Artifact: `experiments/gan_rules_only_three_stage_phase_d_test450_aggregate_20260829.json`
Owner after promotion: `paper_experiments/gan/gan_rules.json`

Dataset `test450` (locked); Purist scorer via `score_label`; zero model
calls. One paired run after Gate A. No holdout row inspection. Per-class
holdout deltas were never computed.

## Gate A

`scripts/measure_gan_rules_only_select_keeps_dev750.py phase_c_candidate`
on current HEAD: baseline 669/750, candidate **691/750**, net +22,
**zero** regressions. `phase_c_candidate_config()` matched the keep-arm
union. Passed.

## Answer

Candidate select Purist **325/450 = 0.7222** versus living
`run_record` and the cited row **321/450 = 0.7133** (Δ **+4**).
Comparator still replayed 321/450, so the run was not blocked by
drift.

Predeclared verdict: **`promotion_accepted`**. The cited five-cell
rules select stop is now **325/450 = 0.72**. Measured stage stops from
the same run (wired into `_gan_grid`): find **292/450**, encode
**292/450**, select **325/450**.

This does not close the cell-3 gap (**0.83**). It replaces the flat
0.71 rules row with a measured gradient.

## History-flagged keeps

The two G1/G2 priors were not read as holdout class deltas. They
remain recorded development history: nightly re-poses G1 Candidate A
(prior aggregate −1); non-epileptic re-poses G2 Candidate B (prior
holdout inert). Promotion does not inspect which keep moved the
aggregate.

## What was not done

- No holdout row, note, label, or error case was read.
- No per-class holdout report. Table 2a in the results draft remains
  the pre-promotion 321-program class reading.
- Pragmatic 341/450 was not recomputed.
- `run_record` (canonical single-stop) is unchanged so Phase A
  identity tests still pin the instrument. Cited replay uses
  `run_record_three_stage(phase_c_candidate_config())`.

## Claim boundary

Aggregate holdout evidence for the frozen Phase C candidate. Not
clinical validation. Not a class study.
