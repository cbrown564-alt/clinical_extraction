# Gan rules-only three-stage Phase C: select keeps

Date: 2026-08-29
Protocol: [three-stage protocol](gan_rules_only_three_stage_protocol_2026-08-29.md)
Phase B: [recall-first result](gan_rules_only_three_stage_phase_b_2026-08-29.md)
Artifacts: `experiments/gan2026_rules_only_three_stage_20260829/keep_arms/`
(one JSON per arm: config, net, rescued/regressed/changed row lists)
Script: `scripts/measure_gan_rules_only_select_keeps_dev750.py`

Dataset `dev750` (development, row review permitted); Purist scorer via
`score_label`; zero model calls; `test450` never loaded. Baseline arm =
Phase B config (all classes gated), which reproduces the cited select
rung 669/750 and is asserted by the script.

## Result: select 669 → 691/750 (0.892 → 0.9213), zero regressions

All seven Phase B classes are accepted into the frozen Phase C
candidate (`phase_c_candidate_config()` in
`gan2026/orchestration/three_stage.py`): five as bare keeps competing
through the existing priority ladder untouched, two behind new named
pre-ladder override rules. Protocol acceptance held for every
component:

| Component | Mechanism | Isolated net | Candidate − LOO | Regressions |
| --- | --- | ---: | ---: | ---: |
| `keep_electrographic_hourly_rate` | bare keep (ladder) | +5 | +5 | 0 |
| `keep_nightly_narrative_rate` | bare keep (ladder) | +5 | +5 | 0 |
| `keep_non_epileptic_current_free` | bare keep (ladder) | +3 | +3 | 0 |
| `keep_vague_multiple_rate` | bare keep (ladder) | +3 | +3 | 0 |
| `keep_monthly_cluster_unclear_count` | bare keep (ladder) | +2 | +2 | 0 |
| `keep_exclusive_trigger_override` | override rule | +2 | +2 | 0 |
| `keep_single_dated_event_override` | override rule | +2 | +2 | 0 |
| **`phase_c_candidate`** | union | **+22** | — | **0** |

Effects are perfectly additive (no interaction between components; the
Phase B rescue rows were already pairwise disjoint).

## Mechanism notes

1. **The existing ladder did most of the select work.** Bare keeps win
   exactly where they should: rate-form provisional candidates (nightly
   1 per day, monthly frequency 30) outrank low-frequency incumbents at
   equal semantic priority; generic-multiple and generic-seizure-free
   provisional candidates beat empty pools and no-reference fallbacks.
   Pool order puts kept candidates after incumbents, so priority ties
   go to the living program's pick — no scoring or cue function was
   touched, and the comparator path is unchanged.
2. **Unconditional trigger promotion fails and was rejected.** Simulated
   on the Phase B ledger, promoting every kept
   `trigger_conditioned_unknown` candidate to top priority rescues 8
   rows but regresses 6 (e.g. "catamenial exacerbation", "events
   precipitated by" — spans where the trigger *modifies a countable
   frequency* that gold keeps). No lexical gate separates the two sets
   ("-linked events" appears on both sides).
   `select.override.exclusive_trigger_conditioned_unknown` therefore
   fires only on spans carrying an exclusivity marker
   (exclusively / only / uncommon-when / rare-when) — the semantic case
   where all seizures are trigger-bound and no countable current rate
   exists: +2, zero regressions.
3. **`select.override.single_dated_event_unknown`** promotes the dated
   single-event class (which is inert at generic-unknown priority 1)
   over competing state/rate picks: +2, zero regressions; the producer
   pattern itself carries the narrowness (fires on 2 of 750 records).
4. Overrides gate on the candidate's own evidence span only, are named
   and individually switchable in `GanThreeStageConfig.select_overrides`,
   and run as an explicit ordered step between the tagged drops and the
   ladder — the protocol's "explicit ordered Select sequence".

## Stage picture after Phase C (dev750)

find 622/750 (0.8293) → encode 622/750 → select **691/750 (0.9213)**;
wide-ledger oracle 709/750 (0.9453). Remaining residual: 18 rows —
roughly the 13 protected benchmark shorthand rows (contract, never
hand-tuned) plus the one-off narrative paraphrases Phase B deliberately
skipped.

## History-flagged keeps

`nightly_narrative_rate` re-poses killed G1 Candidate A (holdout −1);
`non_epileptic_current_free` re-poses G2 Candidate B (holdout inert).
Both are kept in the development candidate on dev evidence. Phase D is
an aggregate-only `test450` replay of the frozen candidate: if the
aggregate disappoints, any successor candidate is a new development
decision made on these recorded priors — holdout rows are never
inspected and no per-class holdout deltas are read.

## Claim boundary

Development evidence on `dev750` only until Phase D. Phase D later
promoted the frozen candidate on aggregate-only `test450`
(**325/450**). This document does not own the holdout number.

## Next (Phase D)

Done: [Phase D result](gan_rules_only_three_stage_phase_d_2026-08-29.md).
Aggregate-only `test450` select **325/450**; verdict
`promotion_accepted`.
