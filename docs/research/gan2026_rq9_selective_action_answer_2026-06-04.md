# Gan 2026 RQ9 Selective-Action Answer

This is a validation-development answer for RQ9: whether the system should make
a prediction, abstain, or route to human review on ambiguous seizure-frequency
rows.

It synthesizes the v3 selective-action router and its follow-up pressure
artifacts. It does not change scorer policy, gold labels, prompts, deterministic
extraction rules, projection policy, locked-test behavior, or
benchmark-comparable claims.

## Answer

RQ9 is answered for saved validation replay as a selective-action problem, not
as whole-pipeline F1. The current best policy is:

- predict on ordinary frequency, seizure-free, no-reference, stable `unknown`,
  cluster/convention, and gold-blinded trigger-context rows;
- abstain on true trigger-only/unquantified evidence and missing-anchor rows;
- route last-event boundary rows to human review;
- keep cluster/convention rows prediction-bearing, with verifier monitoring for
  convention-risk subfamilies.

The v3 router covers 716/750 validation rows, abstains on 26, routes 8 to human
review, and has covered-row Purist accuracy 0.9469. It is useful as a
validation-development selective-action artifact, not as a benchmark-comparable
or holdout-facing claim.

## Evidence Base

- RQ9 contract:
  `docs/research/gan2026_rq9_selective_action_evaluation_contract_2026-06-04.md`
- Unknown/drop-attack boundary policy:
  `docs/research/gan2026_rq9_unknown_drop_attack_boundary_policy_2026-06-04.md`
- V3 selective-action router:
  `experiments/gan2026_rq9_selective_action_router_v3_2026-06-04.*`
- V2 abstention pressure:
  `experiments/gan2026_rq9_abstention_pressure_v0_2026-06-04.*`
- Trigger-context predeclaration:
  `docs/research/gan2026_rq9_trigger_context_narrowing_predeclaration_2026-06-04.md`
- Last-event decision:
  `experiments/gan2026_rq9_last_event_boundary_decision_2026-06-04.*`
- Cluster/convention monitoring:
  `docs/research/gan2026_rq9_cluster_convention_monitoring_predeclaration_2026-06-04.md`
  and `experiments/gan2026_rq9_cluster_convention_monitoring_2026-06-04.*`

## Router Evolution

| Router | Covered | Abstain | Human review | Selective accuracy | Main change |
| --- | ---: | ---: | ---: | ---: | --- |
| v0 | 555/750 | 41 | 154 | 0.9568 | Conservative cluster/convention review |
| v2 | 701/750 | 41 | 8 | 0.9458 | Cluster/convention no longer default review |
| v3 | 716/750 | 26 | 8 | 0.9469 | Gold-blinded trigger-context narrowing |

The useful movement is not a raw accuracy improvement. It is selective-action
calibration: v3 sharply reduces over-review and over-abstention while preserving
review for cases where policy is not stable enough to predict.

## Mechanism

### Trigger Context

The v2 abstention-pressure artifact found 26 trigger-conditioned rows with
non-sentinel candidate labels. Releasing all of them would have been unsafe:
17/26 were development-safe if predicted, but 9/26 were development-unsafe.

The predeclared v3 rule releases only rows with a non-sentinel label, no
`unknown_gold_boundary`, and gold-blinded evidence that names seizure/event
frequency context. It moves 15 trigger abstentions to prediction, and all 15 are
development-safe in offline accounting.

### Missing Anchors

The two missing-anchor rows remain abstentions. They do not have a stable
denominator/window under the frozen boundary policy, so prediction would require
an unstated temporal assumption.

### Last-Event Boundaries

The eight last-event rows remain human review. The slice is not ready for a
frozen date-window projection policy: four rows are unknown-convention
seizure-free projection risks, two are unresolved last-event unknown boundaries,
and two are recent-event frequency-selection failures. A single date rule would
either emit development-wrong seizure-free labels or miss the frequency-selection
failure mode.

### Cluster And Convention Boundaries

V3 keeps all 115 prediction-bearing cluster/convention rows prediction-bearing.
Offline development accounting is 104/115 safe and 11/115 unsafe. The monitoring
artifact assigns 61 rows to high-priority verifier monitoring and 54 to routine
monitoring. This is not a router action; it is an audit queue for future
adjudication or verifier experiments.

## Deterministic Baseline Role

The saved source candidate is treated as the prediction-bearing source for this
selective-action study. Deterministic rules and the safety floor are not claimed
as a general RQ9 solution; they provide the source predictions whose use should
be covered, abstained, reviewed, or monitored. RQ9 is answered by the action
policy around those predictions, not by another aggregate validation score.

## Hidden-Family Readout

The policy is strongest for:

- clear ordinary frequency and seizure-free rows;
- stable `unknown` rows with no convertible current/recent rate;
- cluster/convention rows when kept prediction-bearing and separately monitored;
- trigger-context rows where the selected evidence names a baseline/current
  seizure or event rate.

The weak families remain:

- true trigger-only or condition-only evidence without baseline rate;
- missing-anchor and since-anchor statements;
- last-event boundaries;
- cluster/convention rows whose final label flattens cluster/per-cluster
  semantics or uses sentinel/no-reference labels.

## Transfer Confidence

Development confidence is moderate for the selective-action framing and v3
policy, because the artifacts cover the full validation750 replay and preserve
row-level action packets. Holdout-transfer confidence is low to moderate. The
main risks are validation-shaped ambiguity heuristics, Gan-specific convention
boundaries, and reliance on saved source predictions from the current candidate.

No locked-test or benchmark-comparable claim is authorized. A holdout-facing use
would need a frozen pre-run protocol that fixes the router version, monitoring
slices, review accounting, scorer, source candidate, and inspection policy
before any test execution.

## Promotion Boundary

V3 may be treated as the current validation-development RQ9 selective-action
artifact. It should not be promoted as a final pipeline or benchmark claim.

Allowed next uses:

- paper-facing validation-development tables for coverage, selective accuracy,
  abstention/review rates, and monitoring burden;
- predeclared hard-slice or synthetic robustness checks for trigger, missing
  anchor, last-event, and cluster/convention families;
- a frozen holdout-audit protocol if the broader candidate is otherwise ready.

Not allowed:

- using v3 to rewrite gold labels or scorer policy;
- treating monitored cluster/convention rows as human-review rows in headline
  coverage;
- tuning on locked-test row-level failures;
- claiming benchmark-comparable performance.

## Decision

RQ9 is answered for saved validation replay. The answer is selective action with
bounded prediction, abstention, human review, and monitoring, not broad
abstention and not wholesale prediction on every hard family.

## Next Action

Before any holdout-facing use, write a frozen RQ9 selective-action audit protocol
covering v3, the source candidate, monitoring slices, metrics, and permitted
post-run inspection.
