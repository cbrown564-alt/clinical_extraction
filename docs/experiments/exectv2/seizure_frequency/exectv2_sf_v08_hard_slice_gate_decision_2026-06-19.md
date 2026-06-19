# ExECTv2 SF v0.8 Hard-Slice Gate Decision

Date: 2026-06-19
Scope: SeizureFrequency v0.7 residuals on dev140.
Decision status: rejected for prediction-bearing v0.8 implementation.

## Decision

Do not make a prediction-bearing SeizureFrequency v0.8 change from this panel.
The hard-slice diagnostic is useful as error taxonomy evidence, but no single
predeclared bucket/action class clears the attribution, non-gold-feature, and
stop-rule checks required by the v0.8 predeclaration.

Recommended disposition: stop SF v0.8 as a diagnostic-only slice. Do not write
an implementation-slice predeclaration and do not edit SF prediction code from
this evidence.

## Panel Counts

Source panel:
`experiments/exectv2_sf_v08_hard_slice_panel_dev140_20260618.json`

Source human readout:
`experiments/exectv2_sf_v08_hard_slice_panel_dev140_20260618.md`

Fixed baseline:
`experiments/exectv2_hybrid_sf_unknown_suppression_v07_dev140_20260618.jsonl`

| Surface | Count |
| --- | ---: |
| Rows | 140 |
| Residual records | 82 |
| Residual units | 84 |

Possible action counts:

| Action | Count |
| --- | ---: |
| `no_action` | 35 |
| `drop` | 21 |
| `repair_state` | 12 |
| `repair_benchmark_format` | 9 |
| `repair_ownership` | 4 |
| `add` | 3 |

Bucket/action counts:

| Bucket | Action | Count | Gate read |
| --- | --- | ---: | --- |
| `diagnosis_context_span` | `drop` | 21 | Fails non-gold-feature and stop-rule safety. |
| `diagnosis_context_span` | `no_action` | 20 | Diagnostic only. |
| `state_swap` | `repair_state` | 12 | Fails attribution/non-gold-feature directionality. |
| `seizure_free_cui_convention` | `repair_benchmark_format` | 9 | Fails non-gold-feature directionality for implementation. |
| `generic_named_ownership` | `repair_ownership` | 4 | Fails minimum volume. |
| `other_or_ambiguous` | `add` | 3 | Fails minimum volume and ambiguity rule. |
| `other_or_ambiguous` | `no_action` | 13 | Diagnostic only. |
| `true_candidate_gap` | `no_action` | 2 | Diagnostic only. |

## Gate Checks

The predeclared implementation gate required one primary bucket/action class
with at least 5 possible fixes, an explicit non-gold feature available in the
v0.7 artifact for at least 80 percent of sampled examples, one named action and
portability category, replayable ablation input, a stop condition protecting
active-rate and seizure-free recall, and stated collateral risk.

`diagnosis_context_span/drop` has enough apparent fixes (`21`), but the only
shared feature is the broad context-span cue. That cue is not action-clean: the
same bucket also contains `20` gold-side `no_action` units, including active-rate
and seizure-free gold residuals with candidate spans. A rule that drops on this
feature would be a broad suppression rule, not a finite residual repair, and it
has obvious recall risk for both active-rate and seizure-free states.

`state_swap/repair_state` has enough units (`12`), but the direction of repair is
defined by paired residual disagreement. Only `5` of the `12` units have a
candidate span available, and the panel feature is a diagnostic comparison
between unmatched gold and prediction sides, not a prediction-time feature.
Implementing it would require inferring the gold-side target state, so
attribution and non-gold-feature checks fail.

`seizure_free_cui_convention/repair_benchmark_format` has enough units (`9`) and
is benchmark-format rather than clinical-state repair. It still fails the
implementation gate because the needed direction is not consistent from
prediction-only features: some pairs would need generic seizure-free rendering
changed toward `C1299590`, while others would need the opposite convention. A
broad dual-render or global remap would not be limited to the residual bucket and
could trade false negatives for new false positives without a clean stop rule.

`generic_named_ownership/repair_ownership` (`4`) and `other_or_ambiguous/add`
(`3`) fail the minimum-count threshold before the feature and stop-rule checks
are reached. `true_candidate_gap` has no direct prediction rule surface.

## Next Step

No SF v0.8 implementation step is authorized. Keep the v0.8 panel as a dev140
diagnostic artifact. If SeizureFrequency work resumes later, start a new
predeclaration from prediction-time features, not from this failed v0.8 gate.
