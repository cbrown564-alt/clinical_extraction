# ExECTv2 SF Unknown-Suppression Hard-Slice Predeclaration

Date: 2026-06-18
Scope: SeizureFrequency state projection v0.6 combined output on dev140.
Status: predeclared narrow study; not yet a run result.

## Objective

Test whether a narrow, high-precision deterministic suppression layer can reduce
unknown-state SeizureFrequency over-emission after v0.6 without sacrificing the
active-rate and seizure-free gains that made v0.6 useful.

This is a hard-slice study, not a broad prompt pass, not a new model call, and
not authorization for a full-200 audit.

## Fixed Baseline

Baseline artifact:
`experiments/exectv2_hybrid_sf_state_projection_v06_combined_dev140_20260618.jsonl`

Baseline headline:

| Family | F1 | Precision | Recall | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SeizureFrequency v0.6 combined | 0.763 | 0.722 | 0.807 | 151 | 58 | 36 |

Baseline state slices:

| State | F1 | Precision | Recall | TP | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| active-rate | 0.800 | 0.791 | 0.809 | 72 | 19 | 17 |
| seizure-free | 0.794 | 0.761 | 0.831 | 54 | 17 | 11 |
| unknown | 0.625 | 0.532 | 0.758 | 25 | 22 | 8 |

Hard-slice diagnostic:
`experiments/exectv2_sf_v06_hard_slice_diagnostic_dev140_20260618.md`

## Hypothesis

The remaining unknown-state residual is precision-limited. A finite
`seizure_frequency` deterministic suppression rule set may remove a small,
high-confidence subset of unknown false positives, especially:

- drug-response or treatment-effect scope;
- unsupported or conditional change language;
- unknown predictions whose evidence states an active rate;
- unknown predictions whose evidence states seizure freedom;
- generic/named ownership duplicates where another kept state already owns the
  clinically relevant frequency.

The study should not add a new broad unknown/change recovery rule.

## Allowed Intervention

Allowed:

- replay over the saved v0.6 combined JSONL;
- deterministic rules that only drop or suppress an existing predicted
  `unknown` SeizureFrequency event;
- rules based on evidence text, candidate type, predicted state, local
  temporal/state cues, and already emitted sibling predictions;
- action-count logging for every suppression rule.

Not allowed:

- new LLM calls;
- adding new predicted events;
- changing active-rate or seizure-free predictions directly;
- using gold labels inside the rule implementation;
- inspecting Gan holdout row-level failures.

Rule portability category: `seizure_frequency`. Any CUI-only rendering repair
must be separately labeled `benchmark_format`.

## Metrics

Report all of the following against the fixed v0.6 baseline:

- headline SF F1 / precision / recall / TP / FP / FN;
- state-slice F1 / precision / recall / TP / FP / FN;
- unknown FP and FN counts;
- active-rate and seizure-free recall deltas;
- evidence validity;
- suppression action counts by rule.

## Success Gate

Promote the suppression layer only if all conditions hold:

- headline SF F1 improves by at least `0.010`;
- unknown FP count drops by at least `5`;
- unknown FN count increases by no more than `2`;
- active-rate recall drops by no more than `0.005`;
- seizure-free recall drops by no more than `0.005`;
- evidence validity remains at least `0.99`;
- every suppression action is attributable to a named rule.

## Stop Rule

Stop and reject the layer if either active-rate or seizure-free recall regresses
by more than `0.005`, even if headline F1 improves. Also reject if the gain comes
from broad unknown removal rather than a small set of named, clinically
interpretable suppression rules.

## Claim Boundaries

Supported if the gate passes:

> A predeclared deterministic unknown-suppression hard-slice reduced
> SeizureFrequency unknown over-emission after v0.6 without materially
> regressing active-rate or seizure-free recall.

Not supported even if the gate passes:

> SeizureFrequency generalizes beyond dev140.

> The ExECTv2 key-family architecture is benchmark-complete.

