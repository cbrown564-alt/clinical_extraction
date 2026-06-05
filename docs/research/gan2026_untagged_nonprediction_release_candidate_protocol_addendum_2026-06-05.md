# Gan 2026 Untagged Nonprediction Release Candidate Protocol Addendum

Date: 2026-06-05

## Purpose

This addendum freezes `untagged_nonprediction_release_candidate_v0` as a
validation-development candidate patch before any broader assembly use.

It is not a benchmark protocol, does not authorize locked-test row-level use,
and does not authorize holdout evaluation. Any holdout-facing run requires a
separate frozen protocol and explicit user authorization.

## Split And Source Artifacts

Split manifest: `gan2026_split_v1`

Eligible surface: validation750 only.

Frozen source artifacts:

- Component matrix:
  `experiments/gan2026_hybrid_multi_component_staged_assembly_v0_validation750_component_matrix_2026-06-04.csv`
- H2/H4 validation component-stress panel:
  `experiments/gan2026_h2_h4_validation_component_stress_panel_v0_2026-06-05.json`
- H2/H4 validation component-stress ablation:
  `experiments/gan2026_h2_h4_validation_component_stress_ablation_v0_2026-06-05.json`
- Nonprediction recovery audit:
  `experiments/gan2026_nonprediction_recovery_audit_v0_2026-06-05.json`
- Release-candidate accounting:
  `experiments/gan2026_untagged_nonprediction_release_candidate_v0_2026-06-05.json`

No locked-test row-level artifacts were used to design or score this addendum.

## Frozen Release Rule

For each validation row in the staged assembly component matrix:

1. If the staged final policy emits `abstain` or `human_review`, and
2. the row has no hidden-family tags, and
3. the deterministic comparator has a Gan-compatible label,
4. then release the row as `predict` with the deterministic comparator label.

All other rows keep the staged final-policy action and label unchanged.

This is deterministic-comparator fallback. Prediction-bearing ownership for
released rows must be reported as deterministic or safety-floor fallback, not as
LLM-first selection or LLM semantic rescue.

## Frozen Validation Gate

The release rule passed the validation no-regression gate with:

| Metric | Value |
| --- | ---: |
| validation rows | 750 |
| released rows | 19 |
| release-correct rows | 19 |
| release-wrong rows | 0 |
| candidate prediction-bearing rows | 735 |
| candidate correct prediction rows | 697 |
| H6 controls | 37 |
| H6 control regressions | 0 |

Release transitions:

| Transition | Rows |
| --- | ---: |
| `C_to_abstain` | 17 |
| `C_to_review` | 2 |

The broader `all_nonpredictions` lane remains rejected because it would release
34 nonprediction rows while including 15 wrong-baseline releases.

## Stop Rules

Reject or revise this candidate before any broader assembly use if any of the
following occur:

- any released row is wrong under validation development accounting;
- any H6 control regression appears;
- any hidden-family-tagged row becomes eligible for release;
- the rule changes scorer policy, gold labels, label normalization, or split
  membership;
- released rows are claimed as LLM-owned predictions;
- the candidate is used on locked test without a separate frozen holdout
  protocol and explicit authorization.

## Claim Boundary

This addendum supports only this claim:

`untagged_nonprediction_release_candidate_v0` is a validation-development
candidate patch that recovers deterministic-correct staged nonpredictions with
no observed validation release regressions under the frozen accounting above.

It does not support a benchmark-comparable claim, a generalization claim, a
test450 claim, or an LLM-first improvement claim.

## Next Required Artifact

Before any holdout-facing protocol, materialize an auditable assembled candidate
artifact from this release rule. The artifact must record row-level source
fields, release eligibility, original staged action, fallback label, candidate
action, component ownership, H6 membership, and aggregate accounting.
