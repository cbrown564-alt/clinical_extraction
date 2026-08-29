# Protocol: Gan rules-only three-stage Phase D (`test450` aggregate)

Date: 2026-08-29
Status: predeclared before holdout load
Owner: this file
Parent: [Phases A–C protocol](gan_rules_only_three_stage_protocol_2026-08-29.md)
Frozen candidate: [Phase C result](gan_rules_only_three_stage_phase_c_2026-08-29.md)
Config: `phase_c_candidate_config()` in `gan2026/orchestration/three_stage.py`
Guardrail: `gan2026-scoring-guardrail`; row policy
[holdout is aggregate-only](../../paper/decisions/holdout-is-aggregate-only.md)

## Primary question

Does the frozen Phase C candidate transfer on locked `test450` as one
Purist select-stop count versus the cited living rules row
**321/450 = 0.71**?

This is one consumption of the holdout split. The number is the
promotion gate. It is not a class study and not a stage-rung study.

## Why this matters

Phase C froze a development candidate at **691/750 = 0.9213** on
`dev750` (additive +22, zero comparator-correct regressions). The
cited five-cell rules row remains **0.71** by construction of the
living single-stop program. Phases A–C never loaded `test450`. A
disappointing holdout aggregate does not authorize holdout repair; it
starts a new development candidate from recorded priors.

## Frozen candidate and comparator

| Arm | Program | Development select |
| --- | --- | ---: |
| Comparator | living `run_record(architecture="rules")`; cited `test450` **321/450 = 0.71** | 669/750 = 0.892 |
| Candidate | `run_record_three_stage(phase_c_candidate_config())`: all seven Phase B classes kept; two named pre-ladder overrides | 691/750 = 0.9213 |

Zero model calls. Scorer: Purist via `score_label` / `map_purist`.
No scorer, label-form, parse-bound, or sentinel change.

### History-flagged keeps (recorded priors, not holdout analysis)

These flags come from development history and Phase C. They are not
read from this replay:

| Keep | History flag |
| --- | --- |
| `keep_nightly_narrative_rate` | Re-poses killed G1 Candidate A (`rate.nightly_seizures`); prior aggregate `test450` **−1** |
| `keep_non_epileptic_current_free` | Re-poses G2 Candidate B; prior holdout **inert** |

Per-class holdout deltas from this replay are never computed, never
read, and never written. If the aggregate disappoints, a successor
candidate is a new `dev750` decision that may drop or reshape those
two keeps using only these recorded priors.

## Data and inspection

| Item | Value |
| --- | --- |
| Dataset | Gan 2026 |
| Holdout split | `test450` (locked, 450 records via `load_records_for_split`) |
| Split loader | `gan_machine_split("test450")` |
| Row policy | `aggregate_only` |
| Development split | Gate A only (`dev750`); not in the public holdout artifact |
| Runs | Exactly one paired holdout execution after Gate A |

Do not inspect, quote, or tune on `test450` identifiers, notes,
predictions, evidence, errors, changed rows, or class slices. Do not
change `phase_c_candidate_config()` between Gate A and Gate B.

## Primary metric

One number: candidate select-stop Purist correct count out of 450,
reported as `correct/450` and the four-decimal rate.

Secondary public fields allowed: the comparator select-stop count
(sanity that the living program still replays **321/450**), the
integer delta versus 321, and the predeclared verdict. Pragmatic,
per-class, per-mode, and stage-stop holdout numbers are not public
unless promotion is accepted (stage stops only).

## Predeclared verdict (binding before the number is seen)

Cited comparator: **321/450**.

| Outcome | Condition | Action |
| --- | --- | --- |
| `blocked_by_comparator_drift` | living `run_record` select Purist ≠ 321 | Stop. Do not interpret the candidate. Diagnose on tooling/gold, not holdout rows. |
| `promotion_accepted` | candidate select Purist **> 321** and comparator = 321 | Replace the cited rules row with this aggregate. Wire measured find/encode/select stops into `_gan_grid` from the same run. |
| `disappointing_development_only` | candidate select Purist **≤ 321** and comparator = 321 | Cited row stays **321/450 = 0.71**. Do not wire stage stops. Do not retune from holdout. Start a new development candidate on `dev750` from the G1/G2 priors above. |

Beating 321 is the only promotion bar. Closing the cell-3 **0.83**
gap is not required and is not claimed from a modest lift. A lift
that still sits far below 0.83 is still a rules-row replacement if
and only if it beats 321.

Do not reframe a disappointing aggregate as a near-miss, a class
win, or a stage-rung success. Do not read per-class holdout deltas
to explain either outcome.

## Gate A — development parity (precondition)

`test450` is not loaded until Gate A passes on current HEAD.

Re-run
`scripts/measure_gan_rules_only_select_keeps_dev750.py phase_c_candidate`
and confirm:

| Target | Value |
| --- | ---: |
| Baseline (Phase B gated) select Purist | 669/750 |
| `phase_c_candidate` select Purist | 691/750 |
| Comparator-correct regressions | 0 |
| Arm config equals `phase_c_candidate_config()` | true |

If Gate A fails, do not run Gate B.

## Gate B — holdout execution

One paired run on all 450 test records: comparator `run_record` and
candidate `run_record_three_stage(phase_c_candidate_config())`.

Row-level outputs go to
`scratch/holdout/gan_rules_only_three_stage_test450_20260829/` and
are sealed (path, `sha256`, byte count only in the public artifact).
Do not open the sealed file for analysis.

The public artifact
(`experiments/gan_rules_only_three_stage_phase_d_test450_aggregate_20260829.json`)
contains aggregates only: n, comparator select count, candidate
select count, delta versus 321, verdict. No `source_row_index`,
note, label, class table, or stage-stop block unless promotion is
accepted (then find/encode/select Purist counts only).

`scripts/check_locked_aggregate_safety.py` is extended with the new
path and must pass.

## Claim boundary

Aggregate holdout evidence for one frozen development candidate. Not
clinical validation. Not a class report. The cited five-cell rules
row remains **0.71** until this protocol completes and the
predeclared verdict is `promotion_accepted`.
