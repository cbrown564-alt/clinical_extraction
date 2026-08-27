# ExECTv2 Prescription lens v10 holdout confirmation (test59)

Date: 2026-08-10
Status: **CONFIRMED** on the predeclared kill criterion

Protocol: recovered from git history; this report is the answer.
Parent: [Prescription lens rule decomposition](prescription_lens_rule_decomposition_2026-08-10.md)
Artifact: [`experiments/exectv2_prescription_lens_v10_holdout_20260810.json`](../../experiments/exectv2_prescription_lens_v10_holdout_20260810.json)
Runner: `removed in the 2026-08-16 scripts prune; recover from git history (was `scripts/check_exectv2_prescription_lens_v10_holdout.py`)`

## Plain answer

The simplification transfers, and the holdout effect is **far larger than the
development effect that motivated it**. On 352 sealed `test59` letter x model
cells:

| Arm | Prescription P | R | micro F1 | Letter exactness | Four-family F1 |
| --- | ---: | ---: | ---: | ---: | ---: |
| v09 (two extra rules) | 0.8527 | 0.8059 | 0.8286 | 0.6591 | 0.7756 |
| **v10 (rules removed)** | **0.8730** | **0.8765** | **0.8748** | **0.7472** | **0.7884** |
| Delta | +0.0203 | +0.0706 | **+0.0462** | **+0.0881** | +0.0128 |

Predeclared criterion was *exactness delta >= 0 and F1 delta >= -0.005*. Both
clear it by a wide margin: **CONFIRMED**.

## Why the holdout gain is ~5x the development gain

On `dev140` removing the two rules was worth `+0.0229` exactness and `+0.0008`
F1 — a simplification that paid for itself but barely moved the score. On
`test59` the same removal is worth `+0.0881` exactness and `+0.0462` F1.

This asymmetry is the predicted signature of the dev-fitting flagged in the
decomposition. `_PRESCRIPTION_RESIDUAL_TARGET_KEYS` is a frozenset of 15 exact
`(drug, dose, unit, frequency)` tuples **harvested from dev140**, so on dev140
the residual-add rule was at its best case and *still* net precision-negative.
Off that set it can only add noise. The noise-drop rule has the same shape: its
regex vocabulary was assembled against development letters.

The development number was therefore the **conservative** estimate, not the
optimistic one. The holdout is where a dev-fitted rule's cost actually shows up.

## Per-model

| Model | n | Rx F1 delta | Exactness delta | Four-family delta |
| --- | ---: | ---: | ---: | ---: |
| GPT-5.6 Luna | 59 | +0.0747 | +0.1356 | +0.0197 |
| GPT-5.6 Sol | 59 | +0.0603 | +0.1186 | +0.0156 |
| DeepSeek V4 Flash | 59 | +0.0609 | +0.1356 | +0.0164 |
| Gemma 4 26B | 57 | +0.0546 | +0.0877 | +0.0155 |
| Qwen 3.6 35B | 59 | +0.0353 | +0.0678 | +0.0098 |
| GPT-4.1-mini | 59 | -0.0030 | -0.0170 | -0.0002 |

**Five of six models improve; GPT-4.1-mini is flat-to-marginally-worse.** That
is the same model-compensating pattern measured on dev140: the deleted rules
patch a weaker model's tendency to emit planned regimens, at a cost to every
stronger model. The holdout confirms the trade is worth taking — the one model
that loses, loses least.

## Fidelity

- Replayed cells: 352 of 354 (2 gemma rows carry empty structured events).
- **v09 arm reproduces the retained sealed Prescription keys at rate 1.000.**
  The comparison arm is the real pre-change implementation restored from git,
  not a re-implementation, so this is a true parity check on the replay path.
- Cells whose Prescription keys are changed by the two removed rules: 75 / 352.
- Sol uses the `exectv2_test60_sol_credit_v2` tree, matching the published
  stage panel's `aggregate_source`. The superseded `exectv2_test60/gpt56sol`
  tree has 40/59 empty event rows and was **not** used.

## Row policy

Machine-only scoring under the Decision 0046 Phase C pattern. Per-cell captures
stayed under `scratch/`; this report and the emitted artifact are
aggregate-only. No letter id, row index, note text, prediction, or failure
example left `scratch/`, and no holdout row was inspected by a human. No rule,
threshold, or table was changed as a result of this run.

## Consequence for the parent document

The decomposition's claim boundary reads *"no worse, and materially simpler",
not "better"* — appropriately cautious given dev140 alone. **The holdout
upgrades that claim.** v10 is simpler *and* better, by margins that matter, on
every model but one. The parent document carries a status banner pointing here.

## Claim boundary

Predeclared confirmation of an already-selected simplification on the ExECT
`test59` holdout, six models, zero model calls. Aggregate-only. Not a new
default selection, not clinical validation, not the published ExECT benchmark.
